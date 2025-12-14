"""Minimal test runner (Chapter 17 example).

Runs a small suite with fixtures and writes a Markdown report.

Usage:
  python tools/ci/test_runner.py --out tools/reports/test_runner.md
"""
from __future__ import annotations

import argparse
import pathlib
import datetime as dt
from typing import Callable, List, Tuple


class Fixture:
    def __init__(self):
        self.env_ready = True
        self.seed = 42

    def setup(self):
        # Simulate environment setup
        self.env_ready = True

    def teardown(self):
        # Simulate cleanup
        pass


def case_contract(fx: Fixture) -> Tuple[str, bool, str]:
    return ("contract", fx.env_ready, "schema compatible (demo)")


def case_quality(fx: Fixture) -> Tuple[str, bool, str]:
    p95_latency = 4.3
    ok = p95_latency <= 5.0
    return ("quality_gate", ok, f"p95={p95_latency}s <= 5s")


def case_security(fx: Fixture) -> Tuple[str, bool, str]:
    authn = True
    authz = True
    audit_events = 2
    ok = authn and authz and audit_events >= 1
    return ("security_patrol", ok, "authn/authz/audit OK (demo)")


def run_suite() -> List[Tuple[str, bool, str]]:
    fx = Fixture()
    fx.setup()
    try:
        cases: List[Callable[[Fixture], Tuple[str, bool, str]]] = [
            case_contract,
            case_quality,
            case_security,
        ]
        results = [c(fx) for c in cases]
        return results
    finally:
        fx.teardown()


def main() -> int:
    ap = argparse.ArgumentParser(description="Minimal test runner")
    ap.add_argument("--out", default="tools/reports/test_runner.md")
    args = ap.parse_args()

    results = run_suite()
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    verdict = "PASS" if passed == total else "FAIL"
    lines = [f"- {name}: {'OK' if ok else 'NOT OK'} ({desc})" for name, ok, desc in results]
    report = [
        "# Test Runner Report",
        f"Generated: {now}",
        f"Verdict: {verdict}",
        "",
        "## Results",
        "\n".join(lines),
        "",
        "## Recommendations",
        "(no recommendations)" if verdict == "PASS" else "Investigate failing cases",
    ]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
