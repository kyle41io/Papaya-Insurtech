from __future__ import annotations

from collections import Counter, defaultdict
from typing import Sequence

from .models import Claim, ScoreResult


DEFAULT_THRESHOLDS = (1, 10, 15, 20, 25, 30, 40)


def build_investigation_report(
    claims: Sequence[Claim],
    results: Sequence[ScoreResult],
    *,
    queue_size: int = 30,
    thresholds: Sequence[int] = DEFAULT_THRESHOLDS,
) -> dict:
    claim_by_id = {claim.claim_id: claim for claim in claims}
    result_by_id = {result.claim_id: result for result in results}
    threshold_curve = [threshold_metrics(results, threshold) for threshold in thresholds]
    recommended = max(
        threshold_curve,
        key=lambda item: (item["f1_score"], -item["false_positive_rate"], -item["review_volume"]),
    )

    return {
        "recommended_threshold": recommended,
        "threshold_curve": threshold_curve,
        "review_queue": [
            review_queue_item(result, claim_by_id[result.claim_id])
            for result in results[:queue_size]
        ],
        "provider_profiles": provider_profiles(claims, result_by_id),
        "member_provider_hotspots": member_provider_hotspots(claims, result_by_id),
        "operational_notes": [
            "Use the recommended threshold as a review trigger, not an automatic denial rule.",
            "Start with provider profiles when multiple high-risk claims share the same provider.",
            "Use member-provider hotspots to find concentrated suspicious relationships.",
            "Escalate only after checking the evidence strings attached to each claim.",
        ],
    }


def threshold_metrics(results: Sequence[ScoreResult], threshold: int) -> dict:
    tp = fp = fn = tn = 0
    for result in results:
        predicted = result.risk_score >= threshold
        actual = result.fraud_label
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
    f1_score = 2 * precision * recall / max(precision + recall, 0.0001)

    return {
        "threshold": threshold,
        "review_volume": tp + fp,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "false_positive_rate": round(false_positive_rate, 4),
        "f1_score": round(f1_score, 4),
    }


def review_queue_item(result: ScoreResult, claim: Claim) -> dict:
    return {
        "claim_id": result.claim_id,
        "member_id": claim.member_id,
        "provider_id": claim.provider_id,
        "provider_name": claim.provider_name,
        "claim_date": claim.claim_date,
        "claim_type": claim.claim_type,
        "submitted_amount": round(claim.submitted_amount, 2),
        "risk_score": result.risk_score,
        "recommended_action": recommended_action(result.risk_score),
        "rules": [flag.rule for flag in result.flags],
        "evidence": [flag.evidence for flag in result.flags],
    }


def recommended_action(score: int) -> str:
    if score >= 30:
        return "Open special investigation case"
    if score >= 20:
        return "Request medical records before payment"
    if score >= 13:
        return "Route to manual claim review"
    if score > 0:
        return "Monitor provider and spot-check documentation"
    return "Auto-process"


def provider_profiles(
    claims: Sequence[Claim],
    result_by_id: dict[str, ScoreResult],
    *,
    limit: int = 10,
) -> list[dict]:
    grouped: dict[str, list[Claim]] = defaultdict(list)
    for claim in claims:
        grouped[claim.provider_id].append(claim)

    profiles = []
    for provider_id, provider_claims in grouped.items():
        provider_results = [result_by_id[claim.claim_id] for claim in provider_claims]
        flagged = [result for result in provider_results if result.risk_score > 0]
        rule_counter = Counter(
            flag.rule
            for result in flagged
            for flag in result.flags
        )
        total_amount = sum(claim.submitted_amount for claim in provider_claims)
        suspicious_amount = sum(
            claim.submitted_amount
            for claim in provider_claims
            if result_by_id[claim.claim_id].risk_score > 0
        )
        average_risk = sum(result.risk_score for result in provider_results) / len(provider_results)
        flagged_rate = len(flagged) / len(provider_claims)
        provider_risk_score = min(100, round(average_risk + flagged_rate * 70 + len(rule_counter) * 2))

        profiles.append(
            {
                "provider_id": provider_id,
                "provider_name": provider_claims[0].provider_name,
                "total_claims": len(provider_claims),
                "flagged_claims": len(flagged),
                "flagged_rate": round(flagged_rate, 4),
                "average_risk_score": round(average_risk, 2),
                "suspicious_amount": round(suspicious_amount, 2),
                "total_amount": round(total_amount, 2),
                "dominant_rules": [rule for rule, _ in rule_counter.most_common(3)],
                "provider_risk_score": provider_risk_score,
            }
        )

    return sorted(
        profiles,
        key=lambda item: (-item["provider_risk_score"], -item["suspicious_amount"], item["provider_id"]),
    )[:limit]


def member_provider_hotspots(
    claims: Sequence[Claim],
    result_by_id: dict[str, ScoreResult],
    *,
    limit: int = 10,
) -> list[dict]:
    grouped: dict[tuple[str, str], list[Claim]] = defaultdict(list)
    for claim in claims:
        grouped[(claim.member_id, claim.provider_id)].append(claim)

    hotspots = []
    for (member_id, provider_id), pair_claims in grouped.items():
        flagged = [
            claim for claim in pair_claims
            if result_by_id[claim.claim_id].risk_score > 0
        ]
        if not flagged:
            continue

        rules = Counter(
            flag.rule
            for claim in flagged
            for flag in result_by_id[claim.claim_id].flags
        )
        hotspots.append(
            {
                "member_id": member_id,
                "provider_id": provider_id,
                "claim_count": len(pair_claims),
                "flagged_claims": len(flagged),
                "highest_risk_score": max(result_by_id[claim.claim_id].risk_score for claim in flagged),
                "flagged_amount": round(sum(claim.submitted_amount for claim in flagged), 2),
                "dominant_rules": [rule for rule, _ in rules.most_common(3)],
            }
        )

    return sorted(
        hotspots,
        key=lambda item: (-item["highest_risk_score"], -item["flagged_claims"], -item["flagged_amount"]),
    )[:limit]


def investigation_markdown(report: dict) -> str:
    recommended = report["recommended_threshold"]
    lines = [
        "# Fraud Investigation Workbench",
        "",
        "## Recommended Review Threshold",
        "",
        f"- Threshold: risk score >= {recommended['threshold']}",
        f"- Review volume: {recommended['review_volume']} claims",
        f"- Precision: {recommended['precision']:.2%}",
        f"- Recall: {recommended['recall']:.2%}",
        f"- False positive rate: {recommended['false_positive_rate']:.2%}",
        f"- F1 score: {recommended['f1_score']:.2%}",
        "",
        "## Threshold Sensitivity",
        "",
        "| Threshold | Review volume | Precision | Recall | FPR | F1 |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["threshold_curve"]:
        lines.append(
            f"| {item['threshold']} | {item['review_volume']} | "
            f"{item['precision']:.2%} | {item['recall']:.2%} | "
            f"{item['false_positive_rate']:.2%} | {item['f1_score']:.2%} |"
        )

    lines.extend(
        [
            "",
            "## Analyst Review Queue",
            "",
            "| Rank | Claim ID | Provider | Score | Action | Rules |",
            "|---:|---|---|---:|---|---|",
        ]
    )
    for index, item in enumerate(report["review_queue"], start=1):
        lines.append(
            f"| {index} | {item['claim_id']} | {item['provider_name']} | "
            f"{item['risk_score']} | {item['recommended_action']} | {', '.join(item['rules'])} |"
        )

    lines.extend(
        [
            "",
            "## Provider Risk Profiles",
            "",
            "| Provider | Claims | Flagged | Avg score | Suspicious amount | Dominant rules |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for item in report["provider_profiles"]:
        lines.append(
            f"| {item['provider_name']} | {item['total_claims']} | "
            f"{item['flagged_claims']} | {item['average_risk_score']:.2f} | "
            f"${item['suspicious_amount']:,.2f} | {', '.join(item['dominant_rules']) or '-'} |"
        )

    lines.extend(
        [
            "",
            "## Member-Provider Hotspots",
            "",
            "| Member | Provider | Claims | Flagged | Highest score | Flagged amount | Rules |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for item in report["member_provider_hotspots"]:
        lines.append(
            f"| {item['member_id']} | {item['provider_id']} | {item['claim_count']} | "
            f"{item['flagged_claims']} | {item['highest_risk_score']} | "
            f"${item['flagged_amount']:,.2f} | {', '.join(item['dominant_rules'])} |"
        )

    lines.extend(["", "## Operational Notes", ""])
    lines.extend(f"- {note}" for note in report["operational_notes"])
    return "\n".join(lines) + "\n"
