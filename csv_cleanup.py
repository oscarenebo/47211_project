# Clean up the CSV file from Energinet's API by removing columns that are not needed for the project.
# So it's not so biiiiiiiiig!!!!

import argparse
import csv
from pathlib import Path
from typing import Iterable

DATA_DIRECTORY = Path(__file__).parent / "data"
DEFAULT_INPUT_PATH = DATA_DIRECTORY / "ProductionConsumptionSettlement_DK_total.csv"
DEFAULT_OUTPUT_PATH = DATA_DIRECTORY / "ProductionConsumptionSettlement_small.csv"
DEFAULT_COLUMNS_TO_REMOVE = [
	"CentralPowerMWh",
	"LocalPowerMWh",
	"CommercialPowerMWh",
	"LocalPowerSelfConMWh",
	"HydroPowerMWh",
	"UnknownProdMWh",
	"ExchangeNO_MWh",
	"ExchangeSE_MWh",
	"ExchangeGE_MWh",
	"ExchangeNL_MWh",
	"ExchangeGB_MWh",
	"ExchangeGreatBelt_MWh",
	"GridLossTransmissionMWh",
	"GridLossInterconnectorsMWh",
	"GridLossDistributionMWh",
	"PowerToHeatMWh",
]


def remove_columns(
	input_path: str | Path,
	output_path: str | Path,
	columns_to_remove: Iterable[str],
	delimiter: str = ";",
) -> Path:
	"""Write a copy of a CSV without the named columns."""
	source = Path(input_path)
	destination = Path(output_path)
	columns = set(columns_to_remove)

	if not columns:
		raise ValueError("Select at least one column to remove")
	if len(delimiter) != 1:
		raise ValueError("The delimiter must be a single character")
	if source.resolve() == destination.resolve():
		raise ValueError("The output path must be different from the input path")

	with source.open("r", encoding="utf-8-sig", newline="") as source_file:
		reader = csv.reader(source_file, delimiter=delimiter)
		try:
			header = next(reader)
		except StopIteration as error:
			raise ValueError("The input CSV is empty") from error

		missing_columns = columns - set(header)
		if missing_columns:
			names = ", ".join(sorted(missing_columns))
			raise ValueError(f"Column(s) not found in the input CSV: {names}")

		kept_indexes = [
			index for index, name in enumerate(header) if name not in columns
		]

		with destination.open("w", encoding="utf-8", newline="") as output_file:
			writer = csv.writer(output_file, delimiter=delimiter)
			writer.writerow([header[index] for index in kept_indexes])
			for row in reader:
				if len(row) != len(header):
					raise ValueError(
						f"Expected {len(header)} fields but found {len(row)} "
						f"at line {reader.line_num}"
					)
				writer.writerow([row[index] for index in kept_indexes])

	return destination


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Copy a CSV file while removing selected columns."
	)
	parser.add_argument(
		"input",
		nargs="?",
		type=Path,
		default=DEFAULT_INPUT_PATH,
		help=f"CSV file to clean (default: {DEFAULT_INPUT_PATH})",
	)
	parser.add_argument(
		"output",
		nargs="?",
		type=Path,
		default=DEFAULT_OUTPUT_PATH,
		help=f"path for the cleaned CSV (default: {DEFAULT_OUTPUT_PATH})",
	)
	parser.add_argument(
		"--drop-columns",
		nargs="+",
		default=DEFAULT_COLUMNS_TO_REMOVE,
		metavar="COLUMN",
		help="exact column names to remove (defaults to the project columns)",
	)
	parser.add_argument(
		"--delimiter",
		default=";",
		help="single-character CSV delimiter (default: ';')",
	)
	args = parser.parse_args()

	try:
		output_path = remove_columns(
			args.input,
			args.output,
			args.drop_columns,
			delimiter=args.delimiter,
		)
	except (OSError, ValueError) as error:
		parser.error(str(error))

	print(f"Saved cleaned CSV to {output_path}")


if __name__ == "__main__":
	main()