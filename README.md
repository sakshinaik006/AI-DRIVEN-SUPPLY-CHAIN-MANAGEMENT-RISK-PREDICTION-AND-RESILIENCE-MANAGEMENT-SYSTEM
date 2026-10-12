# AI-Driven Supply Chain Risk Prediction and Resilience Management Platform

Predicts four risks for a smartphone supply chain, 7 days ahead, shows each as
Low / Medium / High, and explains every alert with TreeSHAP.

Risks: supplier failure, manufacturing delay, warehouse stockout, transport disruption.
Window: 1 Apr to 31 Oct 2025. Train = Apr-Aug, Validation = Sep, Test = Oct.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in keys (never commit .env)
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Generate dummy files (until real files arrive)

```bash
python -m src.data.make_dummy
```

Writes parquet/csv files in the agreed format to `data/processed/` and `outputs/`.

## Layout

| Folder | Owner | Contents |
|---|---|---|
| docs/ | M1 | interface, API contract, labels, assumptions, data dictionary, disclosure |
| data/raw, data/synthetic, data/processed | all | pulled data, synthetic tables, parquet files passed between members |
| src/data, src/graph, src/decision | M1 | data, graph, network score and recommendations |
| src/nlp, src/anomaly, src/api | M2 | news NLP, anomaly detection, FastAPI |
| src/forecast, src/stacking, src/explain | M3 | forecasting, CatBoost stacking, SHAP |
| frontend/ | M1 | React (Vite) dashboard |
| notebooks, models, outputs, reports | all | exploration, saved models, predictions/metrics, report |

## Team rules

- `main` is protected. Work on `member1/data-graph-dashboard`, `member2/nlp-anomaly-api`, `member3/forecast-stacking-shap`.
- Small PRs into main at least twice a day (midday and evening). Pull main before every work block.
- Commit message tags: `[data] [graph] [nlp] [anomaly] [api] [model] [shap] [ui]`.
- Secrets live in `.env` only. Never commit keys; never put an LLM key in React code.
- Files over 100 MB are rejected by GitHub: save as parquet, or commit a sample plus the generating script.
- Fix random seeds, use relative paths, so the run reproduces from a fresh clone.
- Tags: `v0.1-day1`, `v0.2-day2`, `v1.0-final`.

## Disclosure

See `docs/disclosure.md` (written on Day 3). Short version: the models partly learn
the rules of the synthetic data generator, so results show that the pipeline works,
not real-world accuracy.
