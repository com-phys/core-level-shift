# Core-Level-Shift Plan for the Remaining Structures

## Objective

Calculate and compare initial-state C 1s and N 1s core-level shifts for five
additional molecular structures using the same controlled Quantum ESPRESSO
workflow used for Planar and PLDC–COOH:

| Project | Canonical structure | Composition | Atoms |
|---|---|---:|---:|
| cross | `cross/structure/cross.xyz` | ZnC44H28N4 | 77 |
| TWco | `TWco/structure/TWco.xyz` | ZnC46H30N4O6 | 87 |
| TWDCOH | `TWDCOH/structure/TWDCOH.xyz` | ZnC46H30N4O6 | 87 |
| twistedH2 | `twistedH2/structure/twistedH2.xyz` | ZnC44H30N4 | 79 |
| twistedO2 | `twistedO2/structure/twistedO2.xyz` | ZnC44H30N4O2 | 81 |

Oxygen core-level shifts are not included in the current scope. They can be
added later with a validated O 1s core-excited pseudopotential.

## Recommended execution order

1. **cross** — same atom count and composition as Planar; use it to validate
   atom ordering, group transfer, and the automated workflow.
2. **twistedH2** — adds two hydrogens but no new carbon or oxygen sites.
3. **twistedO2** — validates the treatment of the two oxygen-containing sites.
4. **TWco** — larger 87-atom oxygenated derivative.
5. **TWDCOH** — run with the same settings as TWco for a controlled comparison.

## Phase 1 — Structure and chemical-state validation

For each XYZ file:

1. Confirm atom count, elemental composition, duplicate atoms, short contacts,
   bond connectivity, molecular charge, protonation, and expected spin state.
2. Measure the molecular dimensions. Choose a cubic cell that leaves at least
   7 Å vacuum from the molecule to the nearest periodic image; start from
   25 Å and enlarge it if required.
3. Confirm whether atoms 2–49 retain the same chemical identities and ordering
   as the Planar structure. Do not reuse group indices only because the numbers
   look similar.
4. Assign every carbon to `C_L_alpha`, `C_alpha`, `C_L_beta`, `C_beta`, `C_M`,
   `C_b`, `C_w`, or a new substituent group. Assign all nitrogen atoms to `N_L`
   or `N` where chemically appropriate.
5. Save an assignment CSV and a labeled molecular figure in `structure/` and
   `figures/` before preparing QE inputs.

## Phase 2 — Quantum ESPRESSO inputs

Use the existing Planar/PLDC setup as the baseline:

- Exchange–correlation: PBE.
- Pseudopotentials: centralized `pseudopotential/` directory.
- Initial cell: 25 Å cubic, subject to the vacuum check.
- Isolated molecule: `assume_isolated = 'mt'`.
- Sampling: Gamma point.
- Working cutoffs: `ecutwfc = 30 Ry`, `ecutrho = 180 Ry`.
- Occupations: Marzari–Vanderbilt smearing, `degauss = 0.02 Ry`.
- SCF mixing: local-TF, initial `mixing_beta = 0.20`.
- Threshold: `conv_thr = 1.0d-6 Ry`.
- Atom-resolved calculation: `nosym = .true.`, `noinv = .true.`.

Before production calculations, verify that total charge and spin give the
intended electron count. If an SCF is unstable, reduce `mixing_beta` before
changing the physical model.

## Phase 3 — Core-level-shift calculation

1. Prepare normal and C 1s/N 1s core-excited species in the SCF input.
2. Run one converged SCF calculation for the complete molecule.
3. Run `initial_state.x` using the converged restart data.
4. Verify that every requested C and N atom maps to the intended excited
   pseudopotential type; check explicitly that no site is silently omitted.
5. Record SCF iterations, total energy, final estimated accuracy, CPU time, and
   wall time in the project report.

## Phase 4 — Analysis and spectra

1. Extract per-atom initial-state contributions to CSV.
2. Apply the Quantum ESPRESSO sign convention
   `shift(site) = IS(reference) - IS(site)`.
3. Use a chemically common reference across the structures. The provisional
   reference is the mean of `C_b + C_w`; confirm that these sites remain
   comparable after inspecting their distributions.
4. Calculate group mean, standard deviation, minimum, maximum, multiplicity,
   and atom indices.
5. Build unit-area Gaussian envelopes using 0.35 eV FWHM. Retain separate
   foreground group curves and the established background envelopes.
6. Produce individual plots and a shared-axis comparison with Planar and
   PLDC–COOH. Do not include a total black line unless requested.

## Phase 5 — Quality checks and reporting

For each project, confirm:

- SCF convergence and absence of fatal QE warnings.
- Correct number of extracted C and N sites.
- Complete carbon-group assignment with no overlap or missing carbon.
- Reproducibility of CSV values from the saved `initial_state.x` output.
- Plot labels, colors, reference definition, and broadening recorded explicitly.
- A PDF/DOCX report containing the labeled structure, method, parameters,
  parameter rationale, results, limitations, and measured calculation time.

## Expected project files

- `input/`: SCF and `initial_state.x` inputs.
- `output/`: completed QE outputs, restart data, and result CSVs.
- `figures/`: labeled structure and spectral plots.
- `report/`: final DOCX and PDF report.
- `script/`: preparation, extraction, analysis, and plotting scripts.
- `structure/`: canonical XYZ and group-assignment CSV.
- `archive/`: superseded trials only.

No new calculation should be treated as production-ready until Phase 1 is
signed off, especially for TWco and TWDCOH, whose oxygen/protonation chemistry
and additional carbon groups must be identified explicitly.
