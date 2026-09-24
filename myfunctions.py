from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd


def dataPlot(
	columns: str | Iterable[str],
	file_path: str | Path | None = None,
	start_time: str | pd.Timestamp | None = None,
	end_time: str | pd.Timestamp | None = None,
	ax: plt.Axes | None = None,
	plot_type: str = "line",
	aggregation: str | None = None,
	title: str | None = None,
) -> plt.Axes:
	"""Plot selected columns from the production and consumption data.

	``start_time`` and ``end_time`` are inclusive. If neither is supplied,
	all rows in the CSV file are plotted. ``aggregation`` can be ``"daily"``,
	``"weekly"``, or ``"monthly"`` to plot summed MWh values for each period.
	``title`` sets the plot title when provided.
	"""
	data_path = (
		Path(file_path)
		if file_path is not None
		else Path(__file__).parent / "data" / "ProductionConsumptionSettlement_DK.csv"
	)
	data = pd.read_csv(
		data_path,
		sep=";",
		decimal=",",
	)
	data["HourDK"] = pd.to_datetime(data["HourDK"])

	selected_columns = [columns] if isinstance(columns, str) else list(columns)
	missing_columns = [column for column in selected_columns if column not in data.columns]
	if missing_columns:
		raise ValueError(f"Unknown data column(s): {', '.join(missing_columns)}")
	if not selected_columns:
		raise ValueError("At least one data column must be selected")

	if start_time is not None:
		data = data[data["HourDK"] >= pd.Timestamp(start_time)]
	if end_time is not None:
		data = data[data["HourDK"] <= pd.Timestamp(end_time)]
	if data.empty:
		raise ValueError("The selected time range contains no data")
	if plot_type not in {"line", "scatter"}:
		raise ValueError("plot_type must be either 'line' or 'scatter'")

	aggregation_rules = {
		"daily": "D",
		"weekly": "W-MON",
		"monthly": "MS",
	}
	if aggregation not in {None, *aggregation_rules}:
		raise ValueError(
			'aggregation must be None, "daily", "weekly", or "monthly"'
		)
	if aggregation is not None:
		data = (
			data.set_index("HourDK")[selected_columns]
			.resample(aggregation_rules[aggregation])
			.sum()
			.reset_index()
		)

	if ax is None:
		_, ax = plt.subplots()
	if plot_type == "scatter":
		for column in selected_columns:
			data.plot.scatter(x="HourDK", y=column, ax=ax, label=column, s=8)
	else:
		data.plot(x="HourDK", y=selected_columns, ax=ax)
	ax.set_xlabel("Time")
	ax.set_ylabel("Energy (MWh)")
	if title is not None:
		ax.set_title(title)
	ax.grid(True, alpha=0.3)
	return ax