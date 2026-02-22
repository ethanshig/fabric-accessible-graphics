# fabric-accessible-graphics — AI Guidelines

## Accessibility Mode (JAWS Screen Reader)

When working with Daniel (or any screen reader user):
- Output plain text only. No markdown formatting (no **, no ##, no ```)
- No emojis in output
- One fact per line
- Keep responses short and direct
- Read back command results verbatim — do not paraphrase or add commentary

## TASC Command Priority

When the user asks you to create or modify geometry in Rhino:

1. CHECK if TASC has a command for it (see command list below)
2. If YES: use the TASC command via Bash. Ask the user for any missing parameters.
3. If NO: fall back to RhinoPython via RhinoMCP. Log what was missing.

TASC commands (deterministic, preferred):
- `tasc site W D` — site boundary
- `tasc grid SPACING` — structural grid
- `tasc zone NAME W D --at X,Y` — program zone
- `tasc bay NAME NxN --spacing SX SY --at X,Y` — structural bay with columns
- `tasc corridor BAY on|off --axis x|y --width W` — corridor in bay
- `tasc void BAY SHAPE WxH --at X,Y` — void in bay
- `tasc label NAME "text" --braille "braille"` — accessible labels
- `tasc describe` — full text description
- `tasc list` — short listing
- `tasc undo` — revert last change
- `tasc export piaf|3dm|text` — export
- `tasc remove NAME` — remove zone or bay
- `tasc reset` — clear all
- `tasc connect` — test Rhino connection

RhinoPython (flexible, fallback):
- Custom geometry not covered by TASC commands
- One-off operations
- Advanced Rhino features (materials, rendering, analysis)

## Parameter Gathering

Before running a TASC command, gather required parameters from the user:
- For `bay`: name, grid dimensions (NxN), spacing
- For `zone`: name, width, depth, position
- For `corridor`: which bay, axis, width
- Do NOT guess dimensions. Ask.

## Feedback

After running a TASC command, read back the output to the user exactly.
Do not add interpretation or commentary unless asked.
