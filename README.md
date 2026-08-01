# Core-Level Shift Calculations

Completed Quantum ESPRESSO initial-state C 1s core-level-shift results for the
Planar and protonated PLDC–COOH molecular structures.

The repository is prepared for collaborators who want to download and inspect
the finished results. Quantum ESPRESSO does **not** need to be installed to view
the reports, figures, structures, CSV tables, or completed text outputs.

## Main downloads

- [Full editable Word report](planarCOOH/report/Full_Planar_PLDC_All_Carbon_CLS_Report.docx)
- [Full PDF report](planarCOOH/report/Full_Planar_PLDC_All_Carbon_CLS_Report.pdf)
- [Planar versus PLDC–COOH spectrum](planarCOOH/figures/planar_vs_PLDC_COOH_all_carbon_envelopes_zoomed.png)
- [Carbon-group comparison](planarCOOH/figures/planar_vs_PLDC_COOH_group_means_split.png)
- [Planar labeled structure](planar/figures/Planar_carbon_groups.png)
- [PLDC–COOH labeled structure](planarCOOH/figures/PLDC_COOH_carbon_groups.png)
- [Combined per-atom shifts](planarCOOH/output/planar_vs_PLDC_COOH_all_carbon_atom_shifts.csv)
- [Group summary](planarCOOH/output/planar_vs_PLDC_COOH_group_summary.csv)

## Folder organization

- `planar/`: Planar inputs, completed outputs, figures, report, structures,
  scripts, and archived historical material.
- `planarCOOH/`: Protonated PLDC–COOH inputs, completed outputs, comparison
  figures, full report, structures, scripts, and archived historical material.
- `pseudopotential/`: Pseudopotentials used in the calculations for provenance
  and reproducibility.

## Calculation summary

- Planar SCF: 32 iterations, 15 min 05 s wall time.
- Planar `initial_state.x`: approximately 13 s.
- PLDC–COOH SCF: 40 iterations, 1 h 38 min wall time.
- PLDC–COOH `initial_state.x`: 1 min 06 s.
- Gaussian spectral broadening: 0.35 eV FWHM.
- Shift convention: reference contribution minus site contribution.

## Repository size note

Large Quantum ESPRESSO restart binaries were intentionally excluded because
they are unnecessary for viewing the completed results and exceed GitHub's
normal file-size limit. Specifically, `wfc1.dat` (361 MB),
`charge-density.dat` (57 MB), and the redundant 390 MB ZIP archive are not
included. The completed `.out` files and all scientific deliverables are
included.
