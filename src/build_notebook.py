"""Generate Notebook 1's readable, self-contained data-preparation workflow."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
cells = []
def md(s): cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): cells.append(nbf.v4.new_code_cell(s.strip()))

md('''# AI exposure and firm valuation: build the historical snapshot
**Question:** Do AI-exposed publicly traded firms trade at higher valuation multiples than other firms, after accounting for revenue growth, profitability, size, leverage, and industry?

**Valuation date: September 30, 2025.** These are historical prices joined to available downloaded financial statements, not current-day data and not a verified point-in-time database. This notebook prepares and audits data only; it does not estimate regressions or select models. The broad working universe is every company with a price on the exact valuation date. Unknown AI exposure is missing, never zero.''')
md('''## 1. Configuration and reproducibility
Run all cells from a fresh Python kernel. Paths resolve from the notebook directory or project root. Raw ZIPs remain untouched. A one-year financial freshness limit and 60–120 day quarterly spacing rule are explicit working choices, not universal reporting standards. No API key or network access is needed to rerun this notebook.''')
code('''from pathlib import Path
import hashlib, json, platform
import numpy as np
import pandas as pd
from IPython.display import display

ROOT = Path.cwd() if (Path.cwd() / 'data/raw').exists() else Path.cwd().parent
assert (ROOT / 'data/raw').exists(), 'Run from the project root or notebooks directory'
RAW, OUT = ROOT / 'data/raw', ROOT / 'data/processed'
OUT.mkdir(parents=True, exist_ok=True)
VALUATION_DATE = pd.Timestamp('2025-09-30')
FRESHNESS_CUTOFF = pd.Timestamp('2024-09-30')
ID = 'SimFinId'
CASH = 'Cash, Cash Equivalents & Short Term Investments'
DA = 'Depreciation & Amortization'
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 30)
print('Historical snapshot:', VALUATION_DATE.date())
print('Python / pandas / numpy:', platform.python_version(), pd.__version__, np.__version__)''')
md('''## 2. Load and audit original data
Company IDs must be unique in the company table. Financial rows must be unique by company, fiscal year, and fiscal period, and also by company/report date. A failed assertion stops the workflow rather than silently choosing a duplicate. Read prices in chunks to avoid holding six million unnecessary observations in memory.''')
code('''companies = pd.read_csv(RAW / 'us-companies.zip', sep=';')
income = pd.read_csv(RAW / 'us-income-quarterly.zip', sep=';')
balance = pd.read_csv(RAW / 'us-balance-quarterly.zip', sep=';')
cashflow = pd.read_csv(RAW / 'us-cashflow-quarterly.zip', sep=';')
assert companies[ID].notna().all() and companies[ID].is_unique
price_parts, price_rows = [], 0
for chunk in pd.read_csv(RAW / 'us-shareprices-daily.zip', sep=';',
                         usecols=['Ticker', ID, 'Date', 'Close', 'Shares Outstanding'], chunksize=250000):
    price_rows += len(chunk)
    price_parts.append(chunk.loc[chunk['Date'].eq(str(VALUATION_DATE.date()))].copy())
market = pd.concat(price_parts, ignore_index=True)
market['Date'] = pd.to_datetime(market['Date'])
assert market[ID].notna().all() and market[ID].is_unique
raw_audit = []
for name, frame in [('income', income), ('balance', balance), ('cashflow', cashflow)]:
    assert frame[ID].notna().all()
    assert not frame.duplicated([ID, 'Fiscal Year', 'Fiscal Period']).any()
    for col in ['Report Date', 'Publish Date', 'Restated Date']:
        frame[col] = pd.to_datetime(frame[col], errors='raise')
    assert not frame.duplicated([ID, 'Report Date']).any()
    assert frame['Fiscal Period'].isin(['Q1', 'Q2', 'Q3', 'Q4']).all()
    raw_audit.append({'dataset': name, 'rows': len(frame), 'companies': frame[ID].nunique(),
                      'published_after_snapshot': int(frame['Publish Date'].gt(VALUATION_DATE).sum()),
                      'report_after_snapshot': int(frame['Report Date'].gt(VALUATION_DATE).sum()),
                      'restated_before_publish': int(frame['Restated Date'].lt(frame['Publish Date']).sum()),
                      'missing_dates': int(frame[['Report Date','Publish Date','Restated Date']].isna().any(axis=1).sum())})
raw_audit = pd.DataFrame(raw_audit)
display(raw_audit)
print('Company records:', len(companies), '| raw daily prices:', price_rows, '| snapshot firms:', len(market))
assert companies['Market'].eq('us').all()
assert companies['Main Currency'].eq('USD').all()
for label,frame in [('income',income),('balance',balance),('cashflow',cashflow)]:
    print(label,'currency counts:',frame['Currency'].value_counts(dropna=False).to_dict())
    print(label,'publication range:',frame['Publish Date'].min(),frame['Publish Date'].max())
display(companies.isna().sum().rename('missing_company_metadata').to_frame())''')
md('''## 3. What the source dates mean
[SimFin's field documentation](https://github.com/SimFin/simfin/blob/master/simfin/names.py) describes publication as first release of the financial report and restatement as the latest revision date; stored figures reflect that revision. When no revision occurred, the two dates coincide. Publication uses 10-K/10-Q dates rather than earlier preliminary 8-K releases. Its `Close` is split-adjusted, not dividend-adjusted.

We require report and publication dates on or before the snapshot, retain source dates, and flag any selected revision after it. These archives contain no original-value/version history, so original historical values cannot be recovered from the supplied files. Even the unflagged subset is **not certified point-in-time**: company metadata, price/share histories, and source-date accuracy are not independently reconstructed. A flag is not proof of an accounting error or fraud. We report sensitivity counts instead of silently deleting revised companies.''')
code('''available = {}
for name, frame in [('Income', income), ('Balance', balance), ('Cashflow', cashflow)]:
    eligible = frame['Publish Date'].le(VALUATION_DATE) & frame['Report Date'].le(VALUATION_DATE)
    available[name] = frame.loc[eligible].sort_values([ID, 'Report Date']).copy()
    assert available[name]['Publish Date'].le(VALUATION_DATE).all()
    assert available[name]['Report Date'].le(VALUATION_DATE).all()
    available[name]['Quarter_Number'] = (available[name]['Fiscal Year'] * 4
                                         + available[name]['Fiscal Period'].str[-1].astype(int))
    available[name]['Date_Chronology_Anomaly'] = (available[name]['Restated Date'].lt(available[name]['Publish Date'])
        | available[name]['Publish Date'].lt(available[name]['Report Date']))
print({name: len(frame) for name, frame in available.items()})''')
md('''## 4. Verify cash flows are individual quarters
Do not difference these quarterly files as if they were year-to-date. Two primary-source checks compare quarterly sums to full-year reported cash flows: [Apple FY2024 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm) and [NVIDIA FY2025 results, February 26, 2025](https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2025/default.aspx). Apple reports D&A of $11.445bn and operating cash flow of $118.254bn; NVIDIA reports $1.864bn and $64.089bn. Summed quarterly values reproduce these annual totals, unlike a sum of cumulative YTD values. This verifies the convention in audited examples, not every issuer's extraction.

SimFin fiscal-year labels can differ from issuer year names; inspect report-date windows as well. Report dates can be normalized to calendar month ends (Apple's actual FY2024 end was September 28). Window matching below uses the source's dates consistently. A separate check compares cash-flow starting income with same-quarter income-statement net income across firms.''')
code('''cf_checks = []
for ticker, source_year, reported_da, reported_ocf in [
    ('AAPL', 2024, 11445e6, 118254e6), ('NVDA', 2024, 1864e6, 64089e6)]:
    q = cashflow.loc[cashflow['Ticker'].eq(ticker) & cashflow['Fiscal Year'].eq(source_year)]
    assert len(q) == 4 and q['Fiscal Period'].nunique() == 4
    for col, expected in [(DA, reported_da), ('Net Cash from Operating Activities', reported_ocf)]:
        actual = q[col].sum(min_count=4)
        assert np.isclose(actual, expected, rtol=0, atol=1), (ticker, col, actual)
        cf_checks.append({'Ticker': ticker, 'SimFin_Fiscal_Year': source_year,
                          'first_report': q['Report Date'].min(), 'last_report': q['Report Date'].max(),
                          'variable': col, 'quarter_sum': actual, 'reported_annual': expected, 'passed': True})
cashflow_validation = pd.DataFrame(cf_checks)
display(cashflow_validation)
cf_income = cashflow[[ID,'Report Date','Net Income/Starting Line']].merge(
    income[[ID,'Report Date','Net Income']], on=[ID,'Report Date'], how='inner', validate='one_to_one')
both = cf_income[['Net Income/Starting Line','Net Income']].notna().all(axis=1)
matches = np.isclose(cf_income.loc[both,'Net Income/Starting Line'], cf_income.loc[both,'Net Income'], rtol=1e-6, atol=1)
print('Same-period cash-flow starting income vs net income:', int(matches.sum()), '/', int(both.sum()), 'matches')
print('Differences can reflect starting-line definitions and revisions; these are review flags, not automatic errors.')''')
md('''## 5. Four-quarter TTM and eight-quarter growth windows
Select the most recent four/eight eligible rows before examining missing values. Require all adjacent fiscal-quarter indices to increase by one and report dates to be 60–120 days apart. Do not backfill missing quarters with older observations. Latest report must be within one year. This rule may exclude unusual calendars and allows financial information up to one year old; age is exported for review.

Each sum requires all four values. Growth additionally requires eight complete revenue values, USD in all eight quarters, a positive prior TTM denominator, and the same current four-quarter dates as the income window. Growth = current TTM revenue / preceding TTM revenue − 1. Fractions, margins, and leverage are decimals, not percentage points.''')
code('''window_audit = []
def select_window(frame, n, label):
    q = frame.groupby(ID, sort=False).tail(n).copy()
    sizes = q.groupby(ID).size()
    q = q.loc[q[ID].isin(sizes[sizes.eq(n)].index)].copy()
    transitions = q.groupby(ID)['Quarter_Number'].diff().eq(1)
    days = q.groupby(ID)['Report Date'].diff().dt.days.between(60,120)
    valid = (transitions & days).groupby(q[ID]).sum().eq(n-1)
    q = q.loc[q[ID].isin(valid[valid].index)].copy()
    latest = q.groupby(ID)['Report Date'].max()
    fresh = latest.ge(FRESHNESS_CUTOFF)
    window_audit.append({'window': label, 'has_n_rows': int(sizes.eq(n).sum()),
                         'consecutive_and_spaced': int(valid.sum()), 'fresh': int(fresh.sum())})
    return q.loc[q[ID].isin(fresh[fresh].index)].copy()

def summarize(q, prefix, variables):
    g = q.groupby(ID)
    result = g[list(variables)].sum(min_count=4).rename(columns=variables)
    result[prefix+'_First_Report_Date'] = g['Report Date'].min()
    result[prefix+'_Latest_Report_Date'] = g['Report Date'].max()
    result[prefix+'_Latest_Publish_Date'] = g['Publish Date'].max()
    result[prefix+'_Latest_Restated_Date'] = g['Restated Date'].max()
    result[prefix+'_Restated_After_Valuation'] = g['Restated Date'].max().gt(VALUATION_DATE)
    result[prefix+'_Timing_Unknown'] = g['Restated Date'].count().lt(4)
    result[prefix+'_Date_Chronology_Anomaly'] = g['Date_Chronology_Anomaly'].max()
    result[prefix+'_USD'] = g['Currency'].apply(lambda x: x.eq('USD').all())
    return result.reset_index()

income4 = select_window(available['Income'], 4, 'income_4')
cashflow4 = select_window(available['Cashflow'], 4, 'cashflow_4')
income8 = select_window(available['Income'], 8, 'income_8_growth')
income_ttm = summarize(income4, 'Income', {'Revenue':'Revenue_TTM', 'Operating Income (Loss)':'Operating_Income_TTM'})
cashflow_ttm = summarize(cashflow4, 'Cashflow', {DA:'DA_TTM_Source'})
income8['Window_Position'] = income8.groupby(ID).cumcount()
prior4 = income8.loc[income8['Window_Position'].lt(4)]
current4 = income8.loc[income8['Window_Position'].ge(4)]
growth = income8.groupby(ID).agg(
    Growth_First_Report_Date=('Report Date','min'), Growth_Latest_Report_Date=('Report Date','max'),
    Growth_Latest_Publish_Date=('Publish Date','max'), Growth_Latest_Restated_Date=('Restated Date','max'))
growth['Prior_Revenue_TTM'] = prior4.groupby(ID)['Revenue'].sum(min_count=4)
growth['Growth_Current_Revenue_TTM'] = current4.groupby(ID)['Revenue'].sum(min_count=4)
growth['Growth_Current_First_Report_Date'] = current4.groupby(ID)['Report Date'].min()
growth['Growth_USD'] = income8.groupby(ID)['Currency'].apply(lambda x: x.eq('USD').all())
growth['Growth_Timing_Unknown'] = income8.groupby(ID)['Restated Date'].count().lt(8)
growth['Growth_Date_Chronology_Anomaly'] = income8.groupby(ID)['Date_Chronology_Anomaly'].max()
growth['Growth_Restated_After_Valuation'] = growth['Growth_Latest_Restated_Date'].gt(VALUATION_DATE)
growth['Revenue_Growth'] = (growth['Growth_Current_Revenue_TTM'] / growth['Prior_Revenue_TTM'] - 1).where(
    growth['Prior_Revenue_TTM'].gt(0) & growth['Growth_USD'])
growth = growth.reset_index()
display(pd.DataFrame(window_audit))''')
md('''## 6. Market value, EBITDA, balance sheets, and leverage
Market cap = source Close × source Shares Outstanding on the same date. No diluted weighted-average statement shares are substituted. Both price and share histories may be vendor-adjusted; we audit the arithmetic, not an independently reconstructed historical share register.

EBITDA = operating income + cash-flow D&A for matching four-quarter windows. This is a standardized proxy, not issuer adjusted EBITDA. Cash-flow D&A may include items not in operating income (Microsoft, for example, reports a broader cash-flow adjustment); this remains a measurement limitation requiring issuer-level review.

Debt = short-term + long-term debt; missing components remain missing. EV = market cap + debt − cash including short-term investments. Preferred equity and noncontrolling interests are unavailable in these simplified files. Balance-sheet stocks are not summed. Stale/non-USD balance sheets cannot yield valid EV or leverage. Leverage = debt / assets only for positive assets. Negative raw values remain visible.''')
code('''merge_audit = []
def merge_one(left, right, label):
    assert left[ID].is_unique and right[ID].is_unique
    before = len(left)
    result = left.merge(right, on=ID, how='left', validate='one_to_one', indicator='_match')
    merge_audit.append({'merge':label,'before':before,'after':len(result),
                        'matched':int(result['_match'].eq('both').sum()),
                        'unmatched':int(result['_match'].eq('left_only').sum())})
    assert len(result) == before and result[ID].is_unique
    return result.drop(columns='_match')

market['Market_Cap'] = market['Close'] * market['Shares Outstanding']
working = merge_one(market, income_ttm, 'income TTM')
working = merge_one(working, cashflow_ttm, 'cashflow TTM')
working = merge_one(working, growth, 'eight-quarter growth')
working['Matching_TTM_Window'] = (working['Income_First_Report_Date'].eq(working['Cashflow_First_Report_Date'])
    & working['Income_Latest_Report_Date'].eq(working['Cashflow_Latest_Report_Date']))
working['Matching_Growth_Window'] = (working['Income_First_Report_Date'].eq(working['Growth_Current_First_Report_Date'])
    & working['Income_Latest_Report_Date'].eq(working['Growth_Latest_Report_Date']))
working['DA_TTM'] = working['DA_TTM_Source'].where(working['Matching_TTM_Window'])
working['Revenue_Growth'] = working['Revenue_Growth'].where(working['Matching_Growth_Window'])
working['EBITDA_TTM'] = working['Operating_Income_TTM'] + working['DA_TTM']
working['EBITDA_Margin'] = (working['EBITDA_TTM']/working['Revenue_TTM']).where(working['Revenue_TTM'].ne(0))
latest = available['Balance'].groupby(ID).tail(1)[
    [ID,'Report Date','Publish Date','Restated Date','Currency','Date_Chronology_Anomaly',CASH,'Short Term Debt','Long Term Debt','Total Assets','Total Equity']].copy()
latest = latest.rename(columns={'Report Date':'Balance_Report_Date','Publish Date':'Balance_Publish_Date',
    'Restated Date':'Balance_Restated_Date','Currency':'Balance_Currency','Date_Chronology_Anomaly':'Balance_Date_Chronology_Anomaly',
    'Total Assets':'Total_Assets','Total Equity':'Total_Equity'})
latest['Total_Debt'] = latest['Short Term Debt'] + latest['Long Term Debt']
latest['Balance_Is_Stale'] = latest['Balance_Report_Date'].lt(FRESHNESS_CUTOFF)
latest['Balance_Restated_After_Valuation'] = latest['Balance_Restated_Date'].gt(VALUATION_DATE)
latest['Balance_Timing_Unknown'] = latest['Balance_Restated_Date'].isna()
working = merge_one(working, latest, 'latest balance sheet')
working['Financials_In_USD'] = (working['Income_USD'].eq(True) & working['Cashflow_USD'].eq(True)
                                & working['Balance_Currency'].eq('USD'))
fresh_balance = working['Balance_Is_Stale'].eq(False) & working['Balance_Currency'].eq('USD')
working['Enterprise_Value_Raw'] = working['Market_Cap'] + working['Total_Debt'] - working[CASH]
working['Enterprise_Value'] = working['Enterprise_Value_Raw'].where(fresh_balance)
working['Leverage_Raw'] = (working['Total_Debt']/working['Total_Assets']).where(working['Total_Assets'].gt(0))
working['Leverage'] = working['Leverage_Raw'].where(fresh_balance)
working['EV_EBITDA'] = (working['Enterprise_Value']/working['EBITDA_TTM']).where(
    working['EBITDA_TTM'].ne(0) & working['Financials_In_USD'])
working['log_Market_Cap'] = np.log(working['Market_Cap'].where(working['Market_Cap'].gt(0)))
info = companies[[ID,'Ticker','Company Name','IndustryId','Market','CIK']].rename(columns={'Ticker':'Company_Ticker'})
working = merge_one(working, info, 'company information')
working['Ticker'] = working['Ticker'].fillna(working['Company_Ticker'])
working = working.drop(columns='Company_Ticker')
for prefix, col in [('Income','Income_Latest_Report_Date'),('Balance','Balance_Report_Date')]:
    working[prefix+'_Age_Days'] = (VALUATION_DATE-working[col]).dt.days
flag_cols = ['Income_Restated_After_Valuation','Cashflow_Restated_After_Valuation',
             'Growth_Restated_After_Valuation','Balance_Restated_After_Valuation']
working['Any_Later_Restatement'] = working[flag_cols].eq(True).any(axis=1)
timing_cols = ['Income_Timing_Unknown','Cashflow_Timing_Unknown','Growth_Timing_Unknown','Balance_Timing_Unknown']
working['Timing_Coverage_Complete'] = working[timing_cols].eq(False).all(axis=1)
chronology_cols = [p+'_Date_Chronology_Anomaly' for p in ['Income','Cashflow','Growth','Balance']]
working['Any_Date_Chronology_Anomaly'] = working[chronology_cols].eq(True).any(axis=1)
display(pd.DataFrame(merge_audit))
display(working[flag_cols+['Balance_Is_Stale','Matching_TTM_Window']].eq(True).sum().to_frame('flagged_firms'))
display(working[['Income_Age_Days','Balance_Age_Days']].describe())''')
md('''The raw audit finds revision dates earlier than publication dates, contrary to the simple documented chronology. We preserve and flag these inconsistencies in all selected windows. They need source clarification; neither a later-revision filter nor an absence of flags repairs them. Sensitivity tables separately report firms with complete timing coverage and no chronology anomaly.''')
md('''## 7. Auditable AI mapping — classification remains incomplete
**Exposure rule:** a material business connection to commercial AI products/services or infrastructure: a substantial disclosed revenue stream, core commercial product, or major deployed AI infrastructure business. Internal use, a passing mention, or an announced aspiration alone is insufficient. This is a qualitative rule; ambiguous materiality stays uncertain. Classification must be based on evidence published by September 30, 2025 and must not depend on valuation outcomes.

Statuses: `confirmed_exposed` (1), `reviewed_comparison` (0 after business/segment review), `uncertain` (missing), `unreviewed` (missing). A comparison label means no material connection identified under this rule, not proof of no AI activity. Record rationale, primary-source URL, evidence publication date, reviewer, and review date. Undated current business summaries are not historical evidence.

Two exposure seed reviews are supplied: [NVIDIA August 27, 2025](https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2026/default.aspx) describes commercial Blackwell AI infrastructure and $41.1bn Data Center quarterly revenue; [Microsoft July 30, 2025 earnings call](https://www.microsoft.com/en-us/investor/events/fy-2025/earnings-fy-2025-q4) describes deployed AI infrastructure and commercial Copilot services. These support material exposure.

Two comparison seed reviews use the business descriptions, segment disclosures, and AI references in [Coca-Cola's 2024 10-K, filed February 20, 2025](https://investors.coca-colacompany.com/filings-reports/annual-filings-10-k/content/0000021344-25-000011/ko-20241231.htm) and [P&G's FY2025 10-K, filed August 4, 2025](https://www.sec.gov/Archives/edgar/data/80424/000008042425000076/pg-20250630.htm). Their disclosed businesses sell beverages and consumer goods; AI references concern internal operations, analytics, and risks rather than a material commercial AI offering. Labeling them zero is an inference under our commercial-exposure rule, not an assertion that they never use AI. These four convenience seeds do not form a representative comparison sample. The mapping remains a review queue. Edit the separate CSV to add evidence; reruns preserve edits and validate them.''')
code('''mapping_path = OUT / 'ai_mapping_PENDING.csv'
mapping_cols = [ID,'AI_Status','AI_Exposed','AI_Rationale','AI_Source','AI_Evidence_Date','AI_Reviewer','AI_Review_Date']
if mapping_path.exists():
    ai = pd.read_csv(mapping_path, dtype={'AI_Status':'string'})[mapping_cols]
    ai['AI_Evidence_Date'] = pd.to_datetime(ai['AI_Evidence_Date'], errors='raise')
    ai['AI_Review_Date'] = pd.to_datetime(ai['AI_Review_Date'], errors='raise')
else:
    ai = working[[ID]].copy()
    ai['AI_Status'] = 'unreviewed'
    ai['AI_Exposed'] = np.nan
    ai['AI_Rationale'] = 'Pending historical business and segment review; no zero assigned.'
    ai['AI_Source'] = ''
    ai['AI_Evidence_Date'] = pd.NaT
    ai['AI_Reviewer'] = ''
    ai['AI_Review_Date'] = pd.NaT
    seeds = {
        172199: ('2025-08-27', 'Blackwell AI compute is a core commercial platform; Data Center revenue was $41.1bn in the quarter.',
                 'https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2026/default.aspx'),
        59265: ('2025-07-30', 'Commercial Copilot services and deployed Azure AI infrastructure establish a material AI business connection.',
                'https://www.microsoft.com/en-us/investor/events/fy-2025/earnings-fy-2025-q4')}
    for sid, (date, rationale, source) in seeds.items():
        ai.loc[ai[ID].eq(sid), ['AI_Status','AI_Exposed','AI_Rationale','AI_Source','AI_Evidence_Date','AI_Reviewer','AI_Review_Date']] = [
            'confirmed_exposed', 1, rationale, source, pd.Timestamp(date), 'Codex primary-source seed review', pd.Timestamp('2026-10-11')]
comparison_seeds = {
    82117: ('2025-02-20','Business and segment review identifies beverage/concentrate sales. AI disclosures concern internal analytics, marketing, and operations; no material commercial AI offering identified under the rule.',
        'https://investors.coca-colacompany.com/filings-reports/annual-filings-10-k/content/0000021344-25-000011/ko-20241231.htm'),
    133209: ('2025-08-04','Business and segment review identifies five consumer-goods segments. AI disclosures concern internal technologies and risks; no material commercial AI offering identified under the rule.',
        'https://www.sec.gov/Archives/edgar/data/80424/000008042425000076/pg-20250630.htm')}
for sid,(date,rationale,source) in comparison_seeds.items():
    pending = ai[ID].eq(sid) & ai['AI_Status'].eq('unreviewed')
    ai.loc[pending, ['AI_Status','AI_Exposed','AI_Rationale','AI_Source','AI_Evidence_Date','AI_Reviewer','AI_Review_Date']] = [
        'reviewed_comparison',0,rationale,source,pd.Timestamp(date),'Codex primary-source seed review',pd.Timestamp('2026-10-11')]
assert ai[ID].notna().all() and ai[ID].is_unique
assert set(ai[ID]) == set(working[ID]), 'Mapping universe changed; reconcile IDs explicitly'
ai['AI_Evidence_Date'] = pd.to_datetime(ai['AI_Evidence_Date'], errors='raise')
ai['AI_Review_Date'] = pd.to_datetime(ai['AI_Review_Date'], errors='raise')
assert ai['AI_Status'].isin(['confirmed_exposed','reviewed_comparison','uncertain','unreviewed']).all()
known = ai['AI_Status'].isin(['confirmed_exposed','reviewed_comparison'])
assert ai.loc[~known,'AI_Exposed'].isna().all()
assert ai.loc[ai['AI_Status'].eq('confirmed_exposed'),'AI_Exposed'].eq(1).all()
assert ai.loc[ai['AI_Status'].eq('reviewed_comparison'),'AI_Exposed'].eq(0).all()
assert ai.loc[known,'AI_Evidence_Date'].notna().all()
assert ai.loc[known,'AI_Evidence_Date'].le(VALUATION_DATE).all()
for col in ['AI_Rationale','AI_Source','AI_Reviewer','AI_Review_Date']:
    assert ai.loc[known,col].notna().all() and ai.loc[known,col].astype(str).str.strip().ne('').all()
working = merge_one(working, ai, 'AI mapping')
display(working['AI_Status'].value_counts().to_frame('firms'))''')
md('''## 8. Candidate sample and industry comparability
Potential predictors are AI exposure, revenue growth, EBITDA margin, log market cap, debt/assets, and categorical industry (six concepts; no dummy coding/model selection yet). The first financial pool requires complete finite controls/outcome, positive market cap, EV, EBITDA and revenue, valid matching windows, fresh statements and USD consistency. The strict candidate additionally requires a reviewed AI label.

Financial firms need special handling because debt is often an operating input and EV/EBITDA is not comparable to ordinary operating companies. [SimFin's loaders](https://github.com/SimFin/simfin/blob/master/simfin/load.py) use separate bank and insurance datasets, absent here. The local company table identifies JPM, BAC, GS and MS as industry 104002. In the absence of the official industry-name dictionary, we conservatively flag the 104xxx family as **financial-related pending dictionary verification** and exclude it from the primary pool; an inclusive pool is reported as sensitivity. This is a provisional screen, not a verified full sector taxonomy. Preserve IndustryId as a categorical code, never interpret it as a numeric scale. The exported industry table highlights whether both reviewed groups coexist within industries; no overlap means comparisons are not yet assessable.''')
code('''working['Financial_Industry_Provisional'] = working['IndustryId'].floordiv(1000).eq(104)
working['Financial_Ready'] = False
selection_rows = []
mask = pd.Series(True, index=working.index)
def step(label, condition):
    global mask
    before = int(mask.sum())
    mask = mask & condition.fillna(False)
    selection_rows.append({'stage':label,'remaining':int(mask.sum()),'excluded_at_stage':before-int(mask.sum())})
step('Exact-date market universe', mask)
step('Positive market capitalization', working['Market_Cap'].gt(0))
step('Positive source price and shares outstanding', working['Close'].gt(0) & working['Shares Outstanding'].gt(0))
step('Eligible fresh four-quarter income window', working['Income_Latest_Report_Date'].notna())
step('Matched four-quarter USD cashflow and balance', working['Financials_In_USD'] & working['Matching_TTM_Window'])
step('Fresh balance sheet', working['Balance_Is_Stale'].eq(False))
step('Positive revenue', working['Revenue_TTM'].gt(0))
step('Positive EBITDA', working['EBITDA_TTM'].gt(0))
step('Positive enterprise value', working['Enterprise_Value'].gt(0))
financial_variables = ['EV_EBITDA','Revenue_Growth','EBITDA_Margin','log_Market_Cap','Leverage','IndustryId']
finite_complete = pd.Series(np.isfinite(working[financial_variables].to_numpy(dtype=float)).all(axis=1),index=working.index)
step('Complete finite financial outcome and controls, including eight-quarter growth', finite_complete)
inclusive_mask = mask.copy()
step('Exclude provisional financial-related industries (104xxx)', ~working['Financial_Industry_Provisional'])
financial_mask = mask.copy()
working.loc[financial_mask,'Financial_Ready'] = True
step('Reviewed AI classification and complete model variables', working['AI_Exposed'].notna())
candidate_mask = mask.copy()
working['Candidate_Analysis'] = candidate_mask
financial_pool = working.loc[financial_mask].copy()
candidate = working.loc[candidate_mask].copy()
selection = pd.DataFrame(selection_rows)
display(selection)
sample_timing = pd.DataFrame([
    {'sample':label,'including_flagged':int(m.sum()),
     'without_later_restatement_flags':int((m & ~working['Any_Later_Restatement']).sum()),
     'without_flags_and_complete_timing':int((m & ~working['Any_Later_Restatement'] & working['Timing_Coverage_Complete']).sum()),
     'also_without_chronology_anomalies':int((m & ~working['Any_Later_Restatement'] & working['Timing_Coverage_Complete'] & ~working['Any_Date_Chronology_Anomaly']).sum())}
    for label,m in [('financial_pool_including_financial_industries',inclusive_mask),
                    ('primary_financial_pool_AI_pending',financial_mask),('reviewed_AI_candidate_INCOMPLETE',candidate_mask)]])
display(sample_timing)
model_variables = ['AI_Exposed'] + financial_variables
missingness = pd.DataFrame({'variable':model_variables + ['Market_Cap','Revenue_TTM','EBITDA_TTM','Total_Debt','Total_Assets','Enterprise_Value'],
    'missing': [int(working[v].isna().sum()) for v in model_variables + ['Market_Cap','Revenue_TTM','EBITDA_TTM','Total_Debt','Total_Assets','Enterprise_Value']]})
missingness['available'] = len(working)-missingness['missing']
display(missingness)
quality_flags = pd.Series({
    'missing_shares':int(working['Shares Outstanding'].isna().sum()),
    'nonpositive_close':int(working['Close'].le(0).sum()),
    'nonpositive_shares':int(working['Shares Outstanding'].le(0).sum()),
    'nonpositive_market_cap':int(working['Market_Cap'].le(0).sum()),
    'negative_debt':int(working['Total_Debt'].lt(0).sum()),
    'negative_cash':int(working[CASH].lt(0).sum()),
    'nonpositive_assets':int(working['Total_Assets'].le(0).sum()),
    'nonpositive_EBITDA':int(working['EBITDA_TTM'].le(0).sum()),
    'nonpositive_EV':int(working['Enterprise_Value'].le(0).sum()),
    'chronology_anomaly_selected_sources':int(working['Any_Date_Chronology_Anomaly'].sum())},name='firms')
display(quality_flags.to_frame())
industry_composition = working.groupby('IndustryId',dropna=False).agg(
    working_firms=(ID,'size'),financial_ready=('Financial_Ready','sum'),candidate_firms=('Candidate_Analysis','sum'))
groups = pd.crosstab(financial_pool['IndustryId'],financial_pool['AI_Status'])
industry_composition = industry_composition.join(groups,how='left').fillna(0)
for status in ['confirmed_exposed','reviewed_comparison','uncertain','unreviewed']:
    if status not in industry_composition: industry_composition[status] = 0
industry_composition['both_reviewed_groups'] = (industry_composition['confirmed_exposed'].gt(0)
    & industry_composition['reviewed_comparison'].gt(0))
display(industry_composition)
classification_counts = pd.concat([working['AI_Status'].value_counts().rename('working'),
    financial_pool['AI_Status'].value_counts().rename('financial_pool'),candidate['AI_Status'].value_counts().rename('candidate')],axis=1).fillna(0).astype(int)
display(classification_counts)
print('Potential predictors: 6 concepts (including categorical industry).')
print('Financial pool >=500:', len(financial_pool)>=500, '| reviewed candidate >=500:', len(candidate)>=500)
print('Reviewed candidate has both groups:', candidate['AI_Exposed'].nunique()==2)''')
md('''## 9. Outlier inspection and source-level review queue
Report tails in the broad dataset and positive-valuation financial pool. Large multiples may reflect tiny EBITDA; large growth may reflect tiny prior revenue or acquisitions; margins and leverage can reveal mismatched units or extraction issues. Checks below verify arithmetic identities and export the exact source quarters and balance sheets behind tail observations. They do not prove economic plausibility. External filing reconciliation of each tail remains pending, so no values are corrected, capped, or removed merely for extremeness.

A **hypothetical** 1st–99th percentile trim is reported for comparison only, with thresholds exported. It is not the primary sample and is not applied to the candidate CSV. Original values remain unchanged. Percentile rules are descriptive sensitivity choices, not evidence of errors.''')
md('''Specific investigations:

- **Tutor Perini (TPC):** EV/EBITDA above 5,000 follows from only $377,000 of source-derived TTM EBITDA against billions of EV. The denominator is operating losses plus D&A almost offsetting each other. This is arithmetically reproducible, but issuer-level full-window reconciliation is pending; magnitude alone is not a deletion rule.
- **Keros (KROS):** huge growth has a $271,000 prior-year denominator. Its [August 6, 2025 results](https://ir.kerostx.com/news-releases/news-release-details/keros-therapeutics-reports-second-quarter-2025-financial-results/) report $229.414m first-half revenue including $195.355m license revenue. Source Q1+Q2 revenue reconciles to that total. This supports a licensing-event explanation, not smooth recurring sales growth.
- **LiveWire (LVWR):** source Q2 2025 operating income is positive $549,000, while its [July 30, 2025 results](https://investor.livewire.com/news-events-1/news/news-details/2025/LiveWire-Group-Inc--Reports-2025-Second-Quarter-Financial-Results/default.aspx) report an $18.264m operating loss with the same $5.873m revenue. Several other source quarters also equate operating income with revenue. This is a verified source-versus-original-filing discrepancy, potentially involving extraction or later revisions. Preserve source values and flag the firm; do not silently substitute numbers from a different vintage. It already fails financial eligibility due to missing debt.
- **BNET:** leverage above 100 reflects source debt around $3.19m divided by only $29,233 of assets. A small denominator explains the arithmetic, but its filing-level units and balance sheet remain pending review.

The remaining tail queue is explicitly unresolved. A financial EDA must show these flags alongside the original ratios.''')
code('''outlier_vars = ['EV_EBITDA','Revenue_Growth','EBITDA_Margin','Leverage']
tail_summary = pd.concat({label:frame[outlier_vars].describe(percentiles=[.01,.05,.5,.95,.99]).T
                         for label,frame in [('working',working),('financial_pool',financial_pool)]},names=['sample','variable'])
display(tail_summary)
identity_checks = {
    'market_cap': (working['Market_Cap'], working['Close']*working['Shares Outstanding']),
    'debt': (working['Total_Debt'], working['Short Term Debt']+working['Long Term Debt']),
    'EV_raw': (working['Enterprise_Value_Raw'],working['Market_Cap']+working['Total_Debt']-working[CASH]),
    'EBITDA': (working['EBITDA_TTM'],working['Operating_Income_TTM']+working['DA_TTM']),
    'margin': (working['EBITDA_Margin'],(working['EBITDA_TTM']/working['Revenue_TTM']).where(working['Revenue_TTM'].ne(0))),
    'leverage_raw': (working['Leverage_Raw'],(working['Total_Debt']/working['Total_Assets']).where(working['Total_Assets'].gt(0))),
    'log_market_cap': (working['log_Market_Cap'],np.log(working['Market_Cap'].where(working['Market_Cap'].gt(0))))}
for label,(actual,expected) in identity_checks.items():
    assert np.allclose(actual.to_numpy(float),expected.to_numpy(float),equal_nan=True),label
assert np.isfinite(working[model_variables].to_numpy(float)[~np.isnan(working[model_variables].to_numpy(float))]).all()
growth_check = working.loc[working['Revenue_Growth'].notna()]
assert np.allclose(growth_check['Revenue_Growth'],growth_check['Revenue_TTM']/growth_check['Prior_Revenue_TTM']-1)
print('All constructed arithmetic identities passed; no infinities in model variables.')
lvwr_q = income.loc[income['Ticker'].eq('LVWR') & income['Report Date'].eq(pd.Timestamp('2025-06-30'))].iloc[0]
kros_half = income.loc[income['Ticker'].eq('KROS') & income['Report Date'].isin(pd.to_datetime(['2025-03-31','2025-06-30'])),'Revenue'].sum(min_count=2)
assert np.isclose(kros_half,229414e3)
source_review = pd.DataFrame([
    {'Ticker':'LVWR','variable':'Q2 2025 operating income','source_value':lvwr_q['Operating Income (Loss)'],
     'historical_filing_value':-18264e3,'evidence_date':'2025-07-30','status':'Verified vintage/source discrepancy; no substitution',
     'source':'https://investor.livewire.com/news-events-1/news/news-details/2025/LiveWire-Group-Inc--Reports-2025-Second-Quarter-Financial-Results/default.aspx'},
    {'Ticker':'KROS','variable':'H1 2025 revenue','source_value':kros_half,'historical_filing_value':229414e3,
     'evidence_date':'2025-08-06','status':'Reconciles; licensing event supports extreme growth',
     'source':'https://ir.kerostx.com/news-releases/news-release-details/keros-therapeutics-reports-second-quarter-2025-financial-results/'}])
working['Known_Source_Discrepancy'] = working['Ticker'].eq('LVWR')
assert not working.loc[candidate_mask,'Known_Source_Discrepancy'].any()
display(source_review)
tail_rows = []
for variable in outlier_vars:
    for direction, rows in [('lowest',working.nsmallest(5,variable)),('highest',working.nlargest(5,variable))]:
        rows = rows.loc[rows[variable].notna()].copy()
        rows['Tail_Variable'],rows['Tail_Direction'] = variable,direction
        rows['Review_Status'] = 'Arithmetic checked; filing-level plausibility review pending'
        tail_rows.append(rows)
outliers = pd.concat(tail_rows,ignore_index=True)
outliers.loc[outliers['Ticker'].eq('LVWR'),'Review_Status'] = 'Verified operating income discrepancy versus 2025-07-30 original filing; preserved source vintage'
outliers.loc[outliers['Ticker'].eq('KROS'),'Review_Status'] = 'H1 revenue reconciles to filing; license revenue explains jump; full TTM audit pending'
review_cols = ['Ticker',ID,'Tail_Variable','Tail_Direction']+outlier_vars+[
    'Revenue_TTM','Prior_Revenue_TTM','EBITDA_TTM','Total_Debt','Total_Assets','Any_Later_Restatement']
display(outliers[review_cols])
tail_ids = outliers[ID].unique()
thresholds = financial_pool[outlier_vars].quantile([.01,.99]).T.rename(columns={.01:'p01',.99:'p99'})
trim_mask = pd.Series(True,index=financial_pool.index)
for v in outlier_vars:
    trim_mask &= financial_pool[v].between(thresholds.loc[v,'p01'],thresholds.loc[v,'p99'])
working['Within_Hypothetical_1_99_Trim'] = False
working.loc[financial_pool.index,'Within_Hypothetical_1_99_Trim'] = trim_mask
trim_counts = pd.DataFrame({'sample':['financial_pool','reviewed_candidate'],
    'original':[len(financial_pool),len(candidate)],
    'hypothetical_trim':[int(trim_mask.sum()),int(working.loc[candidate_mask,'Within_Hypothetical_1_99_Trim'].sum())]})
display(thresholds)
display(trim_counts)
print('No outlier treatment applied. Filing-level checks of the exported tail queue remain pending.')''')
md('''## 10. Export and readiness report
CSV missing values remain blank. `working_dataset.csv` preserves all priced firms. `financial_pool_AI_PENDING.csv` is useful for financial EDA but is not the AI comparison sample. `candidate_analysis_INCOMPLETE.csv` requires all variables including reviewed AI exposure, yet remains incomplete until both groups and adequate coverage exist. The mapping is separate and auditable. Reports include sequential exclusions, missingness, classification counts, industries, timing sensitivity, tail thresholds, and source-quarter review records. No capped values replace originals.

Do not infer causality from this historical cross section. Size measured by market cap shares the valuation outcome's numerator, and profitability shares its EBITDA denominator; acknowledge these mechanical relationships when interpreting later analyses.''')
code('''working.to_csv(OUT/'working_dataset.csv',index=False)
working.loc[financial_mask].to_csv(OUT/'financial_pool_AI_PENDING.csv',index=False)
working.loc[candidate_mask].to_csv(OUT/'candidate_analysis_INCOMPLETE.csv',index=False)
ai.to_csv(mapping_path,index=False)
selection.to_csv(OUT/'sample_selection.csv',index=False)
missingness.to_csv(OUT/'missingness.csv',index=False)
quality_flags.to_csv(OUT/'quality_flag_counts.csv')
classification_counts.to_csv(OUT/'ai_classification_counts.csv')
industry_composition.to_csv(OUT/'industry_composition.csv')
sample_timing.to_csv(OUT/'restatement_sensitivity.csv',index=False)
raw_audit.to_csv(OUT/'raw_data_audit.csv',index=False)
pd.DataFrame(window_audit).to_csv(OUT/'window_audit.csv',index=False)
pd.DataFrame(merge_audit).to_csv(OUT/'merge_audit.csv',index=False)
cashflow_validation.to_csv(OUT/'cashflow_convention_checks.csv',index=False)
source_review.to_csv(OUT/'source_filing_reviews.csv',index=False)
tail_summary.to_csv(OUT/'outlier_summary.csv')
outliers.to_csv(OUT/'outlier_review_PENDING.csv',index=False)
thresholds.to_csv(OUT/'hypothetical_trim_thresholds.csv')
trim_counts.to_csv(OUT/'hypothetical_trim_counts.csv',index=False)
for label,frame in [('income_8',income8),('income_4',income4),('cashflow_4',cashflow4),('balance_latest',latest)]:
    frame.loc[frame[ID].isin(tail_ids)].to_csv(OUT/('outlier_source_'+label+'.csv'),index=False)
source_quarters = pd.concat([income4.assign(Source_Window='Income4'),cashflow4.assign(Source_Window='Cashflow4'),
                            income8.assign(Source_Window='Income8')],ignore_index=True)
source_quarters.to_csv(OUT/'selected_source_quarters.csv',index=False)
manifest = {'valuation_date':str(VALUATION_DATE.date()),'historical_point_in_time_verified':False,
    'working_firms':len(working),'financial_pool_firms':len(financial_pool),'candidate_firms':len(candidate),
    'candidate_has_both_AI_groups':bool(candidate['AI_Exposed'].nunique()==2),
    'requirement_500_met':bool(len(candidate)>=500),'potential_predictor_concepts':6,
    'AI_classification_complete':bool(working['AI_Exposed'].notna().all()),
    'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,
    'raw_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RAW.glob('*.zip'))}}
(OUT/'build_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
dictionary = {
    'AI_Exposed':'1 confirmed material commercial AI exposure; 0 reviewed comparison; blank uncertain/unreviewed.',
    'EV_EBITDA':'Simplified USD enterprise value / matching four-quarter EBITDA; zero EBITDA is missing.',
    'Revenue_Growth':'Current four-quarter revenue / preceding four-quarter revenue - 1; eight consecutive complete USD quarters; prior >0.',
    'EBITDA_Margin':'Operating income plus cash-flow D&A over matching four quarters, divided by nonzero revenue; decimal.',
    'log_Market_Cap':'Natural log of positive same-date source Close times source Shares Outstanding, in USD.',
    'Leverage':'Short-term plus long-term debt / positive total assets; fresh USD balance sheet; decimal.',
    'IndustryId':'SimFin categorical industry identifier; name dictionary not supplied; 104xxx screen provisional.',
    'Market_Cap':'Same-date source split-adjusted Close times source Shares Outstanding; USD proxy; share vintage not independently verified.',
    'Revenue_TTM':'Four complete consecutive latest eligible quarterly revenues; USD consistency checked separately.',
    'Operating_Income_TTM':'Four complete consecutive latest eligible quarterly operating income observations.',
    'DA_TTM_Source':'Four complete consecutive cash-flow depreciation and amortization observations before income-window matching.',
    'DA_TTM':'DA_TTM_Source only when income/cashflow first and last report dates match.',
    'EBITDA_TTM':'Operating_Income_TTM + DA_TTM; standardized proxy, not adjusted EBITDA.',
    'Total_Debt':'Short Term Debt + Long Term Debt; either component missing makes total missing; no zero imputation.',
    'Total_Assets':'Latest available balance-sheet stock, USD before ratio eligibility checks; not a four-quarter sum.',
    'Enterprise_Value_Raw':'Market_Cap + Total_Debt - cash including short-term investments; no preferred or noncontrolling interests.',
    'Enterprise_Value':'Enterprise_Value_Raw only for fresh USD balance sheets.',
    'Prior_Revenue_TTM':'Sum of first four of eight selected consecutive quarters, requiring four nonmissing values.',
    'Known_Source_Discrepancy':'LiveWire operating income differs from original Q2 2025 earnings release; source values preserved.',
    'Any_Date_Chronology_Anomaly':'Any selected source has revision before publication or publication before report date; investigation pending.',
    'Any_Later_Restatement':'Any selected income/cashflow/growth/balance source revision date after snapshot; latest-restated values retained.',
    'Financial_Ready':'Complete positive-valuation financial pool with provisional financial-sector exclusion, regardless of AI review.',
    'Candidate_Analysis':'Financial_Ready plus reviewed AI classification; completeness does not establish adequate group overlap.',
    'Within_Hypothetical_1_99_Trim':'Sensitivity flag only, based on financial-pool p01/p99 for multiple/growth/margin/leverage; originals preserved.'}
pd.DataFrame([{'variable':col,'definition':dictionary.get(col,'Source field or audit field; see notebook construction.'),
               'dtype':str(working[col].dtype)} for col in working]).to_csv(OUT/'variable_dictionary.csv',index=False)
report = f"""# Notebook 1 sample-selection report — historical September 30, 2025 snapshot

Status: INCOMPLETE AI comparison dataset. Financial preparation executed; no regressions/model selection.
Working firms: {len(working)}. Financial-ready non-financial provisional pool: {len(financial_pool)}.
Strict reviewed-AI candidate: {len(candidate)}. Both reviewed groups present: {candidate['AI_Exposed'].nunique()==2}.
Assignment >=500 met by strict candidate: {len(candidate)>=500}. Six potential predictor concepts are prepared.

Sequential selection (order matters; exclusions are not additive across separate diagnostic tables):
{selection.to_string(index=False)}

Missingness:
{missingness.to_string(index=False)}

AI classification:
{classification_counts.to_string()}

With/without later revisions (unflagged is not certified point-in-time):
{sample_timing.to_string(index=False)}

Industry composition and reviewed-group overlap:
{industry_composition.to_string()}

Outlier summaries:
{tail_summary.to_string()}

No primary outlier treatment. Hypothetical joint p01/p99 trim:
{trim_counts.to_string(index=False)}

Unresolved: broad historical AI review coverage and within-industry group overlap; latest-restated values cannot be reversed from these archives;
official industry-name dictionary absent and 104xxx exclusion provisional; issuer-level D&A scope and tail filing checks pending;
source chronology anomalies and LiveWire operating-income discrepancy preserved and flagged; share-count vintage and split conventions not independently reconstructed. Supplied quarterly cash-flow convention checked against
Apple and NVIDIA annual totals. Financial EDA can begin with these limitations; AI-group EDA and regression-ready claims cannot.
See the notebook for primary-source links, exact definitions, and the auditable mapping protocol.
"""
(OUT/'sample_selection_report_INCOMPLETE.md').write_text(report,encoding='utf-8')
print(report)
print('Exports written to:', OUT)
assert working[ID].is_unique and working.loc[candidate_mask,ID].is_unique
for filename,expected in [('working_dataset.csv',len(working)),('candidate_analysis_INCOMPLETE.csv',len(candidate)),
                          ('financial_pool_AI_PENDING.csv',len(financial_pool)),('ai_mapping_PENDING.csv',len(ai))]:
    saved = pd.read_csv(OUT/filename)
    assert len(saved)==expected and saved[ID].is_unique
print('Export row counts and unique IDs verified.')''')

nb = nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
nbf.write(nb,ROOT/'notebooks/01_build_dataset.ipynb')
print('Built',len(cells),'cells')
