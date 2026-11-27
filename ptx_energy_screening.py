"""System-level flexible electrical demand screening, course 47211.
Run from project root alongside battery_simulation.py. No process model.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import battery_simulation as b

TARGET_PJ = 35.42  # annual final fuel energy demand
EFFICIENCIES = [0.40, 0.50, 0.55]
POWER_GW = [2, 4, 6, 8, 10]
OUT = Path('data/ptx_results')


def min_power(surplus, target_mwh):
    if surplus.sum() < target_mwh:
        return np.nan
    lo, hi = 0.0, float(surplus.max())
    for _ in range(60):
        mid = (lo + hi) / 2
        if np.minimum(surplus, mid).sum() >= target_mwh:
            hi = mid
        else:
            lo = mid
    return hi / 1000


def main():
    data = b.load_data(b.INPUT)
    net = data.NetMWh.to_numpy()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for capacity in b.CAPACITIES_GWH:
        r = b.cyclic_dispatch(net, capacity * 1000, capacity * 250)
        surplus = r.SurplusForPtX_MWh.to_numpy()
        for eta in EFFICIENCIES:
            target_el = TARGET_PJ / eta
            minimum = min_power(surplus, target_el / b.PJ_PER_MWH)
            for power in POWER_GW:
                # Potential consumption, not a physical process schedule.
                potential = np.minimum(surplus, power * 1000).sum() * b.PJ_PER_MWH
                used = min(target_el, potential)
                rows.append(dict(battery_GWh=capacity, efficiency=eta,
                                 flexible_load_GW=power, minimum_load_GW=minimum,
                                 potential_electricity_PJ=potential,
                                 target_electricity_PJ=target_el,
                                 allocated_electricity_PJ=used,
                                 final_energy_PJ=used * eta,
                                 demand_coverage_pct=100 * used * eta / TARGET_PJ,
                                 residual_surplus_PJ=surplus.sum()*b.PJ_PER_MWH-used,
                                 biomass_PJ=r.Biomass_MWh.sum()*b.PJ_PER_MWH,
                                 battery_loss_PJ=r.Loss_MWh.sum()*b.PJ_PER_MWH,
                                 unmet_direct_PJ=r.Unmet_MWh.sum()*b.PJ_PER_MWH))
    s = pd.DataFrame(rows)
    s.to_csv(OUT/'ptx_scenarios.csv', index=False)
    print(s.round(3).to_string(index=False))

if __name__ == '__main__':
    main()
