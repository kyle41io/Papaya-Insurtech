# Fraud Detection Metrics Report

## Summary

- Total claims: 2,000
- Labeled fraud claims: 200
- Predicted fraud claims: 235
- Precision: 82.55%
- Recall: 97.00%
- False positive rate: 2.28%
- Processing time: 0.0057s

## Confusion Matrix

| Metric | Count |
|---|---:|
| True positives | 194 |
| False positives | 41 |
| False negatives | 6 |
| True negatives | 1759 |

## Rule Hit Counts

| Rule | Hits |
|---|---:|
| amount_clustering | 21 |
| diagnosis_procedure_mismatch | 35 |
| duplicate_claim | 30 |
| phantom_billing | 31 |
| rapid_resubmission | 44 |
| unbundling | 25 |
| upcoding | 91 |
| weekend_anomaly | 23 |

## Embedded Fraud Pattern Counts

| Pattern | Count |
|---|---:|
| amount_clustering | 20 |
| diagnosis_procedure_mismatch | 20 |
| duplicate_claim | 30 |
| phantom_billing | 25 |
| rapid_resubmission | 30 |
| unbundling | 25 |
| upcoding | 30 |
| weekend_anomaly | 20 |

## Severity Weight Rationale

- Duplicate and phantom billing are weighted highest because they strongly indicate abuse or billing for services not rendered.
- Upcoding, unbundling, and diagnosis mismatches are high-severity because they affect payable amount or clinical validity.
- Rapid re-submission and weekend anomalies are medium severity because they are suspicious but may have legitimate explanations.
- Amount clustering is lower severity because it is a weak signal unless combined with other evidence.
