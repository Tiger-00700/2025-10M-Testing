#!/usr/bin/env python3
"""Compare metrics between two CSV reports (by metric name/value)."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path


def load_metrics(path: Path) -> dict[str, float]:
    metrics: dict[str, float] = {}
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("metric") or row.get("name")
            val = float(row.get("value", 0))
            metrics[str(name)] = val
    return metrics


def reconcile(a: Path, b: Path, tolerance: float) -> int:
    ma = load_metrics(a)
    mb = load_metrics(b)
    missing = set(ma) - set(mb)
    extra = set(mb) - set(ma)
    drift = {
        k: (ma[k], mb[k])
        for k in set(ma) & set(mb)
        if abs(ma[k] - mb[k]) > tolerance
    }
    print(f"missing_in_b: {len(missing)} | extra_in_b: {len(extra)} | drift: {len(drift)}")
    return 0 if not (missing or extra or drift) else 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Report reconciliation")
    p.add_argument("a", type=Path)
    p.add_argument("b", type=Path)
    p.add_argument("--tolerance", type=float, default=0.0)
    args = p.parse_args(argv)
    return reconcile(args.a, args.b, args.tolerance)


if __name__ == "__main__":
    raise SystemExit(main())
