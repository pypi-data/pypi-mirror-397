# final-project-demo

Teaching scaffold for STAT 386 final projects. The repository bundles a Python package, Quarto site, automated tests, and a customizable Streamlit prototype.

We explore the relationship between MBA performance and salaries from 2018-2025. We developed a python package that follows our webscraping, EDA, and multiple linear regression. Our tutorial, documentation, and report are a quarto github pages website, with additonal interactive app via Streamlit.

## Quick start

```bash
uv sync
uv run pytest
```

## Streamlit prototype

- Edit `src/final_project_demo/streamlit_app.py` to point at your own data sources, cleaning logic, and visuals.
- Launch the toy UI with:

```bash
uv run streamlit run src/final_project_demo/streamlit_app.py
```

- Use the sidebar toggles to preview how `run_cleaning_pipeling` and `run_analysis_pipeline` outputs appear, then replace them with real charts or KPIs.

## Quarto site

Rebuild the public site (including the technical report placeholder) with:

```bash
uv run quarto render
```

Serve locally via `uv run quarto preview` while authoring docs.
