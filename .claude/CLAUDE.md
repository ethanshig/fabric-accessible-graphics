# pai-radical-accessibility — AI Guidelines

## Accessibility Mode (JAWS Screen Reader)

Both CLIs (tact and tasc) are designed for screen reader users. All AI output
in this project must follow these rules:

- Output plain text only. No markdown formatting (no **, no ##, no ```)
- No emojis in output
- One fact per line
- Keep responses short and direct
- Read back command results verbatim — do not paraphrase or add commentary
- When reporting errors, include the exact error text and a suggested fix
- Never say "here is the output" — just give the output

## TACT — Tactile Conversion CLI

When the user asks to convert an image to tactile:

1. Ask what image and where it is
2. Suggest an appropriate preset based on image type
3. Run `tact image-to-piaf` with `--verbose` so the user hears each step
4. Read back the results: output path, density percentage, number of Braille labels

Key commands:
- `tact image-to-piaf IMAGE --preset NAME --verbose` — convert one image
- `tact image-to-piaf IMAGE --detect-text --braille-grade 2 --verbose` — with Braille
- `tact batch INPUT_DIR OUTPUT_DIR --preset NAME --verbose` — batch convert
- `tact list-presets` — show available presets

When reporting TACT results, always include:
- Output file path
- Density percentage and whether it is acceptable
- Number of text labels detected (if --detect-text used)
- Number of pages (if tiled)
- Any warnings or errors from the conversion

## TASC — Architectural Design CLI

When the user asks to create or modify geometry in Rhino:

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

Before running any command, gather required parameters from the user:
- For TACT: image path, preset preference, whether Braille labels are wanted
- For `bay`: name, grid dimensions (NxN), spacing
- For `zone`: name, width, depth, position
- For `corridor`: which bay, axis, width
- Do NOT guess dimensions or file paths. Ask.

## Feedback

After running any CLI command (tact or tasc), read back the output to the user
exactly. Do not add interpretation or commentary unless asked.
