---
name: TactileConversion
description: Convert images to tactile-ready PDFs for PIAF printing. USE WHEN convert to tactile, make tactile version, PIAF conversion, convert for printing, tactile PDF, convert this image for PIAF, make this accessible.
context: fork
---

# TactileConversion

Convert existing images to tactile-ready PDFs using code-based algorithms. This skill wraps the `tactile-core` Python library for fast, offline processing.

## When to Use This Skill

Use TactileConversion when:

- Source image is already **clean and high-contrast**
- **Quick processing** needed (no AI API calls)
- **Exact preservation** of source content matters
- Working **offline** without API access
- Processing **batch conversions** of multiple images

## When NOT to Use

Use **TactileGeneration** instead when:

- Source is cluttered, low-contrast, or overly complex
- Image has overlapping systems that need separation (stratification)
- Simplification or artistic reinterpretation is needed
- Creating from text description (no source image)
- Source quality is too poor for code-based processing

## Quick Reference

```bash
# Basic conversion
tact convert floor-plan.jpg

# With preset
tact convert sketch.png --preset sketch

# With Braille labels
tact convert plan.jpg --detect-text --braille-grade 2

# Auto-fix high density
tact convert dense.jpg --auto-reduce-density
```

## Available Presets

| Preset | Best For | Default Threshold |
|--------|----------|-------------------|
| floor_plan | Architectural floor plans | 128 |
| section | Building sections | 130 |
| elevation | Building elevations | 125 |
| site_plan | Site and landscape plans | 120 |
| sketch | Hand-drawn sketches | 140 |
| diagram | Conceptual diagrams | 128 |
| technical_drawing | CAD drawings | 135 |
| photograph | Photographs | 128 |
| presentation | Mixed content boards | 128 |
| detail_drawing | Construction details | 130 |

## Key Options

| Option | Purpose |
|--------|---------|
| `--preset NAME` | Use optimized settings for image type |
| `--detect-text` | Enable OCR and Braille conversion |
| `--braille-grade 1\|2` | Braille grade (2 = contracted) |
| `--auto-reduce-density` | Fix high-density images |
| `--enable-tiling` | Split oversized images |
| `--zoom-region X,Y,W,H` | Crop to specific region |
| `--paper-size letter\|tabloid` | Output paper size |

## Workflow

Execute: `Workflows/ConvertImage.md`

## Tool

Uses: `tools/TactileConvert.ts` which calls the `tact` CLI from the `tactile-core` Python library.

## Context Files

Load before complex conversions:
- `../shared/TactileGuidelines.md` - PIAF technical specifications

## Examples

```bash
# Convert a floor plan with preset and Braille labels
tact convert floor-plan.jpg --preset floor_plan --detect-text --braille-grade 2 --verbose

# Batch convert a folder of sketches
tact batch ./sketches ./output --preset sketch --detect-text --verbose

# Convert with zoom to a specific region
tact convert plan.jpg --preset floor_plan --zoom-region 25,30,50,40 --verbose
```

## Output

- PDF file at 300 DPI
- Pure black and white (no grayscale)
- Optimized for PIAF swell paper
- Optional Braille labels with key page
