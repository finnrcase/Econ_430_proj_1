# UCLA Econ 430 — Project 1

## Research question

Do AI-exposed publicly traded firms trade at higher valuation multiples than other firms, after accounting for revenue growth, profitability, size, leverage, and industry?

## Historical snapshot and status

Valuation date: **September 30, 2025**, not current-day data. Notebook 1 prepares financial data and quality reports; no regressions or model selection have been run.

The financial-ready pool has **742 unique companies** after a provisional financial-industry exclusion. The working universe has **4,699 companies**. AI classification is **incomplete**: four primary-source seed reviews (NVIDIA and Microsoft exposed; Coca-Cola and P&G reviewed comparisons). Only three of those have complete candidate financial data. NVIDIA has missing short-term debt, which remains missing. The strict AI candidate therefore does **not** meet the assignment's 500-observation requirement. Six predictor concepts are available: AI exposure, revenue growth, EBITDA margin, log market cap, leverage, and categorical industry.

These are latest-restated financial values joined to historical prices. Publication-date filters do not make the files fully point-in-time. Only seven financial-ready firms have no later-restatement flags. Source chronology anomalies, a verified LiveWire operating-income discrepancy, D&A definition differences, the absent official industry-name dictionary, and share-history vintage need further review. Originals and flags are retained; no automatic outlier deletion or winsorization is applied.

## Raw data

Original SimFin archives are in `data/raw/`: company metadata, quarterly income statements, balance sheets, cash flows, and daily share prices. Do not edit them. The notebook records SHA-256 hashes and makes all derived transformations reproducible. All merges validate one-to-one company IDs.

Quarterly cash-flow D&A and operating cash flow reconcile to Apple FY2024 and NVIDIA FY2025 annual totals. TTM construction requires four consecutive, complete quarters; revenue growth requires eight and a positive prior-year revenue denominator. Missing debt is never assumed zero. See Notebook 1 for exact rules and primary-source links.

## Run Notebook 1

From the project root, create an environment and install the tested Notebook 1 versions:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook1.lock.txt
.\.venv\Scripts\python.exe src\run_notebook.py
```

Or select that environment in the notebook editor, restart the kernel, and run all cells in order. `src/run_notebook.py` uses a new kernel, saves outputs, and validates successful execution. It does not regenerate the notebook or erase manual edits. `src/build_notebook.py` is the authoring source and regenerates the notebook layout if intentionally invoked.

No network access is needed for notebook execution. External evidence already reviewed is recorded in the mapping and notebook. The separate `requirements.txt` retains broader planned project dependencies.

## Outputs in data/processed/

- `working_dataset.csv`: all priced firms, financial variables, classifications, and audit flags.
- `financial_pool_AI_PENDING.csv`: financial-ready pool for preliminary financial EDA; unknown AI exposure stays blank.
- `candidate_analysis_INCOMPLETE.csv`: complete model variables including reviewed AI labels; not a finished analysis sample.
- `ai_mapping_PENDING.csv`: IDs, status, rationale, primary-source URL, evidence publication date, reviewer, and review date. Reruns preserve reviews and validate labels and dates.
- `sample_selection_report_INCOMPLETE.md`: selection, missingness, classification, industry, timing, and outlier reports.
- Supporting CSVs: sample selection, missingness, industry composition, restatement sensitivity, raw/window/merge audits, original source quarters, outlier review queue, hypothetical trim thresholds, filing reviews, and variable dictionary.
- `build_manifest.json`: historical date, counts, limitations, library versions, and raw archive hashes.

The 104xxx financial-related industry screen is conservative and provisional until checked against the official dictionary. Financial firms remain in the working dataset and inclusive sensitivity counts.

## Next stage

Notebook 2 may start financial EDA with these flags and limitations. AI-group comparisons require broader historical classification and within-industry overlap. The remaining notebooks are placeholders; regression development, diagnostics, and interpretation are outside Notebook 1's scope.
