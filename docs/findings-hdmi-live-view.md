# HDMI and Live-View Constraints

The X-E1 owner's manual describes HDMI/TV output in the playback section, not
as a live shooting output feature. That matches hardware observations so far:
the body can be pushed into interesting internal clean live-view states, but
HDMI has not been observed following live view.

## Current Model

Treat the HDMI problem as two separate research tracks:

1. Find or activate a live output path for HDMI.
2. Suppress debug/OSD overlays on that path.

The hidden OSD cluster is relevant to the second track. It may not solve the
first track.

## AUTO_ACT Probes

The firmware contains AUTO_ACT script vocabulary around raw `0x388cc2` through
`0x389475`.

Observed script keywords and related tokens include:

- `wait`
- `WAITSET`
- `func`
- `LABEL`
- `key`
- `jump`
- `random`
- `END`
- `WT_LOG`
- `set`
- `HDTV`
- `DISP_`
- `K_PLAY`
- `EVF_LCD`

The probe scripts in `probes/` are staged from least speculative to most
speculative:

1. `01_verify_auto_act.SCR`
2. `02_hdtv_key_probe.SCR`
3. `03_route_probe_keys.SCR`
4. `04_v_av_set_probe.SCR`

These scripts are included because they are small original test inputs, not
firmware-derived binaries.

## Open Questions

- Is HDMI live-view support absent in hardware, disabled in firmware, or hidden
  behind a mode gate?
- Does the `HDTV` token route through a key-event path only, or through a real
  output-routing state machine?
- Is the `V_AV` token a writable builtin state or just vocabulary residue?
- Does any firmware path update the `0x5bf1` OSD mode selector from a menu,
  table, or indirect event dispatcher?

