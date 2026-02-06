# GenerateFromDescription Workflow

Generate tactile graphics from text descriptions when no source image exists.

## Prerequisites

- Text description or building name from user
- PAI Art skill available
- API keys configured
- Optional: Research skill for famous buildings

## When to Use

- User wants tactile graphic of a concept (no image)
- Creating precedent study diagrams of famous buildings
- Generating hypothetical layouts
- Teaching architectural concepts

## Workflow Steps

### Step 1: Clarify Requirements

Gather essential information:

**Drawing Type**:
- Floor plan (most common)
- Section
- Site plan
- Diagram

**Subject**:
- Specific building (research needed)
- Building type (generic apartment, house, etc.)
- Concept (circulation diagram, spatial organization)

**Focus**:
- Full building or specific area?
- Which systems to show?
- Level of detail?

**Example clarification**:
> "You want a tactile floor plan of the Barcelona Pavilion. Should I show:
> 1. The main exhibition level with the reflecting pool?
> 2. A simplified diagram of the free-flowing spaces?
> 3. The structural grid with columns highlighted?"

### Step 2: Research (If Famous Building)

For specific buildings, gather accurate information:

**Use web search or Research skill**:
- Plan organization and geometry
- Key architectural features
- Dimensions and proportions
- Historical context

**Barcelona Pavilion Example**:
- Architect: Mies van der Rohe, 1929
- Plan: Open flowing space on raised platform
- Key features: Cruciform columns, onyx wall, reflecting pool
- Dimensions: ~55m x 17m platform
- Concept: "Less is more" - free plan demonstration

### Step 3: Define Spatial Layout

Translate research into geometric description:

**Overall form**:
- Shape (rectangular, L-shaped, circular)
- Approximate dimensions
- Orientation

**Primary elements**:
- Walls and their relationships
- Columns or structural grid
- Major spaces

**Key features**:
- What makes this building distinctive?
- What must be included for recognition?

### Step 4: Construct Prompt

Build generation prompt following `TactilePromptGuide.md`:

**Template**:
```
Architectural [drawing type] of [building name/type], technical drawing style,
bird's eye view, orthographic projection, clean linework, high contrast

[Detailed spatial description]:
- Overall geometry: [shape, dimensions]
- Primary elements: [walls, columns]
- Key features: [distinctive elements]
- Organization: [how spaces relate]

[What to include explicitly]
[What to omit explicitly]

[TACTILE SUFFIX]
```

**Barcelona Pavilion Example**:
```
Architectural floor plan of the Barcelona Pavilion by Mies van der Rohe,
technical drawing style, bird's eye view, orthographic projection

Rectangular platform approximately 55m by 17m. Show:
- Platform edge as bold outline
- Reflecting pool at west end as rectangle
- Main pavilion space in center
- Eight cruciform columns on regular grid as bold cross shapes
- Free-standing walls: L-shaped onyx wall, glass walls indicated as thin lines
- Covered and open areas distinguished by roof edge line

Omit: furniture, people, landscape, dimensions, text labels

Technical requirements for tactile output:
[... full suffix ...]
```

### Step 5: Generate Image

Execute via PAI's Art skill:

```bash
bun run ~/.claude/skills/Art/Tools/Generate.ts \
  --model nano-banana-pro \
  --prompt "[constructed prompt]" \
  --size 2K \
  --aspect-ratio 17:22 \
  --output ~/Downloads/tactile-barcelona.png
```

### Step 6: Validate Accuracy

Compare generated image against research:

- [ ] Overall proportions correct
- [ ] Key elements present
- [ ] Spatial relationships accurate
- [ ] Distinctive features recognizable
- [ ] Meets tactile specifications

**If inaccurate**:
- Adjust prompt with more specific geometry
- Add explicit coordinates or relationships
- Try different model for alternative interpretation

### Step 7: Validate Tactile Quality

Check PIAF requirements:

- [ ] Pure black and white
- [ ] Bold lines (>1.5mm)
- [ ] Adequate spacing (>2.5mm)
- [ ] No gradients or gray
- [ ] No text

### Step 8: Present Results

```
Generated tactile floor plan of the Barcelona Pavilion.

Key features shown:
- Raised platform with reflecting pool
- Eight cruciform columns on grid
- Free-flowing walls (onyx, glass)
- Open pavilion space

Historical context: Designed by Mies van der Rohe for the 1929
Barcelona International Exposition, this pavilion pioneered the
"free plan" concept where walls don't reach the ceiling and
spaces flow into each other.

Output: ~/Downloads/tactile-barcelona.png

Would you like me to:
1. Add Braille labels for key elements?
2. Generate a section showing the roof plane?
3. Create a simpler diagram version?
4. Describe the building in words (AccessibleDescription)?
```

## Building Type Templates

### Generic Apartment

```
Architectural floor plan of a two-bedroom apartment, technical drawing style

Rectangular footprint approximately 800 square feet (25x32 feet).
Entry from east into small foyer. Open living/dining/kitchen in south half.
Galley kitchen along south wall. Two bedrooms in north half separated by
central hallway. One full bathroom between bedrooms. Primary bedroom
slightly larger with small closet.

Walls as bold lines, doors as 3-foot gaps with swing arcs.

[TACTILE SUFFIX]
```

### Single Family House

```
Architectural floor plan of a three-bedroom ranch house, technical drawing style

L-shaped footprint, longer wing running east-west (50 feet),
shorter wing extending south (25 feet). Entry in corner where wings meet.
Living room in east end of main wing. Kitchen/dining in center.
Primary bedroom suite in west end with private bathroom.
Two secondary bedrooms in south wing with shared bathroom.
Attached two-car garage on north side.

[TACTILE SUFFIX]
```

### Classroom

```
Architectural floor plan of a typical classroom, technical drawing style

Rectangular room approximately 30x25 feet. Single entry door on north wall.
Teacher area at west end (whiteboard zone). Student area fills remainder
with implied seating rows running east-west. Windows along south wall
shown as thin parallel lines in wall. Storage closet in northeast corner.

[TACTILE SUFFIX]
```

## Famous Building Quick Reference

| Building | Key Plan Features |
|----------|-------------------|
| Barcelona Pavilion | Free-flowing walls, cruciform columns, reflecting pool |
| Villa Savoye | Square plan on pilotis, central ramp, roof garden |
| Farnsworth House | Single rectangle, core box, column grid |
| Fallingwater | Stacked horizontal trays over waterfall |
| Pantheon | Circular temple, thick walls, central oculus |
| Guggenheim NY | Spiral ramp, central atrium |
| Sydney Opera House | Sail/shell roofs, stepped platforms |

## Error Handling

| Issue | Solution |
|-------|----------|
| Historically inaccurate | More specific research, explicit dimensions |
| Missing key features | List must-have elements in prompt |
| Wrong proportions | Add explicit dimension ratios |
| Unrecognizable | Focus on 2-3 signature elements |
| Too complex | Simplify to essential parti |
