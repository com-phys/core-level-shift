#!/usr/bin/env python3
"""Extract and compare Planar and PLDC-COOH N 1s initial-state shifts."""

from pathlib import Path
import csv
import re

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
PLANAR = ROOT / 'planar'
PLDC = ROOT / 'planarCOOH'
FWHM = 0.35
GROUPS = {'N_L': {46, 49}, 'N': {47, 48}}
COLORS = {'N_L': '#8E244D', 'N': '#173F5F'}
LABELS = {'N_L': r'$N_L$', 'N': r'$N$'}


def read_planar():
    path = PLANAR / 'output' / 'planar_targeted_C_N_atom_shifts.csv'
    with path.open() as handle:
        return [
            {'atom_index': int(row['atom_index']), 'group': row['group'],
             'is_contribution_eV': float(row['is_contribution_eV']),
             'cls_eV': float(row['cls_eV'])}
            for row in csv.DictReader(handle) if row['element'] == 'N'
        ]


def read_pldc():
    path = PLDC / 'output' / 'pldc_cooh_N.istate.out'
    text = path.read_text(errors='replace')
    if 'JOB DONE.' not in text:
        raise RuntimeError('PLDC-COOH N initial_state output is incomplete')
    pattern = re.compile(
        r'atom\s+(46|47|48|49)\s+type\s+\d+\s+shift\s*=\s*[-+0-9.Ee]+\s+Ry,\s*=\s*([-+0-9.Ee]+)\s+eV'
    )
    values = {}
    for match in pattern.finditer(text):
        values.setdefault(int(match.group(1)), float(match.group(2)))
    if set(values) != {46, 47, 48, 49}:
        raise RuntimeError(f'Missing PLDC N atoms: {sorted({46,47,48,49} - set(values))}')
    reference = float(np.mean(list(values.values())))
    rows = []
    for index in sorted(values):
        group = next(group for group, indices in GROUPS.items() if index in indices)
        rows.append({
            'atom_index': index, 'element': 'N', 'group': group,
            'is_contribution_eV': values[index], 'reference': 'mean(all N)',
            'reference_eV': reference, 'cls_eV': reference - values[index],
        })
    with (PLDC / 'output' / 'pldc_cooh_N_atom_shifts.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    return rows


def gaussian(x, centers):
    sigma = FWHM / (2 * np.sqrt(2 * np.log(2)))
    y = np.zeros_like(x)
    for center in centers:
        y += np.exp(-0.5 * ((x - center) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
    return y


def add_structure_inset(ax, path, bounds, crop_right):
    image = plt.imread(path)
    h, w = image.shape[:2]
    crop = image[int(0.07 * h):int(0.98 * h), :int(crop_right * w)]
    mask = np.any(crop[..., :3] < 0.965, axis=2)
    if np.any(mask):
        ys, xs = np.where(mask)
        crop = crop[max(0, ys.min()-20):min(crop.shape[0], ys.max()+20),
                    max(0, xs.min()-20):min(crop.shape[1], xs.max()+20)]
    inset = ax.inset_axes(bounds, zorder=10)
    inset.imshow(crop)
    inset.set_xticks([])
    inset.set_yticks([])
    inset.set_facecolor((1, 1, 1, 0.94))
    for spine in inset.spines.values():
        spine.set_color('#AAB2BD')
        spine.set_linewidth(0.8)


planar = read_planar()
pldc = read_pldc()
all_values = [row['cls_eV'] for row in planar + pldc]
x = np.linspace(min(all_values) - 0.65, max(all_values) + 0.65, 2600)

fig, axes = plt.subplots(2, 1, figsize=(9.4, 7.2), sharex=True, constrained_layout=True)
systems = [
    ('Planar', planar, PLANAR / 'figures' / 'Planar_carbon_groups.png', 0.64),
    ('PLDC-COOH', pldc, PLDC / 'figures' / 'PLDC_COOH_carbon_groups.png', 0.68),
]
summary = []
for ax, (name, rows, structure, crop_right) in zip(axes, systems):
    curves = {
        group: gaussian(x, [row['cls_eV'] for row in rows if row['group'] == group])
        for group in ('N_L', 'N')
    }
    scale = max(float(sum(curves.values()).max()), 1e-12)
    for group in ('N_L', 'N'):
        ax.plot(x, curves[group] / scale, color=COLORS[group], lw=2.5, label=LABELS[group])
        ax.fill_between(x, curves[group] / scale, color=COLORS[group], alpha=0.10)
        values = np.array([row['cls_eV'] for row in rows if row['group'] == group])
        summary.append({'structure': name, 'group': group, 'multiplicity': len(values),
                        'mean_cls_eV': values.mean(), 'std_cls_eV': values.std(),
                        'min_cls_eV': values.min(), 'max_cls_eV': values.max()})
    separation = abs(np.mean([r['cls_eV'] for r in rows if r['group'] == 'N_L']) -
                     np.mean([r['cls_eV'] for r in rows if r['group'] == 'N']))
    bounds = [0.42, 0.40, 0.18, 0.52] if separation > 0.45 else [0.035, 0.45, 0.22, 0.48]
    add_structure_inset(ax, structure, bounds, crop_right)
    ax.set_title(name, loc='left', fontweight='bold')
    ax.set_ylabel('Relative intensity')
    ax.set_ylim(-0.02, 1.08)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc='upper right')

axes[-1].set_xlabel('N 1s core-level shift relative to mean(all N) (eV)')
fig.suptitle(f'Planar and PLDC-COOH N 1s initial-state CLS (Gaussian FWHM {FWHM:.2f} eV)',
             fontweight='bold')
out = PLDC / 'figures' / 'planar_vs_PLDC_COOH_N1s_envelopes'
fig.savefig(out.with_suffix('.png'), dpi=300, bbox_inches='tight')
fig.savefig(out.with_suffix('.pdf'), bbox_inches='tight')
plt.close(fig)

with (PLDC / 'output' / 'planar_vs_PLDC_COOH_N_group_summary.csv').open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=summary[0])
    writer.writeheader()
    writer.writerows(summary)

print(out.with_suffix('.pdf'))
for row in summary:
    print(row)

