from pathlib import Path

import pandas as pd
import os

DATA_DIRECTORY = Path(__file__).parent / "data"
INPUT_PATH = DATA_DIRECTORY / "ProductionConsumptionSettlement.csv"
OUTPUT_PATH = DATA_DIRECTORY / "ProductionConsumptionSettlement_DK.csv"


def sum_dk1_dk2(
	input_path: str | Path = INPUT_PATH,
	output_path: str | Path = OUTPUT_PATH,
) -> pd.DataFrame:
	"""Sum the DK1 and DK2 rows for each timestamp and write a new CSV file."""
	data = pd.read_csv(input_path, sep=";", decimal=",")

	group_columns = ["HourUTC", "HourDK"]
	if "PriceArea" not in data.columns:
		raise ValueError("The input data must contain a PriceArea column")
	if any(column not in data.columns for column in group_columns):
		raise ValueError("The input data must contain HourUTC and HourDK columns")

	combined_data = (
		data.groupby(group_columns, as_index=False, sort=False)
		.sum(numeric_only=True)
	)
	combined_data.to_csv(output_path, sep=";", decimal=",", index=False)
	return combined_data


if __name__ == "__main__":
	cwd = os.getcwd()
	input_path = os.path.join(cwd, "data", "ProductionConsumptionSettlement.csv")
	output_path = os.path.join(cwd, "data", "ProductionConsumptionSettlement_DK.csv")
	sum_dk1_dk2(input_path=input_path, output_path=output_path)
