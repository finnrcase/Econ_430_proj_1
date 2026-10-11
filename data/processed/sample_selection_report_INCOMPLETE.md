# Notebook 1 sample-selection report — historical September 30, 2025 snapshot

Status: INCOMPLETE AI comparison dataset. Financial preparation executed; no regressions/model selection.
Working firms: 4699. Financial-ready non-financial provisional pool: 742.
Strict reviewed-AI candidate: 3. Both reviewed groups present: True.
Assignment >=500 met by strict candidate: False. Six potential predictor concepts are prepared.

Sequential selection (order matters; exclusions are not additive across separate diagnostic tables):
                                                                         stage  remaining  excluded_at_stage
                                                    Exact-date market universe       4699                  0
                                                Positive market capitalization       4440                259
                                  Positive source price and shares outstanding       4440                  0
                                     Eligible fresh four-quarter income window       1948               2492
                                 Matched four-quarter USD cashflow and balance       1943                  5
                                                           Fresh balance sheet       1943                  0
                                                              Positive revenue       1758                185
                                                               Positive EBITDA       1365                393
                                                     Positive enterprise value        779                586
Complete finite financial outcome and controls, including eight-quarter growth        757                 22
                     Exclude provisional financial-related industries (104xxx)        742                 15
                       Reviewed AI classification and complete model variables          3                739

Missingness:
        variable  missing  available
      AI_Exposed     4695          4
       EV_EBITDA     3813        886
  Revenue_Growth     3044       1655
   EBITDA_Margin     2973       1726
  log_Market_Cap      259       4440
        Leverage     3643       1056
      IndustryId      105       4594
      Market_Cap      178       4521
     Revenue_TTM     2931       1768
      EBITDA_TTM     2825       1874
      Total_Debt     3529       1170
    Total_Assets     2202       2497
Enterprise_Value     3647       1052

AI classification:
                     working  financial_pool  candidate
AI_Status                                              
unreviewed              4695             739          0
reviewed_comparison        2               2          2
confirmed_exposed          2               1          1

With/without later revisions (unflagged is not certified point-in-time):
                                       sample  including_flagged  without_later_restatement_flags  without_flags_and_complete_timing  also_without_chronology_anomalies
financial_pool_including_financial_industries                757                                7                                  7                                  0
            primary_financial_pool_AI_pending                742                                7                                  7                                  0
             reviewed_AI_candidate_INCOMPLETE                  3                                0                                  0                                  0

Industry composition and reviewed-group overlap:
            working_firms  financial_ready  candidate_firms  confirmed_exposed  reviewed_comparison  unreviewed  uncertain  both_reviewed_groups
IndustryId                                                                                                                                      
100001.0              163               57                0                0.0                  0.0        57.0          0                 False
100002.0               68               19                0                0.0                  0.0        19.0          0                 False
100003.0               60               31                0                0.0                  0.0        31.0          0                 False
100004.0               15                4                0                0.0                  0.0         4.0          0                 False
100005.0               13                7                0                0.0                  0.0         7.0          0                 False
100006.0               16                2                0                0.0                  0.0         2.0          0                 False
100007.0               30                8                0                0.0                  0.0         8.0          0                 False
100008.0               55               10                0                0.0                  0.0        10.0          0                 False
100009.0               17               11                0                0.0                  0.0        11.0          0                 False
100010.0               87               27                0                0.0                  0.0        27.0          0                 False
100011.0               19                0                0                0.0                  0.0         0.0          0                 False
100012.0                3                0                0                0.0                  0.0         0.0          0                 False
100013.0                4                1                0                0.0                  0.0         1.0          0                 False
101001.0              130               33                0                0.0                  0.0        33.0          0                 False
101002.0               52                7                0                0.0                  0.0         7.0          0                 False
101003.0              365               48                1                1.0                  0.0        47.0          0                 False
101004.0              108               22                0                0.0                  0.0        22.0          0                 False
101005.0               53                9                0                0.0                  0.0         9.0          0                 False
102001.0               44               18                0                0.0                  0.0        18.0          0                 False
102002.0              100               25                1                0.0                  1.0        24.0          0                 False
102003.0               11                2                0                0.0                  0.0         2.0          0                 False
102004.0               12                2                0                0.0                  0.0         2.0          0                 False
102005.0               16                3                1                0.0                  1.0         2.0          0                 False
102006.0               32                3                0                0.0                  0.0         3.0          0                 False
103001.0               66               15                0                0.0                  0.0        15.0          0                 False
103002.0              123               18                0                0.0                  0.0        18.0          0                 False
103003.0               55               16                0                0.0                  0.0        16.0          0                 False
103004.0               60               18                0                0.0                  0.0        18.0          0                 False
103005.0               97               23                0                0.0                  0.0        23.0          0                 False
103011.0               22                4                0                0.0                  0.0         4.0          0                 False
103013.0               26                5                0                0.0                  0.0         5.0          0                 False
103015.0               90               32                0                0.0                  0.0        32.0          0                 False
103018.0               17                8                0                0.0                  0.0         8.0          0                 False
103020.0               16                7                0                0.0                  0.0         7.0          0                 False
103026.0               11                0                0                0.0                  0.0         0.0          0                 False
104001.0              104                0                0                0.0                  0.0         0.0          0                 False
104002.0              488                0                0                0.0                  0.0         0.0          0                 False
104003.0               64                0                0                0.0                  0.0         0.0          0                 False
104004.0               15                0                0                0.0                  0.0         0.0          0                 False
104005.0               17                0                0                0.0                  0.0         0.0          0                 False
104006.0               37                0                0                0.0                  0.0         0.0          0                 False
104007.0               49                0                0                0.0                  0.0         0.0          0                 False
104013.0               22                0                0                0.0                  0.0         0.0          0                 False
105001.0               76               14                0                0.0                  0.0        14.0          0                 False
105002.0                7                2                0                0.0                  0.0         2.0          0                 False
106001.0               56               15                0                0.0                  0.0        15.0          0                 False
106002.0              522               10                0                0.0                  0.0        10.0          0                 False
106003.0               46                9                0                0.0                  0.0         9.0          0                 False
106004.0              105               17                0                0.0                  0.0        17.0          0                 False
106005.0               98               19                0                0.0                  0.0        19.0          0                 False
106006.0               11                1                0                0.0                  0.0         1.0          0                 False
106011.0               45                9                0                0.0                  0.0         9.0          0                 False
106014.0                7                2                0                0.0                  0.0         2.0          0                 False
107001.0               20                7                0                0.0                  0.0         7.0          0                 False
107002.0               64                8                0                0.0                  0.0         8.0          0                 False
107003.0               34               12                0                0.0                  0.0        12.0          0                 False
107004.0               50               16                0                0.0                  0.0        16.0          0                 False
107005.0               15                3                0                0.0                  0.0         3.0          0                 False
107006.0                7                2                0                0.0                  0.0         2.0          0                 False
107007.0               20                0                0                0.0                  0.0         0.0          0                 False
108001.0               59               15                0                0.0                  0.0        15.0          0                 False
108002.0                4                2                0                0.0                  0.0         2.0          0                 False
108003.0                3                0                0                0.0                  0.0         0.0          0                 False
108004.0                5                3                0                0.0                  0.0         3.0          0                 False
109001.0              189               23                0                0.0                  0.0        23.0          0                 False
109002.0               53                6                0                0.0                  0.0         6.0          0                 False
110001.0               65               20                0                0.0                  0.0        20.0          0                 False
110002.0                9                3                0                0.0                  0.0         3.0          0                 False
110003.0               16                3                0                0.0                  0.0         3.0          0                 False
110004.0               96                6                0                0.0                  0.0         6.0          0                 False
110005.0               33               15                0                0.0                  0.0        15.0          0                 False
110006.0                5                1                0                0.0                  0.0         1.0          0                 False
110007.0               17                4                0                0.0                  0.0         4.0          0                 False
111001.0                5                0                0                0.0                  0.0         0.0          0                 False
NaN                   105                0                0                0.0                  0.0         0.0          0                 False

Outlier summaries:
                                count       mean         std           min          1%         5%        50%        95%         99%          max
sample         variable                                                                                                                         
working        EV_EBITDA        886.0  16.316973  185.259458   -838.036752 -121.103798 -12.998217  11.125975  32.990473  107.531974  5345.107789
               Revenue_Growth  1655.0   0.753452   21.406468     -0.998368   -0.649913  -0.227506   0.046693   0.466423    2.004105   858.202952
               EBITDA_Margin   1726.0 -15.301226  357.091181 -13451.716102  -45.009560  -2.521445   0.128424   0.597326    0.793036     1.224498
               Leverage        1056.0   0.535355    3.491474      0.000238    0.006088   0.045971   0.322434   0.796694    3.002489   109.068929
financial_pool EV_EBITDA        742.0  23.740092  197.884355      0.807149    2.731853   5.041459  12.338981  33.086108  101.009255  5345.107789
               Revenue_Growth   742.0   0.055931    0.199453     -0.620754   -0.260156  -0.118203   0.032270   0.273343    0.763764     2.658357
               EBITDA_Margin    742.0   0.202907    0.155017      0.000079    0.013634   0.038280   0.161813   0.523256    0.744603     0.909739
               Leverage         742.0   0.352799    0.222254      0.000238    0.011353   0.069095   0.324917   0.744032    1.153201     1.736276

No primary outlier treatment. Hypothetical joint p01/p99 trim:
            sample  original  hypothetical_trim
    financial_pool       742                686
reviewed_candidate         3                  3

Unresolved: broad historical AI review coverage and within-industry group overlap; latest-restated values cannot be reversed from these archives;
official industry-name dictionary absent and 104xxx exclusion provisional; issuer-level D&A scope and tail filing checks pending;
source chronology anomalies and LiveWire operating-income discrepancy preserved and flagged; share-count vintage and split conventions not independently reconstructed. Supplied quarterly cash-flow convention checked against
Apple and NVIDIA annual totals. Financial EDA can begin with these limitations; AI-group EDA and regression-ready claims cannot.
See the notebook for primary-source links, exact definitions, and the auditable mapping protocol.
