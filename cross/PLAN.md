# cross calculation plan

Canonical structure: `structure/cross.xyz`  
Composition: ZnC44H28N4; 77 atoms.

Follow `../CALCULATION_PLAN.md`. Start with this structure because its atom
count and composition match Planar. First verify that the Planar carbon and
nitrogen group indices still represent the same bonded sites after the cross
distortion. Then prepare C 1s and N 1s inputs, run SCF and `initial_state.x`,
extract all requested sites, plot the grouped envelopes, compare against
Planar, and record the measured runtime.
