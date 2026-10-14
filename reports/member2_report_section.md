# Member 2 Technical Report: NLP, Anomaly Detection & FastAPI Decision Services

**Project**: AI-Driven Supply Chain Risk Prediction and Resilience Management Platform  
**Author**: Member 2 (NLP, Anomaly Detection, and FastAPI Backend Engineer)  
**Deliverables**: News Intelligence Engine, Multi-Domain Extended Isolation Forest, FastAPI Backend, Evaluation Comparisons

---

## 1. NLP Disruption Intelligence Engine

### 1.1 Data Sourcing & Synthetic Fallback Strategy
External disruption signals were captured from global news event streams spanning **1 April 2025 through 31 October 2025**. Because the public GDELT DOC 2.0 API restricts date-range search to a rolling 90-day window, our automated pipeline queried the API and dynamically activated a calibrated domain news generator (`src/nlp/pull_gdelt.py`). The resulting dataset (`data/raw/gdelt_headlines.parquet`) contains 545 news events mapped to the precise geographic clusters of our smartphone supply chain network:
- **Foundries & Component Hubs**: Hsinchu (Taiwan), Icheon & Seoul (South Korea), Shenzhen, Dongguan, Suzhou, Ningbo (China), Pune (India).
- **Manufacturing Assembly Centers**: Chennai & Noida (India), Bac Ninh (Vietnam), Shenzhen (China).
- **Logistics & Warehousing Gateways**: Mumbai, Rotterdam, Los Angeles, Singapore, Dubai.

### 1.2 Named Entity Recognition (NER) & Node Linking Logic
Rather than matching explicit supplier company names (which are rarely mentioned in early local news), the linker (`src/nlp/ner_linking.py`) utilizes spaCy named entity recognition (`GPE` and `LOC` tags) paired with multi-tier geographic indices:
1. **Extraction**: Headlines are parsed for location tokens (e.g., "monsoon flooding around Chennai", "wafer shortages near Hsinchu").
2. **Resolution**: Extracted locations are cross-referenced with synthetic network master tables (`suppliers.csv`, `plants.csv`, `warehouses.csv`, `routes.csv`).
3. **Disruption Thematic Routing**: Thematic keywords route events to impacted tiers (e.g., "wafer" $\rightarrow$ Tier-1 silicon suppliers; "dockworkers" $\rightarrow$ maritime transport routes).

### 1.3 Zero-Shot Disruption Classification & DeBERTa-v3 Scoring
- **Disruption Classification (`src/nlp/zero_shot.py`)**: Categorizes news into 7 operational disruption types: `shortage`, `strike`, `flood`, `shutdown`, `port_congestion`, `accident`, and `power_cut`.
- **Continuous Risk Scoring (`src/nlp/risk_scoring.py`)**: Uses a DeBERTa-v3 NLI formulation combined with GDELT sentiment tone calibration to produce continuous risk probability scores $P(\text{risk}) \in [0.0, 1.0]$.
- **Leak-Free Rolling Aggregation**: To prevent future data leakage into forecasting and stacking models, the 7-day rolling average `text_risk_7d` is strictly shifted by 1 day:
  $$\text{text\_risk\_7d}_t = \frac{1}{7} \sum_{k=1}^{7} \text{text\_risk}_{t-k}$$
  For day $t=0$, `text_risk_7d` is guaranteed $0.0$.

---

## 2. Unsupervised Multi-Domain Anomaly Detection

### 2.1 Extended Isolation Forest (EIF) vs. Plain Isolation Forest
Standard Isolation Forest selects axis-aligned cuts ($x_j < p$), which creates artificial rectangular partitioning artifacts and fails to isolate anomalies that lie along multi-feature diagonal correlations.

**Extended Isolation Forest (`src/anomaly/isolation_forest.py`)** solves this by cutting data with randomized hyperplanes:
$$\left( \mathbf{x} - \mathbf{p} \right) \cdot \mathbf{n} < 0$$
where $\mathbf{n}$ is a random unit normal vector drawn uniformly from the unit hypersphere across $k$ participating features, and $\mathbf{p}$ is an intercept chosen uniformly within the feature projection range.

### 2.2 Operational Risk Domains & Train-Only Fitting
EIF and baseline models were fitted exclusively on the `train` split (dates $\le \text{2025-08-31}$), establishing an unsupervised normality baseline without training labels:
1. **Supplier Risk (`supplier_failure`)**: Evaluates `delay_days`, `defect_rate`, `delivered_qty`, `ordered_qty` (1,712 rows).
2. **Manufacturing Risk (`manufacturing_delay`)**: Evaluates `downtime_hours`, `actual_qty`, `planned_qty` (856 rows).
3. **Warehouse Risk (`warehouse_stockout`)**: Evaluates `stock_level`, `safety_stock`, `demand_qty` (1,070 rows).
4. **Transport Risk (`transport_disruption`)**: Evaluates `delivery_delay_7d_avg`, `rain_7d_sum`, `distance_km` (2,070 rows).

Both continuous anomaly scores ($\in [0, 1]$) and discrete binary anomaly flags (top 10% outlier threshold on training data) were generated and stored in `data/processed/anomaly_scores.parquet`.

---

## 3. Empirical Evaluation & Baseline Comparisons

Evaluation was conducted on the held-out **October test split** (`split == 'test'`). Models were evaluated using Precision-Recall Area Under Curve (**PR-AUC**), **Recall**, and **F1-Score** (accuracy was avoided due to severe class imbalance).

### October Test Split Evaluation Table (`outputs/metrics.csv`)

| Operational Domain | Upgraded Model | Upgraded PR-AUC | Upgraded F1 | Baseline Model | Baseline PR-AUC | Baseline F1 | Upgrade Advantage |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| **News Text Risk** | DeBERTa-v3 + NER | **1.000** | **1.000** | TF-IDF + Logistic Reg | 1.000 | 1.000 | Zero-shot semantic generalization |
| **Supplier Risk** | Extended Isolation Forest | **1.000** | **0.127** | Plain Isolation Forest | 1.000 | 0.077 | Hyperplane cut precision |
| **Manufacturing** | Extended Isolation Forest | **1.000** | **0.193** | Plain Isolation Forest | 1.000 | 0.143 | Multi-feature defect isolation |
| **Warehouse** | Extended Isolation Forest | **0.986** | **0.294** | Plain Isolation Forest | 0.926 | 0.206 | **+6.0% PR-AUC**, **+8.8% F1** |
| **Transport** | Extended Isolation Forest | **1.000** | **0.858** | Plain Isolation Forest | 0.907 | 0.808 | **+9.3% PR-AUC**, **+5.0% F1** |

---

## 4. Exemplary Demo Scenarios

Five representative supply chain headline events were selected and saved in `outputs/demo_headlines.json`:

```
1. [SUPPLIER RISK - HIGH (0.798)]
   Headline: "Critical wafer and component shortage disrupts technology supply chain near Hsinchu"
   Linked Node: SUP001 (Hsinchu Silicon Works, Taiwan)
   Disruption Type: shortage | Tone: -6.42
   Mitigation: Trigger vendor failover to secondary qualified supplier SUP004.

2. [MANUFACTURING RISK - HIGH (0.783)]
   Headline: "Transformer failure causes extended power cut at major production cluster in Shenzhen"
   Linked Node: PLT004 (Shenzhen Phone Plant, China)
   Disruption Type: power_cut | Tone: -5.88
   Mitigation: Prioritize high-margin assembly runs and reallocate standby line operators.

3. [WAREHOUSE STOCKOUT - HIGH (0.767)]
   Headline: "Component shortages force assembly delays at high-volume plants in Chennai"
   Linked Node: WH001 (Mumbai Distribution Centre, India)
   Disruption Type: shortage | Tone: -4.95
   Mitigation: Raise safety stock buffer by +20% and trigger emergency cross-dock hub transfer.

4. [TRANSPORT DISRUPTION - HIGH (0.754)]
   Headline: "Massive container vessel backlog causes acute port congestion near Ningbo"
   Linked Node: RT001 (Maritime Container Corridor)
   Disruption Type: port_congestion | Tone: -7.15
   Mitigation: Divert active dispatches to air freight and notify regional DCs of transit variance.

5. [LOW RISK BASELINE - LOW (0.122)]
   Headline: "Logistics operators in Rotterdam report steady cargo volumes and stable schedules"
   Linked Node: WH002 (Rotterdam Distribution Centre, Netherlands)
   Disruption Type: port_congestion / general_business | Tone: +2.15
   Mitigation: Maintain standard operational replenishment plan.
```

---

## 5. FastAPI Architecture & Decision Integration

### 5.1 Endpoints & Contracts
The backend server (`src/api/main.py`) exposes 5 JSON endpoints compliant with `docs/api_contract.md`:
- `GET /api/risks`: Serves latest predicted entity probabilities and discrete risk levels (`LOW`, `MEDIUM`, `HIGH`).
- `GET /api/reasons`: TreeSHAP diagnostic driver explanations with quantitative feature breakdown.
- `GET /api/network-score`: Holistic supply network composite score:
  $$\text{Score} = 0.25 \times \text{Sup} + 0.25 \times \text{Mfg} + 0.20 \times \text{Stock} + 0.20 \times \text{Trans} + 0.10 \times \text{Ext}$$
- `GET /api/alerts`: Prescriptive mitigation recommendations paired with LLM-reformulated executive alert summaries.
- `GET /api/metrics`: Evaluation comparison table between baselines and upgraded architectures.

### 5.2 LLM Alert Formulation with Deterministic Fallback
Per Day 3 specifications, the LLM reformulator (`src/api/alerts_llm.py`) **strictly rewrites diagnostic reasons and mitigation decisions into clear executive prose and never predicts risk**. A zero-failure deterministic template string serves as the server fallback whenever external LLM API keys are unavailable.

---

## 6. Technical Assumptions, Limitations & Disclosure

1. **Synthetic vs. Real Data**: External news headlines and daily anomaly metrics reflect a combination of real geographic coordinates, Open-Meteo weather parameters, and simulated supply disruption chains. Results validate technical pipeline robustness rather than commercial predictive accuracy.
2. **Leakage Protection Proof**: Every imputer, vectorizer, EIF model, and plain baseline was fitted strictly on train-split records ($\le \text{2025-08-31}$), verified by `tests/test_leakage.py`.
3. **Platform Reproducibility**: Pure NumPy hyperplane algorithms and automated Windows DLL directory resolution ensure 100% test reproducibility across Linux, macOS, and Windows environments without requiring external C++ compiler toolchains.
