---
name: TactileGeneration
description: Generate tactile graphics using AI image generation when source images are too complex or unavailable
triggers:
  - generate tactile
  - create tactile image
  - simplify for tactile
  - stratify this drawing
  - stratify drawing
  - tactile version of
  - make this tactile
  - recreate as tactile
  - tactile graphic of
context: fork
tools:
  - TactileGenerate.ts
---

# TactileGeneration

Generate NEW tactile graphics using AI when source images are too complex, cluttered, or unavailable. This skill leverages PAI's image generation infrastructure with tactile-specific prompt engineering to produce PIAF-ready output.

## When to Use This Skill

Use TactileGeneration when:

- **Source is too complex**: Cluttered drawings with overlapping systems
- **Source quality is poor**: Low contrast, faded, noisy images
- **Simplification needed**: Need to reduce detail for tactile clarity
- **Stratification required**: Multiple systems (structure, circulation, MEP) need separation
- **No source exists**: Creating from text description of a building or concept
- **Precedent studies**: Generating tactile diagrams of famous buildings

## When NOT to Use

Use **TactileConversion** instead when:

- Source image is already clean and high-contrast
- Exact preservation of source matters
- Quick processing without AI needed
- Working offline without API access

## Three Core Workflows

### 1. Simplify Complex Source

**Trigger**: "simplify this for tactile", "recreate as tactile"

Takes a cluttered or complex source image and generates a clean, simplified tactile version.

**Workflow**: `Workflows/GenerateFromImage.md`

### 2. Generate from Description

**Trigger**: "create tactile of [building]", "tactile graphic of"

Creates tactile graphics from text descriptions with no source image required.

**Workflow**: `Workflows/GenerateFromDescription.md`

### 3. Stratify Multi-System

**Trigger**: "stratify this drawing", "separate the systems"

Analyzes a complex drawing and generates multiple tactile layers, each showing one system clearly.

**Workflow**: `Workflows/GenerateFromImage.md` (with stratification flag)

## Tactile Output Requirements

All generated images MUST meet these specifications:

| Requirement | Value |
|-------------|-------|
| Colors | Pure black (#000000) and white (#FFFFFF) only |
| Line width | Minimum 1.5mm (6px at 300 DPI) |
| Element spacing | Minimum 2.5mm (30px at 300 DPI) |
| Gradients | None - solid fills only |
| Text | None - Braille added separately via tactile-core |
| Resolution | 300 DPI for PIAF printing |
| Aspect ratio | Match paper size (8.5:11 for letter) |

## Prompt Engineering

All prompts include the mandatory **Tactile Suffix** (see `TactilePromptGuide.md`):

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

## Model Selection

Uses PAI's image generation infrastructure:

| Model | Best For |
|-------|----------|
| Nano Banana Pro (Recommended) | High quality, reference image support |
| GPT-Image-1 | Alternative interpretation |
| Flux 1.1 Pro | Maximum detail control |

## Stratification Layers

When stratifying, generate separate images for:

### Layer 1: Structure
- Walls and columns
- Load-bearing elements
- Building envelope

### Layer 2: Circulation
- Doors and openings
- Stairs and ramps
- Corridors and paths

### Layer 3: Program
- Room boundaries
- Functional zones
- Space labels (for Braille)

### Layer 4: Systems (optional)
- MEP runs (simplified)
- Furniture layout
- Equipment

## Context Files

Load before generating:
- `TactilePromptGuide.md` - Prompt construction guide
- `../shared/TactileGuidelines.md` - PIAF specifications
- `../shared/ArchitecturalContext.md` - Domain vocabulary

## Tool

Uses: `tools/TactileGenerate.ts` which wraps PAI's Generate.ts with tactile-specific prompt suffix and settings.

## Output

- PNG image ready for PIAF printing
- Pure black and white (verified)
- 300 DPI resolution
- Optional: Run through `tactile` CLI to add Braille labels

## Example Usage

**User**: "Create a tactile floor plan of Mies van der Rohe's Barcelona Pavilion"

**Response**:
1. Research Barcelona Pavilion layout (cross-shaped plan, reflecting pool, glass/onyx walls)
2. Construct prompt with architectural accuracy
3. Add tactile suffix
4. Generate via TactileGenerate.ts
5. Verify output meets tactile specs
6. Offer to add Braille labels via tactile-core
