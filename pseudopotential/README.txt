CENTRAL QUANTUM ESPRESSO PSEUDOPOTENTIALS

This folder is the single canonical location for pseudopotentials used by both
the Planar and Planar-COOH calculations. Active SCF input files point here.

Normal species:
  C.pbe-rrkjus.UPF
  H.pbe-rrkjus.UPF
  N.pbe-van_ak.UPF
  O.pbe-rrkjus.UPF
  Zn.pbe-van.UPF

Core-excited species:
  C.star1s-pbe-rrkjus.UPF
  N.star1s-pbe-van.UPF

The PLDC restart bundle contains relative symbolic links to these canonical
files, avoiding duplicate storage while retaining the filenames expected by QE.
