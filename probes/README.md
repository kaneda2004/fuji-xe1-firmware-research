AUTO_ACT probe scripts for Fujifilm X-E1

Context
- The X-E1 firmware contains AUTO_ACT script keywords and display/output tokens in the same vocabulary space.
- The strongest current candidates are `HDTV`, `K_PLAY`, `EVF_LCD`, and `V_AV`.
- These scripts are staged from safest to most speculative.

Requirements
- The camera only runs `AUTO_ACT.SCR` if EEPROM byte `0xa2` is set to `2`.
- The file must live on the SD card at `DCAA/AUTO_ACT.SCR`.
- The file must use Windows line endings.
- The scripts here already use CRLF line endings.

Suggested order
1. `01_verify_auto_act.SCR`
2. `02_hdtv_key_probe.SCR`
3. `03_route_probe_keys.SCR`
4. `04_v_av_set_probe.SCR`

What each probe does
- `01_verify_auto_act.SCR`
  - Creates a `WT_LOG` proof-of-execution marker and briefly presses `K_PLAY`.
- `02_hdtv_key_probe.SCR`
  - Creates a `WT_LOG` marker and toggles the documented `HDTV` key token.
- `03_route_probe_keys.SCR`
  - Tries a small routing sequence with `HDTV`, `EVF_LCD`, `DISP_B`, and `K_PLAY`.
- `04_v_av_set_probe.SCR`
  - Minimal builtin-state probe that tries `set V_AV = 1`.

Expected outcomes
- If `01_verify_auto_act.SCR` has no effect, do not trust the later probes yet.
- If `02_hdtv_key_probe.SCR` changes HDMI behavior at all, the key-event path is viable.
- If `03_route_probe_keys.SCR` changes whether HDMI leaves playback mode, the display-routing path is likely scriptable.
- If `04_v_av_set_probe.SCR` changes behavior, `V_AV` is probably a real builtin state token rather than just a dead vocabulary string.

Notes
- The AUTO_ACT docs only explicitly document `set` with user variables and EEPROM bytes. `set V_AV = 1` is an informed experiment, not a confirmed command.
- The key probes are grounded more strongly because FujiHack documents `HDTV`, `K_PLAY`, and `EVF_LCD` as key names.
