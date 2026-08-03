#!/bin/bash
set -euo pipefail

ROOT='/Users/behnamazizi/Downloads/core level shifts'
PW='/opt/homebrew/bin/pw.x'
INITIAL_STATE='/opt/homebrew/bin/initial_state.x'
MPI='/opt/homebrew/bin/mpirun'
NPROC=4

if [ "$#" -gt 0 ]; then
  projects=("$@")
else
  projects=(cross twistedH2 twistedO2 TWco TWDCOH)
fi

for project in "${projects[@]}"; do
  folder="$ROOT/$project"
  scf_input="$folder/input/$project.scf.in"
  scf_output="$folder/output/$project.scf.out"
  is_input="$folder/input/$project.istate.in"
  is_output="$folder/output/$project.istate.out"

  if ! grep -q 'JOB DONE.' "$scf_output" 2>/dev/null; then
    env OMP_NUM_THREADS=1 "$MPI" -np "$NPROC" "$PW" -in "$scf_input" | tee "$scf_output"
  fi
  grep -q 'convergence has been achieved' "$scf_output"
  grep -q 'JOB DONE.' "$scf_output"

  if ! grep -q 'JOB DONE.' "$is_output" 2>/dev/null; then
    env OMP_NUM_THREADS=1 "$MPI" -np "$NPROC" "$INITIAL_STATE" -in "$is_input" | tee "$is_output"
  fi
  grep -q 'JOB DONE.' "$is_output"

  python3 "$ROOT/script/analyze_remaining_cls.py" "$project"
done
