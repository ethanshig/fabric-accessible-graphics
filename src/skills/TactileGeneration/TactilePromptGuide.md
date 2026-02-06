# Tactile Prompt Engineering Guide

How to construct prompts that produce PIAF-ready tactile images from AI image generators.

## The Mandatory Tactile Suffix

**Every prompt MUST end with this suffix:**

```
Technical requirements for tactile output:
- Pure black lines on pure white background
- Minimum 2.5mm spacing between all distinct elements
- Bold solid lines, no fine details smaller than 1.5mm
- No gray tones, gradients, or shading
- No text or labels (Braille added separately)
- Consistent line weights throughout
- High contrast suitable for PIAF swell paper printing
- Simplified geometry - reduce curves to essential arcs
- Clear boundaries between distinct areas
```

This suffix is **non-negotiable** - it ensures the output meets PIAF requirements.

## Prompt Structure

### Basic Template

```
[DRAWING TYPE] of [SUBJECT], [STYLE MODIFIERS]

[SPECIFIC CONTENT DESCRIPTION]

[TACTILE SUFFIX]
```

### Example Prompts

**Floor Plan from Description:**
```
Architectural floor plan of a two-bedroom apartment, technical drawing style,
bird's eye view, orthographic projection

Show: rectangular layout approximately 30x40 feet, entry on east side,
open living/dining/kitchen area in south half, two bedrooms and bathroom
in north half separated by central hallway, doors shown as gaps in walls
with arc indicating swing direction

Technical requirements for tactile output:
[... full suffix ...]
```

**Simplification of Complex Source:**
```
Simplified architectural floor plan, technical drawing style,
clean linework, minimal detail

Recreate the essential spatial layout: exterior walls, interior partitions,
door openings, and major circulation paths. Omit furniture, fixtures,
dimensions, and decorative elements. Emphasize wall thickness with
bold solid fills.

Technical requirements for tactile output:
[... full suffix ...]
```

**Stratified Layer (Structure Only):**
```
Structural floor plan showing only load-bearing elements, technical drawing style

Show: exterior bearing walls as thick bold lines, interior load-bearing walls
as medium weight lines, columns as filled black circles approximately 8mm diameter.
Omit all partitions, doors, windows, and non-structural elements.

Technical requirements for tactile output:
[... full suffix ...]
```

## Drawing Type Keywords

Use these precise terms for different drawing types:

| Drawing Type | Keywords |
|--------------|----------|
| Floor plan | "architectural floor plan", "plan view", "bird's eye view" |
| Section | "building section", "sectional view", "cut-through view" |
| Elevation | "building elevation", "facade view", "exterior elevation" |
| Site plan | "site plan", "plot plan", "landscape plan" |
| Diagram | "architectural diagram", "conceptual diagram", "parti diagram" |
| Detail | "construction detail", "assembly detail", "section detail" |

## Style Modifiers

Include these for consistent tactile output:

- "technical drawing style"
- "clean linework"
- "orthographic projection"
- "high contrast"
- "simplified geometry"
- "minimal detail"
- "bold outlines"

## Content Description Guidelines

### Be Specific About Geometry

**Good**: "L-shaped floor plan with longer arm running east-west, approximately 40 feet, shorter arm extending south approximately 20 feet"

**Bad**: "L-shaped house"

### Specify Wall Treatments

**Good**: "exterior walls as thick bold lines (4px), interior partitions as medium lines (2px), door openings as 3-foot gaps"

**Bad**: "show the walls and doors"

### Define Element Hierarchy

**Good**: "primary circulation as bold paths, secondary rooms as enclosed areas with clear boundaries"

**Bad**: "show the layout"

### Avoid Ambiguous Terms

| Avoid | Use Instead |
|-------|-------------|
| "detailed" | "essential elements only" |
| "realistic" | "technical drawing style" |
| "shaded" | "solid black fills" |
| "textured" | "uniform line weight" |
| "colorful" | "pure black on white" |

## Stratification Prompts

### Layer 1: Structure

```
Structural plan showing only load-bearing elements

Include: exterior bearing walls (bold), structural columns (filled circles),
shear walls, building core. Omit: partitions, doors, windows, furniture.

[TACTILE SUFFIX]
```

### Layer 2: Circulation

```
Circulation diagram showing movement paths only

Include: door locations (gaps with swing arcs), corridors (outlined paths),
stairs (parallel lines with direction arrow), entry points (emphasized openings).
Show walls as thin context lines only.

[TACTILE SUFFIX]
```

### Layer 3: Program

```
Program diagram showing functional zones

Include: room boundaries as bold outlines, approximate room shapes,
clear separation between spaces. Omit: doors, windows, interior detail.
Each room should be a distinct enclosed area suitable for Braille labeling.

[TACTILE SUFFIX]
```

## Famous Building Prompts

When generating tactile graphics of well-known buildings:

### Research First

Before prompting, understand:
- Overall plan organization
- Key architectural features
- Scale and proportions
- Historical significance

### Include Accuracy Markers

```
Floor plan of Le Corbusier's Villa Savoye (1929), technical drawing style

Show: rectangular plan on pilotis, central ramp connecting floors,
roof garden, ribbon windows indicated as thin lines in exterior walls.
Main living level with open plan, free-standing columns (pilotis)
as filled circles on regular grid.

[TACTILE SUFFIX]
```

## Quality Checklist for Prompts

Before generating, verify prompt includes:

- [ ] Drawing type keyword (floor plan, section, etc.)
- [ ] Style modifiers (technical drawing, clean linework)
- [ ] Specific content description
- [ ] Element hierarchy (bold/medium/thin)
- [ ] What to INCLUDE explicitly stated
- [ ] What to OMIT explicitly stated
- [ ] Full tactile suffix appended

## Iterating on Results

If first generation doesn't meet specs:

1. **Too much detail**: Add "simplified", "essential elements only", "minimal"
2. **Gray tones present**: Emphasize "pure black and white", "no gradients"
3. **Lines too thin**: Add "bold linework", "thick outlines"
4. **Cluttered**: Add "generous white space", "clear separation"
5. **Text appearing**: Emphasize "no text, no labels, no annotations"

## Model-Specific Notes

### Nano Banana Pro (Gemini)
- Best at following technical specifications
- Good with reference images
- May need extra emphasis on "no gradients"

### GPT-Image-1
- Strong architectural understanding
- Sometimes adds artistic interpretation
- Be very explicit about technical requirements

### Flux 1.1 Pro
- Excellent detail control
- Good with precise specifications
- May need "clean, not sketchy" for crisp lines
