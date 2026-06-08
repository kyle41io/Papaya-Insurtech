from __future__ import annotations

import argparse
from pathlib import Path

from .generator import generate_claims
from .metrics import evaluate_metrics, markdown_report, timed
from .models import read_claims_csv, write_claims_csv, write_json
from .scoring import score_claims


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CLAIMS_CSV = DATA_DIR / "claims.csv"
SCORED_JSON = DATA_DIR / "scored_claims.json"
METRICS_JSON = DATA_DIR / "metrics_report.json"
METRICS_MD = DATA_DIR / "metrics_report.md"


def generate_command(args: argparse.Namespace) -> None:
    claims = generate_claims(seed=args.seed)
    write_claims_csv(CLAIMS_CSV, claims)
    print(f"Generated {len(claims):,} claims at {CLAIMS_CSV}")


def score_command(args: argparse.Namespace) -> None:
    claims = read_claims_csv(CLAIMS_CSV)
    results, processing_seconds = timed(lambda: score_claims(claims))
    metrics = evaluate_metrics(claims, results, processing_seconds=processing_seconds)

    write_json(SCORED_JSON, [result.to_dict() for result in results])
    write_json(METRICS_JSON, metrics.to_dict())
    METRICS_MD.write_text(markdown_report(metrics), encoding="utf-8")

    print(f"Scored {len(claims):,} claims in {processing_seconds:.4f}s")
    print(f"Recall: {metrics.recall:.2%}")
    print(f"False positive rate: {metrics.false_positive_rate:.2%}")
    print(f"Wrote {SCORED_JSON}, {METRICS_JSON}, and {METRICS_MD}")


def run_command(args: argparse.Namespace) -> None:
    generate_command(args)
    score_command(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Insurance fraud scoring engine")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic dataset seed")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    generate_parser = subparsers.add_parser("generate", help="Generate claims.csv")
    generate_parser.set_defaults(func=generate_command)

    score_parser = subparsers.add_parser("score", help="Score generated claims")
    score_parser.set_defaults(func=score_command)

    run_parser = subparsers.add_parser("run", help="Generate and score end-to-end")
    run_parser.set_defaults(func=run_command)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
