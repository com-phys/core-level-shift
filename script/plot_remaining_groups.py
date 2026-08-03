#!/usr/bin/env python3
"""Plot atom-indexed carbon and nitrogen group assignments."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


ROOT = Path('/Users/behnamazizi/Downloads/core level shifts')
PROJECTS = ('cross', 'twistedH2', 'twistedO2', 'TWco', 'TWDCOH')
COLORS = {
    'C_L_alpha': '#1565C0', 'C_alpha': '#56B4E9',
    'C_L_beta': '#C62828', 'C_beta': '#E76F9A',
    'C_M': '#7B2CBF', 'C_b': '#2E7D32', 'C_w': '#E69F00',
    'C_COOH': '#795548', 'N_L': '#8E244D', 'N': '#173F5F',
}
LABELS = {
    'C_L_alpha': r'$C_{L,\alpha}$', 'C_alpha': r'$C_{\alpha}$',
    'C_L_beta': r'$C_{L,\beta}$', 'C_beta': r'$C_{\beta}$',
    'C_M': r'$C_M$', 'C_b': r'$C_b$', 'C_w': r'$C_w$',
    'C_COOH': r'$C_{COOH}$', 'N_L': r'$N_L$', 'N': r'$N$',
}
CUTOFFS = {
    frozenset(('C', 'C')): 1.79, frozenset(('C', 'N')): 1.80,
    frozenset(('C', 'H')): 1.25, frozenset(('C', 'O')): 1.86,
    frozenset(('N', 'O')): 1.55, frozenset(('O', 'H')): 1.25,
    frozenset(('Zn', 'N')): 2.30,
}


def read_xyz(path):
    atoms = []
    for i, line in enumerate(path.read_text().splitlines()[2:], 1):
        f = line.split()
        if len(f) >= 4:
            atoms.append((i, f[0], np.array([float(v) for v in f[1:4]])))
    return atoms


def draw(project):
    folder = ROOT / project
    atoms = read_xyz(folder / 'structure' / f'{project}.xyz')
    with (folder / 'structure' / 'group_assignments.csv').open() as handle:
        assignment = {int(r['atom_index']): r['group'] for r in csv.DictReader(handle)}

    fig, ax = plt.subplots(figsize=(13.4, 10.3), constrained_layout=True)
    for a, (idx_i, e_i, r_i) in enumerate(atoms):
        for idx_j, e_j, r_j in atoms[a + 1:]:
            cutoff = CUTOFFS.get(frozenset((e_i, e_j)))
            if cutoff and np.linalg.norm(r_i - r_j) <= cutoff:
                ax.plot([r_i[0], r_j[0]], [r_i[1], r_j[1]], color='#8A8A8A', lw=1.5, zorder=1)

    styles = {'H': ('#B7DDE2', 42), 'O': ('#D1495B', 185), 'Zn': ('#8AB17D', 390)}
    for idx, element, r in atoms:
        if element in {'C', 'N'}:
            group = assignment[idx]
            size = 250 if element == 'C' else 210
            ax.scatter(r[0], r[1], s=size, c=COLORS[group], edgecolors='white', linewidths=1.1, zorder=4)
            ax.text(r[0], r[1], str(idx), ha='center', va='center', color='white', fontsize=7.2, fontweight='bold', zorder=5)
        else:
            color, size = styles[element]
            ax.scatter(r[0], r[1], s=size, c=color, edgecolors='white', linewidths=1.0, zorder=3)
            if element in {'O', 'Zn'}:
                text = 'Zn' if element == 'Zn' else f'O{idx}'
                if element == 'O' and any(np.linalg.norm(r-rn) < 1.56 for _j, en, rn in atoms if en == 'N'):
                    dx = 9 if r[0] >= 0 else -9
                    ax.annotate(text, (r[0], r[1]), xytext=(dx, 9), textcoords='offset points',
                                ha='left' if dx > 0 else 'right', va='bottom', color='#B3263E',
                                fontsize=7.2, fontweight='bold', zorder=7)
                else:
                    ax.text(r[0], r[1], text, ha='center', va='center', color='white', fontsize=7.0, fontweight='bold', zorder=4)

    order = ['C_L_alpha', 'C_alpha', 'C_L_beta', 'C_beta', 'C_M', 'C_b', 'C_w', 'C_COOH', 'N_L', 'N']
    groups = []
    for name in order:
        ids = sorted(i for i, g in assignment.items() if g == name)
        if ids:
            groups.append((name, ids))
    handles = [
        Line2D([0], [0], marker='o', linestyle='', markersize=9,
               markerfacecolor=COLORS[name], markeredgecolor='white',
               label=f'{LABELS[name]}: ' + ', '.join(map(str, ids)))
        for name, ids in groups
    ]
    legend = ax.legend(handles=handles, title='Core-level groups and XYZ atom indices',
                       loc='upper left', bbox_to_anchor=(1.005, 0.98), frameon=True,
                       borderpad=0.8, labelspacing=0.65, fontsize=9.5, title_fontsize=10.5)
    legend.get_frame().set_edgecolor('#D0D5DB')
    ax.set_title(f'{project}: C and N core-level group assignment', fontsize=19, fontweight='bold', pad=14)
    ax.set_aspect('equal')
    xy = np.array([r[:2] for _i, _e, r in atoms])
    margin = 1.6
    ax.set_xlim(xy[:, 0].min() - margin, xy[:, 0].max() + margin)
    ax.set_ylim(xy[:, 1].min() - margin, xy[:, 1].max() + margin)
    ax.axis('off')
    out = folder / 'figures' / f'{project}_group_assignments'
    fig.savefig(out.with_suffix('.png'), dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(out.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(out.with_suffix('.png'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('projects', nargs='*', choices=PROJECTS)
    args = parser.parse_args()
    for project in args.projects or PROJECTS:
        draw(project)


if __name__ == '__main__':
    main()
