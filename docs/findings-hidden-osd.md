# Hidden OSD and Service Menu

This writeup records the public, high-level research state. It intentionally
avoids publishing patched firmware images or turnkey patch byte sequences.

## Interesting Strings and Tables

| Raw offset | Observation |
| --- | --- |
| `0x35f804` | `DISP_` token table with nearby imaging/menu keys |
| `0x388e27` | `HDTV` token in a settings/key table |
| `0x388e44` | Another `DISP_` token near `HDTV`, `K_PLAY`, `VS_0`, `C_DIAL`, `MF_A` |
| `0x48c5fc` | `OSD DEBUG MODE SCREEN SELECT` |
| `0x48c61c` | `SCREEN   <UP/DOWN>    : ` |
| `0x48c638` | `WARNING  <RIGHT/LEFT> : ` |
| `0x48c654` | `KEY_OK  IS PUSHED TO DISPLAY` |
| `0x48c674` | `KEY_BACK IS PUSHED TO RETURN` |

The `HDTV` and `DISP_` strings appear in token/settings tables. The OSD debug
strings are adjacent to executable ARM code and are a better anchor for
control-flow analysis.

## OSD Cluster

Function-like ARM code exists from raw `0x48c4fc` through at least
`0x48c818`.

The function at raw `0x48c6bc` is a real ARM function. It reads state from
globals near `0x009d01d8` and `0x009d01e4`, branches on a small mode value,
and calls nearby display helpers.

Relevant state fields observed in this cluster:

| Field offset | Working interpretation |
| --- | --- |
| `0x348c` | High-level UI/debug state ID |
| `0x5bf1` | OSD display mode selector with at least three states |
| `0x5bf3` | Gate for the alternate display path |
| `0x5bf5` | Gate for showing screen/warning values |
| `0x5bf6` | Gate for detailed numeric screen rendering |
| `0x5bf7` | Presentation/style toggle |
| `0x5bfc` | Likely hidden `SCREEN` value |
| `0x5c00` | Likely hidden `WARNING` value |

The strongest clean-display candidate in this cluster is the `0x5bf1` mode
selector. That remains a hypothesis until tied to a proven live output path.

## Service Menu

The function at rebased `0x01471bdc` behaves like a 7-page hidden
service/debug menu. It gates on a global flag and dispatches to page handlers
based on a page selector.

Page-level triage:

| Page | Handler | Notes |
| --- | --- | --- |
| P1 | `0x014716d4` | Minimal title-style page |
| P2 | `0x01471868` | Read-heavy diagnostic/status list |
| P3 | `0x014715a4` | Stateful UI transition page |
| P4 | `0x01471580` | Stateful display/menu refresh path |
| P5 | `0x01471380` | Read-heavy diagnostic list |
| P6 | `0x014710c0` | Version/info page |
| P7 | `0x01470ed0` | Diagnostic/log-style page |

Hardware testing confirmed that a service-menu probe could render P6 on a
real body. The observed strings included software version, EEP adjust date,
and script version fields.

## Hardware Observation

An important accidental result: after entering the P6 service page and letting
the body auto-sleep, waking with a half-press produced a clean internal
live-view state. Autofocus and shutter continued to work. HDMI did not follow
that state.

Interpretation:

- The service/debug path can leak into a useful internal display state.
- That does not prove live HDMI is supported on X-E1.
- The problem splits into two independent questions:
  - Is there a usable live HDMI route?
  - Can overlays be suppressed once such a route is active?

