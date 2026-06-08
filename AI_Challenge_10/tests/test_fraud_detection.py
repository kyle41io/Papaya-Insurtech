from __future__ import annotations

import sys
import time
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fraud_detection.config import BUNDLE_MAPPINGS, RULE_WEIGHTS, VALID_DIAGNOSIS_PROCEDURES
from fraud_detection.generator import TARGET_FRAUD_COUNTS, fraud_pattern_counts, generate_claims
from fraud_detection.metrics import evaluate_metrics
from fraud_detection.rules import build_context, evaluate_claim
from fraud_detection.scoring import MAX_WEIGHT_SUM, risk_score_from_weights, score_claims


class FraudDetectionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.claims = generate_claims()
        start = time.perf_counter()
        cls.results = score_claims(cls.claims)
        cls.processing_seconds = time.perf_counter() - start
        cls.metrics = evaluate_metrics(
            cls.claims,
            cls.results,
            processing_seconds=cls.processing_seconds,
        )
        cls.result_by_id = {result.claim_id: result for result in cls.results}

    def test_dataset_has_exactly_2000_claims(self) -> None:
        self.assertEqual(len(self.claims), 2000)

    def test_dataset_has_500_members_and_50_providers_available(self) -> None:
        members = {claim.member_id for claim in self.claims}
        providers = {claim.provider_id for claim in self.claims}
        self.assertGreaterEqual(len(members), 450)
        self.assertEqual(len(providers), 50)

    def test_dataset_has_exactly_200_labeled_fraud_claims(self) -> None:
        self.assertEqual(sum(claim.fraud_label for claim in self.claims), 200)

    def test_fraud_pattern_counts_match_design(self) -> None:
        self.assertEqual(dict(fraud_pattern_counts(self.claims)), TARGET_FRAUD_COUNTS)

    def test_bundle_mapping_has_at_least_five_bundles(self) -> None:
        self.assertGreaterEqual(len(BUNDLE_MAPPINGS), 5)

    def test_diagnosis_mapping_has_at_least_ten_pairs(self) -> None:
        self.assertGreaterEqual(len(VALID_DIAGNOSIS_PROCEDURES), 10)

    def test_rule_weights_are_configurable_severity_range(self) -> None:
        self.assertEqual(len(RULE_WEIGHTS), 8)
        self.assertTrue(all(1 <= weight <= 5 for weight in RULE_WEIGHTS.values()))

    def test_risk_score_normalizes_to_100(self) -> None:
        self.assertEqual(risk_score_from_weights(0), 0)
        self.assertEqual(risk_score_from_weights(MAX_WEIGHT_SUM), 100)

    def test_all_eight_rules_have_hits(self) -> None:
        self.assertEqual(set(self.metrics.rule_hit_counts), set(RULE_WEIGHTS))

    def test_each_flag_has_actionable_evidence(self) -> None:
        for result in self.results:
            for flag in result.flags:
                self.assertIn(flag.rule, RULE_WEIGHTS)
                self.assertGreaterEqual(flag.severity, 1)
                self.assertGreater(len(flag.evidence), 40)
                self.assertNotEqual(flag.evidence.lower(), f"flagged by {flag.rule}")

    def test_metrics_meet_recall_target(self) -> None:
        self.assertGreaterEqual(self.metrics.recall, 0.70)

    def test_metrics_meet_false_positive_target(self) -> None:
        self.assertLessEqual(self.metrics.false_positive_rate, 0.20)

    def test_processing_time_is_under_30_seconds(self) -> None:
        self.assertLess(self.processing_seconds, 30)

    def test_duplicate_claim_rule_flags_later_duplicate(self) -> None:
        duplicate_claims = [
            claim for claim in self.claims if "duplicate_claim" in claim.fraud_patterns
        ]
        self.assertEqual(len(duplicate_claims), 30)
        for claim in duplicate_claims:
            rules = {flag.rule for flag in self.result_by_id[claim.claim_id].flags}
            self.assertIn("duplicate_claim", rules)

    def test_rapid_resubmission_rule_flags_embedded_cases(self) -> None:
        self.assert_pattern_rule_recall("rapid_resubmission", minimum=0.90)

    def test_upcoding_rule_flags_embedded_cases(self) -> None:
        self.assert_pattern_rule_recall("upcoding", minimum=0.80)

    def test_unbundling_rule_flags_embedded_cases(self) -> None:
        self.assert_pattern_rule_recall("unbundling", minimum=1.0)

    def test_phantom_billing_rule_flags_embedded_cases(self) -> None:
        self.assert_pattern_rule_recall("phantom_billing", minimum=1.0)

    def test_weekend_anomaly_rule_flags_embedded_cases(self) -> None:
        self.assert_pattern_rule_recall("weekend_anomaly", minimum=1.0)

    def test_diagnosis_mismatch_rule_flags_embedded_cases(self) -> None:
        self.assert_pattern_rule_recall("diagnosis_procedure_mismatch", minimum=1.0)

    def test_amount_clustering_rule_flags_embedded_cases(self) -> None:
        self.assert_pattern_rule_recall("amount_clustering", minimum=1.0)

    def test_clean_claim_without_flags_scores_zero(self) -> None:
        clean_zero = next(
            result
            for result in self.results
            if not result.fraud_label and result.risk_score == 0
        )
        self.assertEqual(clean_zero.flags, [])

    def test_duplicate_rule_does_not_flag_first_claim_in_exact_group(self) -> None:
        context = build_context(self.claims)
        groups = defaultdict(list)
        for claim in self.claims:
            groups[(claim.member_id, claim.provider_id, claim.claim_date, claim.diagnosis_code)].append(
                claim
            )
        duplicate_group = next(group for group in groups.values() if len(group) > 1)
        first = sorted(duplicate_group, key=lambda item: item.claim_id)[0]
        rules = {flag.rule for flag in evaluate_claim(first, context)}
        self.assertNotIn("duplicate_claim", rules)

    def assert_pattern_rule_recall(self, pattern: str, minimum: float) -> None:
        labeled = [claim for claim in self.claims if pattern in claim.fraud_patterns]
        hits = 0
        for claim in labeled:
            rules = {flag.rule for flag in self.result_by_id[claim.claim_id].flags}
            if pattern in rules:
                hits += 1
        self.assertGreaterEqual(hits / len(labeled), minimum)


if __name__ == "__main__":
    unittest.main()
