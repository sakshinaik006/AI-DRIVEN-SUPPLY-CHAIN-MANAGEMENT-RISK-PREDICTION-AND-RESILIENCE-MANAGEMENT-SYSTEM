"""LLM Alert Message Reformulator with Template Fallback.

Day 3 Requirement:
  Turns TreeSHAP reasons and predicted risk levels into clear, executive-ready
  alert summaries.
  Rule: The LLM NEVER predicts anything or invents facts; it purely reformulates
  the provided diagnostic drivers and mitigation actions into readable prose.
  Maintains a 100% reliable deterministic template fallback when an LLM API key
  is not configured or when network requests time out.
"""
import os
from pathlib import Path
from typing import List, Optional
import requests
ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    env_file = ROOT / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def generate_template_alert_summary(
    entity_id: str,
    risk_level: str,
    probability: float,
    top_reasons: List[str],
    recommended_actions: List[str],
) -> str:
    """Deterministic, robust fallback alert message generator."""
    reasons_str = "; ".join(top_reasons[:2]) if top_reasons else "elevated lead time variability"
    primary_action = recommended_actions[0] if recommended_actions else "maintain continuous operational monitoring"

    summary = (
        f"Alert for {entity_id}: 7-day predicted disruption risk is {risk_level} ({probability:.1%}). "
        f"Key operational drivers identified by TreeSHAP include {reasons_str}. "
        f"Recommended mitigation: {primary_action}."
    )
    return summary


def format_alert_summary_llm(
    entity_id: str,
    risk_level: str,
    probability: float,
    top_reasons: List[str],
    recommended_actions: List[str],
    timeout_secs: float = 3.0,
) -> str:
    """Reformulate alert message using LLM API if available, falling back to template."""
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("LLM_API_KEY")
    )

    if not api_key:
        return generate_template_alert_summary(
            entity_id, risk_level, probability, top_reasons, recommended_actions
        )

    # Prompt enforcing the strict rule: reformulate only, never predict
    prompt = (
        f"You are an AI supply chain risk analyst. Rewrite the following diagnostic facts into a concise 2-sentence executive alert summary.\n"
        f"Do NOT predict new probabilities, invent causes, or alter facts.\n"
        f"Entity: {entity_id}\n"
        f"Risk Level: {risk_level} ({probability:.1%})\n"
        f"Primary TreeSHAP Drivers: {', '.join(top_reasons)}\n"
        f"Recommended Mitigation Actions: {', '.join(recommended_actions)}\n"
        f"Summary:"
    )

    # Try OpenAI-compatible endpoint if OPENAI_API_KEY exists
    if os.getenv("OPENAI_API_KEY"):
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 120,
                "temperature": 0.2,
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=timeout_secs)
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"].strip()
                if text:
                    return text
        except Exception:
            pass

    # Try Gemini endpoint if GEMINI_API_KEY exists
    if os.getenv("GEMINI_API_KEY"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=payload, timeout=timeout_secs)
            if resp.status_code == 200:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text:
                    return text
        except Exception:
            pass

    # Fallback to deterministic template
    return generate_template_alert_summary(
        entity_id, risk_level, probability, top_reasons, recommended_actions
    )


if __name__ == "__main__":
    msg = format_alert_summary_llm(
        entity_id="SUP001",
        risk_level="HIGH",
        probability=0.824,
        top_reasons=["Supplier delivery delay 7-day average exceeded 4.5 days", "Localized severe typhoon flood advisory"],
        recommended_actions=["Switch volume allocation to backup vendor SUP004", "Prioritize flagship order fulfillments"],
    )
    print("Alert Summary Output:")
    print(msg)
