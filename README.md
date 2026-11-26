# 47211 Project

Small data-processing and analysis project for the Danish 100% sustainable energy system study.

## Files

- `data_processing.py` combines the DK1 and DK2 rows in the raw Energinet CSV for each timestamp. Run it from the project directory to create `data/ProductionConsumptionSettlement_DK.csv`.
- `csv_cleanup.py` copies a CSV while streaming through it and removes selected columns.
- `total_annual_energy_consumption_dk.py` stores the project assumptions and annual energy demands in PJ, including the available biomass and the electrified-truck assumption.
- `myfunctions.py` contains the reusable `dataPlot()` helper for plotting selected columns from the processed CSV. It supports time ranges, line/scatter plots, and daily, weekly, or monthly aggregation.
- `ds_api.ipynb` downloads 2024 truck statistics from Statistics Denmark's `NVG1` API, formats the results, calculates transport-work shares, and saves `data/NVG1_2024.csv`.
- `plotting.ipynb` loads the processed electricity data, combines wind and solar production, calculates scaling factors and prosumption, and plots the baseline and electrified-trucking scenarios.

## Basic use

1. Put the raw Energinet file at `data/ProductionConsumptionSettlement.csv`.
2. Run `data_processing.py` to create the DK1+DK2 dataset:

```text
python data_processing.py
```

3. Open and run `plotting.ipynb`. Run `ds_api.ipynb` separately if the truck statistics are needed.

The notebooks expect to be run with the project directory as the working directory. Required Python packages include `pandas`, `matplotlib`, and `requests`.

To create a smaller CSV, run `csv_cleanup.py`. It reads
`data/ProductionConsumptionSettlement.csv`, removes the configured project
columns, and writes `data/ProductionConsumptionSettlement_clean.csv`. The
default delimiter is `;`, matching the Energinet files. You can optionally
provide different paths and columns:

```text
python csv_cleanup.py data/ProductionConsumptionSettlement.csv data/ProductionConsumptionSettlement_clean.csv --drop-columns PriceArea ExchangeNO_MWh ExchangeSE_MWh
```