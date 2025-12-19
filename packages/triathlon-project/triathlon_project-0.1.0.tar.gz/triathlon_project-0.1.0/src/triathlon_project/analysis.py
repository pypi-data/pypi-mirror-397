"""Lightweight helpers for computing triathlon insights."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Mapping, Tuple

import pandas as pd

from triathlon_project.cleaning import clean_results_frame

DISCIPLINE_COLUMNS: Mapping[str, str] = {
	"Swim": "Swim Time (sec)",
	"Bike": "Bike Time (sec)",
	"Run": "Run Time (sec)",
	"Transitions": "Transitions (sec)",
}


def _ensure_dataframe(source: pd.DataFrame | str | Path) -> pd.DataFrame:
	if isinstance(source, (str, Path)):
		return pd.read_csv(source)
	return source


def summarize_participants(df: pd.DataFrame) -> Dict[str, int]:
	total = len(df)
	finishers = int(df.get("Finished", pd.Series(dtype=int)).sum())
	male = female = 0
	if "gender_norm" in df.columns:
		male = int((df["gender_norm"] == "Male").sum())
		female = int((df["gender_norm"] == "Female").sum())
	return {
		"participants": total,
		"finishers": finishers,
		"did_not_finish": total - finishers,
		"male": male,
		"female": female,
	}


def top_finishers_by_gender(
	fin_df: pd.DataFrame, genders: Iterable[str] = ("Female", "Male"), limit: int = 3
) -> Dict[str, pd.DataFrame]:
	results: Dict[str, pd.DataFrame] = {}
	for gender in genders:
		if "gender_norm" not in fin_df.columns:
			results[gender] = fin_df.iloc[0:0]
			continue
		sub = fin_df[fin_df["gender_norm"] == gender]
		results[gender] = sub.nsmallest(limit, "Overall Time (sec)")
	return results


def discipline_correlations(
	fin_df: pd.DataFrame, min_samples: int = 10
) -> Dict[str, float]:
	out: Dict[str, float] = {}
	for label, column in DISCIPLINE_COLUMNS.items():
		if column not in fin_df.columns or "Overall Time (sec)" not in fin_df.columns:
			continue
		valid = fin_df.dropna(subset=[column, "Overall Time (sec)"])
		if len(valid) <= min_samples:
			continue
		out[label] = valid[column].corr(valid["Overall Time (sec)"])
	return out


def best_predictor(fin_df: pd.DataFrame) -> Tuple[str, float] | Tuple[None, None]:
	cors = discipline_correlations(fin_df)
	if not cors:
		return None, None
	best_col = max(cors, key=cors.get)
	return best_col, cors[best_col]


def run_analysis_pipeline(
	source: pd.DataFrame | str | Path | None = None,
) -> Dict[str, object]:
	"""
	Convenience wrapper mirroring the behaviour of ``run_cleaning_pipeling``.

	If ``source`` is provided, the cleaned dataframe is fed into the summary
	helpers above and a dictionary of simple metrics is returned.
	"""
	print("Running analysis pipeline...")
	if source is None:
		return {}

	raw = _ensure_dataframe(source)
	cleaned = clean_results_frame(raw)
	if "Finished" in cleaned.columns:
		finished_mask = cleaned["Finished"].astype(bool)
	else:
		finished_mask = pd.Series(False, index=cleaned.index)
	fin_df = cleaned[finished_mask]

	result = {
		"participants": summarize_participants(cleaned),
		"top_finishers": top_finishers_by_gender(fin_df),
		"discipline_correlations": discipline_correlations(fin_df),
	}
	print("Analysis pipeline finished.")
	return result


def add(a, b):
	return a + b
