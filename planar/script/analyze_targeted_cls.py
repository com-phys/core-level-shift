from pathlib import Path
import csv
import re

import numpy as np


PROJECT = Path(__file__).resolve().parent.parent
XYZ = PROJECT / "structure" / "planar.xyz"
OUTPUT = PROJECT / "output" / "planar_targeted_CN.istate.out"

CARBON_GROUPS = {
    "C_L_alpha": {4, 5, 42, 43},
    "C_alpha": {20, 21, 26, 27},
    "C_L_beta": {2, 3, 44, 45},
    "C_beta": {22, 23, 24, 25},
    "C_M": {6, 13, 28, 35},
    "C_b": {14, 15, 16, 17, 18, 19, 29, 30, 31, 32, 33, 34},
}
NITROGEN_GROUPS = {"N_L": {46, 49}, "N": {47, 48}}
TARGET_C = set().union(*CARBON_GROUPS.values())
TARGET_N = set().union(*NITROGEN_GROUPS.values())
C_W = set(range(7, 13)) | set(range(36, 42))


def group_for(atom_index, mapping):
    for group, indices in mapping.items():
        if atom_index in indices:
            return group
    raise ValueError(f"No target group for atom {atom_index}")


xyz_lines = XYZ.read_text().splitlines()[2:]
geometry = {}
for atom_index, line in enumerate(xyz_lines, start=1):
    fields = line.split()
    geometry[atom_index] = (fields[0], np.array([float(v) for v in fields[1:4]]))

pattern = re.compile(
    r"atom\s+(\d+)\s+type\s+(\d+)\s+shift\s*=\s*([-+0-9.Ee]+)\s+Ry,\s*=\s*([-+0-9.Ee]+)\s+eV"
)
raw = {}
types = {}
for line in OUTPUT.read_text().splitlines():
    match = pattern.search(line)
    if match:
        atom_index = int(match.group(1))
        if atom_index not in raw:  # first block is the complete IS contribution
            types[atom_index] = int(match.group(2))
            raw[atom_index] = float(match.group(4))

assert all(types[i] == 7 and raw[i] == 0.0 for i in C_W)
assert all(types[i] == 2 and raw[i] != 0.0 for i in TARGET_C)
assert all(types[i] == 3 and raw[i] != 0.0 for i in TARGET_N)

# C_b is the carbon reference because C_w is deliberately not evaluated.
c_reference = np.mean([raw[i] for i in CARBON_GROUPS["C_b"]])
n_reference = np.mean([raw[i] for i in TARGET_N])

rows = []
for atom_index in sorted(TARGET_C | TARGET_N):
    element, xyz = geometry[atom_index]
    if element == "C":
        group = group_for(atom_index, CARBON_GROUPS)
        reference = c_reference
        reference_name = "mean(C_b)"
    else:
        group = group_for(atom_index, NITROGEN_GROUPS)
        reference = n_reference
        reference_name = "mean(N)"
    rows.append({
        "atom_index": atom_index,
        "element": element,
        "group": group,
        "x_A": xyz[0], "y_A": xyz[1], "z_A": xyz[2],
        "is_contribution_eV": raw[atom_index],
        "reference": reference_name,
        "cls_eV": reference - raw[atom_index],
    })

atom_csv = PROJECT / "output" / "planar_targeted_C_N_atom_shifts.csv"
with atom_csv.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

summary = []
for group in list(CARBON_GROUPS) + list(NITROGEN_GROUPS):
    members = [row for row in rows if row["group"] == group]
    shifts = np.array([row["cls_eV"] for row in members])
    summary.append({
        "group": group,
        "multiplicity": len(members),
        "mean_cls_eV": shifts.mean(),
        "std_cls_eV": shifts.std(),
        "min_cls_eV": shifts.min(),
        "max_cls_eV": shifts.max(),
        "atom_indices": " ".join(str(row["atom_index"]) for row in members),
    })

summary_csv = PROJECT / "output" / "planar_targeted_C_N_group_summary.csv"
with summary_csv.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)

print(f"C reference mean(C_b): {c_reference:.8f} eV")
print(f"N reference mean(N):   {n_reference:.8f} eV")
print("Cw atoms verified as unexcited:", " ".join(map(str, sorted(C_W))))
for item in summary:
    print(f"{item['group']:10s} n={item['multiplicity']:2d} mean={item['mean_cls_eV']:+.6f} eV")
print(f"Wrote {atom_csv}")
print(f"Wrote {summary_csv}")
