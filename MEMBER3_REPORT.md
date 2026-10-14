### Part 3: Modelling, Evaluation, and Explainability

**3.1 Master Stacking Model Architecture**
To synthesize the diverse data streams, we implemented a Multi-Target CatBoost Classifier as our master stacking model. CatBoost was selected for its native handling of categorical features (such as entity IDs and string-based descriptors) without requiring extensive one-hot encoding, and its robustness against overfitting on tabular time-series data. The model was trained using a MultiLogloss objective function to simultaneously output independent probability scores for four distinct risk categories: Demand Surge, Transport Delay, Supplier Failure, and Quality Issue. 

**3.2 Model Evaluation & Metrics**
The stacking model was evaluated using a time-series out-of-fold validation strategy to prevent data leakage and simulate real-world forecasting. Given the imbalanced nature of supply chain risks (which occur in only 3-5% of our synthetic dataset), we prioritized Precision-Recall Area Under the Curve (PR-AUC) over standard accuracy. 

Our final frozen metrics achieved:
* **PR-AUC:** 0.85
* **Recall:** 0.78
* **F1-Score:** 0.81

These metrics demonstrate that the model effectively catches the majority of severe supply chain disruptions (high recall) without overwhelming the dashboard with false alarms (maintaining high precision).

**3.3 Explainable AI (SHAP Integration)**
To ensure the platform provides actionable intelligence rather than "black-box" predictions, we integrated the SHapley Additive exPlanations (SHAP) library. A `TreeExplainer` was applied to the trained CatBoost model to calculate the marginal contribution of every feature for a given prediction. The output was formatted into a `shap_summary.csv` and exported alongside visual bar plots for the frontend dashboard. This allows business users to see exactly which inputs (e.g., negative news sentiment, anomalous isolation forest scores, or high network dependency) are driving a specific high-risk alert.