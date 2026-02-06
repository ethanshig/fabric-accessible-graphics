# Tactile Graphics Guidelines

Technical requirements and best practices for creating tactile graphics suitable for PIAF (Picture In A Flash) swell paper printing.

## PIAF Technical Requirements

### Line Standards

| Element | Minimum | Recommended | Maximum |
|---------|---------|-------------|---------|
| Line width | 1.5mm | 2.0mm | 4.0mm |
| Line spacing | 2.5mm | 3.0mm | - |
| Symbol size | 6mm | 8mm | - |
| Text height (Braille) | 6mm | 6mm | 6mm |

### Density Limits

- **Target density**: < 30% black pixels
- **Warning threshold**: 40% black pixels
- **Maximum safe**: 45% black pixels
- **Above 45%**: Paper curling, detail loss

### Resolution

- **Output DPI**: 300 (required for PIAF)
- **Minimum input**: 150 DPI recommended
- **Paper sizes**: Letter (8.5x11"), Tabloid (11x17")

## Design Principles

### Simplification

1. **Remove non-essential elements**
   - Furniture in floor plans (unless the focus)
   - Decorative patterns
   - Fine hatching
   - Gradient fills

2. **Consolidate similar elements**
   - Multiple small rooms → labeled zones
   - Repetitive patterns → representative sample
   - Complex curves → simplified geometry

3. **Prioritize hierarchy**
   - Primary structure (walls, columns)
   - Secondary elements (doors, windows)
   - Tertiary details (fixtures) - often omit

### Contrast

- Pure black (#000000) and pure white (#FFFFFF) only
- No grayscale, gradients, or halftones
- Minimum 2.5mm between distinct elements

### Labeling

1. **Braille placement**
   - Preferably inside rooms/spaces
   - Minimum 3mm from walls
   - Avoid overlapping other labels

2. **Abbreviation strategy**
   - Full text if space allows
   - Standard abbreviations (BR=Bedroom, KIT=Kitchen)
   - Letter codes (A, B, C) with key page if needed

3. **Dimensions**
   - Include only critical dimensions
   - Use consistent format (feet-inches or metric)
   - Place parallel to feature being measured

## Stratification Strategy

For complex drawings with multiple systems, create separate tactile graphics:

### Layer 1: Structure
- Walls (load-bearing highlighted)
- Columns
- Core elements
- Building outline

### Layer 2: Circulation
- Doors and openings
- Stairs and ramps
- Corridors
- Entry points

### Layer 3: Program/Spaces
- Room labels
- Key dimensions
- Functional zones

### Layer 4: Systems (if needed)
- MEP runs (simplified)
- Furniture layout
- Equipment locations

## AI Generation Prompt Suffix

When using AI to generate tactile images, always append:

```
Technical requirements for tactile output:
- Pure black lines on pure white background
- Minimum 2.5mm spacing between all distinct elements
- Bold solid lines, no fine details smaller than 1.5mm
- No gray tones, gradients, or shading
- No text or labels (Braille added separately)
- Consistent line weights throughout
- High contrast suitable for PIAF swell paper printing
```

## Common Pitfalls

### Avoid

- Fine line weights (< 1.5mm)
- Dense hatching patterns
- Overlapping elements
- Text smaller than 6mm
- Gradients or shading
- Complex curves with tight radii
- More than 3-4 line weights

### Prefer

- Bold, clear lines (2mm+)
- Solid fills for emphasis
- Clear separation between elements
- Generous white space
- Simple geometric shapes
- Consistent line weights
- High contrast boundaries

## Quality Checklist

Before finalizing a tactile graphic:

- [ ] Density below 40%?
- [ ] All lines 1.5mm+ width?
- [ ] Spacing 2.5mm+ between elements?
- [ ] No gradients or gray tones?
- [ ] Labels readable (6mm+ Braille)?
- [ ] No overlapping labels?
- [ ] Key page if abbreviations used?
- [ ] Tested at actual print size?

## Resources

- BANA (Braille Authority of North America) Guidelines
- APH (American Printing House) Tactile Graphics Guidelines
- "Tactile Graphics" by Polly Edman
- PIAF machine manufacturer specifications
