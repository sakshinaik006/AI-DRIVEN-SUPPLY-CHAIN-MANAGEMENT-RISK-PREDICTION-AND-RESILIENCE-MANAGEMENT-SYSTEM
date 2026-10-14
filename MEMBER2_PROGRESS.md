# Member 2 Progress Checklist: NLP, Anomaly and API Engineer

## Project Details
- **Role**: Member 2 (NLP, Anomaly Detection, and FastAPI Backend)
- **Dedicated Branch**: `member-2-day1-day2`
- **Scope**: Day 1 & Day 2 Assigned Deliverables (Complete & Fully Verified)

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
  - **Commit**: Tag `v0.2-day2`
  - **Next action**: Day 3 tasks (pointing API to final CatBoost predictions, LLM alert prompt formulation, demo preparation, and joint report sections).
