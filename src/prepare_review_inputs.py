"""Record primary-source reviews; these inputs are separate from notebook exports.

This script records the limited manual review, not an automated classifier.
Unknown materiality remains missing. Review dates differ from evidence dates.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data/manual'
DEST.mkdir(parents=True, exist_ok=True)
w = pd.read_csv(ROOT / 'data/processed/working_dataset.csv')
old = pd.read_csv(ROOT / 'data/processed/ai_mapping_PENDING.csv')
rows = []

def review(ticker, label, date, url, rationale, stage='pilot'):
    company = w.loc[w.Ticker.eq(ticker)].iloc[0]
    status = 'uncertain' if label is None else ('confirmed_exposed' if label == 1 else 'reviewed_comparison')
    rows.append(dict(SimFinId=int(company.SimFinId), Ticker=ticker,
        AI_Status=status, AI_Exposed=label, AI_Rationale=rationale,
        AI_Source=url, AI_Evidence_Date=date, AI_Reviewer='Codex primary-source review; independent adjudication pending',
        AI_Review_Date='2026-10-11', Review_Stage=stage))

for ticker in ['MSFT', 'KO', 'PG', 'NVDA']:
    sid = int(w.loc[w.Ticker.eq(ticker), 'SimFinId'].iloc[0])
    r = old.loc[old.SimFinId.eq(sid)].iloc[0]
    review(ticker, int(r.AI_Exposed), r.AI_Evidence_Date, r.AI_Source, r.AI_Rationale,
           'supplement' if ticker == 'NVDA' else 'pilot')

review('ORCL',1,'2024-12-09','https://www.oracle.com/news/announcement/q2fy25-earnings-release-2024-12-09/',
       'OCI commercially supplies GPU infrastructure for training AI models; the earnings release links substantial cloud growth to AI demand. Materiality is qualitative, not an estimated AI revenue share.')
review('IBM',1,'2025-07-23','https://newsroom.ibm.com/2025-07-23-IBM-RELEASES-SECOND-QUARTER-RESULTS',
       'Commercial generative-AI software and consulting are core offerings; reported cumulative generative-AI book of business exceeds $7.5bn. Book of business includes signings and is not recognized revenue.')
review('APLD',1,'2025-07-30','https://ir.applieddigital.com/_assets/_c07fd3c9e220d1bf6764026e5b493a63/appliedblockchaininc/news/2025-07-30_Applied_Digital_Reports_Fiscal_Fourth_Quarter_and__126.pdf',
       'Two signed 15-year CoreWeave AI data-center leases cover 250MW and approximately $7bn contracted revenue. Binding commercial infrastructure contracts qualify; an unsigned additional 150MW option is not counted.')
review('GDDY',1,'2025-05-01','https://investors.godaddy.net/newsroom/news-releases/press-release-details/2025/GoDaddy-Reports-First-Quarter-2025-Financial-Results/default.aspx',
       'Airo supplies customer-facing AI tools for business creation and digital commerce across the core small-business platform. This is commercial product exposure, not employee AI use; AI revenue is not separately disclosed.')
review('CCCS',None,'2025-07-31','https://ir.cccis.com/news-releases/news-release-details/ccc-intelligent-solutions-holdings-inc-announces-second-2',
       'Insurance software has AI-enabled offerings and a Medhub deployment initiative. This initial release review does not establish material commercial deployment versus testing across the firm; business/segment corroboration is required.')
review('CRNC',1,'2025-08-06','https://investors.cerence.com/news-events/press-releases/detail/86/cerence-announces-third-quarter-fiscal-2025-results-revenue-and-profitability-exceed-high-end-of-guidance',
       'Conversational AI for automakers is the core commercial business; quarterly release reports customer momentum and product deployments. The classification does not depend on internal AI adoption.')
review('GEN',1,'2025-02-19','https://investor.gendigital.com/news/news-details/2025/Norton-Launches-Enhanced-AI-Powered-Scam-Protection-Across-Cyber-Safety-Lineup/default.aspx',
       'Genie AI scam detection became available across Norton Cyber Safety products on this date, including commercial protection tiers. Customer-facing AI is integrated across a core product family; no separate AI revenue estimate is assumed.')
review('FICO',1,'2025-07-30','https://investors.fico.com/static-files/03b81cb9-df09-4466-be4f-d94a12c55402',
       'The issuer-hosted earnings transcript describes the commercial AI decisioning platform and software contract activity. Existing commercial decisioning qualifies; announcements of future foundation models alone do not.')
review('SNPS',1,'2024-03-20','https://news.synopsys.com/2024-03-20-Synopsys-Announces-New-AI-Driven-EDA%2C-IP-and-Systems-Design-Solutions-At-SNUG-Silicon-Valley',
       'Synopsys.ai design, verification and test applications are commercially available; issuer reports hundreds of chip tape-outs and expanding customer use. AI software is part of the core EDA offering.')
review('ACIW',1,'2022-03-09','https://investor.aciworldwide.com/node/23416',
       'Fraud Scoring Services commercially delivers machine-learning fraud detection to financial institutions. This supplements longstanding AI/ML fraud products in the core payments software business; not all payment revenue is treated as AI revenue.')
review('BLKB',None,'2025-07-30','https://investor.blackbaud.com/static-files/3ae17474-e545-47fd-9619-57dc2b6120b6',
       'The 10-Q describes AI features in customer solutions and early-stage agentic AI, alongside internal use. Commercial AI materiality and deployment scale remain unresolved; zero is not assigned.')
review('CTLP',None,'2025-05-08','https://cantaloupeinc.gcs-web.com/news-releases/news-release-details/cantaloupe-inc-reports-third-quarter-fiscal-year-2025-financial',
       'Reviewed self-service commerce, transaction/subscription revenue and smart-store discussion. This release cannot determine whether smart-store computer vision or related AI products are material; comparison label remains pending.')
review('FOUR',None,'2025-08-05','https://investors.shift4.com/news-events/press-releases/detail/271/shift4-announces-second-quarter-2025-results',
       'Release establishes payments/commerce business but refers to a separate shareholder letter. It is insufficient to exclude material customer-facing AI in acquired or embedded products; full business review remains necessary.')
review('RPAY',None,'2025-08-11','https://repay.com/repay-reports-second-quarter-2025-financial-results/',
       'Reviewed payment solutions and reported financial results. This release does not resolve commercial AI in fraud or payment services; lack of an AI mention is insufficient for a zero.')
review('PRTH',None,'2025-08-07','https://ir.prioritycommerce.com/news-releases/news-release-details/priority-technology-holdings-inc-reports-second-quarter',
       'Reviewed SMB, B2B and Enterprise payment/banking offerings. Embedded commercial AI materiality is not established or ruled out by this release; uncertain rather than an assumed comparison.')
review('AVGO',1,'2025-09-04','https://investors.broadcom.com/static-files/9836683a-9b92-4bec-9035-27942f21d42e',
       'Quarterly release reports $5.2bn AI revenue from custom accelerators and networking out of $15.952bn total revenue, establishing a material commercial AI infrastructure business.')
review('MU',1,'2025-03-20','https://investors.micron.com/news/press-release/2025/Micron-Technology-Inc--Reports-Results-for-the-Second-Quarter-of-Fiscal-2025-03-20-2025/default.aspx',
       'High-bandwidth memory supplied for AI computing generated over $1bn quarterly revenue. This is identifiable material AI infrastructure sales, not merely general semiconductor demand.')
review('INTC',1,'2024-04-09','https://www.intc.com/news-events/press-releases/detail/1689/intel-unleashes-enterprise-ai-with-gaudi-3-ai-open-systems',
       'Gaudi accelerators, enterprise AI systems and customer/partner deployments establish commercial AI compute products within the core processor business. This is qualitative product materiality, without assigning an AI revenue percentage.')
review('AMAT',None,'2025-05-15','https://ir.appliedmaterials.com/static-files/12e4e543-3e22-460e-90bc-055c95eb0797',
       'Earnings remarks link AI demand to wafer-fabrication investment. General manufacturing equipment benefiting from AI demand is not sufficient to establish a material AI-specific commercial offering; scope remains uncertain.')
review('LRCX',None,'2025-07-30','https://investor.lamresearch.com/2025-07-30-Lam-Research-Corporation-Reports-Financial-Results-for-the-Quarter-Ended-June-29%2C-2025',
       'Deposition/etch equipment demand is linked to the AI investment cycle, but this release does not isolate material AI-specific products. Indirect demand exposure is insufficient; no zero or one assigned.')
review('FSLR',0,'2025-07-31','https://www.sec.gov/Archives/edgar/data/1274494/000127449425000053/ex991pressreleaseq2-2025.htm',
       'Reviewed product/business description and results: thin-film photovoltaic modules sold to third parties are the core business. General power demand or AI-assisted manufacturing does not constitute selling AI products/services/infrastructure under the rule.')
review('ENPH',0,'2025-07-22','https://investor.enphase.com/static-files/4316f85e-4314-4f28-b537-4b73796d8356',
       'Reviewed quarterly product/revenue discussion: solar microinverters, batteries and home energy systems dominate disclosed offerings. No material commercial AI-specific offering is established; this comparison is a business-scope inference, not a claim of no internal AI use.')
review('RUN',0,'2025-08-06','https://investors.sunrun.com/filings-financials/sec-filings/content/0001469367-25-000147/exhibit991q225.htm',
       'Reviewed disclosed residential solar, batteries, subscriptions and home-to-grid services. These sell energy services rather than material AI-specific products or compute infrastructure; smart energy management alone does not qualify.')
review('DIOD',None,'2025-08-07','https://investor.diodes.com/static-files/c377b28c-9b7d-49fc-8b9e-8fd83abb3128',
       'Earnings transcript notes AI-related computing demand for semiconductor components. Attribution and materiality of AI-specific commercial supply remain unclear; indirect customer demand alone cannot determine exposure.')
review('DELL',1,'2025-08-28','https://investors.delltechnologies.com/static-files/e73d4aa5-b24e-439e-91c5-5b301ca80584',
       'Issuer-hosted earnings call reports substantial AI server shipments/orders and $11.7bn Blackwell AI server backlog. Material commercial AI computing infrastructure is identifiable.')
review('HPE',1,'2025-06-03','https://www.hpe.com/us/en/newsroom/blog-post/2025/06/hpe-delivers-fifth-consecutive-quarter-of-year-over-year-revenue-growth-and-impressive-innovation-in-q2.html',
       'Issuer describes commercial AI systems revenue, enterprise AI server orders and growing conversion of backlog. Core AI compute infrastructure sales qualify; generalized internal use is not the basis.')
review('NTAP',1,'2025-08-27','https://investors.netapp.com/news/news-details/2025/NetApp-Reports-First-Quarter-of-Fiscal-Year-2026-Results-08-27-2025/default.aspx',
       'AIPod and AI Data Platform reference storage systems commercially support customer training/inference pipelines. AI infrastructure is within the core storage offering; separate AI revenue is not disclosed.')
review('ENR',0,'2025-08-04','https://investors.energizerholdings.com/2025-08-04-Energizer-Holdings%2C-Inc-Announces-Fiscal-2025-Third-Quarter-Results',
       'Reviewed both reported revenue segments, Batteries & Lights and Auto Care. Disclosed products are consumer batteries, lighting and auto-care goods; no material AI commercial offering identified. This inference concerns commercial business, not internal technology use.')

# Expansion follows the pilot: customer-facing AI devices and same-code suppliers.
review('AAPL',1,'2025-02-19','https://www.apple.com/ie/newsroom/2025/02/apple-debuts-iphone-16e-a-powerful-new-member-of-the-iphone-16-family/',
       'Apple Intelligence is a deployed customer-facing AI system bundled in the flagship iPhone family, including the newly launched 16e. Embedded AI in a core commercial product qualifies qualitatively; no AI revenue fraction is estimated.', 'expansion')
review('HPQ',1,'2024-03-07','https://www.hp.com/us-en/newsroom/press-releases/2024/hp-unveils-largest-portfolio-ai-pc.html',
       'Commercial Elite/Pro AI PCs contain dedicated neural processing units and customer AI workloads across the core PC portfolio. Selling AI-capable computing products qualifies qualitatively; no separate AI revenue estimate is assumed.', 'expansion')
review('MEI',None,'2025-07-09','https://www.sec.gov/Archives/edgar/data/65270/000095017025094781/mei-ex99_1.htm',
       'Industrial revenue growth includes data-center power distribution. The report does not distinguish AI-specific infrastructure from general data centers or establish its firm-wide materiality; cannot classify as a comparison merely because automotive products are prominent.', 'expansion')
review('TRNS',0,'2025-05-19','https://www.transcat.com/news/post/transcat-reports-fiscal-fourth-quarter-and-full-year-2025-financial-results',
       'Reviewed Service and Distribution operations: accredited calibration, instrument distribution/rental and compliance services. No material commercial AI offering is identified in the disclosed business scope; routine technology investment does not qualify.', 'expansion')
review('MLAB',None,'2025-06-02','https://investors.mesalabs.com/news/news-details/2025/Mesa-Labs-Announces-Fourth-Quarter-and-Full-Fiscal-Year-2025-Results/default.aspx',
       'Reviewed life-science tools and quality-control segment discussion. Potential AI-enabled analysis in customer software requires corroboration and a materiality assessment; this preliminary business review does not justify a zero.', 'expansion')

ledger = pd.DataFrame(rows)
assert ledger.SimFinId.is_unique
assert pd.to_datetime(ledger.AI_Evidence_Date).le(pd.Timestamp('2025-09-30')).all()
ledger.to_csv(DEST / 'ai_review_ledger.csv', index=False)
original_pool = pd.read_csv(ROOT / 'data/processed/financial_pool_AI_PENDING.csv')
original_pool[['SimFinId','Ticker','IndustryId']].to_csv(DEST / 'initial_eligible_pool_742.csv', index=False)
assert len(original_pool) == 742
assert set(ledger.loc[ledger.Review_Stage.eq('pilot'), 'SimFinId']).issubset(set(original_pool.SimFinId))
supplement = pd.DataFrame([dict(SimFinId=172199, Field='Short Term Debt', Value=0,
    SimFin_Report_Date='2025-07-31', Filing_Period_End='2025-07-27',
    Evidence_Date='2025-08-27', Currency='USD', Matched_Long_Term_Debt=8466000000,
    Matched_Total_Assets=140740000000,
    Source_URL='https://www.sec.gov/Archives/edgar/data/1045810/000104581025000209/nvda-20250727.htm',
    Rationale='Original 10-Q: all $8.5bn note principal matures beyond one year; net carrying debt $8.466bn; no commercial paper outstanding. No current debt in balance-sheet/current-liability disclosures. Evidence-derived short-term borrowing is zero, excluding operating leases consistently with SimFin debt. Assets and long-term debt match exactly. SimFin July31 normalizes issuer July27 quarter end; this calendar normalization is explicit.')])
supplement.to_csv(DEST / 'financial_supplements.csv', index=False)
print(ledger.groupby(['Review_Stage','AI_Status']).size().to_string())
