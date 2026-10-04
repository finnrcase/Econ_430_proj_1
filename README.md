# UCLA Econ 430 — Project 1

**Course:** UCLA Econ 430 — Applied Econometrics with Python  
**Project:** Project 1 — Applied Econometric Analysis

## Research question

What fundamental firm characteristics explain differences in valuation multiples across publicly traded U.S. companies?

This project will study cross-sectional stock valuation. The repository currently contains original data downloads and organizational placeholders only. No data cleaning, variable construction, or econometric analysis has been performed.

## Data source

SimFin U.S. financial data. Original downloads are preserved in `data/raw/`:

| Dataset | Original file |
| --- | --- |
| Companies | `us-companies.zip` |
| Quarterly income statements | `us-income-quarterly.zip` |
| Quarterly balance sheets | `us-balance-quarterly.zip` |
| Quarterly cash flow statements | `us-cashflow-quarterly.zip` |
| Daily share prices | `us-shareprices-daily.zip` |

**Raw data must NEVER be manually edited.** Preserve each original archive exactly as downloaded, including its filename and contents. All future cleaning and transformations must be reproducible through Python and write derived datasets to `data/processed/`, leaving the raw originals untouched.

## Repository structure

```text
Econ_430_proj_1/
├── data/
│   ├── raw/          # Original, unchanged SimFin downloads
│   └── processed/    # Future reproducibly generated datasets
├── notebooks/        # Numbered workflow notebooks
├── src/              # Reusable Python modules
├── figures/          # Future generated figures
├── tables/           # Future generated tables
├── report/           # Final report and supporting writing
├── README.md
├── requirements.txt
└── .gitignore
```

Empty output directories contain `.gitkeep` files so Git can preserve the structure.

## Planned workflow

Raw data → data cleaning → construct a single cross-sectional company dataset → exploratory data analysis → variable selection → competing OLS models → model comparison → diagnostics → robustness testing → economic interpretation → final report.

| Notebook | Intended purpose |
| --- | --- |
| `01_build_dataset.ipynb` | Load and clean source data, then construct the cross-sectional company dataset. |
| `02_exploratory_analysis.ipynb` | Explore distributions and relationships in the constructed dataset. |
| `03_variable_selection.ipynb` | Assess candidate variables and justify specification choices. |
| `04_model_development.ipynb` | Develop competing OLS models and compare their results. |
| `05_diagnostics_robustness.ipynb` | Assess model diagnostics and robustness to alternative choices. |
| `06_results_interpretation.ipynb` | Interpret economic findings and prepare material for the final report. |

All notebooks currently contain markdown only. Python modules currently contain only module-level docstrings.

Potential future variables include EV/EBITDA or another appropriate valuation multiple, revenue growth, EBITDA margin, ROIC, debt/EBITDA, free cash flow margin, firm size or market capitalization, and sector/industry controls. These are tentative and have not been calculated.

## Python environment

`requirements.txt` lists the anticipated dependencies. When analysis begins, create a virtual environment and install them with:

```sh
python -m venv .venv
# Activate .venv using the command appropriate for your operating system.
python -m pip install -r requirements.txt
jupyter notebook
```

No packages are installed as part of repository organization. Dependency versions are currently unpinned; record the validated versions when the analytical workflow is developed so the final results can be reproduced.
