# TACTILE Hatching System

## Overview

The TACTILE hatching system provides a simplified set of patterns optimized for PIAF (Pictures In A Flash) and swell paper production. This system ensures that tactile graphics are distinguishable by touch while maintaining compliance with accessibility standards.

### Purpose

Traditional architectural hatching conventions include dozens of distinct patterns, many of which are indistinguishable when produced as tactile graphics. This system reduces the pattern vocabulary to six carefully selected textures that:

- Are clearly distinguishable by touch
- Meet BANA (Braille Authority of North America) tactile graphics guidelines
- Can be reliably reproduced on PIAF/swell paper
- Cover the primary materials encountered in structures coursework

### BANA Constraints

The following constraints inform all pattern specifications:

| Constraint | Requirement |
|------------|-------------|
| Maximum distinct textures | 4-6 patterns per diagram |
| Minimum line spacing | 3mm between parallel lines |
| Minimum line weight | 0.5mm for reliable raised lines |
| Recommended line weight | 1mm for optimal tactile detection |
| Dot diameter | 1.5mm minimum for detectability |
| Dot spacing | 3mm minimum center-to-center |
| Pattern boundary | Clear outline required around all hatched regions |

---

## Pattern Definitions

The TACTILE system defines exactly six patterns, each assigned to a specific material category:

| Pattern | Material | Line Spacing | Line Weight | Description |
|---------|----------|--------------|-------------|-------------|
| P1: Solid | Steel | N/A | Solid fill | Solid black fill |
| P2: Stipple | Concrete | 3mm between dots | 1.5mm dot diameter | Random dot pattern |
| P3: Diagonal | Masonry (brick, CMU) | 4mm | 1mm | 45-degree diagonal lines |
| P4: Horizontal | Wood | 4mm | 1mm | Horizontal parallel lines |
| P5: Crosshatch | Earth/Fill | 10mm | 1mm | Perpendicular grid |
| P6: Vertical | Glass | 4mm | 1mm | Vertical parallel lines |

### Pattern Specifications

#### P1: Solid (Steel)

- **Application**: Structural steel members, reinforcing bars, metal plates
- **Specification**: Complete solid black fill with no internal pattern
- **Tactile result**: Uniformly raised flat surface
- **Notes**: Most prominent tactile pattern; reserve for primary structural elements

#### P2: Stipple (Concrete)

- **Application**: Cast-in-place concrete, precast concrete, concrete masonry grout
- **Specification**: Random dot placement with 3mm minimum spacing, 1.5mm dot diameter
- **Tactile result**: Textured surface with distinct raised points
- **Notes**: Dots should appear random but maintain minimum spacing for clarity

#### P3: Diagonal (Masonry)

- **Application**: Brick, concrete masonry units (CMU), stone masonry
- **Specification**: Parallel lines at 45 degrees, 4mm spacing, 1mm weight
- **Tactile result**: Angled ridges detectable by finger sweep
- **Notes**: Direction should be consistent within a single diagram (top-left to bottom-right preferred)

#### P4: Horizontal (Wood)

- **Application**: Dimensional lumber, engineered wood products, timber
- **Specification**: Parallel horizontal lines, 4mm spacing, 1mm weight
- **Tactile result**: Horizontal ridges suggesting wood grain direction
- **Notes**: Represents grain direction in structural wood members

#### P5: Crosshatch (Earth/Fill)

- **Application**: Earth, soil, compacted fill, gravel
- **Specification**: Perpendicular grid at 90 degrees, 10mm spacing, 1mm weight
- **Tactile result**: Waffle-like grid pattern
- **Notes**: Wider spacing distinguishes from line-based patterns; used for ground sections

#### P6: Vertical (Glass)

- **Application**: Glass, glazing, transparent materials
- **Specification**: Parallel vertical lines, 4mm spacing, 1mm weight
- **Tactile result**: Vertical ridges
- **Notes**: Typically used for curtain walls, windows, skylights in section views

---

## Adjacency Rules Matrix

To ensure tactile distinguishability, patterns must be carefully placed to avoid confusion at boundaries.

### Pattern Categories

| Category | Patterns | Characteristic |
|----------|----------|----------------|
| Solid | P1 | Uniform raised surface |
| Point-based | P2 | Discrete raised points |
| Line-based | P3, P4, P5, P6 | Linear raised ridges |

### Adjacency Matrix

| Adjacent To | P1 Solid | P2 Stipple | P3 Diagonal | P4 Horizontal | P5 Crosshatch | P6 Vertical |
|-------------|----------|------------|-------------|---------------|---------------|-------------|
| P1 Solid | NO | YES | YES | YES | YES | YES |
| P2 Stipple | YES | NO | YES | YES | YES | YES |
| P3 Diagonal | YES | YES | NO | AVOID | AVOID | AVOID |
| P4 Horizontal | YES | YES | AVOID | NO | AVOID | AVOID |
| P5 Crosshatch | YES | YES | AVOID | AVOID | NO | AVOID |
| P6 Vertical | YES | YES | AVOID | AVOID | AVOID | NO |

### Adjacency Rules

1. **Same pattern**: Never place identical patterns adjacent to each other
2. **Solid + Any**: P1 (Solid) can be adjacent to any other pattern
3. **Stipple + Any**: P2 (Stipple) can be adjacent to any other pattern
4. **Line-based + Line-based**: Avoid placing any two line-based patterns (P3, P4, P5, P6) adjacent to each other
5. **Boundary requirement**: All pattern regions must have a 1mm minimum outline stroke

### Resolving Adjacency Conflicts

When two materials that would create a prohibited adjacency appear together:

1. **Increase boundary stroke**: Use 1.5mm or 2mm boundary line between regions
2. **Add gap**: Insert 2mm clear space between pattern regions
3. **Use Braille label**: Add abbreviated material label inside region
4. **Substitute pattern**: For secondary materials, use outline-only with label

---

## Usage Guide

### Structural Coursework Applications

#### Foundation Details

| Element | Pattern | Notes |
|---------|---------|-------|
| Concrete footing | P2 Stipple | Primary foundation material |
| Concrete slab | P2 Stipple | Ground-supported slabs |
| Compacted fill | P5 Crosshatch | Below slab, around footings |
| Steel reinforcing | P1 Solid | Rebar shown in section |

#### Steel Frame Construction

| Element | Pattern | Notes |
|---------|---------|-------|
| Wide flange beams | P1 Solid | I-beam sections |
| Steel columns | P1 Solid | Column sections |
| Base plates | P1 Solid | Connection elements |
| Concrete pier | P2 Stipple | Supporting steel above |

#### Wood Frame Construction

| Element | Pattern | Notes |
|---------|---------|-------|
| Studs | P4 Horizontal | Wall framing members |
| Joists | P4 Horizontal | Floor/ceiling framing |
| Beams | P4 Horizontal | Larger wood members |
| Plywood sheathing | P4 Horizontal | Use thinner outline |

#### Masonry Construction

| Element | Pattern | Notes |
|---------|---------|-------|
| Brick veneer | P3 Diagonal | Exterior cladding |
| CMU wall | P3 Diagonal | Structural masonry |
| Grout-filled cells | P2 Stipple | Reinforced masonry cores |
| Stone facing | P3 Diagonal | Cut stone veneer |

#### Building Envelope

| Element | Pattern | Notes |
|---------|---------|-------|
| Glass/glazing | P6 Vertical | Windows, curtain walls |
| Concrete wall | P2 Stipple | Tilt-up, precast panels |
| Brick cavity | P3 Diagonal | Outer wythe |

### Pattern Selection Priority

When multiple patterns could apply, use this priority order:

1. **Primary structural element**: Use assigned pattern
2. **Secondary element**: Use outline-only with label
3. **Tertiary element**: Omit internal pattern, label only

---

## Secondary Materials

Materials not included in the primary six patterns should be handled using the outline-and-label method.

### Outline-Only Convention

For materials without an assigned tactile pattern:

1. **Draw clear boundary**: 1mm minimum stroke around material region
2. **Leave interior clear**: No hatching pattern inside region
3. **Add Braille label**: Abbreviated material name centered in region

### Common Secondary Materials

| Material | Abbreviation | Notes |
|----------|--------------|-------|
| Batt insulation | INS | Wall and ceiling cavities |
| Rigid insulation | RIG | Foundation, roof applications |
| Gypsum board | GYP | Interior finish surfaces |
| Plywood | PLY | Sheathing, subfloor |
| Vapor barrier | VB | Thin membrane materials |
| Waterproofing | WP | Foundation dampproofing |
| Air space | AIR | Cavity wall gaps |
| Metal deck | DK | Floor and roof decking |

### Labeling Guidelines

- Use Grade 1 Braille for material abbreviations
- Minimum label size: 10mm height
- Center label within material region
- For small regions, place label adjacent with leader line

### When to Promote to Primary Pattern

A secondary material should be promoted to use a primary pattern when:

1. It is the focus of the diagram's instructional content
2. It appears in multiple locations requiring pattern recognition
3. The diagram has fewer than 4 other patterns in use

In such cases, assign an unused primary pattern and include in the diagram's legend.

---

## Implementation Notes

### File Formats

- SVG patterns should use `<pattern>` elements with proper scaling
- Pattern definitions should be reusable across multiple diagrams
- Export settings must maintain line weights and spacing

### Quality Verification

Before production, verify:

- [ ] No more than 6 patterns per diagram
- [ ] Minimum 3mm line spacing maintained
- [ ] No prohibited pattern adjacencies
- [ ] All regions have clear boundaries
- [ ] Legend includes all patterns used
- [ ] Braille labels are properly sized and spaced

### PIAF Production Settings

- Heat setting: Medium-high (varies by machine)
- Paper: Swell-touch paper or equivalent
- Print: High-contrast black on white
- Line weight: Verify 1mm minimum prints solid
