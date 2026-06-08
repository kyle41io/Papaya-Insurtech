from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

from .models import Claim, ScoreResult


@dataclass
class Metrics:
    total_claims: int
    labeled_fraud: int
    predicted_fraud: int
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    false_positive_rate: float
    processing_seconds: float
    rule_hit_counts: dict[str, int]
    fraud_pattern_counts: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "total_claims": self.total_claims,
            "labeled_fraud": self.labeled_fraud,
            "predicted_fraud": self.predicted_fraud,
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "true_negatives": self.true_negatives,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "false_positive_rate": round(self.false_positive_rate, 4),
            "processing_seconds": round(self.processing_seconds, 4),
            "rule_hit_counts": self.rule_hit_counts,
            "fraud_pattern_counts": self.fraud_pattern_counts,
        }


def evaluate_metrics(
    claims: Sequence[Claim],
    results: Sequence[ScoreResult],
    *,
    processing_seconds: float,
) -> Metrics:
    labels = {claim.claim_id: claim.fraud_label for claim in claims}
    pattern_counts: Counter = Counter()
    for claim in claims:
        pattern_counts.update(claim.fraud_patterns)

    rule_counts: Counter = Counter()
    tp = fp = fn = tn = 0
    for result in results:
        predicted = result.risk_score > 0
        actual = labels[result.claim_id]
        rule_counts.update(flag.rule for flag in result.flags)

        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    false_positive_rate = fp / max(fp + tn, 1)

    return Metrics(
        total_claims=len(claims),
        labeled_fraud=sum(labels.values()),
        predicted_fraud=tp + fp,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        true_negatives=tn,
        precision=precision,
        recall=recall,
        false_positive_rate=false_positive_rate,
        processing_seconds=processing_seconds,
        rule_hit_counts=dict(sorted(rule_counts.items())),
        fraud_pattern_counts=dict(sorted(pattern_counts.items())),
    )


def timed(callable_):
    start = time.perf_counter()
    value = callable_()
    return value, time.perf_counter() - start


def markdown_report(metrics: Metrics) -> str:
    data = metrics.to_dict()
    lines = [
        "# Fraud Detection Metrics Report",
        "",
        "## Summary",
        "",
        f"- Total claims: {data['total_claims']:,}",
        f"- Labeled fraud claims: {data['labeled_fraud']:,}",
        f"- Predicted fraud claims: {data['predicted_fraud']:,}",
        f"- Precision: {data['precision']:.2%}",
        f"- Recall: {data['recall']:.2%}",
        f"- False positive rate: {data['false_positive_rate']:.2%}",
        f"- Processing time: {data['processing_seconds']:.4f}s",
        "",
        "## Confusion Matrix",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| True positives | {data['true_positives']} |",
        f"| False positives | {data['false_positives']} |",
        f"| False negatives | {data['false_negatives']} |",
        f"| True negatives | {data['true_negatives']} |",
        "",
        "## Rule Hit Counts",
        "",
        "| Rule | Hits |",
        "|---|---:|",
    ]

    lines.extend(f"| {rule} | {count} |" for rule, count in data["rule_hit_counts"].items())
    lines.extend(
        [
            "",
            "## Embedded Fraud Pattern Counts",
            "",
            "| Pattern | Count |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {pattern} | {count} |"
        for pattern, count in data["fraud_pattern_counts"].items()
    )
    lines.extend(
        [
            "",
            "## Severity Weight Rationale",
            "",
            "- Duplicate and phantom billing are weighted highest because they strongly indicate abuse or billing for services not rendered.",
            "- Upcoding, unbundling, and diagnosis mismatches are high-severity because they affect payable amount or clinical validity.",
            "- Rapid re-submission and weekend anomalies are medium severity because they are suspicious but may have legitimate explanations.",
            "- Amount clustering is lower severity because it is a weak signal unless combined with other evidence.",
        ]
    )
    return "\n".join(lines) + "\n"
