"""Deterministic data factory demo (Chapter 17).

Generates synthetic records with fixed seeds and writes a sample report.

Usage:
  python tools/ci/data_factory_demo.py --count 5 --seed 123 --out tools/reports/data_factory_sample.md
"""
from __future__ import annotations

import argparse
import pathlib
import random
import datetime as dt


def make_record(rng: random.Random, idx: int) -> dict:
    return {
        "id": idx,
        "amount": round(rng.gauss(100.0, 15.0), 2),
        "status": rng.choice(["ok", "pending", "failed"]),
        "bucket": rng.choice(["A", "B", "C"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic data factory demo")
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--out", default="tools/reports/data_factory_sample.md")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    records = [make_record(rng, i) for i in range(args.count)]
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    lines = [f"- {r}" for r in records]
    verdict = "PASS" if records else "FAIL"
    report = [
        "# Data Factory Sample",
        f"Generated: {now}",
        f"Verdict: {verdict}",
        f"Seed: {args.seed} Count: {args.count}",
        "",
        "## Records",
        "\n".join(lines),
        "",
        "## Recommendations",
        "(no recommendations)" if verdict == "PASS" else "Ensure factory produces at least one record",
    ]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
