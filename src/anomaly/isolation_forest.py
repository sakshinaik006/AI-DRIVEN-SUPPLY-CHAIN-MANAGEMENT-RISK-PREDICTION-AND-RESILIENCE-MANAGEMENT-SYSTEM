"""Extended Isolation Forest (EIF) and Plain Isolation Forest Anomaly Detectors.

Provides a unified interface for unsupervised anomaly scoring on supply chain metrics:
  - Supplier: lead time, defects, delivery delays
  - Manufacturing: downtime, output shortfall, defect rate
  - Warehouse: inventory movement, stock cover
  - Transport: route delivery delays, transit times

Strictly enforces leak-free training: fits on the train split only,
evaluates across train, val, and test splits.
"""
from pathlib import Path
from typing import Tuple, Optional, List, Union
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[2]


def c_factor(n: int) -> float:
    """Average path length of unsuccessful search in BST for sample size n."""
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.0
    euler_gamma = 0.5772156649
    return 2.0 * (np.log(n - 1.0) + euler_gamma) - (2.0 * (n - 1.0) / n)


class ExtendedIsolationTreeNode:
    """Node in an Extended Isolation Tree with random hyperplane splits."""

    def __init__(self, left=None, right=None, normal_vector=None, split_point=None, size: int = 0):
        self.left = left
        self.right = right
        self.normal_vector = normal_vector
        self.split_point = split_point
        self.size = size
        self.is_leaf = left is None and right is None


class PureExtendedIsolationTree:
    """An individual Extended Isolation Tree using hyperplane cuts."""

    def __init__(self, max_depth: int, extension_level: Optional[int] = None):
        self.max_depth = max_depth
        self.extension_level = extension_level
        self.root = None

    def fit(self, X: np.ndarray, current_depth: int = 0, rng: Optional[np.random.Generator] = None):
        if rng is None:
            rng = np.random.default_rng()

        n_samples, n_features = X.shape

        if current_depth >= self.max_depth or n_samples <= 1:
            return ExtendedIsolationTreeNode(size=n_samples)

        # Extension level: number of random dimensions participating in the hyperplane
        ext = self.extension_level if self.extension_level is not None else n_features
        ext = min(ext, n_features)

        chosen_dims = rng.choice(n_features, size=ext, replace=False)
        normal = np.zeros(n_features)
        normal[chosen_dims] = rng.normal(0, 1, size=ext)
        norm = np.linalg.norm(normal)
        if norm > 0:
            normal = normal / norm

        # Project data along the normal vector
        proj = X @ normal
        min_proj, max_proj = proj.min(), proj.max()

        if np.isclose(min_proj, max_proj):
            return ExtendedIsolationTreeNode(size=n_samples)

        # Select a random split point along the projection range
        split_val = rng.uniform(min_proj, max_proj)
        left_mask = proj < split_val

        if left_mask.all() or (~left_mask).all():
            return ExtendedIsolationTreeNode(size=n_samples)

        left_node = self.fit(X[left_mask], current_depth + 1, rng=rng)
        right_node = self.fit(X[~left_mask], current_depth + 1, rng=rng)

        return ExtendedIsolationTreeNode(
            left=left_node,
            right=right_node,
            normal_vector=normal,
            split_point=split_val,
            size=n_samples
        )

    def path_length(self, x: np.ndarray, node: ExtendedIsolationTreeNode, current_depth: int = 0) -> float:
        """Traverse tree to calculate path length for an observation x."""
        if node.is_leaf or node.normal_vector is None:
            return current_depth + c_factor(node.size)

        proj = np.dot(x, node.normal_vector)
        if proj < node.split_point:
            return self.path_length(x, node.left, current_depth + 1)
        else:
            return self.path_length(x, node.right, current_depth + 1)


class ExtendedIsolationForest:
    """Extended Isolation Forest ensemble using randomized hyperplane cuts."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_samples: Union[int, float] = 256,
        extension_level: Optional[int] = None,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.extension_level = extension_level
        self.random_state = random_state
        self.trees: List[ExtendedIsolationTreeNode] = []
        self.tree_models: List[PureExtendedIsolationTree] = []
        self.threshold = 0.5
        self.subsample_size = 256
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """Fit Extended Isolation Forest strictly on training data."""
        rng = np.random.default_rng(self.random_state)
        n_samples = X.shape[0]

        if isinstance(self.max_samples, float):
            self.subsample_size = int(self.max_samples * n_samples)
        else:
            self.subsample_size = min(self.max_samples, n_samples)

        max_depth = int(np.ceil(np.log2(max(self.subsample_size, 2))))

        self.tree_models = []
        for _ in range(self.n_estimators):
            sample_indices = rng.choice(n_samples, size=self.subsample_size, replace=False)
            X_sub = X[sample_indices]
            tree = PureExtendedIsolationTree(max_depth=max_depth, extension_level=self.extension_level)
            tree.root = tree.fit(X_sub, current_depth=0, rng=rng)
            self.tree_models.append(tree)

        self.is_fitted = True

        # Compute threshold on training samples (90th percentile)
        train_scores = self.score_samples(X)
        self.threshold = float(np.percentile(train_scores, 90))
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly score s in [0, 1] where higher = more anomalous."""
        if not self.is_fitted:
            raise ValueError("ExtendedIsolationForest must be fitted before scoring.")

        n_samples = X.shape[0]
        paths = np.zeros(n_samples)

        for tree in self.tree_models:
            for i in range(n_samples):
                paths[i] += tree.path_length(X[i], tree.root, current_depth=0)

        avg_path = paths / len(self.tree_models)
        c = c_factor(self.subsample_size)
        # Anomaly score s = 2^(-E[h] / c(n))
        scores = 2.0 ** (- (avg_path / c))
        return scores

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Return (anomaly_score, anomaly_flag)."""
        scores = self.score_samples(X)
        flags = (scores >= self.threshold).astype(int)
        return scores, flags


class PlainIsolationForestBaseline:
    """Standard Isolation Forest baseline from scikit-learn with matching interface."""

    def __init__(self, n_estimators: int = 100, max_samples: int = 256, random_state: int = 42):
        self.model = IsolationForest(
            n_estimators=n_estimators,
            max_samples=max_samples,
            random_state=random_state,
            contamination=0.10,
        )
        self.threshold = 0.5
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """Fit strictly on training data."""
        self.model.fit(X)
        # scikit-learn score_samples: opposite of anomaly score (lower means more anomalous)
        raw_train_scores = -self.model.score_samples(X)
        self.threshold = float(np.percentile(raw_train_scores, 90))
        self.is_fitted = True
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Normalized anomaly score where higher = more anomalous."""
        if not self.is_fitted:
            raise ValueError("Baseline model must be fitted before scoring.")
        # Negate so higher = more anomalous, shift and scale to [0, 1]
        raw_scores = -self.model.score_samples(X)
        # Sigmoid or min-max calibration
        scaled = 1.0 / (1.0 + np.exp(-5.0 * (raw_scores - 0.5)))
        return np.round(scaled, 3)

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Return (if_baseline_score, anomaly_flag)."""
        raw_scores = -self.model.score_samples(X)
        flags = (raw_scores >= self.threshold).astype(int)
        scaled_scores = self.score_samples(X)
        return scaled_scores, flags


def run_anomaly_pipeline(
    df: pd.DataFrame,
    feature_cols: List[str],
    risk_type: str,
) -> pd.DataFrame:
    """Fit EIF and baseline Isolation Forest strictly on train rows and score all rows."""
    df_out = df.copy()

    # Fill missing values with median of train split
    train_mask = df_out["split"] == "train"
    train_medians = df_out.loc[train_mask, feature_cols].median()
    df_out[feature_cols] = df_out[feature_cols].fillna(train_medians)

    X_train = df_out.loc[train_mask, feature_cols].values
    X_all = df_out[feature_cols].values

    # 1. Extended Isolation Forest
    eif = ExtendedIsolationForest(n_estimators=80, max_samples=min(256, len(X_train)), random_state=42)
    eif.fit(X_train)
    eif_scores, eif_flags = eif.predict(X_all)

    # 2. Plain Isolation Forest Baseline
    base_if = PlainIsolationForestBaseline(n_estimators=80, random_state=42)
    base_if.fit(X_train)
    base_scores, _ = base_if.predict(X_all)

    res = pd.DataFrame({
        "entity_id": df_out["entity_id"],
        "date": df_out["date"],
        "risk_type": risk_type,
        "anomaly_score": np.round(eif_scores, 3),
        "anomaly_flag": eif_flags,
        "if_baseline_score": base_scores,
    })
    return res


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    # Test on synthetic data
    X_dummy = rng.normal(0, 1, (300, 3))
    # Inject outliers
    X_dummy[0] = [5.0, 5.0, 5.0]

    eif = ExtendedIsolationForest(n_estimators=50, random_state=42)
    eif.fit(X_dummy)
    scores, flags = eif.predict(X_dummy)
    print(f"EIF Outlier sample score: {scores[0]:.3f}, flag: {flags[0]}")
    print(f"EIF Normal sample score: {scores[1]:.3f}, flag: {flags[1]}")

    base = PlainIsolationForestBaseline(n_estimators=50, random_state=42)
    base.fit(X_dummy)
    b_scores, b_flags = base.predict(X_dummy)
    print(f"Base IF Outlier sample score: {b_scores[0]:.3f}, flag: {b_flags[0]}")
    print(f"Base IF Normal sample score: {b_scores[1]:.3f}, flag: {b_flags[1]}")
