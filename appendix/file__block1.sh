#!/usr/bin/env bash

# usage: promql_assert.sh "<promql>" "<operator> <value>" [prom_url]

PROMQL="$1"
PRED="$2"
URL="${3:-http://localhost:9090}"

if [ -z "${PROMQL}" ] || [ -z "${PRED}" ]; then
  echo "usage: promql_assert.sh \"<promql>\" \"<operator> <value>\" [prom_url]"
  exit 2
fi

RESULT=$(curl -s --get --data-urlencode "query=${PROMQL}" "${URL}/api/v1/query" | jq -r '.data.result | length')

# Example: ./promql_assert.sh 'up{job="myjob"}' '> 0'

if eval "[[ ${RESULT} ${PRED} ]]"; then
  echo "OK: ${PROMQL} -> ${RESULT}"
  exit 0
else
  echo "FAIL: ${PROMQL} -> ${RESULT}"
  exit 2
fi
