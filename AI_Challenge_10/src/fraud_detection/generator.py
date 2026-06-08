from __future__ import annotations

import random
from collections import Counter
from datetime import date, timedelta
from typing import List, Sequence

from .config import (
    BUNDLE_MAPPINGS,
    DIAGNOSIS_BY_CLAIM_TYPE,
    PROCEDURES,
    PROVIDER_NAMES,
    VALID_DIAGNOSIS_PROCEDURES,
)
from .models import Claim


BASE_CLEAN_CLAIMS = 1_794
PHANTOM_SUPPORT_CLAIMS = 6
TARGET_FRAUD_COUNTS = {
    "duplicate_claim": 30,
    "rapid_resubmission": 30,
    "upcoding": 30,
    "unbundling": 25,
    "phantom_billing": 25,
    "weekend_anomaly": 20,
    "diagnosis_procedure_mismatch": 20,
    "amount_clustering": 20,
}


class ClaimFactory:
    def __init__(self, seed: int = 42) -> None:
        self.random = random.Random(seed)
        self.next_id = 1
        self.used_exact_keys: set[tuple[str, str, str, str]] = set()

    def claim_id(self) -> str:
        value = f"CLM-{self.next_id:05d}"
        self.next_id += 1
        return value

    def clean_claim(
        self,
        *,
        provider_id: str | None = None,
        claim_date: date | None = None,
        claim_type: str | None = None,
        member_id: str | None = None,
        force_weekday: bool = False,
        amount_override: float | None = None,
        procedure_override: Sequence[str] | None = None,
        diagnosis_override: str | None = None,
        fraud_pattern: str | None = None,
    ) -> Claim:
        provider_id = provider_id or f"PROV-{self.random.randint(1, 50):03d}"
        provider_name = provider_name_for(provider_id)
        claim_type = claim_type or self.random.choice(["OUTPATIENT", "INPATIENT", "DENTAL"])
        member_id = member_id or f"MBR-{self.random.randint(1, 500):04d}"

        if claim_date is None:
            claim_date = self.random_2024_date(force_weekday=force_weekday)

        procedure_codes = list(procedure_override or self.random_valid_procedures(claim_type))
        diagnosis_code = diagnosis_override or self.random_valid_diagnosis(procedure_codes)
        submitted_amount = (
            amount_override
            if amount_override is not None
            else self.amount_for_procedures(procedure_codes)
        )

        return Claim(
            claim_id=self.claim_id(),
            member_id=member_id,
            provider_id=provider_id,
            provider_name=provider_name,
            claim_date=claim_date.isoformat(),
            claim_type=claim_type,
            diagnosis_code=diagnosis_code,
            procedure_codes=procedure_codes,
            submitted_amount=round(submitted_amount, 2),
            is_weekend=claim_date.weekday() >= 5,
            fraud_label=fraud_pattern is not None,
            fraud_patterns=[fraud_pattern] if fraud_pattern else [],
        )

    def unique_clean_claim(self, **kwargs) -> Claim:
        for _ in range(1000):
            claim = self.clean_claim(**kwargs)
            key = exact_duplicate_key(claim)
            if key not in self.used_exact_keys:
                self.used_exact_keys.add(key)
                return claim
        raise RuntimeError("Could not generate a unique clean claim")

    def random_2024_date(self, *, force_weekday: bool = False) -> date:
        start = date(2024, 1, 1)
        while True:
            candidate = start + timedelta(days=self.random.randint(0, 365))
            if not force_weekday or candidate.weekday() < 5:
                return candidate

    def random_valid_procedures(self, claim_type: str) -> List[str]:
        options = [
            procedure.code
            for procedure in PROCEDURES.values()
            if procedure.claim_type == claim_type and not procedure.code.startswith("BND-")
        ]
        return [self.random.choice(options)]

    def random_valid_diagnosis(self, procedure_codes: Sequence[str]) -> str:
        primary = procedure_codes[0]
        candidates = [
            diagnosis
            for diagnosis, procedures in VALID_DIAGNOSIS_PROCEDURES.items()
            if primary in procedures
        ]
        return self.random.choice(candidates)

    def amount_for_procedures(self, procedure_codes: Sequence[str]) -> float:
        total = 0.0
        for code in procedure_codes:
            procedure = PROCEDURES[code]
            total += self.random.gauss(procedure.base_amount, procedure.std_dev * 0.45)
        return max(700, total)


def provider_name_for(provider_id: str) -> str:
    number = int(provider_id.split("-")[1])
    base_name = PROVIDER_NAMES[(number - 1) % len(PROVIDER_NAMES)]
    return f"{base_name} #{number:02d}"


def exact_duplicate_key(claim: Claim) -> tuple[str, str, str, str]:
    return (claim.member_id, claim.provider_id, claim.claim_date, claim.diagnosis_code)


def generate_claims(seed: int = 42) -> List[Claim]:
    factory = ClaimFactory(seed)
    claims: List[Claim] = []

    weekday_provider_id = "PROV-001"
    for _ in range(440):
        claims.append(
            factory.unique_clean_claim(provider_id=weekday_provider_id, force_weekday=True)
        )

    while len(claims) < BASE_CLEAN_CLAIMS:
        claims.append(factory.unique_clean_claim())

    phantom_date = date(2024, 8, 14)
    for index in range(PHANTOM_SUPPORT_CLAIMS):
        claims.append(
            factory.unique_clean_claim(
                provider_id="PROV-049",
                claim_date=phantom_date,
                member_id=f"MBR-{470 + index:04d}",
                claim_type="OUTPATIENT",
                procedure_override=["OP-101"],
                diagnosis_override="J06.9",
            )
        )

    seed_claims = list(claims)
    claims.extend(make_duplicate_claims(factory, seed_claims[:30]))
    claims.extend(make_rapid_resubmissions(factory, seed_claims[30:60]))
    claims.extend(make_upcoded_claims(factory))
    claims.extend(make_unbundled_claims(factory))
    claims.extend(make_phantom_claims(factory, phantom_date))
    claims.extend(make_weekend_anomaly_claims(factory))
    claims.extend(make_mismatch_claims(factory))
    claims.extend(make_amount_cluster_claims(factory))

    assert len(claims) == 2000, len(claims)
    assert sum(claim.fraud_label for claim in claims) == sum(TARGET_FRAUD_COUNTS.values())
    return claims


def make_duplicate_claims(factory: ClaimFactory, source_claims: Sequence[Claim]) -> List[Claim]:
    duplicates: List[Claim] = []
    for source in source_claims:
        duplicates.append(
            Claim(
                claim_id=factory.claim_id(),
                member_id=source.member_id,
                provider_id=source.provider_id,
                provider_name=source.provider_name,
                claim_date=source.claim_date,
                claim_type=source.claim_type,
                diagnosis_code=source.diagnosis_code,
                procedure_codes=list(source.procedure_codes),
                submitted_amount=source.submitted_amount,
                is_weekend=source.is_weekend,
                fraud_label=True,
                fraud_patterns=["duplicate_claim"],
            )
        )
    return duplicates


def make_rapid_resubmissions(factory: ClaimFactory, source_claims: Sequence[Claim]) -> List[Claim]:
    resubmissions: List[Claim] = []
    for source in source_claims:
        original_date = date.fromisoformat(source.claim_date)
        new_date = min(original_date + timedelta(days=3), date(2024, 12, 31))
        resubmissions.append(
            factory.clean_claim(
                provider_id=f"PROV-{factory.random.randint(2, 48):03d}",
                claim_date=new_date,
                claim_type=source.claim_type,
                member_id=source.member_id,
                procedure_override=source.procedure_codes,
                diagnosis_override=source.diagnosis_code,
                amount_override=source.submitted_amount * 0.95,
                fraud_pattern="rapid_resubmission",
            )
        )
    return resubmissions


def make_upcoded_claims(factory: ClaimFactory) -> List[Claim]:
    claims: List[Claim] = []
    codes = ["OP-301", "IP-201", "SUR-201", "DEN-201", "OP-401"]
    for index in range(TARGET_FRAUD_COUNTS["upcoding"]):
        code = codes[index % len(codes)]
        procedure = PROCEDURES[code]
        amount = procedure.base_amount + procedure.std_dev * 4.2 + index * 37
        claims.append(
            factory.clean_claim(
                claim_type=procedure.claim_type,
                procedure_override=[code],
                amount_override=amount,
                fraud_pattern="upcoding",
            )
        )
    return claims


def make_unbundled_claims(factory: ClaimFactory) -> List[Claim]:
    claims: List[Claim] = []
    bundles = list(BUNDLE_MAPPINGS.items())
    for index in range(TARGET_FRAUD_COUNTS["unbundling"]):
        _, individual_codes = bundles[index % len(bundles)]
        procedure_codes = sorted(individual_codes)
        claim_type = PROCEDURES[procedure_codes[0]].claim_type
        amount = sum(PROCEDURES[code].base_amount for code in procedure_codes) * 1.08
        claims.append(
            factory.clean_claim(
                claim_type=claim_type,
                procedure_override=procedure_codes,
                amount_override=amount,
                fraud_pattern="unbundling",
            )
        )
    return claims


def make_phantom_claims(factory: ClaimFactory, claim_date: date) -> List[Claim]:
    claims: List[Claim] = []
    for index in range(TARGET_FRAUD_COUNTS["phantom_billing"]):
        claims.append(
            factory.clean_claim(
                provider_id="PROV-049",
                claim_date=claim_date,
                member_id=f"MBR-{300 + index:04d}",
                claim_type="OUTPATIENT",
                procedure_override=["OP-102"],
                diagnosis_override="J06.9",
                amount_override=4_500 + index * 11,
                fraud_pattern="phantom_billing",
            )
        )
    return claims


def make_weekend_anomaly_claims(factory: ClaimFactory) -> List[Claim]:
    claims: List[Claim] = []
    weekend = date(2024, 9, 7)
    for index in range(TARGET_FRAUD_COUNTS["weekend_anomaly"]):
        code = "SUR-101" if index % 2 == 0 else "SUR-201"
        claims.append(
            factory.clean_claim(
                provider_id="PROV-001",
                claim_date=weekend + timedelta(days=index % 2),
                claim_type="INPATIENT",
                procedure_override=[code],
                diagnosis_override="K35.8" if code == "SUR-101" else "S83.2",
                fraud_pattern="weekend_anomaly",
            )
        )
    return claims


def make_mismatch_claims(factory: ClaimFactory) -> List[Claim]:
    claims: List[Claim] = []
    mismatch_pairs = [
        ("J06.9", "SUR-301"),
        ("K02.9", "SUR-201"),
        ("S83.2", "DEN-101"),
        ("I10", "DEN-201"),
        ("E11.9", "SUR-301"),
    ]
    for index in range(TARGET_FRAUD_COUNTS["diagnosis_procedure_mismatch"]):
        diagnosis, code = mismatch_pairs[index % len(mismatch_pairs)]
        claims.append(
            factory.clean_claim(
                claim_type=PROCEDURES[code].claim_type,
                procedure_override=[code],
                diagnosis_override=diagnosis,
                fraud_pattern="diagnosis_procedure_mismatch",
            )
        )
    return claims


def make_amount_cluster_claims(factory: ClaimFactory) -> List[Claim]:
    claims: List[Claim] = []
    for index in range(TARGET_FRAUD_COUNTS["amount_clustering"]):
        amount = 47_650 + (index * 117) % 2_250
        claims.append(
            factory.clean_claim(
                claim_type="OUTPATIENT",
                procedure_override=["OP-401"],
                diagnosis_override="E11.9",
                amount_override=amount,
                fraud_pattern="amount_clustering",
            )
        )
    return claims


def fraud_pattern_counts(claims: Sequence[Claim]) -> Counter:
    counts: Counter = Counter()
    for claim in claims:
        counts.update(claim.fraud_patterns)
    return counts
