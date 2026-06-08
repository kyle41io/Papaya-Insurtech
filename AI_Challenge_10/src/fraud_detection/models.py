from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, List


@dataclass
class Claim:
    claim_id: str
    member_id: str
    provider_id: str
    provider_name: str
    claim_date: str
    claim_type: str
    diagnosis_code: str
    procedure_codes: List[str]
    submitted_amount: float
    is_weekend: bool
    fraud_label: bool = False
    fraud_patterns: List[str] = field(default_factory=list)

    def to_csv_row(self) -> dict:
        row = asdict(self)
        row["procedure_codes"] = "|".join(self.procedure_codes)
        row["submitted_amount"] = f"{self.submitted_amount:.2f}"
        row["is_weekend"] = str(self.is_weekend).lower()
        row["fraud_label"] = str(self.fraud_label).lower()
        row["fraud_patterns"] = "|".join(self.fraud_patterns)
        return row

    @classmethod
    def from_csv_row(cls, row: dict) -> "Claim":
        return cls(
            claim_id=row["claim_id"],
            member_id=row["member_id"],
            provider_id=row["provider_id"],
            provider_name=row["provider_name"],
            claim_date=row["claim_date"],
            claim_type=row["claim_type"],
            diagnosis_code=row["diagnosis_code"],
            procedure_codes=[code for code in row["procedure_codes"].split("|") if code],
            submitted_amount=float(row["submitted_amount"]),
            is_weekend=row["is_weekend"].lower() == "true",
            fraud_label=row.get("fraud_label", "false").lower() == "true",
            fraud_patterns=[
                pattern for pattern in row.get("fraud_patterns", "").split("|") if pattern
            ],
        )


@dataclass
class Flag:
    rule: str
    severity: int
    evidence: str


@dataclass
class ScoreResult:
    claim_id: str
    risk_score: int
    flags: List[Flag]
    fraud_label: bool
    fraud_patterns: List[str]

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "risk_score": self.risk_score,
            "flags": [asdict(flag) for flag in self.flags],
            "fraud_label": self.fraud_label,
            "fraud_patterns": self.fraud_patterns,
        }


CSV_FIELDS = [
    "claim_id",
    "member_id",
    "provider_id",
    "provider_name",
    "claim_date",
    "claim_type",
    "diagnosis_code",
    "procedure_codes",
    "submitted_amount",
    "is_weekend",
    "fraud_label",
    "fraud_patterns",
]


def write_claims_csv(path: Path, claims: Iterable[Claim]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for claim in claims:
            writer.writerow(claim.to_csv_row())


def read_claims_csv(path: Path) -> List[Claim]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [Claim.from_csv_row(row) for row in csv.DictReader(handle)]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
