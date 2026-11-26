"""Hourly BESS screening for course 47211. Run from the project root.
All hourly energy flows are MWh; since dt = 1 h, their numerical values
also represent average power in MW. Battery capacity is usable capacity.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PJ_PER_MWH = 3.6e-6
ETA_CH = ETA_DIS = 0.95  # illustrative, not technology-specific data
BIOMASS_BUDGET_PJ = 150.0  # assumed electrical output, not fuel input
BIOMASS_POWER_MW = 20_000.0  # illustrative upper bound, not optimized
CAPACITIES_GWH = [0, 25, 50, 100, 200]
INPUT = Path('data/ProductionConsumptionSettlement_DK_modified.csv')
OUTPUT = Path('data/battery_results')


def load_data(path):
    d = pd.read_csv(path, sep=';', decimal=',')
    d['HourUTC'] = pd.to_datetime(d['HourUTC'])
    d = d.sort_values('HourUTC').reset_index(drop=True)
    assert len(d) == 8760 and d['HourUTC'].is_unique
    assert d['HourUTC'].diff().dropna().eq(pd.Timedelta(hours=1)).all()
    # Normalize without intermediate rounding.
    d['RenewableMWh'] = d['TotalRenewableMWh'] * (580 / (d['TotalRenewableMWh'].sum()*PJ_PER_MWH))
    d['DirectDemandMWh'] = d['GrossConsumptionScaledMWh'] + d['TrucksElectricityDemandMWh']
    d['NetMWh'] = d['RenewableMWh'] - d['DirectDemandMWh']
    assert np.isfinite(d[['RenewableMWh','DirectDemandMWh']]).all().all()
    return d


def dispatch(net, capacity_mwh, power_mw, initial_soc):
    soc = initial_soc
    biomass_left = BIOMASS_BUDGET_PJ / PJ_PER_MWH
    rows = []
    for n in net:
        charge = discharge = biomass = surplus = unmet = 0.0
        if n >= 0:
            charge = min(n, power_mw, max(0, capacity_mwh-soc)/ETA_CH)
            soc += ETA_CH*charge
            surplus = n-charge
        else:
            discharge = min(-n, power_mw, soc*ETA_DIS)
            soc -= discharge/ETA_DIS
            remaining = max(0, -n-discharge)
            biomass = min(remaining, BIOMASS_POWER_MW, biomass_left)
            biomass_left = max(0, biomass_left-biomass)
            unmet = remaining-biomass
        loss = charge*(1-ETA_CH) + discharge*(1/ETA_DIS-1)
        rows.append((soc, charge, discharge, biomass, surplus, unmet, loss))
    return pd.DataFrame(rows, columns=['SOC_MWh','Charge_MWh','Discharge_MWh',
        'Biomass_MWh','SurplusForPtX_MWh','Unmet_MWh','Loss_MWh'])


def cyclic_dispatch(net, cap, power):
    # Repeat the same annual profile until end SOC equals initial SOC.
    initial = 0.0
    for _ in range(1000):
        result = dispatch(net, cap, power, initial)
        end = result['SOC_MWh'].iloc[-1]
        if abs(end-initial) < 1e-6:
            assert np.allclose(net + result['Discharge_MWh'] + result['Biomass_MWh'] + result['Unmet_MWh'], result['Charge_MWh']+result['SurplusForPtX_MWh'], atol=1e-6)
            assert np.isclose(end-initial, (result['Charge_MWh']*ETA_CH-result['Discharge_MWh']/ETA_DIS).sum(), atol=1e-5)
            return result
        initial = end
    raise RuntimeError('Cyclic SOC did not converge')


def main():
    d = load_data(INPUT)
    net = d['NetMWh'].to_numpy()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    summary = []
    profiles = {}
    for gwh in CAPACITIES_GWH:
        cap = gwh*1000
        power = cap/4
        r = cyclic_dispatch(net, cap, power)
        profiles[gwh] = r
        row = {'capacity_GWh':gwh, 'rated_power_GW':power/1000,
               'max_charge_GW':r.Charge_MWh.max()/1000,
               'max_discharge_GW':r.Discharge_MWh.max()/1000,
               'max_biomass_GW':r.Biomass_MWh.max()/1000,
               'max_surplus_GW':r.SurplusForPtX_MWh.max()/1000,
               'max_SOC_GWh':r.SOC_MWh.max()/1000}
        for c in ['Charge','Discharge','Biomass','SurplusForPtX','Unmet','Loss']:
            row[c+'_PJ'] = r[c+'_MWh'].sum()*PJ_PER_MWH
        summary.append(row)
        pd.concat([d[['HourUTC','HourDK','RenewableMWh','DirectDemandMWh','NetMWh']],r],axis=1).to_csv(OUTPUT/f'hourly_{gwh}GWh.csv',index=False)
    s = pd.DataFrame(summary)
    s.to_csv(OUTPUT/'battery_scenarios.csv',index=False)
    print(s.round(3).to_string(index=False))
    print('Annual renewable, demand, net PJ:', d[['RenewableMWh','DirectDemandMWh','NetMWh']].sum()*PJ_PER_MWH)
    print('Peak net surplus/deficit GW:', net.max()/1000, -net.min()/1000)
    ax = s.plot(x='capacity_GWh', y=['Biomass_PJ','SurplusForPtX_PJ','Loss_PJ'], marker='o')
    ax.set(xlabel='Usable battery capacity [GWh]',ylabel='Annual energy [PJ]',title='Battery sizing sensitivity (before PtX)')
    ax.grid(alpha=.25)
    plt.tight_layout(); plt.savefig(OUTPUT/'battery_scenarios.png',dpi=180); plt.close()
    # Example operating profile: first seven days, 50 GWh scenario.
    r = profiles[50]
    sl = slice(0,168)
    fig, ax = plt.subplots(figsize=(11,4))
    t = d.HourUTC.iloc[sl]
    for values, label in [(d.NetMWh,'Prosumption'),(r.Biomass_MWh,'Biomass'),(r.SurplusForPtX_MWh,'Available for PtX'),(r.Charge_MWh,'Battery charge'),(r.Discharge_MWh,'Battery discharge')]:
        ax.plot(t,values.iloc[sl]/1000,label=label)
    ax.set(ylabel='Hourly mean power [GW]',title='Example dispatch: 50 GWh battery, first 7 days (UTC)'); ax.legend(ncol=3); ax.grid(alpha=.25); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUTPUT/'example_dispatch.png',dpi=180); plt.close(fig)

if __name__ == '__main__':
    main()
