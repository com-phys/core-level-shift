#!/usr/bin/env python3
"""Prepare a PLDC-COOH SCF/initial_state pair for all four nitrogen atoms."""

from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
BASE = PROJECT / 'input' / 'pldc_cooh_allC.scf.in'
SCF = PROJECT / 'input' / 'pldc_cooh_N.scf.in'
ISTATE = PROJECT / 'input' / 'pldc_cooh_N.istate.in'
SCRATCH = PROJECT / 'output' / 'restart_data'

text = BASE.read_text()
text = text.replace("prefix       = 'pldc_cooh_allC'", "prefix       = 'pldc_cooh_N'")
text = text.replace('ntyp         = 6', 'ntyp         = 7')
text = text.replace(
    'Cs  12.0110  C.star1s-pbe-rrkjus.UPF\n',
    'Cs  12.0110  C.star1s-pbe-rrkjus.UPF\nNs  14.0070  N.star1s-pbe-van.UPF\n',
)
text = text.replace(
    "  diagonalization  = 'david'\n",
    "  diagonalization  = 'david'\n  startingpot      = 'file'\n  startingwfc      = 'file'\n",
)
SCF.write_text(text)

ISTATE.write_text(f"""&INPUTPP
  prefix    = 'pldc_cooh_N'
  outdir    = '{SCRATCH}'
  excite(3) = 7   ! all four N atoms; normal N -> N.star1s
/
""")

print(SCF)
print(ISTATE)

