"""Compute Cohen's kappa for human labels vs judge labels."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from sklearn.metrics import cohen_kappa_score

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def normalize(value: str) -> str:
    value = (value or "").strip().lower()
    if value in {"a", "answer_a"}:
        return "A"
    if value in {"b", "answer_b"}:
        return "B"
    return "tie"


def interpretation(kappa: float) -> str:
    if kappa < 0:
        return "Worse than chance"
    if kappa < 0.2:
        return "Slight agreement"
    if kappa < 0.4:
        return "Fair agreement"
    if kappa < 0.6:
        return "Moderate agreement"
    if kappa < 0.8:
        return "Substantial agreement"
    return "Almost perfect agreement"


def main() -> None:
    with open(ROOT / "phase-b" / "human_labels.csv", encoding="utf-8") as f:
        human_rows = [r for r in csv.DictReader(f) if r.get("human_winner")]
    with open(ROOT / "phase-b" / "pairwise_results.csv", encoding="utf-8") as f:
        judge_rows = list(csv.DictReader(f))
    if not human_rows:
        raise SystemExit("Fill phase-b/human_labels.csv before running kappa analysis.")

    judge_by_id = {str(i): normalize(r["winner_after_swap"]) for i, r in enumerate(judge_rows, start=1)}
    human = [normalize(r["human_winner"]) for r in human_rows]
    judge = [judge_by_id[r["question_id"]] for r in human_rows]
    kappa = cohen_kappa_score(human, judge)
    print(f"Cohen's kappa: {kappa:.3f}")
    print(f"Interpretation: {interpretation(kappa)}")
    if kappa < 0.6:
        print("Root cause note: inspect label normalization, vague ties, and rubric mismatch.")


if __name__ == "__main__":
    main()
