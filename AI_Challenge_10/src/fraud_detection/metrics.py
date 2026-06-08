from __future__ import annotations

import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Sequence

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


def build_analysis_report(
    claims: Sequence[Claim],
    results: Sequence[ScoreResult],
    *,
    top_n: int = 20,
    sample_n: int = 10,
) -> dict:
    labels = {claim.claim_id: claim.fraud_label for claim in claims}
    patterns = {claim.claim_id: claim.fraud_patterns for claim in claims}
    result_by_id = {result.claim_id: result for result in results}

    rule_summary: dict[str, dict[str, int | float]] = defaultdict(
        lambda: {"hits": 0, "true_hits": 0, "false_hits": 0, "precision": 0.0}
    )
    for result in results:
        actual = labels[result.claim_id]
        for flag in result.flags:
            summary = rule_summary[flag.rule]
            summary["hits"] += 1
            if actual:
                summary["true_hits"] += 1
            else:
                summary["false_hits"] += 1

    for summary in rule_summary.values():
        summary["precision"] = round(
            summary["true_hits"] / max(summary["hits"], 1),
            4,
        )

    risk_bands = {
        "0": {"claims": 0, "fraud": 0},
        "1-24": {"claims": 0, "fraud": 0},
        "25-49": {"claims": 0, "fraud": 0},
        "50-74": {"claims": 0, "fraud": 0},
        "75-100": {"claims": 0, "fraud": 0},
    }
    for result in results:
        band = risk_band(result.risk_score)
        risk_bands[band]["claims"] += 1
        risk_bands[band]["fraud"] += int(labels[result.claim_id])

    pattern_coverage = {}
    all_patterns = sorted({pattern for claim in claims for pattern in claim.fraud_patterns})
    for pattern in all_patterns:
        embedded_claims = [claim for claim in claims if pattern in claim.fraud_patterns]
        detected_any = 0
        detected_matching_rule = 0
        for claim in embedded_claims:
            result = result_by_id[claim.claim_id]
            triggered_rules = {flag.rule for flag in result.flags}
            if triggered_rules:
                detected_any += 1
            if pattern in triggered_rules:
                detected_matching_rule += 1

        pattern_coverage[pattern] = {
            "embedded": len(embedded_claims),
            "detected_any_rule": detected_any,
            "detected_matching_rule": detected_matching_rule,
            "matching_rule_recall": round(detected_matching_rule / len(embedded_claims), 4),
        }

    false_positives = [
        compact_result(result, patterns[result.claim_id])
        for result in results
        if result.risk_score > 0 and not labels[result.claim_id]
    ][:sample_n]
    false_negatives = [
        compact_result(result, patterns[result.claim_id])
        for result in results
        if result.risk_score == 0 and labels[result.claim_id]
    ][:sample_n]

    return {
        "top_suspicious_claims": [
            compact_result(result, patterns[result.claim_id])
            for result in results[:top_n]
        ],
        "risk_bands": risk_bands,
        "rule_summary": dict(sorted(rule_summary.items())),
        "fraud_pattern_coverage": pattern_coverage,
        "false_positive_samples": false_positives,
        "false_negative_samples": false_negatives,
        "review_notes": [
            "Risk score > 0 is treated as the review threshold for metrics.",
            "False positives are acceptable when the evidence is actionable because the engine is designed as a triage tool, not an automatic denial system.",
            "False negatives are listed explicitly so reviewers can see remaining blind spots.",
        ],
    }


def risk_band(score: int) -> str:
    if score == 0:
        return "0"
    if score < 25:
        return "1-24"
    if score < 50:
        return "25-49"
    if score < 75:
        return "50-74"
    return "75-100"


def compact_result(result: ScoreResult, patterns: list[str]) -> dict:
    return {
        "claim_id": result.claim_id,
        "risk_score": result.risk_score,
        "fraud_label": result.fraud_label,
        "fraud_patterns": patterns,
        "rules": [flag.rule for flag in result.flags],
        "evidence": [flag.evidence for flag in result.flags],
    }


def analysis_markdown(report: dict) -> str:
    lines = [
        "# Fraud Detection Analysis Report",
        "",
        "## Top Suspicious Claims",
        "",
        "| Rank | Claim ID | Score | Label | Rules |",
        "|---:|---|---:|---|---|",
    ]
    for index, claim in enumerate(report["top_suspicious_claims"], start=1):
        lines.append(
            f"| {index} | {claim['claim_id']} | {claim['risk_score']} | "
            f"{'fraud' if claim['fraud_label'] else 'clean'} | {', '.join(claim['rules'])} |"
        )

    lines.extend(
        [
            "",
            "## Risk Band Distribution",
            "",
            "| Band | Claims | Labeled fraud | Fraud rate |",
            "|---|---:|---:|---:|",
        ]
    )
    for band, values in report["risk_bands"].items():
        fraud_rate = values["fraud"] / max(values["claims"], 1)
        lines.append(f"| {band} | {values['claims']} | {values['fraud']} | {fraud_rate:.2%} |")

    lines.extend(
        [
            "",
            "## Rule-Level Precision",
            "",
            "| Rule | Hits | True hits | False hits | Precision |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for rule, values in report["rule_summary"].items():
        lines.append(
            f"| {rule} | {values['hits']} | {values['true_hits']} | "
            f"{values['false_hits']} | {values['precision']:.2%} |"
        )

    lines.extend(
        [
            "",
            "## Fraud Pattern Coverage",
            "",
            "| Pattern | Embedded | Detected by any rule | Detected by matching rule | Matching recall |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for pattern, values in report["fraud_pattern_coverage"].items():
        lines.append(
            f"| {pattern} | {values['embedded']} | {values['detected_any_rule']} | "
            f"{values['detected_matching_rule']} | {values['matching_rule_recall']:.2%} |"
        )

    lines.extend(["", "## Review Notes", ""])
    lines.extend(f"- {note}" for note in report["review_notes"])
    lines.extend(["", "## False Positive Samples", ""])
    lines.extend(sample_lines(report["false_positive_samples"]))
    lines.extend(["", "## False Negative Samples", ""])
    lines.extend(sample_lines(report["false_negative_samples"]))
    return "\n".join(lines) + "\n"


def sample_lines(samples: list[dict]) -> list[str]:
    if not samples:
        return ["None."]

    lines = ["| Claim ID | Score | Patterns | Rules |", "|---|---:|---|---|"]
    for sample in samples:
        lines.append(
            f"| {sample['claim_id']} | {sample['risk_score']} | "
            f"{', '.join(sample['fraud_patterns']) or '-'} | {', '.join(sample['rules']) or '-'} |"
        )
    return lines
