---
name: Radical Accessibility
pack-id: ethanshig-radical-accessibility-v1.1.0
version: 1.1.0
author: ethanshig
description: Make architectural graphics accessible to blind and low-vision students through tactile conversion, AI generation, and rich descriptions
type: skill-bundle
purpose-type: [accessibility, architecture, tactile-graphics, education]
platform: claude-code
dependencies: [python3.10+, tesseract-ocr, poppler-utils]
keywords: [accessibility, tactile, PIAF, braille, architecture, blind, low-vision]
---

# Radical Accessibility

**Make architectural graphics accessible to blind and low-vision students.**

A PAI Pack providing three skills for converting, generating, and describing architectural images for PIAF (Picture In A Flash) tactile printing.

## The Three Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| **TactileConversion** | Process existing images into tactile PDFs | Source is clean, quick conversion needed |
| **TactileGeneration** | AI-powered tactile image creation | Source is complex/cluttered, or creating from description |
| **AccessibleDescription** | Rich verbal descriptions (Arch-Alt-Text) | Quick understanding without printing, remote access |

## Quick Start

```bash
# Install the pack
cd radical-accessibility
pip install -e ./lib/tactile-core

# Convert an image
tactile image-to-piaf floor-plan.jpg --preset floor_plan --verbose

# With Braille labels
tactile image-to-piaf plan.jpg --detect-text --braille-grade 2
```

See [INSTALL.md](INSTALL.md) for complete installation instructions.

## Skills Overview

### TactileConversion

Convert existing images to tactile-ready PDFs using code-based processing.

**Triggers**: "convert to tactile", "make tactile version", "PIAF conversion"

```bash
# Basic conversion
tactile image-to-piaf floor-plan.jpg

# With preset for optimal settings
tactile image-to-piaf sketch.png --preset sketch

# With Braille labels
tactile image-to-piaf plan.jpg --detect-text --braille-grade 2

# Automatic density reduction for complex images
tactile image-to-piaf dense-drawing.jpg --auto-reduce-density
```

**Available Presets**: floor_plan, section, elevation, site_plan, sketch, diagram, technical_drawing, photograph, presentation, detail_drawing

### TactileGeneration

Create NEW tactile images using AI when source images are too complex or cluttered.

**Triggers**: "generate tactile", "simplify for tactile", "stratify drawing"

- Interpret and recreate complex drawings as clean tactile graphics
- Stratify multi-system drawings into separate layers
- Generate from text descriptions (no source image needed)
- Post-process through tactile-core for Braille labels

### AccessibleDescription

Generate rich verbal descriptions following the Arch-Alt-Text framework.

**Triggers**: "describe image", "explain drawing", "accessibility description"

Three-layer descriptions:
1. **Macro**: Medium, subject, purpose (3 sentences)
2. **Meso**: Composition, layout, relationships (4+ sentences)
3. **Micro**: Details, dimensions, materials, analogies (8+ sentences)

## Features

### Core Capabilities

- **High-contrast processing** - Convert to pure black/white optimized for PIAF
- **10 optimized presets** - Floor plans, sketches, sections, photographs, etc.
- **Text detection** - OCR with Tesseract to identify labels and dimensions
- **Braille conversion** - Grade 1 and Grade 2 Braille using Liblouis
- **Auto-scaling** - Enlarge images so Braille labels fit in original text boxes
- **Abbreviation keys** - Generate key pages for labels that don't fit
- **Density management** - Automatic density reduction to prevent paper curling
- **Image tiling** - Split large images across multiple pages with registration marks
- **Region zoom** - Crop to specific areas (rooms, details) and fill page

### Supported Formats

**Input**: JPG, PNG, TIFF, BMP, GIF, PDF

**Output**: PDF (300 DPI, pure black and white)

### Paper Sizes

- **Letter**: 8.5 x 11 inches (2550 x 3300 pixels at 300 DPI)
- **Tabloid**: 11 x 17 inches (3300 x 5100 pixels at 300 DPI)

## Directory Structure

```
radical-accessibility/
├── lib/
│   ├── tactile-core/          # TACT - image-to-tactile PDF conversion
│   │   ├── pyproject.toml
│   │   └── src/tactile_core/
│   └── tasc-core/             # TASC - programmatic Rhino design CLI
│       ├── pyproject.toml
│       └── src/tasc_core/
├── src/
│   ├── skills/                # PAI skill definitions
│   │   ├── TactileConversion/
│   │   ├── TactileGeneration/
│   │   └── AccessibleDescription/
│   ├── tools/                 # TypeScript tool wrappers
│   ├── hooks/                 # Optional hooks
│   └── shared/                # Shared guidelines
├── mcp/                       # MCP server for non-PAI users
├── samples/                   # Test images
└── docs/                      # Documentation
```

## The Two CLIs

| CLI | Package | Purpose | Install |
|-----|---------|---------|---------|
| `tact` | `tactile-core` | Convert images to PIAF tactile PDFs | `pip install -e lib/tactile-core/` |
| `tasc` | `tasc-core` | Programmatic Rhino design with accessible CLI | `pip install -e lib/tasc-core/` |

See [lib/tasc-core/README.md](lib/tasc-core/README.md) for full TASC documentation.

## Optional Hooks (Learning System)

For enhanced functionality, install the optional hooks:

- **ImageDetector** - Proactively offers tactile conversion when architectural images are detected
- **ConversionTracker** - Records all conversion attempts for learning
- **FeedbackCapture** - Captures student ratings to improve recommendations

```bash
# Test hook functionality
echo '{"message": "here is a floor plan"}' | bun src/hooks/ImageDetector.ts
```

Memory data is stored in `~/.radical-accessibility/memory/` and includes:
- Conversion history with settings used
- Learned preferences by image type
- Student feedback and ratings
- Aggregated insights

See [src/hooks/README.md](src/hooks/README.md) for configuration.

## For Non-PAI Users

If you're using Claude Code without PAI, you can use the MCP server directly:

```json
{
    "mcpServers": {
        "tactile": {
            "command": "python",
            "args": ["/path/to/radical-accessibility/mcp/server.py"]
        }
    }
}
```

See [mcp/README.md](mcp/README.md) for details.

## CLI Reference

### image-to-piaf

Convert an image to PIAF-ready PDF format.

```bash
tactile image-to-piaf IMAGE [OPTIONS]
```

Key options:
- `--output, -o PATH`: Output PDF path
- `--threshold, -t INT`: Black/white threshold 0-255 (default: 128)
- `--paper-size, -p SIZE`: letter or tabloid
- `--preset NAME`: Use optimized preset
- `--detect-text`: Enable OCR text detection
- `--braille-grade GRADE`: 1 (uncontracted) or 2 (contracted)
- `--auto-reduce-density`: Fix high-density images
- `--enable-tiling`: Split oversized images
- `--zoom-region X,Y,W,H`: Crop to region (percentages)
- `--verbose, -v`: Detailed progress

### batch

Batch convert multiple images.

```bash
tactile batch INPUT_DIR OUTPUT_DIR [OPTIONS]
```

### list-presets

Show available conversion presets.

```bash
tactile list-presets
```

## Accessibility Design

This toolkit is designed for screen-reader users:

- Clear, descriptive status messages
- No emoji or visual-only symbols in CLI output
- Consistent message formatting
- Real-time output (no buffering)
- Interactive mode for guided workflow
- Detailed error messages with solutions

## Requirements

- Python 3.10+
- Tesseract OCR (for text detection)
- Poppler (for PDF processing)
- Liblouis (optional, for Grade 2 Braille)
- Bun (optional, for hooks/learning system)
- rhinomcp (optional, `pip install rhinomcp` — for Claude Code ↔ Rhino MCP bridge with native tools)
- RhinoMCP Rhino plugin (optional — for live TASC ↔ Rhino viewport connection)

See [INSTALL.md](INSTALL.md) for installation instructions.

## License

MIT License

## Acknowledgments

Developed for accessible architecture education, enabling blind and low-vision students to access visual materials through tactile graphics.
