"""Top-level package exports for the Triathlon analysis toolkit."""

from .analysis import (
	add,
	best_predictor,
	discipline_correlations,
	run_analysis_pipeline,
	summarize_participants,
	top_finishers_by_gender,
)
from .cleaning import clean_results_frame, run_cleaning_pipeling

__all__ = [
	"add",
	"best_predictor",
	"clean_results_frame",
	"discipline_correlations",
	"run_analysis_pipeline",
	"run_cleaning_pipeling",
	"summarize_participants",
	"top_finishers_by_gender",
]
