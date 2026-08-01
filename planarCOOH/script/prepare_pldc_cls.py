from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
XYZ = ROOT / "structure" / "PLDC.xyz"
SCF_INPUT = ROOT / "archive" / "targeted_trial" / "pldc_targeted.scf.in"
ISTATE_INPUT = ROOT / "archive" / "targeted_trial" / "pldc_targeted_CN.istate.in"
PSEUDO = ROOT.parent / "pseudopotential"
SCRATCH = ROOT / "output" / "targeted_restart_data"

TARGET_C = {
    2, 3, 4, 5, 6, 13, 14, 15, 16, 17, 18, 19,
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    32, 33, 34, 35, 42, 43, 44, 45,
}

atoms = []
for line in XYZ.read_text().splitlines()[2:]:
    fields = line.split()
    if len(fields) >= 4:
        atoms.append((fields[0], *[float(value) for value in fields[1:4]]))

positions = []
for atom_index, (element, x, y, z) in enumerate(atoms, start=1):
    label = element
    if element == "C" and atom_index not in TARGET_C:
        label = "Cx"  # 12 Cw plus two COOH carbons: normal, not excited
    positions.append(f"{label:<3s} {x:16.8f} {y:16.8f} {z:16.8f}")

SCF_INPUT.write_text(f"""&CONTROL
  calculation  = 'scf'
  restart_mode = 'from_scratch'
  prefix       = 'pldc_targeted'
  pseudo_dir   = '{PSEUDO}'
  outdir       = '{SCRATCH}'
  disk_io      = 'low'
/
&SYSTEM
  ibrav        = 1
  A            = 25.0
  nat          = {len(atoms)}
  ntyp         = 8
  tot_charge   = -2.0
  ecutwfc      = 30.0
  ecutrho      = 180.0
  occupations  = 'smearing'
  smearing     = 'mv'
  degauss      = 0.02
  input_dft    = 'PBE'
  assume_isolated = 'mt'
  nosym        = .true.
  noinv        = .true.
/
&ELECTRONS
  conv_thr         = 1.0d-6
  mixing_mode      = 'local-TF'
  mixing_beta      = 0.05
  mixing_ndim      = 20
  electron_maxstep = 300
  diagonalization  = 'david'
  diago_thr_init   = 1.0d-5
/
ATOMIC_SPECIES
Zn  65.3800  Zn.pbe-van.UPF
C   12.0110  C.pbe-rrkjus.UPF
N   14.0070  N.pbe-van_ak.UPF
H    1.0080  H.pbe-rrkjus.UPF
O   15.9990  O.pbe-rrkjus.UPF
Cs  12.0110  C.star1s-pbe-rrkjus.UPF
Ns  14.0070  N.star1s-pbe-van.UPF
Cx  12.0110  C.pbe-rrkjus.UPF
ATOMIC_POSITIONS angstrom
{"\n".join(positions)}
K_POINTS gamma
""")

ISTATE_INPUT.write_text(f"""&INPUTPP
  prefix    = 'pldc_targeted'
  outdir    = '{SCRATCH}'
  excite(2) = 6   ! selected porphyrin C atoms only
  excite(3) = 7   ! all N atoms
/
""")

excluded = [i for i, (element, *_xyz) in enumerate(atoms, 1) if element == "C" and i not in TARGET_C]
print(f"Wrote {SCF_INPUT}")
print(f"Wrote {ISTATE_INPUT}")
print(f"Unexcited carbon atoms: {excluded}")
