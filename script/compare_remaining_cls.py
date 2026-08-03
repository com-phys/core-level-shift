#!/usr/bin/env python3
"""Create shared comparison tables and spectra for the five new structures."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path('/Users/behnamazizi/Downloads/core level shifts')
PROJECTS = ('cross', 'twistedH2', 'twistedO2', 'TWco', 'TWDCOH')
OUT = ROOT / 'comparison_remaining'
OUT.mkdir(exist_ok=True)
FWHM = 0.35
ORDER = ('C_L_alpha', 'C_alpha', 'C_M', 'C_L_beta', 'C_beta', 'C_b', 'C_w', 'C_COOH')
COLORS = {
    'C_L_alpha': '#1565C0', 'C_alpha': '#56B4E9', 'C_M': '#7B2CBF',
    'C_L_beta': '#C62828', 'C_beta': '#E76F9A', 'C_b': '#2E7D32',
    'C_w': '#E69F00', 'C_COOH': '#795548',
}
LABELS = {
    'C_L_alpha': r'$C_{L,\alpha}$', 'C_alpha': r'$C_{\alpha}$',
    'C_M': r'$C_M$', 'C_L_beta': r'$C_{L,\beta}$',
    'C_beta': r'$C_{\beta}$', 'C_b': r'$C_b$', 'C_w': r'$C_w$',
    'C_COOH': r'$C_{COOH}$',
}


def envelope(x, centers):
    sigma = FWHM / (2 * np.sqrt(2 * np.log(2)))
    y = np.zeros_like(x)
    for center in centers:
        y += np.exp(-0.5 * ((x-center)/sigma)**2) / (sigma*np.sqrt(2*np.pi))
    return y


def add_structure_inset(ax, project, bounds):
    """Add a compact labeled-structure thumbnail to a comparison panel."""
    path = ROOT / project / 'figures' / f'{project}_group_assignments.png'
    image = plt.imread(path)
    h, w = image.shape[:2]
    crop = image[int(0.07 * h):int(0.98 * h), :int(0.72 * w)]
    mask = np.any(crop[..., :3] < 0.965, axis=2)
    if np.any(mask):
        ys, xs = np.where(mask)
        crop = crop[max(0, ys.min() - 16):min(crop.shape[0], ys.max() + 16),
                    max(0, xs.min() - 16):min(crop.shape[1], xs.max() + 16)]
    inset = ax.inset_axes(bounds, zorder=10)
    inset.imshow(crop)
    inset.set_xticks([])
    inset.set_yticks([])
    inset.set_facecolor((1, 1, 1, 0.94))
    for spine in inset.spines.values():
        spine.set_color('#AAB2BD')
        spine.set_linewidth(0.6)
    return inset


data = {}
combined = []
for project in PROJECTS:
    path = ROOT / project / 'output' / f'{project}_C_N_atom_shifts.csv'
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row['project'] = project
        row['cls_eV'] = float(row['cls_eV'])
    data[project] = rows
    combined.extend(rows)

fieldnames = ['project'] + [k for k in combined[0] if k != 'project']
with (OUT / 'remaining_structures_C_N_atom_shifts.csv').open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(combined)

common = [r['cls_eV'] for r in combined if r['element'] == 'C' and r['group'] != 'C_COOH']
x = np.linspace(min(common)-0.6, max(common)+0.6, 3200)
fig, axes = plt.subplots(len(PROJECTS), 1, figsize=(11.2, 12.8), sharex=True, constrained_layout=True)
for ax, project in zip(axes, PROJECTS):
    rows = [r for r in data[project] if r['element'] == 'C' and r['group'] != 'C_COOH']
    curves = {g: envelope(x, [r['cls_eV'] for r in rows if r['group'] == g]) for g in ORDER if any(r['group'] == g for r in rows)}
    blue = curves.get('C_L_alpha', 0) + curves.get('C_alpha', 0)
    other = sum((curves[g] for g in curves if g not in {'C_L_alpha', 'C_alpha'}), np.zeros_like(x))
    scale = max(float((blue+other).max()), 1e-12)
    ax.fill_between(x, blue/scale, color='#4E79A7', alpha=0.20, zorder=1)
    ax.fill_between(x, other/scale, color='#F28E2B', alpha=0.20, zorder=1)
    for group in ORDER:
        if group in curves:
            ax.plot(x, curves[group]/scale, color=COLORS[group], lw=1.55, zorder=3,
                    label=LABELS[group] if project == PROJECTS[0] else None)
    ax.text(0.01, 0.83, project, transform=ax.transAxes, fontweight='bold')
    add_structure_inset(ax, project, [0.825, 0.18, 0.155, 0.70])
    ax.set_ylim(0, 1.08)
    ax.spines[['top', 'right']].set_visible(False)
axes[-1].set_xlabel('C 1s shift relative to mean(Cb+Cw) (eV)')
fig.supylabel('Relative intensity')
axes[0].legend(frameon=False, ncol=7, fontsize=8, loc='upper center', bbox_to_anchor=(0.52, 1.35))
fig.suptitle(f'Common-carbon initial-state CLS comparison (Gaussian FWHM {FWHM:.2f} eV)', fontsize=14, fontweight='bold')
fig.savefig(OUT / 'remaining_structures_C1s_comparison.png', dpi=300, bbox_inches='tight')
fig.savefig(OUT / 'remaining_structures_C1s_comparison.pdf', bbox_inches='tight')
plt.close(fig)

fig, axes = plt.subplots(len(PROJECTS), 1, figsize=(9.2, 11.5), sharex=True, constrained_layout=True)
n_all = [r['cls_eV'] for r in combined if r['element'] == 'N']
nx = np.linspace(min(n_all)-0.6, max(n_all)+0.6, 2600)
for ax, project in zip(axes, PROJECTS):
    rows = [r for r in data[project] if r['element'] == 'N']
    curves = {g: envelope(nx, [r['cls_eV'] for r in rows if r['group'] == g]) for g in ('N_L', 'N')}
    scale = max(float(sum(curves.values()).max()), 1e-12)
    for group, color in [('N_L', '#8E244D'), ('N', '#173F5F')]:
        ax.plot(nx, curves[group]/scale, color=color, lw=2.2, label=group if project == PROJECTS[0] else None)
        ax.fill_between(nx, curves[group]/scale, color=color, alpha=0.10)
    ax.text(0.01, 0.82, project, transform=ax.transAxes, fontweight='bold')
    n_bounds = ([0.82, 0.19, 0.15, 0.68]
                if project in {'cross', 'twistedH2'}
                else [0.445, 0.17, 0.12, 0.70])
    add_structure_inset(ax, project, n_bounds)
    ax.set_ylim(0, 1.08)
    ax.spines[['top', 'right']].set_visible(False)
axes[-1].set_xlabel('N 1s shift relative to mean(all N) (eV)')
fig.supylabel('Relative intensity')
axes[0].legend(frameon=False, ncol=2)
fig.suptitle(f'N 1s initial-state CLS comparison (Gaussian FWHM {FWHM:.2f} eV)', fontsize=14, fontweight='bold')
fig.savefig(OUT / 'remaining_structures_N1s_comparison.png', dpi=300, bbox_inches='tight')
fig.savefig(OUT / 'remaining_structures_N1s_comparison.pdf', bbox_inches='tight')
plt.close(fig)

# Focused side-by-side comparison for the two twisted structures.
twisted = ('twistedH2', 'twistedO2')
fig, axes = plt.subplots(2, 1, figsize=(10.8, 6.8), sharex=True, constrained_layout=True)
for ax, project in zip(axes, twisted):
    rows = [r for r in data[project] if r['element'] == 'C' and r['group'] != 'C_COOH']
    curves = {
        g: envelope(x, [r['cls_eV'] for r in rows if r['group'] == g])
        for g in ORDER if any(r['group'] == g for r in rows)
    }
    blue = curves.get('C_L_alpha', 0) + curves.get('C_alpha', 0)
    other = sum((curves[g] for g in curves if g not in {'C_L_alpha', 'C_alpha'}), np.zeros_like(x))
    scale = max(float((blue + other).max()), 1e-12)
    ax.fill_between(x, blue / scale, color='#4E79A7', alpha=0.20, zorder=1,
                    label=r'$C_{L,\alpha}+C_\alpha$ envelope' if project == twisted[0] else None)
    ax.fill_between(x, other / scale, color='#F28E2B', alpha=0.20, zorder=1,
                    label='other C envelope' if project == twisted[0] else None)
    for group in ORDER:
        if group in curves:
            ax.plot(x, curves[group] / scale, color=COLORS[group], lw=1.7, zorder=3,
                    label=LABELS[group] if project == twisted[0] else None)
    ax.text(0.015, 0.82, project, transform=ax.transAxes, fontweight='bold')
    add_structure_inset(ax, project, [0.82, 0.15, 0.16, 0.70])
    ax.set_ylim(0, 1.08)
    ax.spines[['top', 'right']].set_visible(False)
axes[-1].set_xlabel('C 1s shift relative to mean(Cb+Cw) (eV)')
fig.supylabel('Relative intensity')
axes[0].legend(frameon=False, ncol=5, fontsize=8, loc='upper center',
               bbox_to_anchor=(0.57, 1.36))
fig.suptitle(f'Twisted-structure C 1s CLS comparison (Gaussian FWHM {FWHM:.2f} eV)',
             fontsize=14, fontweight='bold')
fig.savefig(OUT / 'twisted_C1s_comparison.png', dpi=300, bbox_inches='tight')
fig.savefig(OUT / 'twisted_C1s_comparison.pdf', bbox_inches='tight')
plt.close(fig)

fig, axes = plt.subplots(2, 1, figsize=(9.2, 6.4), sharex=True, constrained_layout=True)
for ax, project in zip(axes, twisted):
    rows = [r for r in data[project] if r['element'] == 'N']
    curves = {g: envelope(nx, [r['cls_eV'] for r in rows if r['group'] == g]) for g in ('N_L', 'N')}
    scale = max(float(sum(curves.values()).max()), 1e-12)
    for group, color in [('N_L', '#8E244D'), ('N', '#173F5F')]:
        ax.plot(nx, curves[group] / scale, color=color, lw=2.2,
                label=group if project == twisted[0] else None)
        ax.fill_between(nx, curves[group] / scale, color=color, alpha=0.10)
    ax.text(0.015, 0.80, project, transform=ax.transAxes, fontweight='bold')
    focused_n_bounds = ([0.82, 0.16, 0.15, 0.70]
                        if project == 'twistedH2'
                        else [0.445, 0.15, 0.12, 0.72])
    add_structure_inset(ax, project, focused_n_bounds)
    ax.set_ylim(0, 1.08)
    ax.spines[['top', 'right']].set_visible(False)
axes[-1].set_xlabel('N 1s shift relative to mean(all N) (eV)')
fig.supylabel('Relative intensity')
axes[0].legend(frameon=False, ncol=2)
fig.suptitle(f'Twisted-structure N 1s CLS comparison (Gaussian FWHM {FWHM:.2f} eV)',
             fontsize=14, fontweight='bold')
fig.savefig(OUT / 'twisted_N1s_comparison.png', dpi=300, bbox_inches='tight')
fig.savefig(OUT / 'twisted_N1s_comparison.pdf', bbox_inches='tight')
plt.close(fig)

summary_rows = []
for project in PROJECTS:
    for group in ORDER + ('N_L', 'N'):
        values = [r['cls_eV'] for r in data[project] if r['group'] == group]
        if values:
            a = np.array(values)
            summary_rows.append({
                'project': project, 'group': group, 'multiplicity': len(a),
                'mean_cls_eV': a.mean(), 'std_cls_eV': a.std(),
                'min_cls_eV': a.min(), 'max_cls_eV': a.max(),
            })
with (OUT / 'remaining_structures_group_summary.csv').open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=summary_rows[0].keys())
    writer.writeheader()
    writer.writerows(summary_rows)

print(OUT)
