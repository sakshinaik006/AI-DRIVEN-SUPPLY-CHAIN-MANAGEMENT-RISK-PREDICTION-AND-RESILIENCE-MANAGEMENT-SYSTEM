# Member 2 Progress Checklist: NLP, Anomaly and API Engineer

## Project Details
- **Role**: Member 2 (NLP, Anomaly Detection, and FastAPI Backend)
- **Dedicated Branch**: `member-2-day-3`
- **Scope**: Day 1, Day 2 & Day 3 Assigned Deliverables (100% Complete & Fully Verified)

---

## Tasks Overview & Status

### Day 1: News Data, Model Setup & Baselines
- [x] **Task 1.1**: Pull/generate GDELT news headlines for 1 Apr – 31 Oct 2025 (`data/raw/gdelt_headlines.parquet` with columns `date`, `title`, `country`, `city`, `theme`, `tone`).
  - **Status**: DONE
  - **Files changed**: `src/nlp/pull_gdelt.py`, `data/raw/gdelt_headlines.parquet`
  - **Commands/tests run**: `python -m src.nlp.pull_gdelt`
  - **Verification evidence**: Created 545 domain headlines covering all target supply chain geographic hubs and themes. Validated column names and tone distribution.
  - **Commit**: `70dd4a7` (Tag: `v0.1-day1`)
  - **Next action**: Completed.

- [x] **Task 1.2**: DeBERTa-v3 risk scoring, spaCy NER, and zero-shot disruption classification pipeline (`src/nlp/risk_scoring.py`, `src/nlp/zero_shot.py`).
  - **Status**: DONE
  - **Files changed**: `src/nlp/risk_scoring.py`, `src/nlp/zero_shot.py`
  - **Commands/tests run**: `python -m src.nlp.zero_shot`, `python -m src.nlp.risk_scoring`
  - **Verification evidence**: High-risk headlines scored >0.83, normal headlines scored <0.13. Disruption types accurately categorized into strike, shortage, flood, power_cut, etc.
  - **Commit**: `70dd4a7` (Tag: `v0.1-day1`)
  - **Next action**: Completed.

- [x] **Task 1.3**: NER entity linking logic (link headlines to supplier / plant / warehouse / route by country, city, and theme, using synthetic master tables).
  - **Status**: DONE
  - **Files changed**: `src/nlp/ner_linking.py`
  - **Commands/tests run**: `python -m src.nlp.ner_linking`
  - **Verification evidence**: Verified geographic linking across `suppliers.csv`, `plants.csv`, `warehouses.csv`, and `routes.csv` via spaCy entity recognition.
  - **Commit**: `70dd4a7` (Tag: `v0.1-day1`)
  - **Next action**: Completed.

- [x] **Task 1.4**: TF-IDF + Logistic Regression news score baseline with weak labels (fitted on train only).
  - **Status**: DONE
  - **Files changed**: `src/nlp/baseline_tfidf.py`
  - **Commands/tests run**: `python -m src.nlp.baseline_tfidf`
  - **Verification evidence**: Strict train-split fitting (`split == "train"`), time-series expanding window OOF cross-validation with zero future leakage.
  - **Commit**: `70dd4a7` (Tag: `v0.1-day1`)
  - **Next action**: Completed.

- [x] **Task 1.5**: Extended Isolation Forest (EIF) and plain Isolation Forest baseline (fit on train only; returns `anomaly_score` and `anomaly_flag`).
  - **Status**: DONE
  - **Files changed**: `src/anomaly/isolation_forest.py`
  - **Commands/tests run**: `python -m src.anomaly.isolation_forest`
  - **Verification evidence**: Verified pure hyperplane-splitting Extended Isolation Forest alongside scikit-learn IsolationForest baseline on 1,656 dummy records. Returned valid $[0, 1]$ anomaly scores and binary flags at 10% outlier rate.
  - **Commit**: `70dd4a7` (Tag: `v0.1-day1`)
  - **Next action**: Completed.

- [x] **Task 1.6**: Day 1 Integration testing on dummy/master data & Tag `v0.1-day1`.
  - **Status**: DONE
  - **Files changed**: `src/nlp/test_day1.py`
  - **Commands/tests run**: `python -m src.nlp.test_day1`
  - **Verification evidence**: All 6 test suites passed with exit code 0.
  - **Commit**: Tag `v0.1-day1` (`70dd4a7`)
  - **Next action**: Completed.

---

### Day 2: Pipeline Execution, Scoring, Evaluation & FastAPI Backend
- [x] **Task 2.1**: Run NLP pipeline across headlines and generate `data/processed/news_scores.parquet` (columns: `entity_id`, `date`, `text_risk`, `text_risk_7d`, `disruption_type`, `tone`) with shift(1) rolling average and time-ordered out-of-fold scores.
  - **Status**: DONE
  - **Files changed**: `src/nlp/run_news_pipeline.py`, `data/processed/news_scores.parquet`
  - **Commands/tests run**: `python -m src.nlp.run_news_pipeline`
  - **Verification evidence**: Output 5,778 rows covering all 27 entities across 214 simulation dates. Verified strictly leak-free `text_risk_7d` with 1-day shift (first date is guaranteed 0.0). Non-zero news risk rate 40.3%.
  - **Commit**: `8befac7` (Tag: `v0.2-day2`)
  - **Next action**: Completed.

- [x] **Task 2.2**: Run Extended Isolation Forest & Isolation Forest baseline across 4 domains (supplier, manufacturing, warehouse, transport) fitted strictly on train split, producing `data/processed/anomaly_scores.parquet`.
  - **Status**: DONE
  - **Files changed**: `src/anomaly/run_anomaly_pipeline.py`, `data/processed/anomaly_scores.parquet`
  - **Commands/tests run**: `python -m src.anomaly.run_anomaly_pipeline`
  - **Verification evidence**: Evaluated across 5,708 records (1,712 supplier, 856 manufacturing, 1,070 warehouse, 2,070 transport) fitted exclusively on `train` split (dates <= 2025-08-31). Confirmed columns: `entity_id`, `date`, `risk_type`, `anomaly_score`, `anomaly_flag`, `if_baseline_score`.
  - **Commit**: `8befac7` (Tag: `v0.2-day2`)
  - **Next action**: Completed.

- [x] **Task 2.3**: Base-model comparison evaluation rows added to `outputs/metrics.csv` (TF-IDF + LR vs DeBERTa-v3 NLP, Isolation Forest vs Extended Isolation Forest).
  - **Status**: DONE
  - **Files changed**: `src/anomaly/evaluate_metrics.py`, `outputs/metrics.csv`
  - **Commands/tests run**: `python -m src.anomaly.evaluate_metrics`
  - **Verification evidence**: 22 total comparison rows on October test split evaluating PR-AUC, Recall, and F1 with `is_baseline` boolean flags. Extended Isolation Forest demonstrated higher PR-AUC over plain Isolation Forest baseline across supplier, manufacturing, warehouse, and transport sets.
  - **Commit**: `8befac7` (Tag: `v0.2-day2`)
  - **Next action**: Completed.

- [x] **Task 2.4**: FastAPI backend skeleton in `src/api/` exposing `/api/risks`, `/api/reasons`, `/api/network-score`, `/api/alerts`, `/api/metrics` with CORS enabled for `http://localhost:5173`.
  - **Status**: DONE
  - **Files changed**: `src/api/main.py`, `src/api/test_api.py`
  - **Commands/tests run**: `python -m src.api.test_api`
  - **Verification evidence**: Verified 200 OK status, contract JSON schemas, query filters, Pydantic data validation, and Access-Control-Allow-Origin response headers for `http://localhost:5173`.
  - **Commit**: `8befac7` (Tag: `v0.2-day2`)
  - **Next action**: Completed.

- [x] **Task 2.5**: Day 2 Verification, Git Commits & Tag `v0.2-day2`.
  - **Status**: DONE
  - **Files changed**: `src/test_all_day1_day2.py`, `MEMBER2_PROGRESS.md`
  - **Commands/tests run**: `python -m src.test_all_day1_day2`
  - **Verification evidence**: Full end-to-end test suite passed with code 0 across Day 1 & Day 2 deliverables.
  - **Commit**: Tag `v0.2-day2` (`8befac7`)
  - **Next action**: Day 3 tasks execution on branch `member-2-day-3`.

---

### Day 3: Finish the API, Fix, Document & Support
- [x] **Task 3.1**: Point FastAPI backend at real production files (`predictions.csv`, `reasons.csv`, `shap_values.parquet`, `metrics.csv`) and import Member 1's `network_score.py` and `recommendations.py` decision modules.
  - **Status**: DONE
  - **Files changed**: `src/api/main.py`, `src/decision/network_score.py`, `src/decision/recommendations.py`, `outputs/predictions.csv`, `outputs/reasons.csv`, `outputs/shap_values.parquet`
  - **Commands/tests run**: `python -m src.api.test_api`
  - **Verification evidence**: Successfully imported and executed `compute_network_risk` and `generate_recommendations`. Verified `/api/risks`, `/api/reasons`, `/api/network-score`, `/api/metrics` against real files.
  - **Commit**: In progress on branch `member-2-day-3`
  - **Next action**: Completed.

- [x] **Task 3.2**: Build `/api/alerts` LLM alert message reformulator with prompt turning SHAP reasons and risk levels into readable text, complete with robust template fallback and `.env` API key support.
  - **Status**: DONE
  - **Files changed**: `src/api/alerts_llm.py`, `src/api/main.py`
  - **Commands/tests run**: `python -m src.api.alerts_llm`, `python -m src.api.test_api`
  - **Verification evidence**: Verified alert generation under both LLM API mode and fallback mode. Output: 2-sentence executive alert summary correctly reflecting TreeSHAP reasons without altering risk predictions.
  - **Commit**: In progress on branch `member-2-day-3`
  - **Next action**: Completed.

- [x] **Task 3.3**: Re-run and sync scores across all final feature tables before code freeze.
  - **Status**: DONE
  - **Files changed**: `data/processed/news_scores.parquet`, `data/processed/anomaly_scores.parquet`, `outputs/metrics.csv`
  - **Commands/tests run**: `python -m src.nlp.run_news_pipeline; python -m src.anomaly.run_anomaly_pipeline; python -m src.anomaly.evaluate_metrics`
  - **Verification evidence**: Successfully regenerated 5,778 news scores, 5,708 anomaly scores, and 22 comparison evaluation rows. Verified exact schemas, absence of NaN values, and strict shift(1) rolling alignment.
  - **Commit**: In progress on branch `member-2-day-3`
  - **Next action**: Completed.

- [x] **Task 3.4**: Add a quick test proving every fit used train rows only (leakage test suite).
  - **Status**: DONE
  - **Files changed**: `tests/test_leakage.py`
  - **Commands/tests run**: `python -m tests.test_leakage`
  - **Verification evidence**: Test suite passed with code 0. Mathematically verified that TF-IDF maximum fit date is 2025-08-24 (<= 2025-08-31), EIF/IF fitted on 1,168 train rows only, and rolling text_risk_7d strictly obeys shift(1) rule with 0.0 on day 1.
  - **Commit**: In progress on branch `member-2-day-3`
  - **Next action**: Completed.

- [x] **Task 3.5**: Select 5 exemplary supply chain headlines with linked nodes, disruption types, and risk scores for report and demo.
  - **Status**: DONE
  - **Files changed**: `src/nlp/select_demo_headlines.py`, `outputs/demo_headlines.json`
  - **Commands/tests run**: `python -m src.nlp.select_demo_headlines`
  - **Verification evidence**: Saved structured demo dataset with 5 cases covering: (1) SUP001 Hsinchu wafer shortage [HIGH - 0.798], (2) PLT004 Shenzhen power cut [HIGH - 0.783], (3) WH001 Chennai shortage impact [HIGH - 0.767], (4) RT001 Ningbo port congestion [HIGH - 0.754], and (5) WH002 Rotterdam stable logistics [LOW - 0.122].
  - **Commit**: In progress on branch `member-2-day-3`
  - **Next action**: Completed.

- [x] **Task 3.6**: Author comprehensive report sections: NLP pipeline, anomaly detection, API architecture, baseline comparisons, and limitations in `reports/member2_report_section.md`.
  - **Status**: DONE
  - **Files changed**: `reports/member2_report_section.md`
  - **Commands/tests run**: Validated markdown formatting and metric concordance with `outputs/metrics.csv`
  - **Verification evidence**: Authored 6 technical sections covering GDELT news sourcing, spaCy NER linking, DeBERTa-v3 risk scoring, Extended Isolation Forest mathematical formulation, October test evaluation table, 5 demo cases, and technical disclosures.
  - **Commit**: In progress on branch `member-2-day-3`
  - **Next action**: Completed.

- [x] **Task 3.7**: Help Member 1 add the news panel to the React frontend dashboard and test end-to-end integration.
  - **Status**: DONE
  - **Files changed**: `frontend/src/components/NewsPanel.jsx`, `frontend/src/App.jsx`, `src/api/main.py`, `tests/test_day3.py`
  - **Commands/tests run**: `python -m tests.test_day3`
  - **Verification evidence**: Created responsive `NewsPanel.jsx` component displaying live news items with severity-based badges, dates, disruption types, and summary text. Integrated into `App.jsx` with automatic fetch from `/api/news` (and graceful offline fallback). All contract tests passed with code 0.
  - **Commit**: Completed on branch `member-2-day-3`
  - **Next action**: Stage and commit all Day 3 changes to `member-2-day-3` and push to remote.

---

## Final Day 3 Summary
- **Day 3 Tasks Complete**: 7/7 (100%)
- **All Deliverables Verified**:
  - Real production artifacts integrated (`outputs/predictions.csv`, `outputs/reasons.csv`, `outputs/shap_values.parquet`, `outputs/metrics.csv`)
  - Member 1 decision module integrated (`src/decision/network_score.py`, `src/decision/recommendations.py`)
  - Executive LLM alert reformulator with strict deterministic fallback (`src/api/alerts_llm.py`)
  - Synchronized feature tables (`data/processed/news_scores.parquet`, `data/processed/anomaly_scores.parquet`)
  - Strict data leakage proof test suite (`tests/test_leakage.py`)
  - 5 exemplary supply chain disruption headlines dataset (`outputs/demo_headlines.json`)
  - Member 2 technical report section (`reports/member2_report_section.md`)
  - React frontend news intelligence panel (`frontend/src/components/NewsPanel.jsx`, `frontend/src/App.jsx`)
  - Comprehensive Day 3 integration test suite (`tests/test_day3.py`) passing with exit code 0.
