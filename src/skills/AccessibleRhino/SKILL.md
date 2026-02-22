---
name: AccessibleRhino
description: Programmatic Rhino design for blind and low-vision architects via the TASC CLI. USE WHEN design in Rhino, create floor plan, place structural bay, TASC command, site layout, add columns, place zone, Rhino design, accessible architecture, programmatic design.
context: fork
---

# AccessibleRhino

Programmatic architectural design through the TASC (Tactile Architecture Scripting Console) CLI. Gives blind and low-vision architects direct, deterministic control of Rhino site layouts with screen-reader-friendly text feedback.

## When to Use This Skill

Use AccessibleRhino when:

- **Creating site layouts** from scratch (site boundary, grid, zones, bays)
- **Structural design** with column grids, corridors, and voids
- **Modifying existing layouts** (add/remove zones, bays, undo)
- **Exporting designs** to Rhino .3dm, tactile PIAF PDF, or text description
- User mentions Rhino, TASC, or programmatic design

## When NOT to Use

Use **TactileConversion** instead when:

- Converting an existing image to tactile format
- Source is a photograph or scan, not a design intent

Use **TactileGeneration** instead when:

- AI-powered image creation is needed
- Source is too complex for code-based processing

## TASC Command Reference

TASC commands are deterministic and preferred over RhinoPython for supported operations.

### Site and Grid

```bash
tasc site 200 150                    # 200x150 foot site boundary
tasc grid 10                         # 10-foot structural grid
```

### Zones (Program Areas)

```bash
tasc zone living 50 40 --at 10,10   # rectangular zone
tasc zone lobby --corners "0,0 20,0 20,15 0,15"  # polygon zone
```

### Bays (Structural Column Grids)

```bash
tasc bay A 6x3 --spacing 24 24 --at 18,8   # 6x3 bay with columns
tasc bay B 3x3 --spacing-x 24,30,24        # irregular spacing
```

### Corridors and Voids

```bash
tasc corridor A on --axis x --width 8       # east-west corridor in bay A
tasc void A rectangle 30x18 --at 90,44     # courtyard in bay A
```

### Labels

```bash
tasc label A "Library" --braille "..."  # text + Braille label
```

### Inspection and Export

```bash
tasc list                               # short listing
tasc describe                           # full text description
tasc export 3dm                         # Rhino file (works offline)
tasc export piaf                        # tactile PDF via TACT
tasc export text                        # text description
```

### Undo and Remove

```bash
tasc undo                               # revert last command
tasc remove kitchen                     # remove zone or bay by name
tasc reset                              # clear everything
```

## Bay vs Zone

- **Zone**: Named program area (living, kitchen). Freeform shape. No structure.
- **Bay**: Structural column grid (6x3 at 24ft). Contains columns. Supports corridors and voids.

Both coexist on the same site. Use zones for spatial programming, bays for structural logic.

## Rhino Connection

TASC works in three modes:

1. **Live viewport** (RhinoMCP running) -- geometry appears in Rhino as you type
2. **Offline .3dm export** -- no Rhino needed, open exported files later
3. **Text-only** -- full feedback without any Rhino connection

## Parameter Gathering

Before running TASC commands, gather required parameters from the user:

- For `bay`: name, grid dimensions (NxN), spacing
- For `zone`: name, width, depth, position
- For `corridor`: which bay, axis, width
- Do NOT guess dimensions. Ask.

## Context Files

- `lib/tasc-core/README.md` -- Full CLI and DSL reference
- `.claude/CLAUDE.md` -- Screen-reader interaction rules (plain text only, no markdown)

## Output

All feedback is screen-reader-friendly plain text. After running any TASC command, read back the output to the user exactly without interpretation.
