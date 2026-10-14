"""Zero-Shot Disruption Classifier for Supply Chain News.

Classifies news headlines into standard disruption categories:
  - shortage
  - strike
  - flood
  - shutdown
  - port_congestion
  - accident
  - power_cut

Supports Hugging Face zero-shot classification pipeline with high-precision
semantic keyword matching fallback for fast, offline, and deterministic execution.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Union

_dll_cookie = None
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    torch_lib = os.path.join(sys.prefix, "Lib", "site-packages", "torch", "lib")
    if os.path.exists(torch_lib):
        try:
            _dll_cookie = os.add_dll_directory(torch_lib)
        except Exception:
            pass

try:
    import torch
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]

CANDIDATE_LABELS = [
    "shortage",
    "strike",
    "flood",
    "shutdown",
    "port_congestion",
    "accident",
    "power_cut",
]

KEYWORD_MAP = {
    "shortage": ["shortage", "scarcity", "depleted", "wafer", "lithium", "deficit", "rationing", "insufficient"],
    "strike": ["strike", "walkout", "protest", "union", "labour dispute", "picket", "stoppage", "work-to-rule"],
    "flood": ["flood", "monsoon", "typhoon", "submerged", "inundation", "heavy rain", "overflow", "storm surge"],
    "shutdown": ["shutdown", "closed", "maintenance", "regulatory order", "halted", "suspended", "lockout"],
    "port_congestion": ["port", "congestion", "berth", "container", "backlog", "vessel", "customs bottleneck", "dock"],
    "accident": ["accident", "fire", "explosion", "collision", "derailment", "spill", "hazard", "structural collapse"],
    "power_cut": ["power cut", "blackout", "grid outage", "power outage", "load shedding", "electricity failure", "transformer"],
}


class DisruptionZeroShotClassifier:
    """Zero-shot disruption classifier with transformer pipeline and semantic fallback."""

    def __init__(self, model_name: str = "typeform/distilbert-base-uncased-mnli", use_transformers: bool = False):
        self.candidate_labels = CANDIDATE_LABELS
        self.pipeline = None
        if use_transformers:
            try:
                from transformers import pipeline
                self.pipeline = pipeline("zero-shot-classification", model=model_name)
            except Exception:
                self.pipeline = None

    def classify_rule_based(self, text: str) -> Dict[str, Union[str, float]]:
        """Fast, robust deterministic keyword-frequency zero-shot matching."""
        text_lower = text.lower()
        scores = {}
        for label, keywords in KEYWORD_MAP.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            scores[label] = matches

        best_label = max(scores, key=scores.get)
        if scores[best_label] == 0:
            best_label = "general_business"
            confidence = 0.5
        else:
            total = sum(scores.values())
            confidence = round(scores[best_label] / total, 3)

        return {
            "disruption_type": best_label,
            "confidence": confidence,
            "all_scores": scores,
        }

    def predict(self, text: str) -> str:
        """Classify a single headline and return the most likely disruption type."""
        if self.pipeline:
            try:
                result = self.pipeline(text, candidate_labels=self.candidate_labels)
                return result["labels"][0]
            except Exception:
                pass
        return self.classify_rule_based(text)["disruption_type"]

    def predict_batch(self, texts: List[str]) -> List[str]:
        """Classify a list of headlines."""
        return [self.predict(t) for t in texts]


if __name__ == "__main__":
    classifier = DisruptionZeroShotClassifier()
    test_cases = [
        "Dockworkers announce indefinite strike impacting container terminals near Ningbo",
        "Transformer failure causes extended power cut at major production cluster in Shenzhen",
        "Critical wafer and component shortage disrupts technology supply chain near Hsinchu",
        "Typhoon-induced flash floods submerge industrial zones near Chennai",
    ]
    for tc in test_cases:
        res = classifier.predict(tc)
        print(f"'{tc[:60]}...' -> {res}")
