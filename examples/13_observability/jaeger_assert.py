#!/usr/bin/env python3
"""
jaeger_assert.py: Minimal assertion against Jaeger Query API.

Checks that at least N traces exist for a service (and optional operation)
within a lookback window. Uses Jaeger /api/traces endpoint.

Usage:
  python jaeger_assert.py --base http://localhost:16686 --service demo --operation '*' --lookback 1h --limit 5 --min-count 1

Exit codes: 0 pass, 2 fail, 3 error
"""
import argparse, sys, json, urllib.parse, urllib.request

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://localhost:16686', help='Jaeger UI base URL')
    ap.add_argument('--service', required=True)
    ap.add_argument('--operation', default='')
    ap.add_argument('--lookback', default='1h', help='Jaeger lookback (e.g., 1h, 2m)')
    ap.add_argument('--limit', type=int, default=20)
    ap.add_argument('--min-count', type=int, default=1)
    args = ap.parse_args()

    params = {
        'service': args.service,
        'lookback': args.lookback,
        'limit': str(args.limit),
    }
    if args.operation:
        params['operation'] = args.operation
    url = f"{args.base.rstrip('/')}/api/traces?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"ERROR: request failed: {e}", file=sys.stderr)
        return 3

    traces = data.get('data', [])
    count = len(traces)
    print(f"Found {count} traces for service={args.service} operation={args.operation or '*'} lookback={args.lookback}")
    if count >= args.min_count:
        return 0
    else:
        print(f"Assertion failed: expected at least {args.min_count} traces", file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
