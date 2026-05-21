# Methodology

The research workflow is designed to be reproducible from a local firmware
image.

## Workflow

1. Place the firmware update image in a local working directory.
2. Record the file size and SHA-256 hash.
3. Parse the update header with `tools/extract_fujifilm_firmware.py`.
4. Extract the bit-flipped payload locally.
5. Import the payload into Ghidra as raw ARM little-endian code.
6. Start with strings and token tables, then trace xrefs into executable code.
7. Name functions only after checking call sites and state references.
8. Validate hypotheses with the smallest possible hardware probe.
9. Keep generated payloads, Ghidra databases, and patch artifacts in local
   working directories.

## Evidence Standards

Labels in the docs use the following bar:

- Confirmed: observed directly in firmware and supported by hardware behavior.
- Strong lead: supported by multiple firmware references, not fully proven.
- Hypothesis: plausible interpretation that needs more tracing or hardware
  validation.

## Notes Style

The notes stay focused on:

- Original notes and diagrams.
- Offsets, hashes, and small metadata.
- Short string references.
- Tooling written from scratch.
- Small metadata samples that do not contain firmware bytes.
