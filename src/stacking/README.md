## Member 3: Forecasting, Stacking, and Explainability

This section contains the time-series forecasting, out-of-fold (OOF) cross-validation, and multi-target CatBoost stacking pipelines. 

### Directory Structure
* `src/forecast/`: Time-series forecasting models (Exponential Smoothing, Chronos-2, PatchTST).
* `src/stacking/`: Multi-target classification, risk stacking, and validation logic.
* `src/explain/`: TreeSHAP explainability engine for feature attribution.
* `outputs/`: Generated predictions and SHAP value files (tracked via Git LFS or excluded if large).
* `models/`: Saved model binaries (e.g., CatBoost `.cbm` or `.joblib`).

### Current Implementations (Day 1)

#### 1. Time-Ordered Out-of-Fold Splitter (`src/stacking/oof.py`)
Implements an expanding-window cross-validator (`TimeSeriesOOF`) tailored for supply chain metrics. This ensures strict adherence to the project's leakage rules by guaranteeing that base models (forecasts, anomaly scores) never train on future data before generating the probabilities fed into the final CatBoost multi-target model.

#### 2. Stacking Scaffold (`src/stacking/stack_scaffold.py`)
A temporary generator built to fulfill **Handover #6**. It outputs dummy probabilities and risk levels (Low/Medium/High) across the agreed time window (1 April to 31 October 2025) for all four risk types (Supplier, Manufacturing, Warehouse, Transport). 

### How to Run the Scaffold
To generate the dummy `predictions.csv` for backend API integration testing:

1. Ensure your virtual environment is active.
2. Run the generator from the root directory:
   ```bash
   python src/stacking/stack_scaffold.py