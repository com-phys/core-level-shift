PLANAR VERSUS PROTONATED PLDC — ALL-CARBON CORE-LEVEL SHIFTS
Completed: 1 August 2026

Full report:
  Full_Planar_PLDC_All_Carbon_CLS_Report.docx
  Full_Planar_PLDC_All_Carbon_CLS_Report.pdf

The 11-page report contains the labeled molecular structures and atom-group
indices, calculation workflow and equations, parameter-selection rationale,
convergence and timing information, numerical group results, spectra, limits,
and reproducibility paths.

Primary plots:
  planar_vs_PLDC_COOH_all_carbon_envelopes_zoomed.png/pdf
  planar_vs_PLDC_COOH_group_means_split.png/pdf

Numerical results:
  planar_all_carbon_atom_shifts.csv
  PLDC_COOH_all_carbon_atom_shifts.csv
  planar_vs_PLDC_COOH_all_carbon_atom_shifts.csv
  planar_vs_PLDC_COOH_group_summary.csv

Reference and sign convention:
  reference = mean(C_b + C_w) within each molecule
  shift = initial_state(reference) - initial_state(site)
  This matches the Quantum ESPRESSO CLS_IS_example convention.

Broadening:
  Unit-area Gaussian per carbon atom, FWHM = 0.35 eV.
  Blue background envelope = C_L,alpha + C_alpha.
  Amber background envelope = all remaining carbon groups.
  Individual group curves are in the foreground; the total line is removed.

Convergence:
  Planar: 32 SCF iterations, 15 min 05 s wall.
  PLDC-COOH: 40 SCF iterations, 1 h 38 min wall; final estimated accuracy
  5.6e-7 Ry. initial_state.x took 1 min 06 s.

Modeling note:
  PLDC_COOH.xyz is neutral ZnC46H28N4O4. H82 was added to O78 and H83 to
  O80 with O-H = 0.98 A. This was a single-point calculation; the constructed
  O-H geometry was not optimized.
