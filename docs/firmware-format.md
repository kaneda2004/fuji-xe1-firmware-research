# Firmware Format

The X-E1 update file inspected in this project uses a small header followed by
a transformed payload.

## Header

Observed values for the `FWUP0001.DAT` sample:

| Field | Value |
| --- | --- |
| Header type | `4` |
| Header code size | `512` bytes |
| Header size | `532` bytes |
| Firmware version | `2.71` |
| End marker | `1` |

The header parser in `tools/extract_fujifilm_firmware.py` supports the header
types found in the FujiHack patcher lineage:

```python
HEADER_CODE_SIZES = {
    1: 64,
    2: 128,
    3: 512,
    4: 512,
    5: 512,
    6: 512,
    8: 512,
}
```

## Payload Transform

The payload starts immediately after the header. For header type `4`, that
means offset `0x214` decimal `532`.

Extraction rule:

```python
payload[i] = (~dat[header_size + i]) & 0xff
```

This produces a monolithic ROM-like image. It is not a standard archive or
filesystem image.

## Checksums

The header contains a checksum field. The extractor records it for comparison
against local experiments.

## Sample Metadata

`samples/FWUP0001.header.example.json` is metadata-only. It records sizes,
version fields, and hashes useful for reproducing the analysis from a
local firmware image.
