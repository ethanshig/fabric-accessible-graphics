# MCP Server Setup Guide

This guide explains how to set up the fabric-access MCP server so Claude can convert architectural images to tactile graphics automatically.

## What is MCP?

MCP (Model Context Protocol) allows Claude to interact with local tools on your computer. With the fabric-access MCP server, you can simply tell Claude "convert this floor plan to tactile" and Claude will handle all the processing automatically.

## Prerequisites

1. fabric-accessible-graphics toolkit installed
2. Virtual environment activated
3. All dependencies installed (including `mcp>=1.0.0`)

## Installation

The MCP server is installed automatically with the toolkit. Verify it's available:

```bash
cd /mnt/c/Users/ethan/fabric-accessible-graphics
source venv/bin/activate
which fabric-access-mcp
```

## Configuration

### Claude Code

Add this to your Claude Code MCP settings (typically in `~/.config/claude-code/settings.json` or via the `/mcp` command):

```json
{
  "mcpServers": {
    "fabric-access": {
      "command": "/mnt/c/Users/ethan/fabric-accessible-graphics/venv/bin/fabric-access-mcp",
      "args": []
    }
  }
}
```

Or using Python directly:

```json
{
  "mcpServers": {
    "fabric-access": {
      "command": "/mnt/c/Users/ethan/fabric-accessible-graphics/venv/bin/python",
      "args": ["-m", "fabric_access.mcp_server.server"]
    }
  }
}
```

### Claude Desktop

For Claude Desktop, add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fabric-access": {
      "command": "/mnt/c/Users/ethan/fabric-accessible-graphics/venv/bin/fabric-access-mcp"
    }
  }
}
```

## Available Tools

After configuration, Claude has access to these tools:

### convert_to_tactile

Convert an image to PIAF-ready PDF.

**Parameters:**
- `image_path` (required): Path to input image
- `output_path`: Output PDF path (auto-generated if not specified)
- `preset`: Preset name (floor_plan, section, sketch, etc.)
- `threshold`: Black/white threshold 0-255
- `paper_size`: "letter" or "tabloid"
- `detect_text`: Enable OCR text detection (default: true)
- `braille_grade`: Braille grade 1 or 2 (default: 2)
- `auto_reduce_density`: Auto-reduce density if too high
- `tile_overlap`: Overlap between tiles 0.0-1.0 (default: 0.0)

**Auto-Scaling Parameters:**
- `auto_scale`: Enable automatic image scaling to fit Braille labels (default: true)
- `max_scale_factor`: Maximum scale factor (default: unlimited, warning at 300%+)
- `scale_percent`: Manual scale override (bypasses auto-scale calculation)

**Abbreviation Key Parameters:**
- `use_abbreviation_key`: Enable abbreviation key for labels that don't fit (default: true)
- `force_abbreviation_key`: Force ALL labels to use abbreviations (default: false)

**Zoom Parameters:**
- `zoom_region`: Percentage-based region [x%, y%, width%, height%] (e.g., [25, 30, 50, 40])
- `zoom_to`: Natural language zoom target (e.g., "kitchen", "Bedroom 1") - uses Claude vision
- `zoom_regions`: List of regions for multi-page output (each with x_percent, y_percent, width_percent, height_percent, label)

**Example usage:**
> "Convert /home/student/floor-plan.jpg to tactile"
> "Convert section-detail.png using the section preset"
> "Convert this plan without auto-scaling" (set auto_scale=false)
> "Convert with maximum 150% scaling" (set max_scale_factor=1.5)
> "Convert floor-plan.jpg and zoom to the kitchen"
> "Convert plan.png with separate pages for each bedroom"

### list_presets

List available conversion presets.

**Example usage:**
> "What presets are available?"
> "Show me the conversion presets"

### analyze_image

Analyze an image before conversion.

**Parameters:**
- `image_path` (required): Path to image to analyze

**Example usage:**
> "Analyze /home/student/drawing.jpg before converting"
> "Check if this image will work for PIAF"

### describe_image

Generate a detailed architectural description of an image for accessibility. Uses the Arch-Alt-Text system to create multi-sensory descriptions specifically designed for blind/low-vision architecture students.

**Parameters:**
- `image_path` (required): Path to image to describe
- `detail_level`: "full" (default) or "brief"

**Output format:**
- Title: Identifies the piece
- Macro Layer: Medium, subject, purpose (3 sentences)
- Meso Layer: Composition, materials, orientation, scale (4+ sentences)
- Micro Layer: Details, textures, dimensions, multi-sensory analogies (8+ sentences)

**Requirements:**
- Requires `ANTHROPIC_API_KEY` environment variable to be set
- Uses Claude's vision API for image analysis

**Example usage:**
> "Describe the image at /home/student/section-drawing.jpg"
> "Give me a brief description of this floor plan"

## Example Conversations

### Basic Conversion

**Student:** Convert the floor plan at /home/student/structures/floor-plan.jpg to tactile

**Claude:** I'll convert that floor plan for you.

*[Uses convert_to_tactile tool]*

Converted successfully. Output saved to floor-plan_piaf.pdf. Added 12 Braille labels for detected text. Density 28% - optimal for PIAF printing. Ready to print!

### Using a Preset

**Student:** I have a structural section drawing at section.png - convert it

**Claude:** I'll use the section preset which is optimized for structural drawings.

*[Uses convert_to_tactile with preset="section"]*

Done! Converted using the 'section' preset. Output: section_piaf.pdf. 8 dimension labels converted to Grade 2 Braille. Ready for PIAF.

### Pre-flight Check

**Student:** Can you check if my drawing will work before converting?

**Claude:** I'll analyze it first.

*[Uses analyze_image tool]*

Analysis complete:
- Dimensions: 3300x2550 pixels (fits on tabloid)
- Estimated density: 35% (good for PIAF)
- Detected 23 text labels
- Recommended preset: floor_plan

Ready for conversion. Want me to proceed?

### Image Description

**Student:** Describe the building section at /home/student/structures/beam-section.png

**Claude:** I'll generate a detailed description for you.

*[Uses describe_image tool]*

Title: Unknown

A technical line drawing presents a structural building section cut through a multi-story frame. The image serves an analytical purpose, revealing the vertical organization of floors, beams, and columns. The atmosphere is clinical and instructional, typical of engineering coursework.

The composition centers on a rectangular frame approximately three stories tall, with the cut plane running vertically through the middle. Heavy line weights define the section-cut elements—columns and floor slabs shown in profile—while lighter lines indicate elements beyond the cut plane. The viewpoint is orthographic, looking perpendicular to the cut plane, with the top of the page representing the roof level...

[continues with Micro layer details about structural connections, dimensions, and multi-sensory analogies]

### Zooming to a Region

**Student:** Convert the floor plan at plan.jpg but just zoom to the kitchen area

**Claude:** I'll identify the kitchen region and zoom to it.

*[Uses convert_to_tactile with zoom_to="kitchen"]*

I found the kitchen in the upper-right area of the floor plan. Zoomed in and scaled to fill the page. Output: plan_kitchen_piaf.pdf. 4 Braille labels added for the zoomed region. Ready for PIAF!

### Multi-Region Zoom

**Student:** I need separate pages for each bedroom in this floor plan

**Claude:** I'll identify all bedrooms and create a multi-page PDF.

*[Uses convert_to_tactile with zoom_regions for each bedroom]*

Created a 3-page PDF:
- Page 1: Bedroom 1 (master, upper-left)
- Page 2: Bedroom 2 (lower-left)
- Page 3: Bedroom 3 (lower-right)

Each room is scaled to fill the page. Output: plan_zoomed_piaf.pdf

## Troubleshooting

### Server not starting

Check that the virtual environment is activated and dependencies are installed:

```bash
source venv/bin/activate
pip install mcp>=1.0.0
pip install -e .
```

### Tools not appearing in Claude

1. Restart Claude Code/Desktop after changing MCP configuration
2. Check the server path is correct
3. Verify the server can start: `fabric-access-mcp`

### Conversion fails

1. Check the image path is correct and accessible
2. Try with a different preset
3. Use `analyze_image` first to check the image

## Notes

- All processing happens locally on your computer
- Images never leave your machine (except for describe_image which uses Claude API)
- Grade 2 Braille is used by default (contracted)
- Text detection is enabled by default

## Environment Variables

For the `describe_image` tool, you need to set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or add it to the MCP server configuration:

```json
{
  "mcpServers": {
    "fabric-access": {
      "command": "/mnt/c/Users/ethan/fabric-accessible-graphics/venv/bin/fabric-access-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```
