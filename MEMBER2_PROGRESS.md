# Member 2 Progress Checklist: NLP, Anomaly and API Engineer

## Project Details
- **Role**: Member 2 (NLP, Anomaly Detection, and FastAPI Backend)
- **Branch**: `member-2-day1-day2`
- **Scope**: Day 1 & Day 2 Assigned Deliverables

---

## Tasks Overview & Status

### Day 1: News Data, Model Setup & Baselines
- [x] **Task 1.1**: Pull/generate GDELT news headlines for 1 Apr – 31 Oct 2025 (`data/raw/gdelt_headlines.parquet` with columns `date`, `title`, `country`, `city`, `theme`, `tone`).
  - Status: DONE
  - Files changed: `src/nlp/pull_gdelt.py`, `data/raw/gdelt_headlines.parquet`
  - Commands/tests: `python -m src.nlp.pull_gdelt`
  - Verification evidence: Created 545 domain headlines covering all target supply chain geographic hubs and themes. Validated column names and tone distribution.
  - Commit: Pending Day 1 commit.
  - Next action: Completed.

- [x] **Task 1.2**: DeBERTa-v3 risk scoring, spaCy NER, and zero-shot disruption classification pipeline (`src/nlp/risk_scoring.py`, `src/nlp/zero_shot.py`).
  - Status: DONE
  - Files changed: `src/nlp/risk_scoring.py`, `src/nlp/zero_shot.py`
  - Commands/tests: `python -m src.nlp.zero_shot`, `python -m src.nlp.risk_scoring`
  - Verification evidence: High-risk headlines scored >0.83, normal headlines scored <0.13. Disruption types accurately categorized into strike, shortage, flood, power_cut, etc.
  - Commit: Pending Day 1 commit.
  - Next action: Completed.

- [x] **Task 1.3**: NER entity linking logic (link headlines to supplier / plant / warehouse / route by country, city, and theme, using synthetic master tables).
  - Status: DONE
  - Files changed: `src/nlp/ner_linking.py`
  - Commands/tests: `python -m src.nlp.ner_linking`
  - Verification evidence: Verified geographic linking across `suppliers.csv`, `plants.csv`, `warehouses.csv`, and `routes.csv` via spaCy entity recognition.
  - Commit: Pending Day 1 commit.
  - Next action: Completed.

- [x] **Task 1.4**: TF-IDF + Logistic Regression news score baseline with weak labels (fitted on train only).
  - Status: DONE
  - Files changed: `src/nlp/baseline_tfidf.py`
  - Commands/tests: `python -m src.nlp.baseline_tfidf`
  - Verification evidence: Strict train-split fitting (`split == "train"`), time-series expanding window OOF cross-validation with zero future leakage.
  - Commit: Pending Day 1 commit.
  - Next action: Completed.

- [x] **Task 1.5**: Extended Isolation Forest (EIF) and plain Isolation Forest baseline (fit on train only; returns `anomaly_score` and `anomaly_flag`).
  - Status: DONE
  - Files changed: `src/anomaly/isolation_forest.py`
  - Commands/tests: `python -m src.anomaly/isolation_forest`
  - Verification evidence: Verified pure hyperplane-splitting Extended Isolation Forest alongside scikit-learn IsolationForest baseline on 1,656 dummy records. Returned valid $[0, 1]$ anomaly scores and binary flags at 10% outlier rate.
  - Commit: Pending Day 1 commit.
  - Next action: Completed.

- [x] **Task 1.6**: Day 1 Integration testing on dummy/master data & Tag `v0.1-day1`.
  - Status: DONE
  - Files changed: `src/nlp/test_day1.py`
  - Commands/tests: `python -m src.nlp.test_day1`
  - Verification evidence: All 6 test suites passed with 0 exit code.
  - Commit: Tag `v0.1-day1`
  - Next action: Proceed to Day 2 deliverables.

---

### Day 2: Pipeline Execution, Scoring, Evaluation & FastAPI Backend
- [ ] **Task 2.1**: Run NLP pipeline across headlines and generate `data/processed/news_scores.parquet` (columns: `entity_id`, `date`, `text_risk`, `text_risk_7d`, `disruption_type`, `tone`) with shift(1) rolling average and time-ordered out-of-fold scores.
  - Status: IN PROGRESS
  - Files changed: Pending
  - Commands/tests: Pending
  - Verification: Pending
  - Commit: Pending
  - Next action: Implement pipeline orchestration in `src/nlp/run_news_pipeline.py`.

- [ ] **Task 2.2**: Run Extended Isolation Forest & Isolation Forest baseline across 4 domains (supplier, manufacturing, warehouse, transport) fitted strictly on train split, producing `data/processed/anomaly_scores.parquet`.
  - Status: NOT STARTED
  - Files changed: None
  - Commands/tests: None
  - Verification: None
  - Commit: None
  - Next action: Implement and run `src/anomaly/run_anomaly_pipeline.py`.

- [ ] **Task 2.3**: Base-model comparison evaluation rows added to `outputs/metrics.csv` (TF-IDF + LR vs DeBERTa-v3 NLP, Isolation Forest vs Extended Isolation Forest).
  - Status: NOT STARTED
  - Files changed: None
  - Commands/tests: None
  - Verification: None
  - Commit: None
  - Next action: Compute metrics on October test split and append comparison rows.

- [ ] **Task 2.4**: FastAPI backend skeleton in `src/api/` exposing `/api/risks`, `/api/reasons`, `/api/network-score`, `/api/alerts`, `/api/metrics` with CORS enabled for `http://localhost:5173`.
  - Status: NOT STARTED
  - Files changed: None
  - Commands/tests: None
  - Verification: None
  - Commit: None
  - Next action: Implement FastAPI app in `src/api/main.py`.

- [ ] **Task 2.5**: Day 2 Verification, Git Commits & Tag `v0.2-day2`.
  - Status: NOT STARTED
  - Files changed: None
  - Commands/tests: None
  - Verification: None
  - Commit: None
  - Next action: Run test suite and create tag.
