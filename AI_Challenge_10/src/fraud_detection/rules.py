from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Callable, Dict, Iterable, List, Sequence

from .config import (
    AUTO_APPROVAL_THRESHOLD,
    BUNDLE_MAPPINGS,
    PROCEDURES,
    RULE_WEIGHTS,
    VALID_DIAGNOSIS_PROCEDURES,
)
from .models import Claim, Flag


@dataclass
class RuleContext:
    duplicate_positions: Dict[str, int]
    claims_by_member_diagnosis: Dict[tuple[str, str], List[Claim]]
    procedure_stats: Dict[str, tuple[float, float]]
    provider_day_counts: Dict[tuple[str, str], int]
    provider_weekend_rates: Dict[str, float]


def build_context(claims: Sequence[Claim]) -> RuleContext:
    exact_groups: Dict[tuple[str, str, str, str], List[Claim]] = defaultdict(list)
    by_member_diagnosis: Dict[tuple[str, str], List[Claim]] = defaultdict(list)
    amounts_by_procedure: Dict[str, List[float]] = defaultdict(list)
    provider_day_counts: Dict[tuple[str, str], int] = defaultdict(int)
    provider_total: Dict[str, int] = defaultdict(int)
    provider_weekend: Dict[str, int] = defaultdict(int)

    for claim in claims:
        exact_groups[
            (claim.member_id, claim.provider_id, claim.claim_date, claim.diagnosis_code)
        ].append(claim)
        by_member_diagnosis[(claim.member_id, claim.diagnosis_code)].append(claim)
        provider_day_counts[(claim.provider_id, claim.claim_date)] += 1

        for code in claim.procedure_codes:
            amounts_by_procedure[code].append(claim.submitted_amount)

        has_surgical_code = any(PROCEDURES[code].surgical for code in claim.procedure_codes)
        if not has_surgical_code:
            provider_total[claim.provider_id] += 1
            if claim.is_weekend:
                provider_weekend[claim.provider_id] += 1

    duplicate_positions: Dict[str, int] = {}
    for group in exact_groups.values():
        if len(group) > 1:
            for index, claim in enumerate(sorted(group, key=lambda item: item.claim_id)):
                duplicate_positions[claim.claim_id] = index

    procedure_stats = {}
    for code, amounts in amounts_by_procedure.items():
        baseline_amounts = trimmed_baseline(amounts)
        if len(baseline_amounts) < 2:
            procedure_stats[code] = (baseline_amounts[0], 0.0)
        else:
            procedure_stats[code] = (
                statistics.mean(baseline_amounts),
                statistics.pstdev(baseline_amounts),
            )

    provider_weekend_rates = {
        provider_id: provider_weekend[provider_id] / max(provider_total[provider_id], 1)
        for provider_id in provider_total
    }

    for group in by_member_diagnosis.values():
        group.sort(key=lambda item: (item.claim_date, item.claim_id))

    return RuleContext(
        duplicate_positions=duplicate_positions,
        claims_by_member_diagnosis=by_member_diagnosis,
        procedure_stats=procedure_stats,
        provider_day_counts=provider_day_counts,
        provider_weekend_rates=provider_weekend_rates,
    )


def trimmed_baseline(amounts: Sequence[float]) -> List[float]:
    """Estimate ordinary procedure pricing without letting extreme claims set the bar."""
    if len(amounts) < 20:
        return list(amounts)

    sorted_amounts = sorted(amounts)
    trim_count = max(1, int(len(sorted_amounts) * 0.05))
    return sorted_amounts[:-trim_count]


def severity(rule_name: str) -> int:
    return RULE_WEIGHTS[rule_name]


def duplicate_claim(claim: Claim, context: RuleContext) -> Flag | None:
    position = context.duplicate_positions.get(claim.claim_id)
    if position is None or position == 0:
        return None

    return Flag(
        rule="duplicate_claim",
        severity=severity("duplicate_claim"),
        evidence=(
            f"Claim duplicates an earlier submission for member {claim.member_id}, "
            f"provider {claim.provider_id}, date {claim.claim_date}, and diagnosis "
            f"{claim.diagnosis_code}"
        ),
    )


def rapid_resubmission(claim: Claim, context: RuleContext) -> Flag | None:
    group = context.claims_by_member_diagnosis[(claim.member_id, claim.diagnosis_code)]
    claim_date = date.fromisoformat(claim.claim_date)
    for other in group:
        if other.claim_id == claim.claim_id:
            break
        days = (claim_date - date.fromisoformat(other.claim_date)).days
        if 0 < days <= 7:
            return Flag(
                rule="rapid_resubmission",
                severity=severity("rapid_resubmission"),
                evidence=(
                    f"Member {claim.member_id} submitted diagnosis {claim.diagnosis_code} "
                    f"again after {days} days; prior claim {other.claim_id} was on "
                    f"{other.claim_date}"
                ),
            )
    return None


def upcoding(claim: Claim, context: RuleContext) -> Flag | None:
    primary_code = claim.procedure_codes[0]
    mean, std_dev = context.procedure_stats[primary_code]
    if std_dev <= 0:
        return None

    z_score = (claim.submitted_amount - mean) / std_dev
    if z_score <= 2:
        return None

    return Flag(
        rule="upcoding",
        severity=severity("upcoding"),
        evidence=(
            f"Submitted amount {claim.submitted_amount:,.0f} for procedure {primary_code} "
            f"is {z_score:.1f} standard deviations above the mean of {mean:,.0f}"
        ),
    )


def unbundling(claim: Claim, context: RuleContext) -> Flag | None:
    submitted = set(claim.procedure_codes)
    for bundle_code, individual_codes in BUNDLE_MAPPINGS.items():
        if bundle_code not in submitted and individual_codes.issubset(submitted):
            return Flag(
                rule="unbundling",
                severity=severity("unbundling"),
                evidence=(
                    f"Procedures {', '.join(sorted(individual_codes))} were billed "
                    f"separately although bundle {bundle_code} should be used"
                ),
            )
    return None


def phantom_billing(claim: Claim, context: RuleContext) -> Flag | None:
    count = context.provider_day_counts[(claim.provider_id, claim.claim_date)]
    if count <= 30:
        return None

    return Flag(
        rule="phantom_billing",
        severity=severity("phantom_billing"),
        evidence=(
            f"Provider {claim.provider_id} submitted {count} claims on "
            f"{claim.claim_date}, exceeding the 30-claim daily review threshold"
        ),
    )


def weekend_anomaly(claim: Claim, context: RuleContext) -> Flag | None:
    if not claim.is_weekend:
        return None

    surgical_codes = [code for code in claim.procedure_codes if PROCEDURES[code].surgical]
    if not surgical_codes:
        return None

    weekend_rate = context.provider_weekend_rates.get(claim.provider_id, 0.0)
    if weekend_rate >= 0.05:
        return None

    return Flag(
        rule="weekend_anomaly",
        severity=severity("weekend_anomaly"),
        evidence=(
            f"Surgical procedure(s) {', '.join(surgical_codes)} occurred on a weekend "
            f"for provider {claim.provider_id}, whose historical weekend volume is "
            f"{weekend_rate:.1%}"
        ),
    )


def diagnosis_procedure_mismatch(claim: Claim, context: RuleContext) -> Flag | None:
    valid_codes = VALID_DIAGNOSIS_PROCEDURES.get(claim.diagnosis_code, set())
    invalid_codes = [code for code in claim.procedure_codes if code not in valid_codes]
    if not invalid_codes:
        return None

    return Flag(
        rule="diagnosis_procedure_mismatch",
        severity=severity("diagnosis_procedure_mismatch"),
        evidence=(
            f"Diagnosis {claim.diagnosis_code} is not clinically associated with "
            f"procedure(s) {', '.join(invalid_codes)}"
        ),
    )


def amount_clustering(claim: Claim, context: RuleContext) -> Flag | None:
    lower_bound = AUTO_APPROVAL_THRESHOLD * 0.95
    if not lower_bound <= claim.submitted_amount < AUTO_APPROVAL_THRESHOLD:
        return None

    percent = claim.submitted_amount / AUTO_APPROVAL_THRESHOLD
    return Flag(
        rule="amount_clustering",
        severity=severity("amount_clustering"),
        evidence=(
            f"Amount {claim.submitted_amount:,.0f} is {percent:.0%} of the "
            f"{AUTO_APPROVAL_THRESHOLD:,.0f} auto-approval threshold"
        ),
    )


RuleFunction = Callable[[Claim, RuleContext], Flag | None]

ALL_RULES: List[RuleFunction] = [
    duplicate_claim,
    rapid_resubmission,
    upcoding,
    unbundling,
    phantom_billing,
    weekend_anomaly,
    diagnosis_procedure_mismatch,
    amount_clustering,
]


def evaluate_claim(claim: Claim, context: RuleContext) -> List[Flag]:
    flags: List[Flag] = []
    for rule in ALL_RULES:
        flag = rule(claim, context)
        if flag:
            flags.append(flag)
    return flags


def rule_names(flags: Iterable[Flag]) -> set[str]:
    return {flag.rule for flag in flags}
