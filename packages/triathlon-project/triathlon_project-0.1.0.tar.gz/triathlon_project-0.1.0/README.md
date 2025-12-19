# Triathlon project

This is our STAT 386 Data Science Project. The repository bundles a Python package, Quarto site, automated tests, and a customizable Streamlit prototype.

## Quick start

```bash
uv sync
uv run pytest
```

## Streamlit prototype

- Edit `src/triathlon_project/streamlit_app.py` to point at your own data sources, cleaning logic, and visuals.
- Launch the toy UI with:

```bash
uv run streamlit run src/triathlon_project/streamlit_app.py
```

- Use the sidebar toggles to preview how `run_cleaning_pipeling` and `run_analysis_pipeline` outputs appear, then replace them with real charts or KPIs.

## Quarto site

Rebuild the public site (including the technical report placeholder) with:

```bash
uv run quarto render
```

Serve locally via `uv run quarto preview` while authoring docs.
