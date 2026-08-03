# Core-Level Shift Calculations

Completed Quantum ESPRESSO initial-state C 1s and N 1s core-level-shift results
for Planar, protonated PLDC-COOH, Cross, TwistedH2, TwistedO2, TWco, and
TWDCOH molecular structures.

The repository is prepared for collaborators who want to download and inspect
the finished results. Quantum ESPRESSO does **not** need to be installed to view
the reports, figures, structures, CSV tables, or completed text outputs.

## Main downloads

- [All core-level-shift plots in one PDF](output/pdf/all_core_level_shift_plots_comparison.pdf)
- [Full editable Planar/PLDC report](planarCOOH/report/Full_Planar_PLDC_All_Carbon_CLS_Report.docx)
- [Full Planar/PLDC PDF report](planarCOOH/report/Full_Planar_PLDC_All_Carbon_CLS_Report.pdf)
- [Planar versus PLDC–COOH spectrum](planarCOOH/figures/planar_vs_PLDC_COOH_all_carbon_envelopes_zoomed.png)
- [Planar versus PLDC-COOH N 1s spectrum](planarCOOH/figures/planar_vs_PLDC_COOH_N1s_envelopes.png)
- [Five-structure C 1s comparison](comparison_remaining/remaining_structures_C1s_comparison.png)
- [Five-structure N 1s comparison](comparison_remaining/remaining_structures_N1s_comparison.png)
- [Planar labeled structure](planar/figures/Planar_carbon_groups.png)
- [PLDC–COOH labeled structure](planarCOOH/figures/PLDC_COOH_carbon_groups.png)
- [Combined per-atom shifts](planarCOOH/output/planar_vs_PLDC_COOH_all_carbon_atom_shifts.csv)
- [Five-structure per-atom C/N shifts](comparison_remaining/remaining_structures_C_N_atom_shifts.csv)

## Folder organization

- `planar/`: Planar inputs, completed outputs, figures, report, structures,
  scripts, and archived historical material.
- `planarCOOH/`: Protonated PLDC–COOH inputs, completed outputs, comparison
  figures, full report, structures, scripts, and archived historical material.
- `cross/`, `twistedH2/`, `twistedO2/`, `TWco/`, and `TWDCOH/`: complete
  inputs, SCF and `initial_state.x` outputs, atom/group CSV data, labeled
  structures, figures, scripts, and restart data.
- `comparison_remaining/`: common-axis C 1s and N 1s comparison figures and
  combined CSV tables.
- `output/pdf/`: the bookmarked 18-page plot-comparison PDF.
- `script/`: reusable preparation, analysis, plotting, and batch-run scripts.
- `pseudopotential/`: Pseudopotentials used in the calculations for provenance
  and reproducibility.

## Calculation summary

- Planar SCF: 32 iterations, 15 min 05 s wall time.
- Planar `initial_state.x`: approximately 13 s.
- PLDC–COOH SCF: 40 iterations, 1 h 38 min wall time.
- PLDC–COOH `initial_state.x`: 1 min 06 s.
- Corrected PLDC-COOH N SCF: 3 restart iterations, 1 min 40 s wall time.
- Corrected PLDC-COOH N `initial_state.x`: 14 s wall time.
- Gaussian spectral broadening: 0.35 eV FWHM.
- Shift convention: reference contribution minus site contribution.

## Quantum ESPRESSO restart data

Complete restart directories are included for PLDC-COOH, its corrected N run,
Cross, TwistedH2, TwistedO2, TWco, and TWDCOH. Wavefunction and charge-density
`.dat` files are stored with Git LFS because the wavefunctions exceed GitHub's
normal per-file limit. A collaborator should install Git LFS before cloning, or
run `git lfs pull` afterward. Quantum ESPRESSO is not required merely to inspect
the finished outputs, CSV tables, figures, and reports.
