# Stacking Architecture & TreeSHAP Explainability

This module coordinates multi-tier CatBoost risk modeling, chronological out-of-fold cross-validation, and TreeSHAP root-cause feature attribution.

## Architecture & Modules

- **`train_catboost.py`**: Trains independent CatBoost classifiers across all 4 supply chain operational tiers (Suppliers, Manufacturing, Warehouses, Logistics Corridors). Applies moderated square-root class weighting $\min(\sqrt{N_{neg}/N_{pos}}, 3.0)$ with $L_2$ leaf regularization ($\lambda = 3.0$) to prevent single-tree early-stopping collapse on imbalanced disruption targets.
- **`explain_model.py`**: Computes exact Shapley feature attributions via `shap.TreeExplainer`, exports `outputs/shap_values.parquet`, and parses top-3 operational disruption drivers into `outputs/reasons.csv`.
- **`generate_demos.py`**: Dynamically generates verified executive demonstration scenarios (`outputs/demos/demo_cases.json`) and local waterfall visualizations directly from genuine model predictions.
- **`oof.py`**: Time-ordered expanding-window cross-validation generator enforcing strict 7-day purge gaps between folds.

## Running the Pipeline

```bash
# Train multi-tier CatBoost models
python -m src.stacking.train_catboost

# Generate TreeSHAP values and diagnostic root-cause reasons
python -m src.stacking.explain_model

# Produce executive demo cases and waterfall charts
python -m src.stacking.generate_demos
```
