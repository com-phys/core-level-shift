#!/bin/bash
set -euo pipefail

ROOT='/Users/behnamazizi/Downloads/core level shifts'
CROSS_OUTPUT="$ROOT/cross/output/cross.scf.out"
STATUS="$ROOT/batch_status.txt"

printf 'Waiting for active cross SCF: %s\n' "$(date)" > "$STATUS"
while ! grep -q 'JOB DONE.' "$CROSS_OUTPUT" 2>/dev/null; do
  if ! pgrep -f '/opt/homebrew/bin/pw.x -in.*/cross/input/cross.scf.in' >/dev/null; then
    printf 'cross SCF stopped before JOB DONE: %s\n' "$(date)" >> "$STATUS"
    exit 1
  fi
  sleep 30
done

printf 'cross SCF complete; starting post-processing and remaining structures: %s\n' "$(date)" >> "$STATUS"
"$ROOT/script/run_remaining_cls.sh" cross twistedH2 twistedO2 TWco TWDCOH >> "$ROOT/batch_calculations.log" 2>&1
printf 'All five calculations and analyses complete: %s\n' "$(date)" >> "$STATUS"
