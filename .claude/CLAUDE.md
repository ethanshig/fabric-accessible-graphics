# pai-radical-accessibility — AI Guidelines

## Screen Reader Mode (JAWS / NVDA)

This project is used by blind and low-vision users with JAWS or NVDA screen readers.
All AI output MUST follow these rules. Violations make the tool unusable.

MANDATORY OUTPUT RULES:
- Plain text only. No markdown: no **, no ##, no ```, no ---, no bullet symbols
- No emojis anywhere
- No tables. Use one item per line with a label prefix instead
- No multi-column layouts
- One fact per line. Short sentences.
- Keep responses under 10 lines when possible
- Read back command results verbatim. Do not paraphrase or add commentary
- When reporting errors, include the exact error text and a suggested fix
- Never say "here is the output" or "let me" or "I will now" — just give the output
- Never produce ANSI escape codes, color codes, or terminal formatting in output
- When asking questions, state the question clearly, then list each option on its own
  line as "1. option" "2. option" etc. Always end with "Type a number or your answer."

INTERACTION RULES:
- Do not use the AskUserQuestion tool with more than 3 options
- Prefer asking one question at a time, not multiple
- After every tool use, give a one-line status: what happened, success or failure
- When a long operation starts, say what is happening and approximately how long
- When done with a task, give a clear "Done." line so the screen reader announces it

## TACT — Tactile Conversion CLI

When the user asks to convert an image to tactile:

1. Ask what image and where it is
2. Suggest an appropriate preset based on image type
3. Run `tact convert` with `--verbose` so the user hears each step
4. Read back the results: output path, density percentage, number of Braille labels

Key commands:
- `tact convert IMAGE --preset NAME --verbose` — convert one image
- `tact convert IMAGE --detect-text --braille-grade 2 --verbose` — with Braille
- `tact batch INPUT_DIR OUTPUT_DIR --preset NAME --verbose` — batch convert
- `tact presets` — show available presets

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
- `tasc connect` — test Rhino connection (auto-sets LightPen display mode)
- `tasc display [MODE]` — get or set viewport display mode (e.g., LightPen, Wireframe)
- `tasc capture [FILE]` — capture viewport for TACT (auto Pen mode, white bg, black lines)

Rhino-to-TACT pipeline:
- Design uses LightPen (dark bg, light lines) — good for sighted review
- TACT needs Pen mode (white bg, black lines) — required for correct thresholding
- `tasc capture` handles the switch automatically: Pen for capture, restore LightPen after
- NEVER send a LightPen viewport directly to TACT — result will be a black square

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

## acclaude — Accessible Claude Client

A JAWS-compatible wrapper around Claude Code that bypasses the Ink TUI.
Launcher: `bin/acclaude.bat` (Windows) or `bin/acclaude` (bash/WSL2).
Uses `claude -p` headless mode with `--resume SESSION_ID` for multi-turn.
Slash commands: /help, /repeat, /history, /new, /quit.
Session memory persists at `~/.radical-accessibility/memory/`.
