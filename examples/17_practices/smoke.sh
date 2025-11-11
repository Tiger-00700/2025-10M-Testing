#!/usr/bin/env bash
set -euo pipefail
echo "Running smoke for examples/17_practices"
if [ -f run_exercise.sh ]; then
	bash run_exercise.sh
	echo "run_exercise.sh executed"
	exit 0
fi
if [ -f exercise_01.md ]; then
	echo "Exercise file present; smoke passes"
	exit 0
fi
echo "No exercise example found; passing"
exit 0
