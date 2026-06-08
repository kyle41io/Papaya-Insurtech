# AI Challenge 10 - Fraud Detection Scoring Engine

## Overview

This project implements a rule-based insurance fraud scoring engine. It generates a deterministic dataset of 2,000 synthetic claims, embeds 200 known fraudulent claims across eight fraud patterns, scores every claim from 0 to 100, and reports precision, recall, false-positive rate, rule hit counts, runtime, rule-level precision, risk-band distribution, and review samples.

The solution uses only the Python standard library so reviewers can run it immediately.

## Timeline Estimate

- Domain modeling and rule design: 45 minutes
- Dataset generator: 75 minutes
- Scoring engine and metrics: 75 minutes
- Tests and report generation: 60 minutes
- README and final verification: 30 minutes

Estimated total: 4.75 hours.

## Quickstart

```bash
cd AI_Challenge_10
PYTHONPATH=src python3 -m fraud_detection.cli run
PYTHONPATH=src python3 -m unittest discover -s tests
```

Generated outputs:

- `data/claims.csv`
- `data/scored_claims.json`
- `data/metrics_report.json`
- `data/metrics_report.md`
- `data/analysis_report.json`
- `data/analysis_report.md`

## Review Artifacts

The project produces two reviewer-facing reports:

- `metrics_report.md`: high-level model quality, confusion matrix, rule hit counts, embedded fraud counts, and severity rationale.
- `analysis_report.md`: operational analysis with top suspicious claims, risk-band distribution, rule-level precision, fraud-pattern coverage, false-positive examples, and false-negative examples.

This split keeps the headline metrics easy to scan while still showing the evidence a reviewer would need before trusting the scoring engine.

## Detection Rules

The engine implements all eight required rules:

1. Duplicate claim: same member, provider, date, and diagnosis.
2. Rapid re-submission: same member and diagnosis within 7 days.
3. Upcoding: submitted amount more than 2 standard deviations above the procedure mean.
4. Unbundling: individual procedures billed separately when a configured bundle exists.
5. Phantom billing: provider submits more than 30 claims in one day.
6. Weekend anomaly: surgical procedure on a weekend for providers with under 5% historical weekend volume.
7. Diagnosis-procedure mismatch: procedure not clinically associated with the diagnosis.
8. Amount clustering: submitted amount within 5% below the 50,000 auto-approval threshold.

## Scoring

Each rule has a configurable severity weight from 1 to 5. The composite risk score is:

```text
round(sum(triggered_rule_weights) / sum(all_rule_weights) * 100)
```

Weights are intentionally explainable:

- Duplicate and phantom billing are highest severity because they strongly indicate abuse or billing for services not rendered.
- Upcoding, unbundling, and diagnosis mismatches are high severity because they affect payable amount or clinical validity.
- Rapid re-submission and weekend anomalies are medium severity because they are suspicious but may have legitimate explanations.
- Amount clustering is lower severity because it is a weak signal unless combined with other evidence.

## Dataset Design

The generator creates:

- 2,000 total claims.
- Around 500 members and 50 providers.
- Claim dates across 2024.
- Claim types: `OUTPATIENT`, `INPATIENT`, and `DENTAL`.
- 200 labeled fraudulent claims:
  - 30 duplicate claims
  - 30 rapid re-submissions
  - 30 upcoded claims
  - 25 unbundled claims
  - 25 phantom billing claims
  - 20 weekend surgical anomalies
  - 20 diagnosis-procedure mismatches
  - 20 amount clustering claims

The dataset includes `fraud_label` and `fraud_patterns` so metrics can be calculated against known ground truth.

## AI-Assisted Workflow

I used AI assistance to decompose the fraud patterns, design deterministic edge cases, and review the implementation against the challenge criteria. I then verified the result with unit tests, generated metrics, and checked that the outputs meet the recall, false-positive-rate, and runtime targets.

## Why This Is Estimated at 4-6 Hours

The implementation itself can be written quickly with AI assistance, but the real work is making the output defensible:

- Translating ambiguous fraud descriptions into deterministic, testable rules.
- Designing synthetic data with enough normal variation that the rules are not trivially perfect.
- Embedding labeled fraud cases without accidentally creating too many overlapping labels.
- Calibrating severity weights so the score is useful for triage instead of just a binary flag.
- Producing evidence strings that explain exactly why each claim was flagged.
- Measuring false positives and false negatives so reviewers can see the remaining blind spots.
- Writing tests that lock the dataset size, fraud coverage, runtime target, and rule behavior.

AI reduces typing and boilerplate time, but the challenge still requires judgment around data quality, rule design, explainability, and validation.

## Reproducibility

The default seed is `42`. To regenerate the same dataset and outputs:

```bash
PYTHONPATH=src python3 -m fraud_detection.cli run --seed 42
```

To use another deterministic dataset:

```bash
PYTHONPATH=src python3 -m fraud_detection.cli run --seed 2026
```
