# Floor Plans - Tactile Conversion Guidelines

VERSION: 1.0
LAST_UPDATED: 2025-12-26
PARENT_DOC: ../ARCHITECTURAL_TACTILE_GUIDELINES.md

---

## 1. What is a Floor Plan

A floor plan is a horizontal section through a building, typically cut at about 4 feet above the floor level. It shows the arrangement of spaces, walls, doors, windows, and circulation paths as seen from above.

### When Students Encounter Floor Plans

- **Design Studio**: Creating and analyzing spatial layouts
- **Architectural History**: Understanding historical building organization
- **Building Technology**: Analyzing structure and systems integration
- **Site Planning**: Understanding building footprint in context

### Common Floor Plan Types

| Type | Purpose | Complexity |
|------|---------|------------|
| Schematic | Early design, room relationships | Simple |
| Design Development | Refined layouts with dimensions | Moderate |
| Construction | Full detail with annotations | Complex |
| Furniture | Interior layouts and clearances | Moderate |
| Finish | Material specifications | Moderate |
| Demolition | Existing conditions to remove | Moderate |

---

## 2. Information Hierarchy

### Essential (Always Include)

These elements MUST be present for the floor plan to be useful:

- **Walls**: All wall lines with clear thickness distinction
- **Doors**: Location and swing direction (arc showing door movement)
- **Windows**: Location indicated in wall
- **Major Circulation**: Hallways, corridors, main paths
- **Stairs and Ramps**: With direction indicators
- **Room Labels**: Name or function of each space

### Important (Include If Space Allows)

Include these when they fit without causing overlap:

- **Key Dimensions**: Overall building size, room sizes
- **Door/Window Sizes**: Width annotations
- **Wall Thicknesses**: When structural distinction matters
- **Grid Lines**: For structural plans

### Optional (Context-Dependent)

Include based on the specific plan type:

- **Furniture**: Essential for furniture plans, optional otherwise
- **Finishes**: Essential for finish plans, optional otherwise
- **Fixtures**: Plumbing fixtures, built-ins
- **Minor Annotations**: Notes, references
- **Material Indications**: Floor patterns, ceiling types

### Omit (Visual-Only Elements)

Remove these as they do not translate to tactile:

- **Shadows and Gradients**: 3D rendering effects
- **Decorative Elements**: Entourage, plants, people
- **Poche**: Solid black wall fills (replace with outline)

### Transform (Requires Consistent System)

These elements need conversion using an established system:

- **Material Hatching**: Original hatching patterns should be replaced with standardized tactile hatches. See `/patterns/references/HATCH_SYSTEM.md` for the established system. Consistency across all graphics is critical - the same hatch must always mean the same thing.
- **Color Fills**: Zone coloring and department coding should be converted to hatches from the standard system, with meanings documented on a key page.

---

## 3. Common Challenges and Solutions

### Challenge: Dense Labeling in Small Rooms

PROBLEM: Multiple room labels crowded together cause overlap

SOLUTIONS:
1. Use symbol key (a, b, c) with key page listing full names
2. Abbreviate consistently: KITCHEN -> KIT, BATHROOM -> BATH
3. Place labels outside rooms with leader lines (if space exists)
4. Prioritize: label only primary spaces, describe secondary in text

TOOL_BEHAVIOR: Image-to-PIAF automatically repositions overlapping labels. Labels that cannot be repositioned become symbols with a key page.

### Challenge: Multiple Overlapping Dimensions

PROBLEM: Dimension strings stack and become unreadable

SOLUTIONS:
1. Keep only overall dimensions and key room sizes
2. Remove redundant dimension chains
3. Describe detailed dimensions in text description
4. Consider separate dimensioned version if critical

### Challenge: Furniture Overwhelming Room Boundaries

PROBLEM: Furniture lines compete with wall lines

SOLUTIONS:
1. For standard floor plans: Remove furniture entirely
2. For furniture plans: Use lighter line weight for walls (not possible in current tool - describe relationship in text)
3. Create two versions: one with, one without furniture

### Challenge: Very Large Plans

PROBLEM: Building too large for single sheet at original scale

SOLUTIONS:
1. Try tabloid paper first (11x17)
2. Enable tiling with `--enable-tiling`
3. Consider processing wings/sections separately
4. For very complex buildings, create overview + detailed area plans

### Challenge: Poche (Solid Black Fills)

PROBLEM: Cut walls shown as solid black create large raised areas

SOLUTIONS:
1. Convert to outline only (increase threshold)
2. Use double-line walls instead of filled
3. Note in description that walls are shown as outlines

---

## 4. Recommended Parameters

### Standard Floor Plan

```bash
fabric-access image-to-piaf floor_plan.jpg \
  --preset floor_plan \
  --detect-text \
  --braille-grade 2 \
  --paper-size letter \
  --verbose
```

PRESET_SETTINGS (floor_plan):
- Threshold: 140
- Enhancement: s_curve (strength 1.0)

### Large/Complex Floor Plan

```bash
fabric-access image-to-piaf large_plan.jpg \
  --preset floor_plan \
  --detect-text \
  --braille-grade 2 \
  --paper-size tabloid \
  --verbose
```

### Very Large Floor Plan (Tiling Required)

```bash
fabric-access image-to-piaf very_large_plan.jpg \
  --preset floor_plan \
  --detect-text \
  --braille-grade 2 \
  --enable-tiling \
  --paper-size tabloid \
  --verbose
```

### Floor Plan with Heavy Poche

```bash
fabric-access image-to-piaf poche_plan.jpg \
  --preset floor_plan \
  --threshold 160 \
  --detect-text \
  --braille-grade 2 \
  --verbose
```

NOTE: Higher threshold (160 vs 140) reduces solid black areas

### Furniture Plan

```bash
fabric-access image-to-piaf furniture_plan.jpg \
  --preset floor_plan \
  --threshold 130 \
  --detect-text \
  --braille-grade 2 \
  --verbose
```

NOTE: Lower threshold (130) captures lighter furniture lines

---

## 5. Examples

### Reference: ANNEX-PLANS-OFFICIAL_Page_1.jpg

LOCATION: /mnt/c/Users/ethan/fabric-accessible-graphics/ANNEX-PLANS-OFFICIAL_Page_1.jpg
TYPE: Foundation/structural floor plan
SIZE: 6221 x 7155 pixels (requires tiling or scaling)

FEATURES:
- Structural grid with column footings
- Central staircase
- Detail callout bubbles
- Dimension strings
- Grid labels (A, B, C... and 1, 2, 3...)

RECOMMENDED_COMMAND:
```bash
fabric-access image-to-piaf ANNEX-PLANS-OFFICIAL_Page_1.jpg \
  --preset floor_plan \
  --detect-text \
  --braille-grade 2 \
  --paper-size tabloid \
  --verbose
```

CONSIDERATIONS:
- Large image will be scaled to fit tabloid
- 185 text elements detected - many will use symbol key
- Structural grid provides good tactile reference framework

### Reference: plan_test.jpg

LOCATION: /mnt/c/Users/ethan/fabric-accessible-graphics/plan_test.jpg
TYPE: Simple floor plan sketch
SIZE: 792 x 612 pixels (fits on letter)

RECOMMENDED_COMMAND:
```bash
fabric-access image-to-piaf plan_test.jpg \
  --preset floor_plan \
  --detect-text \
  --braille-grade 2 \
  --verbose
```

---

## 6. Testing Notes

### Testing Protocol for Floor Plans

1. Convert using recommended parameters
2. Print on PIAF machine
3. Student traces wall outlines first
4. Student locates doors and identifies swing direction
5. Student reads room labels
6. Record time to comprehension and confusion points

### Test Log

```
DATE: [YYYY-MM-DD]
SOURCE_FILE: [Filename]
PARAMETERS_USED: [CLI command]
OUTCOME: [Success / Partial / Failed]
WALL_CLARITY: [Clear / Needs adjustment]
DOOR_RECOGNITION: [Easy / Difficult / Impossible]
LABEL_READABILITY: [Good / Some overlap / Too dense]
STUDENT_FEEDBACK:
  - [Comment 1]
  - [Comment 2]
ADJUSTMENTS_MADE:
  - [Change 1]
  - [Change 2]
---
```

### Pending Tests

- [ ] Standard residential floor plan
- [ ] Commercial floor plan with many rooms
- [ ] Floor plan with furniture overlay
- [ ] Multi-story building (stacked plans)
- [ ] Historical floor plan (from textbook)

### Known Issues Specific to Floor Plans

```
ISSUE: FP-001
DESCRIPTION: Door swings sometimes merge with wall lines
STATUS: Open
WORKAROUND: Describe door locations in text if unclear
---
ISSUE: FP-002
DESCRIPTION: Grid bubbles (detail callouts) clutter drawing
STATUS: Open
WORKAROUND: Consider removing if not essential to understanding
---
```

---

## Quick Reference

```
FLOOR PLAN CONVERSION CHECKLIST:

[ ] Identify plan type (schematic, construction, furniture, etc.)
[ ] Check image size - will it need tiling?
[ ] Note density of labels - may need symbol key
[ ] Check for poche - may need higher threshold
[ ] Run with --verbose to see processing details
[ ] Review label count in output
[ ] Verify key page generated if symbols used

STANDARD COMMAND:
fabric-access image-to-piaf [FILE] --preset floor_plan --detect-text --braille-grade 2 --verbose

ADJUSTMENTS:
- Too dark? -> increase threshold (150, 160, 170)
- Labels overlapping? -> handled automatically with symbol key
- Too large? -> try tabloid, then enable tiling
```
