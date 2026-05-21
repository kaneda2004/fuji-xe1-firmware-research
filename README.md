# Fujifilm X-E1 Firmware Research

Reverse-engineering notes and tooling for the Fujifilm X-E1 firmware update
format, extracted ARM payload, hidden display/debug-menu paths, and AUTO_ACT
script behavior.

This repository contains original notes, scripts, and small analysis helpers.

## Goals

- Document the update container and payload extraction format.
- Record Ghidra import settings and address conventions.
- Track hidden OSD, service-menu, and HDMI/live-view findings.
- Keep reproduction steps tied to a user-supplied firmware image.

## Current Scope

The research target is a Fujifilm X-E1 firmware update image identified as
version `2.71`.

The public findings currently cover:

- DAT container header parsing and payload bit-flip extraction.
- Ghidra import settings for the extracted monolithic ARM payload.
- Address conventions for raw offsets and rebased analysis.
- Hidden OSD/debug-menu cluster triage.
- Service-menu and HDMI/live-view research constraints.
- AUTO_ACT probe scripts for key/event vocabulary experiments.

## Repository Layout

```text
docs/                  Research writeups and repository scope
tools/                 Original analysis helpers
probes/                Small AUTO_ACT probe scripts
samples/               Metadata-only sample output
```

## Quick Start

Extract metadata and the bit-flipped payload from a user-supplied firmware
file:

```sh
python3 tools/extract_fujifilm_firmware.py FWUP0001.DAT -o extracted
```

The extractor writes:

- `extracted/FWUP0001.bin`
- `extracted/FWUP0001.header.json`

Generated outputs are ignored by Git.

## Key Findings

See the detailed notes:

- [Firmware Format](docs/firmware-format.md)
- [Ghidra Import](docs/ghidra-import.md)
- [Hidden OSD and Service Menu](docs/findings-hidden-osd.md)
- [HDMI and Live-View Constraints](docs/findings-hdmi-live-view.md)
- [Repository Scope](docs/repo-scope.md)

## Safety

Firmware work can brick hardware. Treat every experiment as hardware-risky
and work from your own local copies.

## License

Original tooling and documentation in this repository are released under the
MIT license. See [NOTICE.md](NOTICE.md) for the scope of that license.
