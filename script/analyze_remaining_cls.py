#!/usr/bin/env python3
"""Extract, summarize, and plot C 1s/N 1s initial-state CLS results."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path('/Users/behnamazizi/Downloads/core level shifts')
PROJECTS = ('cross', 'twistedH2', 'twistedO2', 'TWco', 'TWDCOH')
FWHM_EV = 0.35
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
C_ORDER = ('C_L_alpha', 'C_alpha', 'C_M', 'C_L_beta', 'C_beta', 'C_b', 'C_w', 'C_COOH')
N_ORDER = ('N_L', 'N')


def add_structure_inset(ax, project, bounds):
    """Add the labeled molecular structure while cropping away its large legend."""
    path = ROOT / project / 'figures' / f'{project}_group_assignments.png'
    image = plt.imread(path)
    h, w = image.shape[:2]
    crop = image[int(0.07 * h):int(0.98 * h), :int(0.72 * w)]
    rgb = crop[..., :3]
    mask = np.any(rgb < 0.965, axis=2)
    if np.any(mask):
        ys, xs = np.where(mask)
        pad = 20
        crop = crop[max(0, ys.min() - pad):min(crop.shape[0], ys.max() + pad),
                    max(0, xs.min() - pad):min(crop.shape[1], xs.max() + pad)]
    inset = ax.inset_axes(bounds, zorder=10)
    inset.imshow(crop)
    inset.set_xticks([])
    inset.set_yticks([])
    inset.set_facecolor((1, 1, 1, 0.94))
    for spine in inset.spines.values():
        spine.set_color('#AAB2BD')
        spine.set_linewidth(0.8)
    return inset


def read_xyz(path):
    atoms = []
    for i, line in enumerate(path.read_text().splitlines()[2:], 1):
        f = line.split()
        if len(f) >= 4:
            atoms.append((i, f[0], *(float(v) for v in f[1:4])))
    return atoms


def gaussian(x, centers):
    sigma = FWHM_EV / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    y = np.zeros_like(x)
    for center in centers:
        y += np.exp(-0.5 * ((x - center) / sigma) ** 2) / (sigma * np.sqrt(2.0 * np.pi))
    return y


def extract_runtime(text, program):
    match = re.search(rf'{program}\s*:\s*.+?WALL', text)
    return match.group(0).strip() if match else 'not found'


def analyze(project):
    folder = ROOT / project
    scf_path = folder / 'output' / f'{project}.scf.out'
    is_path = folder / 'output' / f'{project}.istate.out'
    if not scf_path.exists() or not is_path.exists():
        raise FileNotFoundError(f'{project}: missing SCF or initial_state output')
    scf_text = scf_path.read_text(errors='replace')
    is_text = is_path.read_text(errors='replace')
    if 'JOB DONE.' not in scf_text or 'JOB DONE.' not in is_text:
        raise RuntimeError(f'{project}: calculation output is incomplete')

    assignment = {}
    with (folder / 'structure' / 'group_assignments.csv').open() as handle:
        for row in csv.DictReader(handle):
            assignment[int(row['atom_index'])] = row['group']
    atoms = {i: (e, x, y, z) for i, e, x, y, z in read_xyz(folder / 'structure' / f'{project}.xyz')}

    pattern = re.compile(
        r'atom\s+(\d+)\s+type\s+(\d+)\s+shift\s*=\s*([-+0-9.Ee]+)\s+Ry,\s*=\s*([-+0-9.Ee]+)\s+eV'
    )
    raw = {}
    atom_types = {}
    for line in is_text.splitlines():
        match = pattern.search(line)
        if match:
            idx = int(match.group(1))
            if idx not in raw:
                atom_types[idx] = int(match.group(2))
                raw[idx] = float(match.group(4))
    expected = set(assignment)
    missing = expected - set(raw)
    if missing:
        raise RuntimeError(f'{project}: missing mapped atoms {sorted(missing)}')

    c_reference_ids = [i for i, g in assignment.items() if g in {'C_b', 'C_w'}]
    n_reference_ids = [i for i, g in assignment.items() if g in {'N_L', 'N'}]
    c_reference = float(np.mean([raw[i] for i in c_reference_ids]))
    n_reference = float(np.mean([raw[i] for i in n_reference_ids]))

    rows = []
    for idx in sorted(expected):
        element, x, y, z = atoms[idx]
        reference = c_reference if element == 'C' else n_reference
        rows.append({
            'atom_index': idx, 'element': element, 'group': assignment[idx],
            'x_A': x, 'y_A': y, 'z_A': z, 'qe_type': atom_types[idx],
            'is_contribution_eV': raw[idx],
            'reference_definition': 'mean(C_b+C_w)' if element == 'C' else 'mean(all N)',
            'reference_eV': reference, 'cls_eV': reference - raw[idx],
        })

    atom_csv = folder / 'output' / f'{project}_C_N_atom_shifts.csv'
    with atom_csv.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    summary = []
    for group in C_ORDER + N_ORDER:
        members = [r for r in rows if r['group'] == group]
        if not members:
            continue
        shifts = np.array([r['cls_eV'] for r in members])
        summary.append({
            'group': group, 'element': members[0]['element'], 'multiplicity': len(members),
            'mean_cls_eV': shifts.mean(), 'std_cls_eV': shifts.std(),
            'min_cls_eV': shifts.min(), 'max_cls_eV': shifts.max(),
            'atom_indices': ' '.join(str(r['atom_index']) for r in members),
        })
    summary_csv = folder / 'output' / f'{project}_group_summary.csv'
    with summary_csv.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)

    c_rows = [r for r in rows if r['element'] == 'C']
    common_shifts = [r['cls_eV'] for r in c_rows if r['group'] != 'C_COOH']
    energy = np.linspace(min(common_shifts) - 0.65, max(common_shifts) + 0.65, 3000)
    curves = {g: gaussian(energy, [r['cls_eV'] for r in c_rows if r['group'] == g]) for g in C_ORDER if any(r['group'] == g for r in c_rows)}
    blue = curves.get('C_L_alpha', 0) + curves.get('C_alpha', 0)
    other = sum((curves[g] for g in curves if g not in {'C_L_alpha', 'C_alpha', 'C_COOH'}), np.zeros_like(energy))
    scale = max(float((blue + other).max()), 1e-12)

    fig, ax = plt.subplots(figsize=(10.8, 6.2), constrained_layout=True)
    ax.fill_between(energy, blue / scale, color='#4E79A7', alpha=0.22, zorder=1,
                    label=r'background: $C_{L,\alpha}+C_\alpha$')
    ax.fill_between(energy, other / scale, color='#F28E2B', alpha=0.22, zorder=1,
                    label='background: remaining common C groups')
    for group in C_ORDER:
        if group in curves and group != 'C_COOH':
            ax.plot(energy, curves[group] / scale, color=COLORS[group], lw=2.0,
                    label=LABELS[group], zorder=3)
    ax.set_xlabel('C 1s core-level shift relative to mean(Cb+Cw) (eV)')
    ax.set_ylabel('Relative intensity')
    ax.set_title(f'{project}: C 1s initial-state core-level shifts')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, ncol=2, fontsize=9, title=f'Gaussian FWHM = {FWHM_EV:.2f} eV')

    cooh = [r['cls_eV'] for r in c_rows if r['group'] == 'C_COOH']
    if cooh:
        inset = ax.inset_axes([0.045, 0.57, 0.27, 0.30])
        x2 = np.linspace(min(cooh) - 0.6, max(cooh) + 0.6, 1200)
        y2 = gaussian(x2, cooh)
        inset.plot(x2, y2 / max(y2.max(), 1e-12), color=COLORS['C_COOH'], lw=2.2)
        inset.fill_between(x2, y2 / max(y2.max(), 1e-12), color=COLORS['C_COOH'], alpha=0.16)
        inset.set_title(r'$C_{COOH}$', fontsize=9)
        inset.tick_params(labelsize=8)
        inset.spines[['top', 'right']].set_visible(False)
    add_structure_inset(ax, project, [0.755, 0.54, 0.225, 0.40])
    c_png = folder / 'figures' / f'{project}_C1s_envelopes.png'
    fig.savefig(c_png, dpi=300, bbox_inches='tight')
    fig.savefig(c_png.with_suffix('.pdf'), bbox_inches='tight')
    plt.close(fig)

    n_rows = [r for r in rows if r['element'] == 'N']
    n_shifts = [r['cls_eV'] for r in n_rows]
    n_energy = np.linspace(min(n_shifts) - 0.65, max(n_shifts) + 0.65, 2200)
    n_curves = {g: gaussian(n_energy, [r['cls_eV'] for r in n_rows if r['group'] == g]) for g in N_ORDER}
    n_scale = max(float(sum(n_curves.values()).max()), 1e-12)
    fig, ax = plt.subplots(figsize=(8.5, 5.2), constrained_layout=True)
    for group in N_ORDER:
        ax.plot(n_energy, n_curves[group] / n_scale, color=COLORS[group], lw=2.7, label=LABELS[group])
        ax.fill_between(n_energy, n_curves[group] / n_scale, color=COLORS[group], alpha=0.10)
    ax.set_xlabel('N 1s core-level shift relative to mean(all N) (eV)')
    ax.set_ylabel('Relative intensity')
    ax.set_title(f'{project}: N 1s initial-state core-level shifts')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, title=f'Gaussian FWHM = {FWHM_EV:.2f} eV')
    if project == 'cross':
        n_structure_bounds = [0.035, 0.49, 0.245, 0.45]
    elif project == 'twistedH2':
        n_structure_bounds = [0.405, 0.43, 0.19, 0.49]
    else:
        n_structure_bounds = [0.405, 0.43, 0.19, 0.49]
    add_structure_inset(ax, project, n_structure_bounds)
    n_png = folder / 'figures' / f'{project}_N1s_envelopes.png'
    fig.savefig(n_png, dpi=300, bbox_inches='tight')
    fig.savefig(n_png.with_suffix('.pdf'), bbox_inches='tight')
    plt.close(fig)

    iterations = re.search(r'convergence has been achieved in\s+(\d+) iterations', scf_text)
    energy_match = re.findall(r'!\s+total energy\s+=\s+([-+0-9.]+)\s+Ry', scf_text)
    runtime = folder / 'output' / f'{project}_runtime_summary.txt'
    runtime.write_text(
        f'Project: {project}\n'
        f'SCF iterations: {iterations.group(1) if iterations else "not found"}\n'
        f'Final total energy (Ry): {energy_match[-1] if energy_match else "not found"}\n'
        f'SCF runtime: {extract_runtime(scf_text, "PWSCF")}\n'
        f'initial_state runtime: {extract_runtime(is_text, "initstate")}\n'
        f'C reference contribution (eV): {c_reference:.8f}\n'
        f'N reference contribution (eV): {n_reference:.8f}\n'
        f'Gaussian FWHM (eV): {FWHM_EV:.2f}\n'
    )
    print(f'{project}: wrote {atom_csv.name}, {summary_csv.name}, C/N plots, and runtime summary')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('projects', nargs='*', choices=PROJECTS)
    args = parser.parse_args()
    for project in args.projects or PROJECTS:
        analyze(project)


if __name__ == '__main__':
    main()
