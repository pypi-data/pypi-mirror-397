"""Utility functions for cleaning raw triathlon race data."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

# Columns we expect to contain time data. Each gets a companion "(sec)" column.
TIME_COLUMNS: Sequence[str] = (
	"Overall Time",
	"Swim Time",
	"Bike Time",
	"Run Time",
	"Transition 1 Time",
	"Transition 2 Time",
)


def parse_time_to_seconds(value: object) -> float:
	"""Convert hh:mm:ss or mm:ss strings (and floats) into total seconds."""
	if pd.isna(value):
		return np.nan
	text = str(value).strip()
	if not text:
		return np.nan
	parts = [p for p in text.replace(".", ":").split(":") if p]
	try:
		if len(parts) == 2:
			minutes, seconds = (int(parts[0]), int(parts[1]))
			return minutes * 60 + seconds
		if len(parts) == 3:
			hours, minutes, seconds = (int(parts[0]), int(parts[1]), int(parts[2]))
			return hours * 3600 + minutes * 60 + seconds
	except ValueError:
		return np.nan
	return np.nan


def normalize_gender(value: object) -> str:
	"""Map messy gender labels into Male/Female buckets when possible."""
	if pd.isna(value):
		return ""
	text = str(value).strip().lower()
	if text in {"m", "male"}:
		return "Male"
	if text in {"f", "female"}:
		return "Female"
	return str(value).strip().title()


def _add_time_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
	for column in columns:
		if column in df.columns:
			df[f"{column} (sec)"] = df[column].apply(parse_time_to_seconds)


def clean_results_frame(frame: pd.DataFrame) -> pd.DataFrame:
	df = frame.copy()

	_add_time_columns(df, TIME_COLUMNS)

	if {"Transition 1 Time (sec)", "Transition 2 Time (sec)"}.issubset(df.columns):
		df["Transitions (sec)"] = (
			df["Transition 1 Time (sec)"] + df["Transition 2 Time (sec)"]
		)

	if "gender" in df.columns:
		df["gender_norm"] = df["gender"].apply(normalize_gender)

	if "Overall Time (sec)" in df.columns:
		df["Finished"] = df["Overall Time (sec)"].notna() & (
			df["Overall Time (sec)"] > 0
		)
	else:
		df["Finished"] = False

	if "Finish" in df.columns:
		df["Finished"] = df["Finished"] & (
			df["Finish"].astype(str).str.upper().str.strip() == "FIN"
		)

	return df


def run_cleaning_pipeling(source: str | Path | pd.DataFrame | None = None) -> pd.DataFrame:
	"""
	High-level entry point used in tutorials/tests.

	If ``source`` is provided it can be a dataframe or path to a CSV file,
	and a cleaned dataframe will be returned. When ``source`` is omitted the
	function simply prints a status message (keeping the original behaviour
	so existing tests continue to pass).
	"""
	print("Running cleaning pipeline...")
	if source is None:
		return pd.DataFrame()

	if isinstance(source, (str, Path)):
		raw = pd.read_csv(source)
	else:
		raw = source

	cleaned = clean_results_frame(raw)
	print(f"Parsed {len(cleaned):,} records.")
	return cleaned
