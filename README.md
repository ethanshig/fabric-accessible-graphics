---
name: pai-radical-accessibility
pack-id: pai-radical-accessibility-v1.1.0
version: 1.1.0
author: ethanshig
description: Make architectural graphics accessible to blind and low-vision students through tactile conversion, AI generation, and rich descriptions
type: skill-bundle
purpose-type: [accessibility, architecture, tactile-graphics, education]
platform: any
dependencies: [python3.10+]
keywords: [accessibility, tactile, PIAF, braille, architecture, blind, low-vision]
---

# pai-radical-accessibility

**Make architectural graphics accessible to blind and low-vision students.**

A PAI Pack providing four skills for converting, generating, describing, and designing architectural graphics for PIAF (Picture In A Flash) tactile printing.

## The Four Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| **TactileConversion** | Process existing images into tactile PDFs | Source is clean, quick conversion needed |
| **TactileGeneration** | AI-powered tactile image creation | Source is complex/cluttered, or creating from description |
| **AccessibleDescription** | Rich verbal descriptions (Arch-Alt-Text) | Quick understanding without printing, remote access |
| **AccessibleRhino** | Programmatic Rhino design via TASC CLI | Creating or modifying building layouts with accessible feedback |

## Quick Start

```bash
# Install the pack
cd radical-accessibility
pip install -e ./lib/tactile-core

# Convert an image
tact image-to-piaf floor-plan.jpg --preset floor_plan --verbose

# With Braille labels
tact image-to-piaf plan.jpg --detect-text --braille-grade 2
```

See [INSTALL.md](INSTALL.md) for complete installation instructions.

## Skills Overview

### TactileConversion

Convert existing images to tactile-ready PDFs using code-based processing.

**Triggers**: "convert to tactile", "make tactile version", "PIAF conversion"

```bash
# Basic conversion
tact image-to-piaf floor-plan.jpg

# With preset for optimal settings
tact image-to-piaf sketch.png --preset sketch

# With Braille labels
tact image-to-piaf plan.jpg --detect-text --braille-grade 2

# Automatic density reduction for complex images
tact image-to-piaf dense-drawing.jpg --auto-reduce-density
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

### AccessibleRhino

Programmatic architectural design through the TASC (Tactile Architecture Scripting Console) CLI. Gives blind and low-vision architects direct control of Rhino site layouts with accessible text feedback.

**Triggers**: "design in Rhino", "create floor plan", "place bay", "TASC command"

TASC commands cover the full structural design workflow:

| Command | Purpose |
|---------|---------|
| `tasc site` / `tasc grid` | Site boundary and structural grid |
| `tasc zone` / `tasc bay` | Program zones and structural bays with columns |
| `tasc corridor` / `tasc void` | Corridors and courtyards within bays |
| `tasc label` | Text and Braille labels |
| `tasc undo` / `tasc remove` | Undo last command or remove elements |
| `tasc export piaf\|3dm\|text` | Export to tactile PDF, Rhino file, or text |

See [lib/tasc-core/README.md](lib/tasc-core/README.md) for the full TASC CLI and DSL reference.

## AI Installation

This pack is designed for AI-assisted installation. When Claude Code opens this repository:

1. It reads `.claude.md` for project context and capabilities
2. It reads `src/skills/*/SKILL.md` for available skills and triggers
3. It reads `.claude/CLAUDE.md` for screen-reader-specific interaction rules

To install the Python libraries:

```bash
pip install -e lib/tactile-core/    # TACT: image-to-tactile conversion
pip install -e lib/tasc-core/       # TASC: programmatic Rhino design
```

For human setup instructions, see [INSTALL.md](INSTALL.md).

## Features

### Core Capabilities

- **High-contrast processing** - Convert to pure black/white optimized for PIAF
- **10 optimized presets** - Floor plans, sketches, sections, photographs, etc.
- **Text detection** - OCR with EasyOCR to identify labels and dimensions
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
│   │   ├── AccessibleDescription/
│   │   └── AccessibleRhino/
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
tact image-to-piaf IMAGE [OPTIONS]
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
tact batch INPUT_DIR OUTPUT_DIR [OPTIONS]
```

### list-presets

Show available conversion presets.

```bash
tact list-presets
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
- EasyOCR (for text detection — installed via pip, no system package needed)
- Liblouis (optional, for Grade 2 Braille)
- Poppler (optional, for multi-page PDF input — `apt install poppler-utils`)
- Bun (optional, for hooks/learning system)
- rhinomcp (optional, `pip install rhinomcp` — for Claude Code to Rhino MCP bridge)
- RhinoMCP Rhino plugin (optional — for live TASC to Rhino viewport connection)

See [INSTALL.md](INSTALL.md) for installation instructions.

## License

MIT License

## Acknowledgments

Developed for accessible architecture education, enabling blind and low-vision students to access visual materials through tactile graphics.
