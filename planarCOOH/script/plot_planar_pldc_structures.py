from pathlib import Path
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np


SOURCE = Path(__file__).resolve().parents[2]
DEST = SOURCE / "planarCOOH" / "figures"

COLORS = {"Zn": "#8ab17d", "C": "#244b36", "N": "#2486b8", "O": "#d1495b", "H": "#63d8d8"}
SIZES = {"Zn": 250, "C": 85, "N": 115, "O": 115, "H": 35}
CUTOFFS = {
    frozenset(("C", "C")): 1.78,
    frozenset(("C", "N")): 1.78,
    frozenset(("C", "H")): 1.25,
    frozenset(("C", "O")): 1.85,
    frozenset(("O", "H")): 1.25,
    frozenset(("Zn", "N")): 2.30,
}


def read_xyz(path):
    atoms = []
    for line in path.read_text().splitlines()[2:]:
        fields = line.split()
        if len(fields) >= 4:
            atoms.append((fields[0], np.array([float(v) for v in fields[1:4]])))
    return atoms


def bonds(atoms):
    links = []
    for i, (symbol_i, r_i) in enumerate(atoms):
        for j in range(i + 1, len(atoms)):
            symbol_j, r_j = atoms[j]
            cutoff = CUTOFFS.get(frozenset((symbol_i, symbol_j)))
            if cutoff and np.linalg.norm(r_i - r_j) <= cutoff:
                links.append((i, j))
    return links


structures = {
    "Planar": read_xyz(SOURCE / "planar" / "structure" / "planar.xyz"),
    "PLDC": read_xyz(SOURCE / "planarCOOH" / "structure" / "PLDC.xyz"),
}

fig, axes = plt.subplots(1, 2, figsize=(13, 6.7), constrained_layout=True, sharex=True, sharey=True)

for ax, (name, atoms) in zip(axes, structures.items()):
    for i, j in bonds(atoms):
        p, q = atoms[i][1], atoms[j][1]
        ax.plot([p[0], q[0]], [p[1], q[1]], color="#777777", lw=1.5, zorder=1)
    for element in ("H", "C", "N", "O", "Zn"):
        selected = np.array([r for symbol, r in atoms if symbol == element])
        if selected.size:
            ax.scatter(
                selected[:, 0], selected[:, 1], s=SIZES[element], c=COLORS[element],
                edgecolors="white", linewidths=0.6, zorder=2, label=element,
            )
    formula = "".join(f"{element}{count}" for element, count in sorted(Counter(s for s, _ in atoms).items()))
    ax.set_title(f"{name}\n{formula}")
    ax.set_aspect("equal")
    ax.set_xlim(-9.0, 9.0)
    ax.set_ylim(-9.0, 9.0)
    ax.axis("off")

axes[1].annotate(
    "added COO group", xy=(-7.1, -6.7), xytext=(-8.7, -2.6),
    arrowprops=dict(arrowstyle="->", color="#d1495b", lw=1.4), color="#d1495b",
)
axes[1].annotate(
    "added COO group", xy=(6.9, 7.1), xytext=(2.8, 8.4),
    arrowprops=dict(arrowstyle="->", color="#d1495b", lw=1.4), color="#d1495b",
)
axes[1].legend(loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.05))

fig.savefig(DEST / "planar_vs_PLDC_structures.png", dpi=300, bbox_inches="tight")
fig.savefig(DEST / "planar_vs_PLDC_structures.pdf", bbox_inches="tight")
print(f"Saved {DEST / 'planar_vs_PLDC_structures.png'}")
print(f"Saved {DEST / 'planar_vs_PLDC_structures.pdf'}")
