#!/usr/bin/env python3
"""Prepare consistent QE C 1s and N 1s initial-state CLS inputs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path('/Users/behnamazizi/Downloads/core level shifts')
PROJECTS = ('cross', 'twistedH2', 'twistedO2', 'TWco', 'TWDCOH')
PSEUDO = ROOT / 'pseudopotential'

CARBON_GROUPS = {
    'C_L_alpha': {4, 5, 42, 43},
    'C_alpha': {20, 21, 26, 27},
    'C_L_beta': {2, 3, 44, 45},
    'C_beta': {22, 23, 24, 25},
    'C_M': {6, 13, 28, 35},
    'C_b': {14, 15, 16, 17, 18, 19, 29, 30, 31, 32, 33, 34},
    'C_w': {7, 8, 9, 10, 11, 12, 36, 37, 38, 39, 40, 41},
}

MASSES = {'Zn': 65.3800, 'C': 12.0110, 'N': 14.0070, 'H': 1.0080, 'O': 15.9990}
PSEUDOS = {
    'Zn': 'Zn.pbe-van.UPF', 'C': 'C.pbe-rrkjus.UPF',
    'N': 'N.pbe-van_ak.UPF', 'H': 'H.pbe-rrkjus.UPF',
    'O': 'O.pbe-rrkjus.UPF',
}


def read_xyz(path: Path):
    raw = path.read_text().splitlines()
    declared = int(raw[0].strip())
    atoms = []
    for line in raw[2:]:
        fields = line.split()
        if len(fields) >= 4:
            atoms.append((fields[0], *(float(v) for v in fields[1:4])))
    if len(atoms) != declared:
        raise ValueError(f'{path}: declared {declared} atoms but read {len(atoms)}')
    return atoms


def group_map(project: str, atoms):
    groups = {name: set(indices) for name, indices in CARBON_GROUPS.items()}
    if project in {'TWco', 'TWDCOH'}:
        groups['C_COOH'] = {80, 84}
    n_groups = {'N_L': {74, 77}, 'N': {75, 76}} if project == 'cross' else {
        'N_L': {46, 49}, 'N': {47, 48}
    }
    carbon_indices = {i for i, (e, *_xyz) in enumerate(atoms, 1) if e == 'C'}
    assigned = set().union(*groups.values())
    if carbon_indices != assigned:
        raise ValueError(
            f'{project}: carbon assignment mismatch; '
            f'missing={sorted(carbon_indices-assigned)}, extra={sorted(assigned-carbon_indices)}'
        )
    nitrogen_indices = {i for i, (e, *_xyz) in enumerate(atoms, 1) if e == 'N'}
    n_assigned = set().union(*n_groups.values())
    if nitrogen_indices != n_assigned:
        raise ValueError(f'{project}: nitrogen assignment mismatch')
    return groups, n_groups


def write_project(project: str):
    folder = ROOT / project
    xyz = folder / 'structure' / f'{project}.xyz'
    atoms = read_xyz(xyz)
    c_groups, n_groups = group_map(project, atoms)

    normal_species = [e for e in ('Zn', 'C', 'N', 'H', 'O') if any(a[0] == e for a in atoms)]
    species = normal_species + ['Cs', 'Ns']
    c_type = species.index('C') + 1
    n_type = species.index('N') + 1
    cs_type = species.index('Cs') + 1
    ns_type = species.index('Ns') + 1

    prefix = f'{project.lower()}_cls'
    restart = folder / 'output' / 'restart_data'
    restart.mkdir(parents=True, exist_ok=True)

    species_lines = [f'{e:<3s} {MASSES[e]:8.4f}  {PSEUDOS[e]}' for e in normal_species]
    species_lines += [
        'Cs   12.0110  C.star1s-pbe-rrkjus.UPF',
        'Ns   14.0070  N.star1s-pbe-van.UPF',
    ]
    position_lines = [
        f'{e:<3s} {x:16.8f} {y:16.8f} {z:16.8f}' for e, x, y, z in atoms
    ]

    scf = f"""&CONTROL
  calculation  = 'scf'
  restart_mode = 'from_scratch'
  prefix       = '{prefix}'
  pseudo_dir   = '{PSEUDO}'
  outdir       = '{restart}'
  disk_io      = 'low'
/
&SYSTEM
  ibrav        = 1
  A            = 25.0
  nat          = {len(atoms)}
  ntyp         = {len(species)}
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
{chr(10).join(species_lines)}
ATOMIC_POSITIONS angstrom
{chr(10).join(position_lines)}
K_POINTS gamma
"""
    istate = f"""&INPUTPP
  prefix          = '{prefix}'
  outdir          = '{restart}'
  excite({c_type}) = {cs_type}   ! all carbon atoms: C 1s
  excite({n_type}) = {ns_type}   ! all nitrogen atoms: N 1s
/
"""

    (folder / 'input' / f'{project}.scf.in').write_text(scf)
    (folder / 'input' / f'{project}.istate.in').write_text(istate)

    rows = []
    for group, indices in c_groups.items():
        rows += [{'atom_index': i, 'element': 'C', 'group': group} for i in sorted(indices)]
    for group, indices in n_groups.items():
        rows += [{'atom_index': i, 'element': 'N', 'group': group} for i in sorted(indices)]
    rows.sort(key=lambda r: r['atom_index'])
    with (folder / 'structure' / 'group_assignments.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=('atom_index', 'element', 'group'))
        writer.writeheader()
        writer.writerows(rows)

    electrons = sum({'Zn': 12, 'C': 4, 'N': 5, 'H': 1, 'O': 6}[a[0]] for a in atoms)
    if electrons % 2:
        raise ValueError(f'{project}: odd neutral valence-electron count {electrons}')
    print(
        f'{project:10s}: nat={len(atoms)}, electrons={electrons}, '
        f'C={sum(a[0]=="C" for a in atoms)}, N={sum(a[0]=="N" for a in atoms)}, '
        f'ntyp={len(species)}'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('projects', nargs='*', choices=PROJECTS)
    args = parser.parse_args()
    for project in args.projects or PROJECTS:
        write_project(project)


if __name__ == '__main__':
    main()
