from pathlib import Path
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'structure' / 'PLDC.xyz'
DEST = ROOT / 'structure' / 'PLDC_COOH.xyz'
OH_BOND_A = 0.98

lines = SOURCE.read_text().splitlines()
atoms = []
for line in lines[2:]:
    fields = line.split()
    atoms.append((fields[0], np.array([float(v) for v in fields[1:4]])))

# One proton per carboxyl group. The longer C-O bond is selected as C-OH:
# bottom group C76-O78; top group C79-O80. Atom indices refer to PLDC.xyz.
protonation_pairs = [(76, 78), (79, 80)]
new_hydrogens = []
for carbon_index, oxygen_index in protonation_pairs:
    carbon = atoms[carbon_index - 1][1]
    oxygen = atoms[oxygen_index - 1][1]
    direction = oxygen - carbon
    direction /= np.linalg.norm(direction)
    new_hydrogens.append(oxygen + OH_BOND_A * direction)

output = [str(len(atoms) + len(new_hydrogens)),
          'PLDC protonated as two COOH groups; H82 on O78 and H83 on O80; O-H = 0.98 A']
for element, r in atoms:
    output.append(f'{element:<2s} {r[0]:14.8f} {r[1]:14.8f} {r[2]:14.8f}')
for r in new_hydrogens:
    output.append(f'H  {r[0]:14.8f} {r[1]:14.8f} {r[2]:14.8f}')

DEST.write_text('\n'.join(output) + '\n')
print(DEST)
for new_index, ((_, oxygen_index), r) in enumerate(zip(protonation_pairs, new_hydrogens), start=82):
    print(f'H{new_index} bonded to O{oxygen_index}: {r[0]:.6f} {r[1]:.6f} {r[2]:.6f}')
