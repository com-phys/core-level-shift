from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
XYZ = PROJECT / 'structure' / 'PLDC_COOH.xyz'
SCF_INPUT = PROJECT / 'input' / 'pldc_cooh_allC.scf.in'
ISTATE_INPUT = PROJECT / 'input' / 'pldc_cooh_allC.istate.in'
SCRATCH = PROJECT / 'output' / 'restart_data'
PSEUDO = PROJECT.parent / 'pseudopotential'

atoms = []
for line in XYZ.read_text().splitlines()[2:]:
    fields = line.split()
    if len(fields) >= 4:
        atoms.append((fields[0], *[float(v) for v in fields[1:4]]))

counts = {element: sum(a[0] == element for a in atoms) for element in {'Zn', 'C', 'N', 'H', 'O'}}
assert len(atoms) == 83, len(atoms)
assert counts == {'Zn': 1, 'C': 46, 'N': 4, 'H': 28, 'O': 4}, counts

positions = '\n'.join(
    f'{element:<3s} {x:16.8f} {y:16.8f} {z:16.8f}'
    for element, x, y, z in atoms
)

SCF_INPUT.write_text(f'''&CONTROL
  calculation  = 'scf'
  restart_mode = 'from_scratch'
  prefix       = 'pldc_cooh_allC'
  pseudo_dir   = '{PSEUDO}'
  outdir       = '{SCRATCH}'
  disk_io      = 'low'
/
&SYSTEM
  ibrav        = 1
  A            = 25.0
  nat          = {len(atoms)}
  ntyp         = 6
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
  mixing_beta      = 0.20
  mixing_ndim      = 20
  electron_maxstep = 300
  diagonalization  = 'david'
/
ATOMIC_SPECIES
Zn  65.3800  Zn.pbe-van.UPF
C   12.0110  C.pbe-rrkjus.UPF
N   14.0070  N.pbe-van_ak.UPF
H    1.0080  H.pbe-rrkjus.UPF
O   15.9990  O.pbe-rrkjus.UPF
Cs  12.0110  C.star1s-pbe-rrkjus.UPF
ATOMIC_POSITIONS angstrom
{positions}
K_POINTS gamma
''')

ISTATE_INPUT.write_text(f'''&INPUTPP
  prefix    = 'pldc_cooh_allC'
  outdir    = '{SCRATCH}'
  excite(2) = 6   ! all 46 carbon atoms
/
''')

print(SCF_INPUT)
print(ISTATE_INPUT)
print(f'Atoms: {counts}; neutral closed-shell electron count expected')
