# Ghidra Import

The extracted X-E1 payload is best treated as a raw ARM firmware image.

## Import Settings

| Setting | Value |
| --- | --- |
| Format | Raw binary |
| Endianness | Little endian |
| ISA | ARM 32-bit |
| Suggested language | `ARM:LE:32:v7` |
| Preferred analysis base | `0x01000000` |

Thumb did not appear to be the primary execution mode in the regions inspected.

## Address Convention

The notes use raw file offsets unless explicitly marked as rebased addresses.
For Ghidra work, rebasing to `0x01000000` made switch tables and branch targets
easier to reason about.

Examples:

| Raw offset | Rebased address |
| --- | --- |
| `0x48c6bc` | `0x0148c6bc` |
| `0x48d514` | `0x0148d514` |
| `0x4c3a38` | `0x014c3a38` |
| `0x4c1818` | `0x014c1818` |

## Helper Script

`tools/ghidra/ghidra_query.py` is a small PyGhidra helper for headless queries
against an already-created Ghidra project.

Example:

```sh
GHIDRA_INSTALL_DIR=/path/to/ghidra \
python3 tools/ghidra/ghidra_query.py \
  --project-dir pyghidra_xe1_base1000000 \
  --project-name xe1_base1000000 \
  --program-name FWUP0001_ARMv7 \
  functions 0x0148c000 0x0148e000
```

Recreate the Ghidra project locally with the import settings above.
