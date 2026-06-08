# Fraud Investigation Workbench

## Recommended Review Threshold

- Threshold: risk score >= 1
- Review volume: 235 claims
- Precision: 82.55%
- Recall: 97.00%
- False positive rate: 2.28%
- F1 score: 89.20%

## Threshold Sensitivity

| Threshold | Review volume | Precision | Recall | FPR | F1 |
|---:|---:|---:|---:|---:|---:|
| 1 | 235 | 82.55% | 97.00% | 2.28% | 89.20% |
| 10 | 235 | 82.55% | 97.00% | 2.28% | 89.20% |
| 15 | 109 | 93.58% | 51.00% | 0.39% | 66.02% |
| 20 | 50 | 98.00% | 24.50% | 0.06% | 39.20% |
| 25 | 27 | 100.00% | 13.50% | 0.00% | 23.79% |
| 30 | 16 | 100.00% | 8.00% | 0.00% | 14.81% |
| 40 | 15 | 100.00% | 7.50% | 0.00% | 13.95% |

## Analyst Review Queue

| Rank | Claim ID | Provider | Score | Action | Rules |
|---:|---|---|---:|---|---|
| 1 | CLM-01891 | Mekong General Hospital #24 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 2 | CLM-01893 | Unity Health Center #20 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 3 | CLM-01896 | Mekong General Hospital #34 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 4 | CLM-01898 | Sunrise Specialty Clinic #16 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 5 | CLM-01900 | Pacific Wellness Hospital #37 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 6 | CLM-01903 | Emerald Health Partners #15 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 7 | CLM-01904 | Lotus Dental Center #33 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 8 | CLM-01905 | Golden Bridge Dental #49 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 9 | CLM-01906 | Bangkok Care Clinic #11 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 10 | CLM-01908 | Bangkok Care Clinic #01 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 11 | CLM-01910 | Pacific Wellness Hospital #37 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 12 | CLM-01911 | Pacific Wellness Hospital #47 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 13 | CLM-01913 | Sunrise Specialty Clinic #16 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 14 | CLM-01914 | Lotus Dental Center #13 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 15 | CLM-01915 | Unity Health Center #50 | 40 | Open special investigation case | upcoding, unbundling, diagnosis_procedure_mismatch |
| 16 | CLM-01822 | Bangkok Care Clinic #01 | 30 | Open special investigation case | duplicate_claim, upcoding |
| 17 | CLM-01892 | Golden Bridge Dental #19 | 27 | Request medical records before payment | upcoding, unbundling |
| 18 | CLM-01894 | Sunrise Specialty Clinic #16 | 27 | Request medical records before payment | upcoding, unbundling |
| 19 | CLM-01895 | Bangkok Care Clinic #01 | 27 | Request medical records before payment | upcoding, unbundling |
| 20 | CLM-01897 | Saigon Family Medical #22 | 27 | Request medical records before payment | upcoding, unbundling |
| 21 | CLM-01899 | Unity Health Center #40 | 27 | Request medical records before payment | upcoding, unbundling |
| 22 | CLM-01901 | Emerald Health Partners #25 | 27 | Request medical records before payment | upcoding, unbundling |
| 23 | CLM-01902 | Bangkok Care Clinic #21 | 27 | Request medical records before payment | upcoding, unbundling |
| 24 | CLM-01907 | Sunrise Specialty Clinic #06 | 27 | Request medical records before payment | upcoding, unbundling |
| 25 | CLM-01909 | Saigon Family Medical #02 | 27 | Request medical records before payment | upcoding, unbundling |
| 26 | CLM-01912 | Bangkok Care Clinic #41 | 27 | Request medical records before payment | upcoding, unbundling |
| 27 | CLM-01927 | Golden Bridge Dental #49 | 27 | Request medical records before payment | rapid_resubmission, phantom_billing |
| 28 | CLM-01869 | Emerald Health Partners #45 | 23 | Request medical records before payment | rapid_resubmission, upcoding |
| 29 | CLM-01943 | Bangkok Care Clinic #01 | 23 | Request medical records before payment | upcoding, weekend_anomaly |
| 30 | CLM-00950 | Lotus Dental Center #33 | 20 | Request medical records before payment | upcoding, amount_clustering |

## Provider Risk Profiles

| Provider | Claims | Flagged | Avg score | Suspicious amount | Dominant rules |
|---|---:|---:|---:|---:|---|
| Golden Bridge Dental #49 | 53 | 32 | 10.89 | $158,328.21 | phantom_billing, upcoding, unbundling |
| Lotus Dental Center #23 | 31 | 7 | 3.29 | $317,087.09 | upcoding, diagnosis_procedure_mismatch, amount_clustering |
| Lotus Dental Center #33 | 31 | 6 | 3.84 | $480,568.08 | upcoding, amount_clustering, diagnosis_procedure_mismatch |
| Mekong General Hospital #24 | 37 | 6 | 2.86 | $276,705.35 | upcoding, rapid_resubmission, unbundling |
| Bangkok Care Clinic #01 | 522 | 67 | 1.86 | $2,075,882.12 | duplicate_claim, weekend_anomaly, upcoding |
| Mekong General Hospital #14 | 33 | 6 | 2.52 | $287,218.82 | rapid_resubmission, upcoding, amount_clustering |
| Bangkok Care Clinic #21 | 29 | 5 | 2.76 | $256,103.15 | upcoding, rapid_resubmission, unbundling |
| Pacific Wellness Hospital #37 | 22 | 3 | 4.09 | $56,713.36 | upcoding, unbundling, diagnosis_procedure_mismatch |
| CityCare Medical Group #08 | 29 | 5 | 2.72 | $277,173.22 | upcoding, diagnosis_procedure_mismatch, amount_clustering |
| Golden Bridge Dental #29 | 32 | 5 | 2.06 | $156,683.07 | rapid_resubmission, upcoding, diagnosis_procedure_mismatch |

## Member-Provider Hotspots

| Member | Provider | Claims | Flagged | Highest score | Flagged amount | Rules |
|---|---|---:|---:|---:|---:|---|
| MBR-0322 | PROV-049 | 2 | 2 | 40 | $31,742.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0061 | PROV-033 | 1 | 1 | 40 | $120,420.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0275 | PROV-013 | 1 | 1 | 40 | $120,420.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0430 | PROV-020 | 1 | 1 | 40 | $78,300.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0285 | PROV-016 | 1 | 1 | 40 | $78,300.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0051 | PROV-015 | 1 | 1 | 40 | $78,300.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0322 | PROV-001 | 1 | 1 | 40 | $78,300.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0335 | PROV-016 | 1 | 1 | 40 | $78,300.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0220 | PROV-037 | 1 | 1 | 40 | $27,000.00 | upcoding, unbundling, diagnosis_procedure_mismatch |
| MBR-0196 | PROV-037 | 1 | 1 | 40 | $27,000.00 | upcoding, unbundling, diagnosis_procedure_mismatch |

## Operational Notes

- Use the recommended threshold as a review trigger, not an automatic denial rule.
- Start with provider profiles when multiple high-risk claims share the same provider.
- Use member-provider hotspots to find concentrated suspicious relationships.
- Escalate only after checking the evidence strings attached to each claim.
