# 47211 Project

Small data-processing and analysis project for the Danish 100% sustainable energy system study.

## Files

- `data_processing.py` combines the DK1 and DK2 rows in the raw Energinet CSV for each timestamp. Run it from the project directory to create `data/ProductionConsumptionSettlement_DK.csv`.
- `csv_cleanup.py` copies a CSV while streaming through it and removes selected columns.
- `total_annual_energy_consumption_dk.py` stores the project assumptions and annual energy demands in PJ, including the available biomass and the electrified-truck assumption.
- `myfunctions.py` contains the reusable `dataPlot()` helper for plotting selected columns from the processed CSV. It supports time ranges, line/scatter plots, and daily, weekly, or monthly aggregation.
- `ds_api.ipynb` downloads 2024 truck statistics from Statistics Denmark's `NVG1` API, formats the results, calculates transport-work shares, and saves `data/NVG1_2024.csv`.
- `plotting.ipynb` loads the processed electricity data, combines wind and solar production, calculates scaling factors and prosumption, and adds hourly truck electricity and methanol demand.
- `simulation.ipynb` runs an hourly, fixed-capacity dispatch simulation for electricity, battery storage, biomass generation, P2X methanol production, and methanol storage.

## Basic use

1. Put the raw Energinet file at `data/ProductionConsumptionSettlement.csv`.
2. Run `data_processing.py` to create the DK1+DK2 dataset:

```text
python data_processing.py
```

3. Ensure `data/ProductionConsumptionSettlement_small.csv` is available, then run `plotting.ipynb` through the trucking-demand cell to create `data/ProductionConsumptionSettlement_DK_modified.csv`. Run `ds_api.ipynb` separately if the truck statistics are needed.
4. Open and run `simulation.ipynb` to simulate the hourly electricity and truck-methanol balances. The example plant capacities and efficiencies in that notebook are illustrative inputs and should be replaced before interpreting scenario results.

The notebooks expect to be run with the project directory as the working directory. Required Python packages include `pandas`, `matplotlib`, and `requests`.

To create a smaller CSV, run `csv_cleanup.py`. It reads
`data/ProductionConsumptionSettlement.csv`, removes the configured project
columns, and writes `data/ProductionConsumptionSettlement_clean.csv`. The
default delimiter is `;`, matching the Energinet files. You can optionally
provide different paths and columns:

```text
python csv_cleanup.py data/ProductionConsumptionSettlement.csv data/ProductionConsumptionSettlement_clean.csv --drop-columns PriceArea ExchangeNO_MWh ExchangeSE_MWh
```