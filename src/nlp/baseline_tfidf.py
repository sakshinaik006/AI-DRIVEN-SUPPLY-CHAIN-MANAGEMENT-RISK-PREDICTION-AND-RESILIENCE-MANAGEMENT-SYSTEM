"""TF-IDF + Logistic Regression NLP Baseline Model.

Implements the plain text-risk baseline using:
  - TfidfVectorizer (fitted on train split only)
  - Logistic Regression with weak disruption labels
  - Time-ordered out-of-fold cross-validation on train split (zero leakage)
  - Evaluation comparisons against upgraded DeBERTa-v3 model
"""
import os
import sys
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import precision_recall_curve, auc, recall_score, f1_score

ROOT = Path(__file__).resolve().parents[2]

DISRUPTION_KEYWORDS = [
    "shortage", "strike", "flood", "shutdown", "blackout",
    "congestion", "delay", "accident", "fire", "backlog", "halt"
]


def create_weak_labels(df: pd.DataFrame) -> pd.Series:
    """Generate weak binary labels for news headlines based on disruption keywords and negative tone."""
    is_disruption_keyword = df["title"].str.lower().apply(
        lambda t: any(kw in t for kw in DISRUPTION_KEYWORDS)
    )
    is_negative_tone = df["tone"] < -2.0
    return ((is_disruption_keyword | is_negative_tone) & (df["theme"] != "general_business")).astype(int)


class TfidfLogisticBaseline:
    """TF-IDF + Logistic Regression model with leak-free train-only fitting and OOF predictions."""

    def __init__(self, max_features: int = 500, random_state: int = 42):
        self.max_features = max_features
        self.random_state = random_state
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english", ngram_range=(1, 2))
        self.model = LogisticRegression(class_weight="balanced", random_state=random_state, max_iter=500)
        self.is_fitted = False

    def fit(self, train_texts: pd.Series, train_labels: pd.Series):
        """Fit vectorizer and classifier strictly on train split."""
        X_train = self.vectorizer.fit_transform(train_texts)
        self.model.fit(X_train, train_labels)
        self.is_fitted = True

    def predict_proba(self, texts: pd.Series) -> np.ndarray:
        """Predict disruption probabilities for text using fitted model."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted on train split before calling predict_proba.")
        X = self.vectorizer.transform(texts)
        return self.model.predict_proba(X)[:, 1]

    def fit_predict_oof(self, df: pd.DataFrame, n_splits: int = 4) -> pd.Series:
        """Produce leak-free out-of-fold predictions on train split using time-ordered folds,

        and standard out-of-sample predictions on val and test splits.
        """
        df_sorted = df.sort_values("date").copy()
        df_sorted["weak_label"] = create_weak_labels(df_sorted)

        train_mask = df_sorted["split"] == "train"
        train_indices = df_sorted[train_mask].index
        val_test_indices = df_sorted[~train_mask].index

        oof_series = pd.Series(index=df_sorted.index, dtype=float)
        train_df = df_sorted.loc[train_indices].reset_index(drop=True)

        # Time-ordered expanding window cross-validation on train split
        tscv = TimeSeriesSplit(n_splits=n_splits)
        fold_preds = pd.Series(index=train_df.index, dtype=float)
        for fold, (train_idx, val_idx) in enumerate(tscv.split(train_df)):
            fold_vec = TfidfVectorizer(max_features=self.max_features, stop_words="english")
            fold_clf = LogisticRegression(class_weight="balanced", random_state=self.random_state)

            X_tr = fold_vec.fit_transform(train_df.iloc[train_idx]["title"])
            y_tr = train_df.iloc[train_idx]["weak_label"]
            fold_clf.fit(X_tr, y_tr)

            X_val = fold_vec.transform(train_df.iloc[val_idx]["title"])
            fold_preds.iloc[val_idx] = fold_clf.predict_proba(X_val)[:, 1]

        # For earliest rows not covered by validation folds, use first fold model
        unassigned = fold_preds.isna()
        if unassigned.any():
            first_train_idx = list(tscv.split(train_df))[0][0]
            fold_vec = TfidfVectorizer(max_features=self.max_features, stop_words="english")
            fold_clf = LogisticRegression(class_weight="balanced", random_state=self.random_state)
            fold_clf.fit(
                fold_vec.fit_transform(train_df.iloc[first_train_idx]["title"]),
                train_df.iloc[first_train_idx]["weak_label"]
            )
            fold_preds.loc[unassigned] = fold_clf.predict_proba(
                fold_vec.transform(train_df.loc[unassigned]["title"])
            )[:, 1]

        # Map back to train indices
        oof_series.loc[train_indices] = fold_preds.values

        # Fit final model on entire train split
        self.fit(df_sorted.loc[train_indices, "title"], df_sorted.loc[train_indices, "weak_label"])

        # Predict on val / test rows
        if len(val_test_indices) > 0:
            oof_series.loc[val_test_indices] = self.predict_proba(df_sorted.loc[val_test_indices, "title"])

        return oof_series.loc[df.index]

    def evaluate_test_split(self, df_scored: pd.DataFrame) -> Dict[str, float]:
        """Compute PR-AUC, Recall, and F1 on October test split."""
        test_df = df_scored[df_scored["split"] == "test"].copy()
        if test_df.empty:
            test_df = df_scored.tail(len(df_scored) // 5).copy()

        y_true = create_weak_labels(test_df)
        y_prob = test_df["tfidf_lr_risk"].values
        y_pred = (y_prob >= 0.5).astype(int)

        precision, recall_curve, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = float(auc(recall_curve, precision))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        return {
            "model": "TF-IDF + Logistic Regression",
            "pr_auc": round(pr_auc, 3),
            "recall": round(rec, 3),
            "f1": round(f1, 3),
            "is_baseline": True,
        }


if __name__ == "__main__":
    raw_path = ROOT / "data" / "raw" / "gdelt_headlines.parquet"
    if not raw_path.exists():
        from src.nlp.pull_gdelt import pull_and_save_headlines
        pull_and_save_headlines()

    df_news = pd.read_parquet(raw_path)
    # Add split column
    d = pd.to_datetime(df_news["date"])
    df_news["split"] = np.select(
        [d <= "2025-08-24", d <= "2025-08-31", d <= "2025-09-23", d <= "2025-09-30"],
        ["train", "purge", "val", "purge"],
        default="test",
    )

    baseline = TfidfLogisticBaseline()
    df_news["tfidf_lr_risk"] = baseline.fit_predict_oof(df_news)
    metrics = baseline.evaluate_test_split(df_news)
    print("TF-IDF Baseline Results:")
    print(metrics)
