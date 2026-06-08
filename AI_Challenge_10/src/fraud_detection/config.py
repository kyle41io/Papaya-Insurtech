from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set


AUTO_APPROVAL_THRESHOLD = 50_000

RULE_WEIGHTS: Dict[str, int] = {
    "duplicate_claim": 5,
    "rapid_resubmission": 3,
    "upcoding": 4,
    "unbundling": 4,
    "phantom_billing": 5,
    "weekend_anomaly": 3,
    "diagnosis_procedure_mismatch": 4,
    "amount_clustering": 2,
}


@dataclass(frozen=True)
class Procedure:
    code: str
    claim_type: str
    base_amount: int
    std_dev: int
    surgical: bool = False


PROCEDURES: Dict[str, Procedure] = {
    "OP-101": Procedure("OP-101", "OUTPATIENT", 2_500, 500),
    "OP-102": Procedure("OP-102", "OUTPATIENT", 4_500, 700),
    "OP-201": Procedure("OP-201", "OUTPATIENT", 7_500, 1_100),
    "OP-301": Procedure("OP-301", "OUTPATIENT", 12_000, 1_800),
    "OP-401": Procedure("OP-401", "OUTPATIENT", 18_000, 2_200),
    "IP-101": Procedure("IP-101", "INPATIENT", 26_000, 3_500),
    "IP-201": Procedure("IP-201", "INPATIENT", 36_000, 4_000),
    "SUR-101": Procedure("SUR-101", "INPATIENT", 42_000, 4_800, surgical=True),
    "SUR-201": Procedure("SUR-201", "INPATIENT", 68_000, 7_500, surgical=True),
    "SUR-301": Procedure("SUR-301", "INPATIENT", 92_000, 9_500, surgical=True),
    "DEN-101": Procedure("DEN-101", "DENTAL", 3_000, 600),
    "DEN-201": Procedure("DEN-201", "DENTAL", 9_000, 1_300),
    "DEN-301": Procedure("DEN-301", "DENTAL", 16_000, 2_100, surgical=True),
    "BND-CARDIAC": Procedure("BND-CARDIAC", "OUTPATIENT", 18_500, 2_000),
    "BND-DENTAL": Procedure("BND-DENTAL", "DENTAL", 20_000, 2_500),
    "BND-MINOR-SURGERY": Procedure("BND-MINOR-SURGERY", "INPATIENT", 48_000, 5_200, surgical=True),
    "BND-ORTHO": Procedure("BND-ORTHO", "INPATIENT", 78_000, 7_200, surgical=True),
    "BND-DIABETES": Procedure("BND-DIABETES", "OUTPATIENT", 14_000, 1_600),
}


BUNDLE_MAPPINGS: Dict[str, Set[str]] = {
    "BND-CARDIAC": {"OP-101", "OP-201", "OP-301"},
    "BND-DENTAL": {"DEN-101", "DEN-201", "DEN-301"},
    "BND-MINOR-SURGERY": {"OP-102", "IP-101", "SUR-101"},
    "BND-ORTHO": {"OP-201", "IP-201", "SUR-201"},
    "BND-DIABETES": {"OP-101", "OP-102", "OP-401"},
}


VALID_DIAGNOSIS_PROCEDURES: Dict[str, Set[str]] = {
    "J06.9": {"OP-101", "OP-102"},
    "K02.9": {"DEN-101", "DEN-201", "DEN-301", "BND-DENTAL"},
    "S83.2": {"OP-201", "IP-201", "SUR-201", "BND-ORTHO"},
    "I10": {"OP-101", "OP-301"},
    "E11.9": {"OP-101", "OP-102", "OP-401", "BND-DIABETES"},
    "I25.1": {"OP-101", "OP-201", "OP-301", "BND-CARDIAC"},
    "K35.8": {"IP-101", "SUR-101", "BND-MINOR-SURGERY"},
    "M54.5": {"OP-101", "OP-201", "IP-201"},
    "N18.9": {"OP-401", "IP-101"},
    "C50.9": {"IP-201", "SUR-301"},
    "O80": {"IP-101", "IP-201"},
    "H10.9": {"OP-101", "OP-102"},
}


DIAGNOSIS_BY_CLAIM_TYPE: Dict[str, List[str]] = {
    "OUTPATIENT": ["J06.9", "I10", "E11.9", "I25.1", "M54.5", "N18.9", "H10.9"],
    "INPATIENT": ["S83.2", "K35.8", "M54.5", "N18.9", "C50.9", "O80"],
    "DENTAL": ["K02.9"],
}


PROVIDER_NAMES = [
    "Bangkok Care Clinic",
    "Saigon Family Medical",
    "Lotus Dental Center",
    "Mekong General Hospital",
    "Emerald Health Partners",
    "Sunrise Specialty Clinic",
    "Pacific Wellness Hospital",
    "CityCare Medical Group",
    "Golden Bridge Dental",
    "Unity Health Center",
]
