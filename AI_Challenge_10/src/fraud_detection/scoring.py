from __future__ import annotations

from typing import List, Sequence

from .config import RULE_WEIGHTS
from .models import Claim, ScoreResult
from .rules import build_context, evaluate_claim


MAX_WEIGHT_SUM = sum(RULE_WEIGHTS.values())


def risk_score_from_weights(weight_sum: int) -> int:
    if weight_sum <= 0:
        return 0
    return min(100, round(weight_sum / MAX_WEIGHT_SUM * 100))


def score_claims(claims: Sequence[Claim]) -> List[ScoreResult]:
    context = build_context(claims)
    results: List[ScoreResult] = []

    for claim in claims:
        flags = evaluate_claim(claim, context)
        weight_sum = sum(flag.severity for flag in flags)
        results.append(
            ScoreResult(
                claim_id=claim.claim_id,
                risk_score=risk_score_from_weights(weight_sum),
                flags=flags,
                fraud_label=claim.fraud_label,
                fraud_patterns=list(claim.fraud_patterns),
            )
        )

    return sorted(results, key=lambda item: (-item.risk_score, item.claim_id))
