"""
Placeholder for basic quality metrics scan script.
"""
if __name__ == "__main__":
    print("quality_scan placeholder")
"""Chapter 2 example: minimal quality metric scan.

Reads a small CSV and computes simple completeness
and basic statistics for one numeric column, printing
results to stdout. Dependency-light so it can run in CI.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class ColumnStats:
    non_null: int = 0
    total: int = 0
    min_value: float | None = None
    max_value: float | None = None

    def update(self, raw: str | None) -> None:
        self.total += 1
        if raw is None or str(raw).strip() == "":
            return
        self.non_null += 1
        try:
            v = float(raw)
        except ValueError:
            return
        if self.min_value is None or v < self.min_value:
            self.min_value = v
        if self.max_value is None or v > self.max_value:
            self.max_value = v

    @property
    def completeness(self) -> float:
        if self.total == 0:
            return 0.0
        return self.non_null / self.total


def scan(path: Path, numeric_column: str) -> Dict[str, str]:
    stats = ColumnStats()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats.update(row.get(numeric_column))

    result: Dict[str, str] = {
        "total_rows": str(stats.total),
        "non_null_rows": str(stats.non_null),
        "completeness": f"{stats.completeness:.2%}",
    }
    if stats.min_value is not None:
        result["min"] = str(stats.min_value)
    if stats.max_value is not None:
        result["max"] = str(stats.max_value)
    return result


def main() -> None:
    here = Path(__file__).parent
    data_path = here / "sample_orders_for_metrics.csv"

    if not data_path.exists():
        print(f"[ERROR] Sample data not found: {data_path}")
        raise SystemExit(1)

    metrics = scan(data_path, numeric_column="amount")
    print("Quality metrics for column 'amount':")
    for k, v in metrics.items():
        print(f"- {k}: {v}")


if __name__ == "__main__":  # pragma: no cover
    main()
