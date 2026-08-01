from pathlib import Path
import csv
import re

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
PLANAR = ROOT / 'planar'
PLDC = ROOT / 'planarCOOH'
DATA = PLDC / 'output'
FIGURES = PLDC / 'figures'

PLANAR_XYZ = PLANAR / 'structure' / 'planar.xyz'
PLANAR_OUT = PLANAR / 'archive' / 'full_C_N' / 'planar_CN.istate.out'
PLDC_XYZ = PLDC / 'structure' / 'PLDC_COOH.xyz'
PLDC_OUT = PLDC / 'output' / 'pldc_cooh_allC.istate.out'

GROUPS = {
    'C_L_alpha': {4, 5, 42, 43},
    'C_alpha': {20, 21, 26, 27},
    'C_L_beta': {2, 3, 44, 45},
    'C_beta': {22, 23, 24, 25},
    'C_M': {6, 13, 28, 35},
    'C_b': {14, 15, 16, 17, 18, 19, 29, 30, 31, 32, 33, 34},
    'C_w': {7, 8, 9, 10, 11, 12, 36, 37, 38, 39, 40, 41},
    'C_COOH': {76, 79},
}
ORDER = ['C_L_alpha', 'C_alpha', 'C_M', 'C_L_beta', 'C_beta', 'C_b', 'C_w', 'C_COOH']
LABELS = {
    'C_L_alpha': r'$C_{L,\alpha}$', 'C_alpha': r'$C_{\alpha}$',
    'C_L_beta': r'$C_{L,\beta}$', 'C_beta': r'$C_{\beta}$',
    'C_M': r'$C_M$', 'C_b': r'$C_b$', 'C_w': r'$C_w$',
    'C_COOH': r'$C_{COOH}$',
}
COLORS = {
    'C_L_alpha': '#1565C0', 'C_alpha': '#56B4E9',
    'C_L_beta': '#C62828', 'C_beta': '#E76F9A',
    'C_M': '#7B2CBF', 'C_b': '#2E7D32', 'C_w': '#E69F00',
    'C_COOH': '#795548',
}


def read_xyz(path):
    atoms = []
    for index, line in enumerate(path.read_text().splitlines()[2:], start=1):
        fields = line.split()
        if len(fields) >= 4:
            atoms.append((index, fields[0], np.array([float(v) for v in fields[1:4]])))
    return atoms


def read_initial_state(path):
    pattern = re.compile(
        r'atom\s+(\d+)\s+type\s+(\d+)\s+shift\s*=\s*([-+0-9.Ee]+)\s+Ry,\s*=\s*([-+0-9.Ee]+)\s+eV'
    )
    values = {}
    for line in path.read_text().splitlines():
        match = pattern.search(line)
        if match:
            values.setdefault(int(match.group(1)), float(match.group(4)))
    return values


def group_for(index, structure):
    for group, indices in GROUPS.items():
        if index in indices and not (structure == 'Planar' and group == 'C_COOH'):
            return group
    raise ValueError(f'No carbon group for {structure} atom {index}')


def analyze(name, xyz_path, out_path):
    atoms = read_xyz(xyz_path)
    contributions = read_initial_state(out_path)
    carbon_atoms = [(i, r) for i, element, r in atoms if element == 'C']
    missing = [i for i, _ in carbon_atoms if i not in contributions]
    if missing:
        raise ValueError(f'{name}: initial_state output lacks carbon atoms {missing}')

    reference_indices = GROUPS['C_b'] | GROUPS['C_w']
    reference = np.mean([contributions[i] for i in reference_indices])
    rows = []
    for index, r in carbon_atoms:
        group = group_for(index, name)
        rows.append({
            'structure': name,
            'atom_index': index,
            'element': 'C',
            'group': group,
            'x_A': r[0], 'y_A': r[1], 'z_A': r[2],
            'is_contribution_eV': contributions[index],
            'reference': 'mean(C_b+C_w)',
            'reference_contribution_eV': reference,
            'cls_eV': reference - contributions[index],
        })
    return rows


planar = analyze('Planar', PLANAR_XYZ, PLANAR_OUT)
pldc = analyze('PLDC-COOH', PLDC_XYZ, PLDC_OUT)
all_rows = planar + pldc

atom_fields = list(all_rows[0])
for name, rows in [('planar', planar), ('PLDC_COOH', pldc), ('planar_vs_PLDC_COOH', all_rows)]:
    with (DATA / f'{name}_all_carbon_atom_shifts.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=atom_fields)
        writer.writeheader()
        writer.writerows(rows)

summary = []
for structure, rows in [('Planar', planar), ('PLDC-COOH', pldc)]:
    groups_present = [group for group in ORDER if any(r['group'] == group for r in rows)]
    for group in groups_present:
        members = [r for r in rows if r['group'] == group]
        shifts = np.array([r['cls_eV'] for r in members])
        summary.append({
            'structure': structure,
            'group': group,
            'multiplicity': len(members),
            'mean_cls_eV': shifts.mean(),
            'std_cls_eV': shifts.std(),
            'min_cls_eV': shifts.min(),
            'max_cls_eV': shifts.max(),
            'atom_indices': ' '.join(str(r['atom_index']) for r in members),
        })

with (DATA / 'planar_vs_PLDC_COOH_group_summary.csv').open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)

# Gaussian broadened spectra. Two aggregate envelopes are drawn behind the
# individual group curves: the alpha pair and all remaining carbon groups.
fwhm = 0.35
all_shifts = np.array([r['cls_eV'] for r in all_rows])
energy = np.linspace(all_shifts.min() - 0.65, all_shifts.max() + 0.65, 3500)
fig, axes = plt.subplots(2, 1, figsize=(10.5, 8.0), sharex=True, constrained_layout=True)
for ax, (structure, rows) in zip(axes, [('Planar', planar), ('PLDC–COOH', pldc)]):
    components = {}
    total = np.zeros_like(energy)
    for group in ORDER:
        members = [r for r in rows if r['group'] == group]
        if not members:
            continue
        curve = np.zeros_like(energy)
        for row in members:
            curve += np.exp(-4 * np.log(2) * ((energy - row['cls_eV']) / fwhm) ** 2)
        components[group] = curve
        total += curve
    alpha_pair = components['C_L_alpha'] + components['C_alpha']
    other = sum((curve for group, curve in components.items()
                 if group not in {'C_L_alpha', 'C_alpha'}), start=np.zeros_like(energy))
    scale = total.max()
    ax.fill_between(energy, alpha_pair / scale, color='#2F80ED', alpha=0.24,
                    label=r'Envelope: $C_{L,\alpha}+C_{\alpha}$', zorder=0)
    ax.plot(energy, alpha_pair / scale, color='#0B4FA3', lw=2.5, alpha=0.78, zorder=1)
    ax.fill_between(energy, other / scale, color='#F2A900', alpha=0.20,
                    label='Envelope: all other C', zorder=0)
    ax.plot(energy, other / scale, color='#A66200', lw=2.5, alpha=0.78, zorder=1)
    for group in ORDER:
        if group in components:
            ax.plot(energy, components[group] / scale, lw=1.65, color=COLORS[group],
                    label=LABELS[group], zorder=3)
    ax.axvline(0, color='#777777', lw=0.8, ls='--')
    ax.set_title(f'{structure}: all carbon groups', loc='left', fontweight='bold')
    ax.set_ylabel('Normalized intensity')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, ncol=5, fontsize=8, loc='upper right')
axes[-1].set_xlabel(r'C 1s initial-state shift relative to mean($C_b+C_w$) (eV)')
fig.suptitle(f'Planar and PLDC–COOH C 1s core-level-shift envelopes (Gaussian FWHM = {fwhm:.2f} eV)', fontweight='bold')
fig.savefig(FIGURES / 'planar_vs_PLDC_COOH_all_carbon_envelopes.png', dpi=300, bbox_inches='tight')
fig.savefig(FIGURES / 'planar_vs_PLDC_COOH_all_carbon_envelopes.pdf', bbox_inches='tight')

# Group means and site spread provide a direct numerical comparison.
fig, ax = plt.subplots(figsize=(10.5, 5.8), constrained_layout=True)
x = np.arange(len(ORDER))
offsets = {'Planar': -0.12, 'PLDC-COOH': 0.12}
markers = {'Planar': 'o', 'PLDC-COOH': 's'}
structure_colors = {'Planar': '#222222', 'PLDC-COOH': '#0072B2'}
for structure in ('Planar', 'PLDC-COOH'):
    selected = {r['group']: r for r in summary if r['structure'] == structure}
    xs, means, lower, upper = [], [], [], []
    for i, group in enumerate(ORDER):
        if group not in selected:
            continue
        row = selected[group]
        xs.append(i + offsets[structure])
        means.append(row['mean_cls_eV'])
        lower.append(row['mean_cls_eV'] - row['min_cls_eV'])
        upper.append(row['max_cls_eV'] - row['mean_cls_eV'])
    ax.errorbar(xs, means, yerr=np.array([lower, upper]), fmt=markers[structure], ms=7,
                capsize=4, lw=1.4, color=structure_colors[structure], label=structure)
ax.axhline(0, color='#777777', lw=0.8, ls='--')
ax.set_xticks(x, [LABELS[g] for g in ORDER])
ax.set_ylabel(r'Mean C 1s shift relative to mean($C_b+C_w$) (eV)')
ax.set_title('Carbon-group mean shifts: Planar versus PLDC–COOH', loc='left', fontweight='bold')
ax.legend(frameon=False)
ax.spines[['top', 'right']].set_visible(False)
fig.savefig(FIGURES / 'planar_vs_PLDC_COOH_group_means.png', dpi=300, bbox_inches='tight')
fig.savefig(FIGURES / 'planar_vs_PLDC_COOH_group_means.pdf', bbox_inches='tight')

# Readable main-window spectra plus a dedicated inset for the distant COOH feature.
fig, axes = plt.subplots(2, 1, figsize=(10.5, 8.0), sharex=True, constrained_layout=True)
for ax, (structure, rows) in zip(axes, [('Planar', planar), ('PLDC–COOH', pldc)]):
    components = {}
    total = np.zeros_like(energy)
    for group in ORDER:
        members = [r for r in rows if r['group'] == group]
        if not members:
            continue
        curve = sum((np.exp(-4 * np.log(2) * ((energy - r['cls_eV']) / fwhm) ** 2)
                     for r in members), start=np.zeros_like(energy))
        components[group] = curve
        total += curve
    alpha_pair = components['C_L_alpha'] + components['C_alpha']
    other = sum((curve for group, curve in components.items()
                 if group not in {'C_L_alpha', 'C_alpha'}), start=np.zeros_like(energy))
    scale = total[(energy > -1.5) & (energy < 0.8)].max()
    ax.fill_between(energy, alpha_pair / scale, color='#2F80ED', alpha=0.25,
                    label=r'Envelope: $C_{L,\alpha}+C_{\alpha}$', zorder=0)
    ax.plot(energy, alpha_pair / scale, color='#0B4FA3', lw=2.7, alpha=0.82, zorder=1)
    ax.fill_between(energy, other / scale, color='#F2A900', alpha=0.21,
                    label='Envelope: all other C', zorder=0)
    ax.plot(energy, other / scale, color='#A66200', lw=2.7, alpha=0.82, zorder=1)
    for group in ORDER:
        if group in components and group != 'C_COOH':
            ax.plot(energy, components[group] / scale, lw=1.65, color=COLORS[group],
                    label=LABELS[group], zorder=3)
    ax.axvline(0, color='#777777', lw=0.8, ls='--')
    ax.set_xlim(-1.45, 0.80)
    ax.set_ylim(-0.02, 1.08)
    ax.set_title(f'{structure}: all porphyrin and phenyl carbon groups', loc='left', fontweight='bold')
    ax.set_ylabel('Normalized intensity')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, ncol=5, fontsize=7.7, loc='upper right')
    if structure == 'PLDC–COOH':
        inset = ax.inset_axes([0.055, 0.49, 0.25, 0.40])
        cooh = components['C_COOH'] / scale
        inset.plot(energy, cooh, color=COLORS['C_COOH'], lw=2.0)
        inset.fill_between(energy, cooh, color=COLORS['C_COOH'], alpha=0.15)
        inset.set_xlim(-4.20, -3.20)
        inset.set_ylim(0, max(cooh) * 1.18)
        inset.set_title(r'$C_{COOH}$ (2 atoms)', fontsize=8)
        inset.set_xlabel('Shift (eV)', fontsize=7)
        inset.tick_params(labelsize=7)
        inset.spines[['top', 'right']].set_visible(False)
axes[-1].set_xlabel(r'C 1s initial-state shift, QE convention: IS$_{ref}$ − IS$_{site}$ (eV)')
fig.suptitle(f'Planar and PLDC–COOH C 1s envelopes (Gaussian FWHM = {fwhm:.2f} eV)', fontweight='bold')
fig.savefig(FIGURES / 'planar_vs_PLDC_COOH_all_carbon_envelopes_zoomed.png', dpi=300, bbox_inches='tight')
fig.savefig(FIGURES / 'planar_vs_PLDC_COOH_all_carbon_envelopes_zoomed.pdf', bbox_inches='tight')

# Split-scale group means: seven common groups at left, COOH at right.
fig, (ax, ax_cooh) = plt.subplots(1, 2, figsize=(11.0, 5.8), gridspec_kw={'width_ratios': [7, 1]}, constrained_layout=True)
main_groups = ORDER[:-1]
xmain = np.arange(len(main_groups))
for structure in ('Planar', 'PLDC-COOH'):
    selected = {r['group']: r for r in summary if r['structure'] == structure}
    xs, means, lower, upper = [], [], [], []
    for i, group in enumerate(main_groups):
        row = selected[group]
        xs.append(i + offsets[structure])
        means.append(row['mean_cls_eV'])
        lower.append(row['mean_cls_eV'] - row['min_cls_eV'])
        upper.append(row['max_cls_eV'] - row['mean_cls_eV'])
    ax.errorbar(xs, means, yerr=np.array([lower, upper]), fmt=markers[structure], ms=7,
                capsize=4, lw=1.4, color=structure_colors[structure], label=structure)
ax.axhline(0, color='#777777', lw=0.8, ls='--')
ax.set_xticks(xmain, [LABELS[g] for g in main_groups])
ax.set_ylim(-1.30, 0.42)
ax.set_ylabel(r'Mean C 1s shift relative to mean($C_b+C_w$) (eV)')
ax.set_title('Common carbon groups', loc='left', fontweight='bold')
ax.legend(frameon=False)
ax.spines[['top', 'right']].set_visible(False)
cooh_row = next(r for r in summary if r['structure'] == 'PLDC-COOH' and r['group'] == 'C_COOH')
ax_cooh.errorbar([0], [cooh_row['mean_cls_eV']],
                 yerr=[[cooh_row['mean_cls_eV'] - cooh_row['min_cls_eV']],
                       [cooh_row['max_cls_eV'] - cooh_row['mean_cls_eV']]],
                 fmt='s', ms=7, capsize=4, lw=1.4, color=structure_colors['PLDC-COOH'])
ax_cooh.set_xticks([0], [LABELS['C_COOH']])
ax_cooh.set_xlim(-0.55, 0.55)
ax_cooh.set_ylim(-3.88, -3.45)
ax_cooh.set_title('PLDC only', fontweight='bold')
ax_cooh.spines[['top', 'right']].set_visible(False)
fig.suptitle('Carbon-group mean shifts: Planar versus PLDC–COOH', fontweight='bold')
fig.savefig(FIGURES / 'planar_vs_PLDC_COOH_group_means_split.png', dpi=300, bbox_inches='tight')
fig.savefig(FIGURES / 'planar_vs_PLDC_COOH_group_means_split.pdf', bbox_inches='tight')

for row in summary:
    print(f"{row['structure']:10s} {row['group']:10s} n={row['multiplicity']:2d} "
          f"mean={row['mean_cls_eV']:+.5f} eV range=[{row['min_cls_eV']:+.5f}, {row['max_cls_eV']:+.5f}]")
