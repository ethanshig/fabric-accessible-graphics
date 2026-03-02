---
name: pai-radical-accessibility
pack-id: pai-radical-accessibility-v1.1.0
version: 1.1.0
author: ethanshig
description: Make architectural graphics accessible to blind and low-vision students through tactile conversion, AI generation, and rich descriptions
type: toolkit
purpose-type: [accessibility, architecture, tactile-graphics, education]
platform: any
dependencies: [python3.10+]
keywords: [accessibility, tactile, PIAF, braille, architecture, blind, low-vision]
---

# pai-radical-accessibility

**Make architectural graphics accessible to blind and low-vision students.**

A toolkit for converting, generating, describing, and designing architectural graphics for PIAF (Picture In A Flash) tactile printing. Works standalone with Claude Code or as a PAI Pack.

## Capabilities

| Capability | Purpose | Use When |
|------------|---------|----------|
| **Tactile Conversion** (TACT CLI + MCP) | Convert images to PIAF-ready tactile PDFs | You have an image that needs tactile output |
| **Accessible Description** (MCP tool) | Rich verbal descriptions via Arch-Alt-Text | Quick understanding without printing |
| **Accessible Rhino** (TASC CLI) | Programmatic Rhino design with accessible feedback | Creating or modifying building layouts |

## Quick Start

```bash
# Install the pack
cd radical-accessibility
pip install -e ./lib/tactile-core

# Convert an image
tact convert floor-plan.jpg --preset floor_plan --verbose

# With Braille labels
tact convert plan.jpg --detect-text --braille-grade 2
```

See [INSTALL.md](INSTALL.md) for complete installation instructions.

## Usage

### Tactile Conversion

Convert existing images to tactile-ready PDFs using code-based processing.

```bash
# Basic conversion
tact convert floor-plan.jpg

# With preset for optimal settings
tact convert sketch.png --preset sketch

# With Braille labels
tact convert plan.jpg --detect-text --braille-grade 2

# Automatic density reduction for complex images
tact convert dense-drawing.jpg --auto-reduce-density
```

**Available Presets**: floor_plan, section, elevation, site_plan, sketch, diagram, technical_drawing, photograph, presentation, detail_drawing

### Accessible Description

Generate rich verbal descriptions following the Arch-Alt-Text framework.

Three-layer descriptions:
1. **Macro**: Medium, subject, purpose (3 sentences)
2. **Meso**: Composition, layout, relationships (4+ sentences)
3. **Micro**: Details, dimensions, materials, analogies (8+ sentences)

Use the MCP tool `describe_image` or see `docs/references/ArchAltText.md` for the full framework.

### Accessible Rhino

Programmatic architectural design through the TASC (Tactile Architecture Scripting Console) CLI. Gives blind and low-vision architects direct control of Rhino site layouts with accessible text feedback.

TASC commands cover the full structural design workflow:

| Command | Purpose |
|---------|---------|
| `tasc site` / `tasc grid` | Site boundary and structural grid |
| `tasc zone` / `tasc bay` | Program zones and structural bays with columns |
| `tasc corridor` / `tasc void` | Corridors and courtyards within bays |
| `tasc label` | Text and Braille labels |
| `tasc undo` / `tasc remove` | Undo last command or remove elements |
| `tasc connect` | Test Rhino connection (auto-sets LightPen display mode) |
| `tasc display [MODE]` | Get or set viewport display mode |
| `tasc capture [FILE]` | Capture viewport for TACT (switches to Pen mode, captures, restores LightPen) |
| `tasc export piaf\|3dm\|text` | Export to tactile PDF, Rhino file, or text |

**Rhino-to-TACT workflow**: TASC uses LightPen display mode for design (dark background, light lines). For TACT/PIAF export, `tasc capture` temporarily switches to Pen mode (white background, black lines), captures the viewport, and restores LightPen. This ensures correct thresholding.

See [lib/tasc-core/README.md](lib/tasc-core/README.md) for the full TASC CLI and DSL reference.

### Accessible Client (acclaude)

A JAWS/NVDA-compatible Claude Code client that bypasses the Ink TUI entirely. Uses `claude -p` headless mode with plain text output only.

```bash
# From WSL2/Linux:
./bin/acclaude

# From Windows (double-click):
bin\acclaude.bat
```

Features: multi-turn sessions, session persistence, JAWS announcement, slash commands (`/help`, `/repeat`, `/history`, `/new`, `/quit`).

See [INSTALL.md](INSTALL.md) Step 7 for setup.

## AI Integration

When Claude Code opens this repository:

1. It reads `.claude.md` for project context and capabilities
2. It reads `.claude/CLAUDE.md` for screen-reader-specific interaction rules
3. The TACT MCP server provides conversion tools directly to Claude

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
│   ├── accessible-client/     # acclaude - JAWS-compatible Claude client
│   └── hooks/                 # Screen reader + learning hooks
├── mcp/                       # MCP server entry point for Claude Code
├── patterns/                  # Tactile guidelines + Arch-Alt-Text prompt
├── samples/                   # Test images
└── docs/                      # Documentation and references
```

## The Two CLIs

| CLI | Package | Purpose | Install |
|-----|---------|---------|---------|
| `tact` | `tactile-core` | Convert images to PIAF tactile PDFs | `pip install -e lib/tactile-core/` |
| `tasc` | `tasc-core` | Programmatic Rhino design with accessible CLI | `pip install -e lib/tasc-core/` |

See [lib/tasc-core/README.md](lib/tasc-core/README.md) for full TASC documentation.

## MCP Server Setup (Claude Code)

To use with Claude Code, configure the MCP server. See [docs/MCP_SETUP.md](docs/MCP_SETUP.md) for full details, or use the quick setup:

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

## Optional Hooks (Learning System)

Screen reader hooks and conversion tracking hooks are included in `src/hooks/`. See [src/hooks/README.md](src/hooks/README.md) for configuration.

## CLI Reference

### convert

Convert an image to PIAF-ready PDF format.

```bash
tact convert IMAGE [OPTIONS]
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

### presets

Show available conversion presets.

```bash
tact presets
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
- Node.js (optional, for screen reader hooks)
- rhinomcp (optional, `pip install rhinomcp` — for Claude Code to Rhino MCP bridge)
- RhinoMCP Rhino plugin (optional — for live TASC to Rhino viewport connection)

See [INSTALL.md](INSTALL.md) for installation instructions.

## License

MIT License

## Acknowledgments

Developed for accessible architecture education, enabling blind and low-vision students to access visual materials through tactile graphics.
