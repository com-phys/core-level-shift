PLANAR–PLDC COMPARISON

planar_vs_PLDC_structures.png/pdf:
  Completed structural comparison. The two COO groups present in PLDC are
  highlighted.

PLDC.xyz:
  Supplied 81-atom structure (ZnC46H26N4O4).

PLDC_COOH.xyz:
  Protonated 83-atom structure (ZnC46H28N4O4). Two H atoms were added, one to
  each carboxyl group: H82 on O78 and H83 on O80. The selected O atoms have the
  longer C-O distances in the supplied geometry, consistent with C-OH.

PLDC_COOH_carbon_groups.png/pdf:
  Updated carbon-group figure showing both newly added O-H hydrogen atoms.

pldc_targeted.scf.in, pldc_targeted_CN.istate.in, prepare_pldc_cls.py:
  Prepared templates only. They are not completed results.

The PLDC XYZ has COO fragments without acidic H atoms. Before calculating a
reliable isolated-molecule spectrum, confirm whether the intended model is a
dianion (charge -2), a neutral open-shell species, or a protonated COOH model.
