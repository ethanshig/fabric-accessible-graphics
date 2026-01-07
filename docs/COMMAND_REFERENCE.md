# Fabric Accessible Graphics - Command Reference

Quick-lookup reference for all CLI commands and MCP tools. For tutorials and workflows, see [WALKTHROUGH.md](guides/WALKTHROUGH.md).

**Related docs:** [MCP_SETUP.md](guides/MCP_SETUP.md) | [TEXT-AND-BRAILLE-GUIDE.md](TEXT-AND-BRAILLE-GUIDE.md)

---

## Quick Start

```bash
# Most common usage:
fabric-access image-to-piaf floor-plan.jpg --preset floor_plan --detect-text --verbose
```

---

# PART 1: CLI Commands

## `fabric-access image-to-piaf`

Convert an image to PIAF-ready PDF.

```bash
fabric-access image-to-piaf INPUT_PATH [OPTIONS]
```

### Basic Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `INPUT_PATH` | path | required | Input image file |
| `--output, -o` | path | auto | Output PDF path |
| `--threshold, -t` | int | 128 | Black/white threshold (0-255) |
| `--paper-size, -p` | choice | letter | `letter` or `tabloid` |
| `--preset` | string | none | Preset name (see `list-presets`) |
| `--verbose, -v` | flag | false | Show detailed progress |
| `--interactive, -i` | flag | false | Step-by-step prompts |
| `--config` | path | none | Custom config file path |

### Enhancement Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--enhance, -e` | choice | none | `s_curve`, `auto_contrast`, `clahe`, `histogram` |
| `--enhance-strength` | float | 1.0 | S-curve strength (0.0-2.0) |

### Text & Braille Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--detect-text` | flag | false | Enable OCR text detection |
| `--braille-grade` | choice | 1 | `1` (uncontracted) or `2` (contracted) |
| `--braille-placement` | choice | overlay | `overlay` or `margin` |

### Zoom Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--zoom-region` | string | none | Region: `x%,y%,w%,h%` (e.g., `25,30,50,40`) |

### Tiling Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--enable-tiling` | flag | false | Split large images into pages |
| `--tile-overlap` | float | 0.0 | Overlap between tiles (0.0-1.0) |
| `--no-registration-marks` | flag | false | Disable alignment marks |

### Density Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--auto-reduce-density` | flag | false | Auto-reduce if >45% black |
| `--target-density` | float | 0.30 | Target density (0.0-1.0) |
| `--max-reduction-iterations` | int | 10 | Max erosion passes |

### Examples

```bash
# Basic with preset
fabric-access image-to-piaf plan.jpg --preset floor_plan --verbose

# With Braille labels (Grade 2)
fabric-access image-to-piaf plan.jpg --detect-text --braille-grade 2 --verbose

# Zoom to a region (25% from left, 30% from top, 50% wide, 40% tall)
fabric-access image-to-piaf plan.jpg --zoom-region 25,30,50,40 --verbose
```

---

## `fabric-access batch`

Batch convert multiple images.

```bash
fabric-access batch INPUT_DIR OUTPUT_DIR [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `INPUT_DIR` | path | required | Source directory |
| `OUTPUT_DIR` | path | required | Output directory |
| `--pattern` | string | `*.jpg,*.jpeg,*.png,*.tiff,*.tif` | File patterns |
| `--recursive, -r` | flag | false | Include subdirectories |

*Inherits all `image-to-piaf` options (threshold, preset, detect-text, etc.)*

### Example

```bash
fabric-access batch ./drawings ./output --preset floor_plan --detect-text --recursive --verbose
```

---

## `fabric-access list-presets`

Display all available conversion presets.

```bash
fabric-access list-presets
```

---

## `fabric-access info`

Display toolkit information and supported formats.

```bash
fabric-access info
```

---

## `fabric-access version`

Display version number.

```bash
fabric-access version
```

---

# PART 2: MCP Tools

For MCP server setup, see [MCP_SETUP.md](guides/MCP_SETUP.md).

## `convert_to_tactile`

Convert an image to PIAF-ready PDF.

### Basic Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | string | required | Input image path |
| `output_path` | string | auto | Output PDF path |
| `preset` | string | none | Preset name |
| `threshold` | int | 128 | B&W threshold (0-255) |
| `paper_size` | string | letter | `letter` or `tabloid` |

### Text & Braille Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `detect_text` | bool | true | Enable OCR |
| `braille_grade` | int | 2 | 1 or 2 |
| `claude_text_json` | string/list | none | Phase 2 hybrid OCR text |
| `use_grid_overlay` | bool | false | Grid cell positioning |

### Scaling Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_scale` | bool | true | Auto-scale for Braille fit |
| `max_scale_factor` | float | none | Scale cap (e.g., 2.0=200%) |
| `scale_percent` | float | none | Manual scale override |

### Abbreviation Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_abbreviation_key` | bool | true | Auto-abbreviate oversized labels |
| `force_abbreviation_key` | bool | false | Abbreviate ALL labels |

### Zoom Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `zoom_region` | tuple | none | `(x%, y%, w%, h%)` |
| `zoom_to` | string | none | Natural language target ("kitchen") |
| `zoom_regions` | list | none | Multi-region for multi-page output |

### Other Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_reduce_density` | bool | false | Auto-reduce if too dense |
| `tile_overlap` | float | 0.0 | Tile overlap (0.0-1.0) |
| `assess_quality` | bool | false | Return quality assessment |

### Natural Language Examples

| Task | Say to Claude |
|------|---------------|
| Basic conversion | "Convert floor-plan.jpg to tactile" |
| With preset | "Convert plan.jpg using the sketch preset" |
| Zoom to room | "Convert floor-plan.jpg and zoom to the kitchen" |
| Multi-region | "Convert plan.png with separate pages for each bedroom" |
| No auto-scale | "Convert plan.jpg with auto_scale=false" |

---

## `list_presets`

List available presets.

*No parameters*

---

## `analyze_image`

Pre-flight check with recommendations.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | string | required | Image to analyze |

---

## `describe_image`

Generate Arch-Alt-Text description for accessibility.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | string | required | Image to describe |
| `detail_level` | string | full | `full` or `brief` |

---

## `extract_text_with_vision`

Extract text using Claude's vision.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | string | required | Image path |
| `include_handwritten` | bool | true | Include handwriting |
| `include_dimensions` | bool | true | Identify dimensions |

---

## `assess_tactile_quality`

Compare original vs processed for quality.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `original_image_path` | string | required | Original image |
| `processed_image_path` | string | required | Processed B&W image |
| `image_type` | string | floor_plan | Image type for criteria |
| `current_params` | dict | none | Current conversion params |

---

# PART 3: Quick Reference

## Presets

| Preset | Best For | Threshold | Enhancement | Paper |
|--------|----------|-----------|-------------|-------|
| `floor_plan` | CAD floor plans | 140 | s_curve 1.0 | letter |
| `sketch` | Hand drawings | 130 | s_curve 1.3 | letter |
| `photograph` | Model photos | 120 | clahe | letter |
| `elevation` | Building elevations | 135 | s_curve 1.0 | letter |
| `section` | Building sections | 145 | s_curve 1.2 | letter |
| `site_plan` | Site/master plans | 140 | s_curve 1.0 | tabloid |
| `technical_drawing` | CAD exports | 150 | none | letter |
| `detail_drawing` | Fine linework | 145 | s_curve 1.1 | letter |
| `diagram` | Schematics | 135 | auto_contrast | letter |
| `presentation` | Large boards | 125 | clahe | tabloid |

## Common CLI Tasks

| Task | Command |
|------|---------|
| Basic conversion | `fabric-access image-to-piaf plan.jpg --preset floor_plan` |
| With Braille | `... --detect-text --braille-grade 2` |
| Zoom to region | `... --zoom-region 25,30,50,40` |
| Auto-reduce density | `... --auto-reduce-density` |
| Large image tiling | `... --enable-tiling --paper-size tabloid` |
| Batch folder | `fabric-access batch ./in ./out --preset floor_plan` |
| Recursive batch | `... --recursive` |

## Supported Formats

**Input:** JPG, JPEG, PNG, TIFF, TIF, BMP, GIF, PDF

**Output:** PDF (300 DPI, pure black & white)

## Paper Sizes

| Size | Dimensions | Pixels at 300 DPI |
|------|------------|-------------------|
| letter | 8.5" x 11" | 2550 x 3300 |
| tabloid | 11" x 17" | 3300 x 5100 |
