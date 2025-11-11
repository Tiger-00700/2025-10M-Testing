#!/usr/bin/env bash
set -euo pipefail
echo "examples/07_batch: running batch demo"

OUT_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t batch_demo)
echo "creating sample input"
cat > "$OUT_DIR/sample_input.csv" <<'CSV'
id,amount
1,10
2,15
3,7
4,20
CSV

echo "processing: summing amounts"
awk -F, 'NR>1{sum+=$2} END{print "total,"sum}' "$OUT_DIR/sample_input.csv" > "$OUT_DIR/result.csv"

echo "result:" && cat "$OUT_DIR/result.csv"
echo "wrote outputs to $OUT_DIR"
exit 0
