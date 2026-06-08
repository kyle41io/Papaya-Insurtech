# Fraud Detection Analysis Report

## Top Suspicious Claims

| Rank | Claim ID | Score | Label | Rules |
|---:|---|---:|---|---|
| 1 | CLM-01891 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 2 | CLM-01893 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 3 | CLM-01896 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 4 | CLM-01898 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 5 | CLM-01900 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 6 | CLM-01903 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 7 | CLM-01904 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 8 | CLM-01905 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 9 | CLM-01906 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 10 | CLM-01908 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 11 | CLM-01910 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 12 | CLM-01911 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 13 | CLM-01913 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 14 | CLM-01914 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 15 | CLM-01915 | 40 | fraud | upcoding, unbundling, diagnosis_procedure_mismatch |
| 16 | CLM-01822 | 30 | fraud | duplicate_claim, upcoding |
| 17 | CLM-01892 | 27 | fraud | upcoding, unbundling |
| 18 | CLM-01894 | 27 | fraud | upcoding, unbundling |
| 19 | CLM-01895 | 27 | fraud | upcoding, unbundling |
| 20 | CLM-01897 | 27 | fraud | upcoding, unbundling |

## Risk Band Distribution

| Band | Claims | Labeled fraud | Fraud rate |
|---|---:|---:|---:|
| 0 | 1765 | 6 | 0.34% |
| 1-24 | 208 | 167 | 80.29% |
| 25-49 | 27 | 27 | 100.00% |
| 50-74 | 0 | 0 | 0.00% |
| 75-100 | 0 | 0 | 0.00% |

## Rule-Level Precision

| Rule | Hits | True hits | False hits | Precision |
|---|---:|---:|---:|---:|
| amount_clustering | 21 | 20 | 1 | 95.24% |
| diagnosis_procedure_mismatch | 35 | 35 | 0 | 100.00% |
| duplicate_claim | 30 | 30 | 0 | 100.00% |
| phantom_billing | 31 | 25 | 6 | 80.65% |
| rapid_resubmission | 44 | 32 | 12 | 72.73% |
| unbundling | 25 | 25 | 0 | 100.00% |
| upcoding | 91 | 71 | 20 | 78.02% |
| weekend_anomaly | 23 | 20 | 3 | 86.96% |

## Fraud Pattern Coverage

| Pattern | Embedded | Detected by any rule | Detected by matching rule | Matching recall |
|---|---:|---:|---:|---:|
| amount_clustering | 20 | 20 | 20 | 100.00% |
| diagnosis_procedure_mismatch | 20 | 20 | 20 | 100.00% |
| duplicate_claim | 30 | 30 | 30 | 100.00% |
| phantom_billing | 25 | 25 | 25 | 100.00% |
| rapid_resubmission | 30 | 30 | 30 | 100.00% |
| unbundling | 25 | 25 | 25 | 100.00% |
| upcoding | 30 | 24 | 24 | 80.00% |
| weekend_anomaly | 20 | 20 | 20 | 100.00% |

## Review Notes

- Risk score > 0 is treated as the review threshold for metrics.
- False positives are acceptable when the evidence is actionable because the engine is designed as a triage tool, not an automatic denial system.
- False negatives are listed explicitly so reviewers can see remaining blind spots.

## False Positive Samples

| Claim ID | Score | Patterns | Rules |
|---|---:|---|---|
| CLM-00950 | 20 | - | upcoding, amount_clustering |
| CLM-01795 | 17 | - | phantom_billing |
| CLM-01796 | 17 | - | phantom_billing |
| CLM-01797 | 17 | - | phantom_billing |
| CLM-01798 | 17 | - | phantom_billing |
| CLM-01799 | 17 | - | phantom_billing |
| CLM-01800 | 17 | - | phantom_billing |
| CLM-00022 | 13 | - | upcoding |
| CLM-00042 | 13 | - | upcoding |
| CLM-00087 | 13 | - | upcoding |

## False Negative Samples

| Claim ID | Score | Patterns | Rules |
|---|---:|---|---|
| CLM-01865 | 0 | upcoding | - |
| CLM-01870 | 0 | upcoding | - |
| CLM-01875 | 0 | upcoding | - |
| CLM-01880 | 0 | upcoding | - |
| CLM-01885 | 0 | upcoding | - |
| CLM-01890 | 0 | upcoding | - |
