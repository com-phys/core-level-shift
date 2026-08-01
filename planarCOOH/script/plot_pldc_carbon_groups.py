from pathlib import Path
import csv

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
XYZ = ROOT / 'structure' / 'PLDC_COOH.xyz'
OUT = ROOT / 'figures' / 'PLDC_COOH_carbon_groups'

GROUPS = {
    r'$C_{L,\alpha}$': [4, 5, 42, 43],
    r'$C_{\alpha}$': [20, 21, 26, 27],
    r'$C_{L,\beta}$': [2, 3, 44, 45],
    r'$C_{\beta}$': [22, 23, 24, 25],
    r'$C_M$': [6, 13, 28, 35],
    r'$C_b$': [14, 15, 16, 17, 18, 19, 29, 30, 31, 32, 33, 34],
    r'$C_w$': [7, 8, 9, 10, 11, 12, 36, 37, 38, 39, 40, 41],
    r'$C_{COO}$ (added)': [76, 79],
}

COLORS = {
    r'$C_{L,\alpha}$': '#1565C0',
    r'$C_{\alpha}$': '#56B4E9',
    r'$C_{L,\beta}$': '#C62828',
    r'$C_{\beta}$': '#E76F9A',
    r'$C_M$': '#7B2CBF',
    r'$C_b$': '#2E7D32',
    r'$C_w$': '#E69F00',
    r'$C_{COO}$ (added)': '#795548',
}

CUTOFFS = {
    frozenset(('C', 'C')): 1.78,
    frozenset(('C', 'N')): 1.78,
    frozenset(('C', 'H')): 1.25,
    frozenset(('C', 'O')): 1.85,
    frozenset(('O', 'H')): 1.25,
    frozenset(('Zn', 'N')): 2.30,
}


def read_xyz(path):
    atoms = []
    for atom_index, line in enumerate(path.read_text().splitlines()[2:], start=1):
        fields = line.split()
        if len(fields) >= 4:
            atoms.append((atom_index, fields[0], np.array([float(x) for x in fields[1:4]])))
    return atoms


def find_bonds(atoms):
    links = []
    for i, (_, element_i, ri) in enumerate(atoms):
        for j in range(i + 1, len(atoms)):
            _, element_j, rj = atoms[j]
            cutoff = CUTOFFS.get(frozenset((element_i, element_j)))
            if cutoff and np.linalg.norm(ri - rj) <= cutoff:
                links.append((i, j))
    return links


def group_for(atom_index):
    for name, indices in GROUPS.items():
        if atom_index in indices:
            return name
    return None


atoms = read_xyz(XYZ)
carbon_indices = {idx for idx, element, _ in atoms if element == 'C'}
assigned_indices = {idx for indices in GROUPS.values() for idx in indices}
if carbon_indices != assigned_indices:
    raise ValueError(f'Carbon assignment mismatch: missing={carbon_indices-assigned_indices}, extra={assigned_indices-carbon_indices}')

fig, ax = plt.subplots(figsize=(13.2, 10.5), constrained_layout=True)

for i, j in find_bonds(atoms):
    ri, rj = atoms[i][2], atoms[j][2]
    ax.plot([ri[0], rj[0]], [ri[1], rj[1]], color='#8A8A8A', lw=1.55, zorder=1)

# Draw non-carbon atoms first.
element_style = {
    'H': ('#B7DDE2', 42, '#FFFFFF'),
    'N': ('#173F5F', 180, '#FFFFFF'),
    'O': ('#D1495B', 190, '#FFFFFF'),
    'Zn': ('#8AB17D', 390, '#FFFFFF'),
}
for idx, element, r in atoms:
    if element == 'C':
        continue
    color, size, edge = element_style[element]
    if element == 'H' and idx in {82, 83}:
        color, size, edge = '#27C7D8', 150, '#135D66'
    ax.scatter(r[0], r[1], s=size, c=color, edgecolors=edge, linewidths=1.0, zorder=3)
    if element in {'N', 'O', 'Zn'}:
        label = 'Zn' if element == 'Zn' else f'{element}{idx}'
        ax.text(r[0], r[1], label, ha='center', va='center', color='white',
                fontsize=7.4 if element != 'Zn' else 8.5, fontweight='bold', zorder=4)
    elif element == 'H' and idx in {82, 83}:
        ax.text(r[0], r[1], f'H{idx}', ha='center', va='center', color='#133A40',
                fontsize=7.0, fontweight='bold', zorder=4)

# Carbon color identifies the requested group; the printed number is the XYZ atom index.
for idx, element, r in atoms:
    if element != 'C':
        continue
    group = group_for(idx)
    ax.scatter(r[0], r[1], s=250, c=COLORS[group], edgecolors='white', linewidths=1.25, zorder=5)
    ax.text(r[0], r[1], str(idx), ha='center', va='center', color='white',
            fontsize=7.5, fontweight='bold', zorder=6)

handles = [
    Line2D([0], [0], marker='o', linestyle='', markersize=9.5,
           markerfacecolor=COLORS[name], markeredgecolor='white', label=f'{name}: ' + ', '.join(map(str, indices)))
    for name, indices in GROUPS.items()
]
legend = ax.legend(handles=handles, title='Carbon groups and XYZ atom indices',
                   loc='upper left', bbox_to_anchor=(1.005, 0.97), frameon=True,
                   borderpad=0.8, labelspacing=0.8, handletextpad=0.7, fontsize=10,
                   title_fontsize=11)
legend.get_frame().set_edgecolor('#D0D5DB')
legend.get_frame().set_linewidth(0.8)

ax.text(1.01, 0.25,
        'Other atoms\n'
        'N: dark blue\nO: red\nZn: green\nH: pale cyan\nadded O-H: bright cyan',
        transform=ax.transAxes, ha='left', va='top', fontsize=10,
        bbox=dict(boxstyle='round,pad=0.6', facecolor='#F5F7F9', edgecolor='#D0D5DB'))

ax.text(0.02, 0.02,
        r'Two COOH groups: H82 is bonded to O78 and H83 is bonded to O80 (O-H = 0.98 Å).',
        transform=ax.transAxes, ha='left', va='bottom', fontsize=9.3, color='#555555')

ax.set_title('Protonated PLDC (two COOH groups): carbon-group assignment', fontsize=20, fontweight='bold', pad=14)
ax.set_subtitle = None
ax.set_aspect('equal')
ax.set_xlim(-9.3, 9.3)
ax.set_ylim(-9.1, 9.25)
ax.axis('off')

fig.savefig(OUT.with_suffix('.png'), dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
with (ROOT / 'structure' / 'PLDC_C_group_assignments.csv').open('w', newline='') as handle:
    writer = csv.writer(handle)
    writer.writerow(['atom_index', 'element', 'carbon_group', 'x_A', 'y_A', 'z_A'])
    for idx, element, r in atoms:
        if element == 'C':
            writer.writerow([idx, element, group_for(idx).replace('$', ''), *r])
print(OUT.with_suffix('.png'))
print(OUT.with_suffix('.pdf'))
