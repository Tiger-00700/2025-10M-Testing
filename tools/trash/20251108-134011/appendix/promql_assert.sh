#!/usr/bin/env sh
set -eu

# promql_assert.sh: Assert Prometheus query result against a threshold.
#
# Env:
#   PROM_URL  Base URL of Prometheus (e.g., http://localhost:9090)
# Args:
#   1: QUERY (PromQL)
#   2: OP (gt|ge|lt|le|eq|ne) [default: gt]
#   3: THRESHOLD (number)
#
# Exit codes: 0 pass, 2 fail, 3 error

error() { echo "[promql_assert] ERROR: $*" >&2; }
info()  { echo "[promql_assert] $*"; }

PROM_URL=${PROM_URL:-}
QUERY=${1:-}
OP=${2:-gt}
THRESHOLD=${3:-}

if [ -z "$PROM_URL" ] || [ -z "$QUERY" ] || [ -z "$THRESHOLD" ]; then
  echo "Usage: PROM_URL=<prometheus_url> $0 <query> [op] <threshold>" >&2
  echo "  op: gt|ge|lt|le|eq|ne (default gt)" >&2
  exit 3
fi

# URL-encode query (basic)
urlencode() {
  # shellcheck disable=SC2018,SC2019
  printf '%s' "$1" | od -An -tx1 | tr ' ' '\n' | while read -r c; do
    case "$c" in
      2d|5f|2e|7e|2a|27|28|29|2f|3a|40|2b|27|2c|3b|3d|26|3f|25) printf '%%%s' "$c";; # reserved will remain encoded
      0a|0d|'') ;;
      *) printf '%%%s' "$c" ;;
    esac
  done
}

ENCQ=$(urlencode "$QUERY")
URL="$PROM_URL/api/v1/query?query=$ENCQ"

RAW=$(curl -sS --fail "$URL") || { error "curl failed for $URL"; exit 3; }

# Try to parse using jq, else Python, else naive.
parse_values_jq() {
  echo "$RAW" | jq -r '.data.result[].value[1]' 2>/dev/null || return 1
}

parse_values_py() {
  python - "$RAW" <<'PY'
import sys, json
try:
    data=json.loads(sys.stdin.read())
    for r in data.get('data',{}).get('result',[]):
        print(r.get('value',[None,''])[1])
except Exception:
    sys.exit(1)
PY
}

parse_values_naive() {
  # Very naive: look for "value":[<ts>,"<val>"]
  echo "$RAW" | sed -n 's/.*\"value\"\s*:\s*\[[^]]*,\s*\"\([0-9.eE+-]\+\)\".*/\1/p'
}

VALUES=$(parse_values_jq || parse_values_py || parse_values_naive)
if [ -z "$VALUES" ]; then
  error "could not parse numeric values from response"
  exit 3
fi

pass=true
reason=""

cmp() {
  a=$1; b=$2; op=$3
  awk -v a="$a" -v b="$b" -v op="$op" 'BEGIN {
    if (op=="gt") exit !(a>b);
    if (op=="ge") exit !(a>=b);
    if (op=="lt") exit !(a<b);
    if (op=="le") exit !(a<=b);
    if (op=="eq") exit !(a==b);
    if (op=="ne") exit !(a!=b);
    exit 2;
  }'
}

count=0
failcount=0
echo "$VALUES" | while IFS= read -r v; do
  [ -z "$v" ] && continue
  count=$((count+1))
  if cmp "$v" "$THRESHOLD" "$OP"; then
    info "value=$v op=$OP threshold=$THRESHOLD => PASS"
  else
    info "value=$v op=$OP threshold=$THRESHOLD => FAIL"
    failcount=$((failcount+1))
  fi
done

# The above loop in sh runs in a subshell; compute status by re-evaluating quickly
FAILS=$(echo "$VALUES" | awk -v t="$THRESHOLD" -v op="$OP" '{
  v=$1; ok=0;
  if (op=="gt") ok=(v>t);
  else if (op=="ge") ok=(v>=t);
  else if (op=="lt") ok=(v<t);
  else if (op=="le") ok=(v<=t);
  else if (op=="eq") ok=(v==t);
  else if (op=="ne") ok=(v!=t);
  if (!ok) print v;
}')

if [ -n "$FAILS" ]; then
  error "assertion failed for some series: $(echo "$FAILS" | tr '\n' ' ')"
  exit 2
fi
info "assertion passed for all $(echo "$VALUES" | wc -l | tr -d ' ') series"
exit 0
