PLANAR-COOH / PLDC-COOH CORE-LEVEL-SHIFT PROJECT

input/      Quantum ESPRESSO SCF and initial_state.x input files
output/     SCF/initial-state outputs, restart data, and numerical CSV results
figures/    Final PLDC-COOH and Planar-versus-PLDC comparison figures
report/     Final full DOCX/PDF report and report notes
archive/    Older plots, reports, trial inputs, scripts, and unused structures
script/     Active preparation, analysis, plotting, and report scripts
structure/  Canonical PLDC and protonated PLDC-COOH structures and assignments

Canonical structure:
  structure/PLDC_COOH.xyz

Canonical calculation inputs:
  input/pldc_cooh_allC.scf.in
  input/pldc_cooh_allC.istate.in

Primary report:
  report/Full_Planar_PLDC_All_Carbon_CLS_Report.docx
  report/Full_Planar_PLDC_All_Carbon_CLS_Report.pdf

The active input uses the centralized pseudopotentials in ../pseudopotential.
The complete QE restart directory is included. Its large wavefunction and
charge-density files are stored with Git LFS.
