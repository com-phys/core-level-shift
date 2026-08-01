from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT / "archive" / "full_C_N" / "planar.scf.in"
SCF_INPUT = PROJECT / "input" / "planar_targeted.scf.in"
ISTATE_INPUT = PROJECT / "input" / "planar_targeted_CN.istate.in"
PSEUDO = PROJECT.parent / "pseudopotential"
SCRATCH = PROJECT / "output" / "restart_data"

# C_w atoms are intentionally kept as a separate, normal-carbon QE species.
# They participate in the ground-state density but are not mapped to a core-hole
# pseudopotential by initial_state.x.
C_W_ATOMS = set(range(7, 13)) | set(range(36, 42))

lines = SOURCE.read_text().splitlines()
result = []
in_positions = False
atom_index = 0

for line in lines:
    stripped = line.strip()
    if stripped.startswith("prefix"):
        line = "  prefix       = 'planar_targeted'"
    elif stripped.startswith("pseudo_dir"):
        line = f"  pseudo_dir   = '{PSEUDO}'"
    elif stripped.startswith("outdir"):
        line = f"  outdir       = '{SCRATCH}'"
    elif stripped.startswith("ntyp"):
        line = "  ntyp         = 7"

    if stripped == "ATOMIC_POSITIONS angstrom":
        in_positions = True
        atom_index = 0
    elif stripped == "K_POINTS gamma":
        in_positions = False

    if stripped.startswith("Ns  "):
        result.append(line)
        result.append("Cw  12.0110  C.pbe-rrkjus.UPF")
        continue

    if in_positions and stripped != "ATOMIC_POSITIONS angstrom" and stripped:
        atom_index += 1
        if atom_index in C_W_ATOMS:
            fields = line.split(maxsplit=1)
            line = f"Cw  {fields[1]}"

    result.append(line)

SCF_INPUT.write_text("\n".join(result) + "\n")

ISTATE_INPUT.write_text(
    "&INPUTPP\n"
    "  prefix    = 'planar_targeted'\n"
    f"  outdir    = '{SCRATCH}'\n"
    "  excite(2) = 5   ! selected C atoms only; Cw is type 7 and is not mapped\n"
    "  excite(3) = 6   ! all N atoms\n"
    "/\n"
)

print(f"Wrote {SCF_INPUT}")
print(f"Wrote {ISTATE_INPUT}")
print(f"Cw atoms excluded from core-hole mapping: {sorted(C_W_ATOMS)}")
