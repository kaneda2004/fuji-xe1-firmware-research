# Tools

## `extract_fujifilm_firmware.py`

Parses the small Fujifilm DAT header and writes a bit-flipped payload plus a
metadata JSON file.

```sh
python3 tools/extract_fujifilm_firmware.py FWUP0001.DAT -o extracted
```

Generated outputs are ignored by Git.

## `ghidra/ghidra_query.py`

Runs small headless queries against a local PyGhidra project. The Ghidra
project itself is not included because it is derived from proprietary firmware.

