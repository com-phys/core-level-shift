from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np


PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "output" / "planar_targeted_C_N_atom_shifts.csv"
FWHM_EV = 0.35

BLUE_GROUPS = {"C_L_alpha", "C_alpha", "C_M"}
RED_GROUPS = {"C_L_beta", "C_beta", "C_b"}

with DATA.open() as handle:
    rows = list(csv.DictReader(handle))

blue_shifts = np.array([
    float(row["cls_eV"]) for row in rows if row["group"] in BLUE_GROUPS
])
red_shifts = np.array([
    float(row["cls_eV"]) for row in rows if row["group"] in RED_GROUPS
])

energy = np.linspace(-1.30, 0.80, 3000)


def gaussian_envelope(shifts):
    envelope = np.zeros_like(energy)
    for shift in shifts:
        envelope += np.exp(-4.0 * np.log(2.0) * ((energy - shift) / FWHM_EV) ** 2)
    return envelope


blue = gaussian_envelope(blue_shifts)
red = gaussian_envelope(red_shifts)

# One common normalization retains the relative atom-count weighting between
# the two targeted envelopes.
common_max = max(blue.max(), red.max())
blue /= common_max
red /= common_max

fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)

ax.plot(
    energy, blue, color="#1565c0", linewidth=3.0,
    label=r"$C_{L,\alpha}+C_\alpha+C_M$ (12 atoms)",
)
ax.fill_between(energy, blue, color="#1565c0", alpha=0.12)

ax.plot(
    energy, red, color="#d62728", linewidth=3.0,
    label=r"$C_{L,\beta}+C_\beta+C_b$ (20 atoms)",
)
ax.fill_between(energy, red, color="#d62728", alpha=0.12)

ax.set_xlabel("C 1s core-level shift relative to reference (eV)")
ax.set_ylabel("Normalized intensity")
ax.set_xlim(energy.min(), energy.max())
ax.set_ylim(0, 1.05)
ax.legend(title=f"Gaussian FWHM = {FWHM_EV:.2f} eV", frameon=False)
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(direction="out")

fig.savefig(PROJECT / "figures" / "planar_selected_C_envelopes.png", dpi=300, bbox_inches="tight")
fig.savefig(PROJECT / "figures" / "planar_selected_C_envelopes.pdf", bbox_inches="tight")

print(f"Blue: {len(blue_shifts)} atoms; Red: {len(red_shifts)} atoms")
print(f"Saved {PROJECT / 'figures' / 'planar_selected_C_envelopes.png'}")
print(f"Saved {PROJECT / 'figures' / 'planar_selected_C_envelopes.pdf'}")
