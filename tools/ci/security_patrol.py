"""Security patrol (Chapter 16 exercise): AuthN/AuthZ/Audit/Masking.

Usage:
  python tools/ci/security_patrol.py --authn yes --authz yes --audit 3 --masking yes --out tools/reports/security_patrol.md

Notes:
  - Demo flags simulate checks; integrate with real IdP/logs/policy later.
"""
from __future__ import annotations

import argparse
import pathlib
import datetime as dt


def check(authn: bool, authz: bool, audit_events: int, masking: bool):
    results = []
    results.append(("Authentication", authn, "MFA/short-lived creds enabled"))
    results.append(("Authorization", authz, "Least privilege + temporary elevation"))
    results.append(("Audit", audit_events >= 1, f"events={audit_events} (non-repudiation)"))
    results.append(("Masking", masking, "PII/PHI masked or tokenized"))
    verdict = "PASS" if all(ok for _, ok, _ in results) else "FAIL"
    lines = [f"- {name}: {'OK' if ok else 'NOT OK'} ({desc})" for name, ok, desc in results]
    recommendations = []
    if not authn:
        recommendations.append("Enable MFA and rotate service accounts")
    if not authz:
        recommendations.append("Enforce least privilege; add ABAC/RBAC reviews")
    if audit_events < 1:
        recommendations.append("Ensure audit pipeline writes immutable logs")
    if not masking:
        recommendations.append("Apply masking/tokenization for sensitive fields")
    return verdict, "\n".join(lines), ("\n".join(recommendations) or "(no recommendations)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Security patrol demo")
    ap.add_argument("--authn", choices=["yes", "no"], default="yes")
    ap.add_argument("--authz", choices=["yes", "no"], default="yes")
    ap.add_argument("--audit", type=int, default=3)
    ap.add_argument("--masking", choices=["yes", "no"], default="yes")
    ap.add_argument("--out", default="tools/reports/security_patrol.md")
    args = ap.parse_args()

    verdict, details, recs = check(
        authn=args.authn == "yes",
        authz=args.authz == "yes",
        audit_events=args.audit,
        masking=args.masking == "yes",
    )
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = [
        "# Security Patrol Report",
        f"Generated: {now}",
        f"Verdict: {verdict}",
        "",
        "## Checks",
        details,
        "",
        "## Recommendations",
        recs,
    ]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
