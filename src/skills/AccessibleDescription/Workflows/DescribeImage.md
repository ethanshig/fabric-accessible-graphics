# DescribeImage Workflow

Generate rich accessibility descriptions of architectural images using the Arch-Alt-Text framework.

## Prerequisites

- Image provided by user (file path or in conversation)
- Claude vision capability available
- Context files loaded:
  - `../shared/ArchitecturalContext.md`

## Workflow Steps

### Step 1: Identify Image Type

Analyze the image to determine:

1. **Drawing type**:
   - Floor plan (horizontal cut)
   - Section (vertical cut)
   - Elevation (exterior face)
   - Site plan (bird's eye)
   - Detail (enlarged assembly)
   - Photograph (real building)
   - Rendering (visualization)
   - Diagram (conceptual)

2. **Content**:
   - What building or space?
   - What scale/scope?
   - What level of detail?

3. **Context**:
   - Academic exercise or real project?
   - Famous building or generic?
   - Historical or contemporary?

### Step 2: Generate Macro Layer

Write **3 sentences** covering:

1. **Medium**: What type of drawing/image is this?
   - "This is an architectural floor plan..."
   - "This photograph shows..."
   - "This building section reveals..."

2. **Subject**: What does it depict?
   - "...showing the ground level of a three-bedroom residence"
   - "...the exterior of Le Corbusier's Villa Savoye"
   - "...the vertical organization of a five-story office building"

3. **Purpose**: Why does this matter?
   - "The plan demonstrates an open-concept living arrangement"
   - "This iconic modernist building pioneered the free plan concept"
   - "The section shows how natural light penetrates to lower floors"

### Step 3: Generate Meso Layer

Write **4+ sentences** covering:

1. **Organization**: How is the space/building arranged?
   - Overall shape (rectangular, L-shaped, circular)
   - Major divisions (public/private, served/servant)
   - Circulation patterns

2. **Relationships**: How do parts connect?
   - Adjacent spaces
   - Visual connections
   - Functional groupings

3. **Orientation**: How is it positioned?
   - Cardinal directions (if known)
   - Entry location
   - Primary views

4. **Scale**: How big is it?
   - Overall dimensions
   - Room sizes
   - Human reference points

### Step 4: Generate Micro Layer

Write **8+ sentences** covering:

1. **Entry sequence**:
   - Where do you enter?
   - What do you encounter first?
   - How do you move through?

2. **Specific elements**:
   - Room by room description
   - Notable features
   - Dimensions of key spaces

3. **Materials and textures** (if visible):
   - Floor materials
   - Wall treatments
   - Ceiling conditions

4. **Analogies**:
   - Compare sizes to familiar objects
   - Relate shapes to common forms
   - Use body-scale references

5. **Wayfinding cues**:
   - How to navigate
   - Landmarks within the space
   - Decision points

### Step 5: Offer Follow-ups

Provide options:

1. **Detailed focus**: "Would you like me to describe [specific area] in more detail?"
2. **Tactile conversion**: "Should I convert this to a tactile graphic for PIAF printing?"
3. **Concept explanation**: "Would you like me to explain [architectural term]?"
4. **Comparison**: "Should I compare this to [familiar building type]?"

## Output Template

```
**Macro (Overview)**:
[3 sentences: medium, subject, purpose]

**Meso (Composition)**:
[4+ sentences: organization, relationships, orientation, scale]

**Micro (Details)**:
[8+ sentences: entry sequence, specific elements, materials, analogies, wayfinding]

**Would you like me to**:
1. [Specific detail option based on image]
2. Convert this to a tactile graphic?
3. Explain any architectural terms?
```

## Language Guidelines

### Do Use

- Cardinal directions (north, south, east, west)
- Specific dimensions ("approximately 12 by 15 feet")
- Human scale references ("arm's length", "two steps")
- Familiar analogies ("the size of a small car")
- Tactile qualities ("rough concrete", "smooth glass")

### Avoid

- "On the left/right" without reference point
- Subjective aesthetic terms ("beautiful", "ugly")
- Assumptions about visual experience
- Color alone (pair with material/texture)
- Unexplained jargon

## Special Cases

### Famous Buildings

If recognizable, provide:
- Architect name
- Year completed
- Location
- Historical significance
- Key design concepts

### Complex Drawings

If image has multiple systems:
- Describe each layer separately
- Explain what each system represents
- Suggest stratified tactile output

### Poor Quality Images

If image is unclear:
- State what can be determined
- Note areas of uncertainty
- Suggest user provide clearer image

## Example: Floor Plan

**User shows a floor plan image**

**Response**:

**Macro (Overview)**:
This is an architectural floor plan showing the main level of a single-family home. The drawing presents a modern open-plan layout with living areas facing south toward what appears to be a garden. Dimensioned annotations indicate this is a working drawing, likely at 1/4 inch to 1 foot scale.

**Meso (Composition)**:
The home is organized as an elongated rectangle, roughly 50 feet wide by 32 feet deep. Public spaces (living, dining, kitchen) occupy the southern two-thirds, while private spaces (bedrooms, bathrooms) are arranged along the northern edge. Entry is through the east side, marked by a small covered porch. A central hallway running east-west divides public from private zones.

**Micro (Details)**:
Approaching from the east, you enter through a door into a foyer approximately 6 by 8 feet, just large enough for a small bench and coat hooks. Straight ahead, the living room opens up dramatically, a space of about 18 by 20 feet, similar in area to a two-car garage but with higher ceilings suggested by the section indicator.

To your left as you enter, the kitchen occupies the northeast corner. It features an L-shaped counter arrangement with an island measuring roughly 4 by 8 feet, positioned about 3 feet from the main counter, creating a working aisle just wide enough for one person to pass.

The dining area sits between kitchen and living room, defined not by walls but by a change in ceiling height indicated in the section reference. This space measures about 12 by 14 feet, appropriate for a table seating six to eight.

Along the north wall, three doors open from the central hallway. The westernmost leads to the primary bedroom, a generous 14 by 16 feet with an attached bathroom accessed through a walk-in closet. The middle door opens to a hall bathroom serving the home's secondary bedroom and guests. The easternmost door reveals a second bedroom of about 11 by 12 feet.

**Would you like me to**:
1. Describe the primary bedroom suite in more detail?
2. Convert this floor plan to a tactile graphic?
3. Explain what the section indicator symbols mean?
