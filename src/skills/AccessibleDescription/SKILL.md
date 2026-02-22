---
name: AccessibleDescription
description: Generate detailed accessibility descriptions of architectural images using Arch-Alt-Text. USE WHEN describe this image, describe this drawing, what does this show, explain this drawing, accessibility description, describe for accessibility, what am I looking at.
context: fork
---

# AccessibleDescription

Generate rich verbal descriptions of architectural images following the Arch-Alt-Text framework. Designed for blind and low-vision architecture students who need to understand visual materials without tactile printing.

## When to Use This Skill

Use AccessibleDescription when:

- **Quick understanding** needed without PIAF printing
- **Supplementing** tactile graphics with verbal context
- Images that **don't translate well** to tactile format
- **Remote/mobile** situations without PIAF access
- **Initial exploration** before deciding on tactile conversion
- User asks "what is this?" about an image

## When NOT to Use

Use **TactileConversion** or **TactileGeneration** when:

- User specifically wants a printable tactile graphic
- Physical exploration is the goal
- PIAF machine is available

## The Arch-Alt-Text Framework

Descriptions follow three layers, from general to specific:

### 1. Macro Layer (Overview)
**3 sentences** covering:
- Medium and format (floor plan, section, photograph, rendering)
- Subject (what building, space, or element)
- Purpose (design intent, context, why it matters)

### 2. Meso Layer (Composition)
**4+ sentences** covering:
- Overall organization and layout
- Key relationships between spaces/elements
- Orientation (north, entry, cardinal directions)
- Scale (dimensions, human reference points)

### 3. Micro Layer (Details)
**8+ sentences** covering:
- Specific elements and their precise locations
- Dimensions and proportions
- Textures.and material qualities
- Analogies to familiar objects/spaces
- Wayfinding cues
- Notable features or anomalies

## Workflow

Execute: `Workflows/DescribeImage.md`

## Context Files

Load before generating descriptions:
- `ArchAltText.md` - Full framework documentation
- `../shared/ArchitecturalContext.md` - Domain vocabulary

## Description Guidelines

### Language Principles

1. **Be specific, not vague**
   - Wrong: "The room is large"
   - Right: "The living room spans approximately 20 by 15 feet, comparable to a small tennis court"

2. **Use cardinal directions**
   - Wrong: "On the left side"
   - Right: "On the west wall" or "To the left as you enter from the main door"

3. **Provide analogies**
   - "The curved wall follows a gentle arc, like the inside of a bowl"
   - "The columns are spaced about two arm-spans apart"

4. **Describe relationships**
   - "The kitchen opens directly to the dining area with no wall between them"
   - "To reach the bedroom, you pass through the living room"

### What to Include

- Entry and circulation paths
- Room names and functions
- Door and window locations
- Vertical elements (stairs, double-heights)
- Materials when visible
- Scale references

### What to Avoid

- Subjective aesthetic judgments
- Assumptions about user's visual experience
- Overly technical jargon without explanation
- References to colors alone (include texture/material)

## Follow-up Options

After providing a description, offer:

1. **Describe specific area** - Zoom in on a particular room or element
2. **Generate tactile version** - Invoke TactileConversion or TactileGeneration
3. **Explain concepts** - Define architectural terms mentioned
4. **Compare to familiar** - Relate to common buildings/spaces

## Example Output

**User**: "What does this show?"

**Response**:

**Macro (Overview)**:
This is an architectural floor plan showing the ground level of a single-family residence. The drawing presents a contemporary open-plan design with living spaces oriented toward the rear of the lot. It appears to be a working drawing with dimensions and room labels.

**Meso (Composition)**:
The plan is organized around a central open living area that combines kitchen, dining, and living functions. Entry is from the east through a small vestibule. Private rooms (bedrooms, bathrooms) are clustered on the north side. The south wall features large openings, likely windows or sliding doors, suggesting a connection to outdoor space. The overall footprint is roughly rectangular, approximately 45 by 30 feet.

**Micro (Details)**:
Entering from the east, you step into a vestibule roughly 6 by 8 feet, similar to a small closet in size. Directly ahead, the living area opens up with the kitchen on your left (north). The kitchen is L-shaped, with counters along the north and west walls, and an island parallel to the west counter, about 4 feet away. The island measures approximately 8 feet long, enough for three bar stools.

Moving west from the kitchen, the dining area occupies the northwest corner, dimensioned at 12 by 10 feet, comfortable for a table seating six. The living area continues to the southwest, bounded by the large south-facing openings. This space is approximately 18 by 16 feet.

A hallway extends north from near the entry, leading to two bedrooms and a bathroom. The primary bedroom is at the end of the hall, measuring 14 by 12 feet with its own bathroom accessed through a walk-in closet. The second bedroom is smaller, approximately 11 by 10 feet, located between the hall bathroom and the primary suite.

**Would you like me to**:
1. Describe any specific room in more detail?
2. Convert this to a tactile graphic for PIAF printing?
3. Explain any architectural terms used?
