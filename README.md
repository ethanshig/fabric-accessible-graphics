# Fabric Accessible Graphics Toolkit

A command-line toolkit for converting images to high-contrast, tactile-ready formats for PIAF (Picture In A Flash) machines. Designed with accessibility in mind for full screen-reader compatibility.

## Overview

This toolkit helps convert visual images into tactile graphics suitable for printing on PIAF machines, making architectural drawings, floor plans, and other visual materials accessible to blind and low-vision users.

## Features

### Core Features
- Convert images to high-contrast black and white PDFs
- Optimized for PIAF tactile printing (300 DPI)
- Full screen-reader accessibility
- Automatic density checking to prevent paper swelling
- Support for multiple paper sizes (Letter, Tabloid)
- Interactive mode with step-by-step guidance
- Customizable threshold settings

### Phase 2 Features
- **S-Curve Enhancement**: Professional contrast adjustment like Photoshop curves
- **Preset System**: 10 optimized presets for common image types (floor_plan, sketch, photograph, etc.)
- **Batch Processing**: Convert entire directories of images at once
- **Multiple Enhancement Methods**: S-curve, auto-contrast, CLAHE, histogram equalization
- **Recursive Processing**: Handle nested folder structures
- **Progress Tracking**: See detailed progress for batch operations
- **Image Tiling**: Automatically split large images into multiple pages with registration marks for assembly
- **Automatic Density Reduction**: Automatically fix high-density images that would cause paper curling

### Phase 3 Features (NEW!)
- **Text & Dimension Detection**: OCR-based detection of dimensions and labels using Tesseract
- **Braille Conversion**: Automatic Braille label generation (Grade 1 and 2) using Liblouis
- **Unicode Braille Labels**: Overlaid on PDFs for tactile reading
- **Dimension Format Support**: Feet, inches, meters, millimeters, centimeters (10'-6", 3m, 120mm, etc.)
- **Configurable Placement**: Overlay or margin positioning for Braille labels
- **Text Whiteout**: Original text removed before Braille placement (prevents PIAF overlap)
- **Automatic Overlap Prevention**: Overlapping Braille labels automatically repositioned

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. Navigate to the project directory:

```bash
cd fabric-accessible-graphics
```

2. Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install the package:

```bash
pip install -e .
```

5. Verify installation:

```bash
fabric-access --version
fabric-access --help
```

## Usage

### Basic Usage

Convert an image to PIAF-ready PDF:

```bash
fabric-access image-to-piaf floor-plan.jpg
```

This will create `floor-plan_piaf.pdf` in the same directory.

### Specify Output File

```bash
fabric-access image-to-piaf sketch.png --output my-output.pdf
```

### Custom Threshold

Adjust the black/white threshold (0-255). Higher values produce more black:

```bash
fabric-access image-to-piaf drawing.jpg --threshold 140
```

### Paper Size

Specify paper size (letter or tabloid):

```bash
fabric-access image-to-piaf large-plan.png --paper-size tabloid
```

### Verbose Mode

Get detailed progress messages:

```bash
fabric-access image-to-piaf plan.jpg --verbose
```

### Interactive Mode

Step-by-step guidance with prompts:

```bash
fabric-access image-to-piaf sketch.png --interactive
```

### Complete Example

```bash
fabric-access image-to-piaf floor-plan.jpg \
  --output result.pdf \
  --threshold 135 \
  --paper-size letter \
  --verbose \
  --interactive
```

### Phase 2 Features

#### Using Presets (Recommended - Easiest!)

```bash
# List all available presets
fabric-access list-presets

# Use a preset optimized for your image type
fabric-access image-to-piaf floor-plan.jpg --preset floor_plan --verbose
fabric-access image-to-piaf sketch.png --preset sketch
fabric-access image-to-piaf photo.jpg --preset photograph
```

Available presets: `floor_plan`, `sketch`, `photograph`, `elevation`, `section`, `technical_drawing`, `diagram`, `site_plan`, `detail_drawing`, `presentation`

#### S-Curve Enhancement

Boost contrast like Photoshop curves:

```bash
# Standard S-curve enhancement (recommended)
fabric-access image-to-piaf plan.jpg --enhance s_curve --verbose

# Stronger enhancement for faint images
fabric-access image-to-piaf faint-sketch.jpg --enhance s_curve --enhance-strength 1.5

# Other enhancement methods
fabric-access image-to-piaf scan.jpg --enhance auto_contrast
fabric-access image-to-piaf photo.jpg --enhance clahe
```

#### Batch Processing

Convert multiple files at once:

```bash
# Process all images in a folder with a preset
fabric-access batch ./drawings ./output --preset floor_plan

# Process recursively through subdirectories
fabric-access batch ./all-plans ./output --preset floor_plan --recursive

# Custom settings for all files
fabric-access batch ./sketches ./output --threshold 130 --enhance s_curve

# Process only specific file types
fabric-access batch ./images ./output --pattern "*.png,*.jpg" --preset photograph
```

#### Automatic Density Reduction

PIAF paper swells when heated. Too much black (greater than 45% density) causes excessive swelling, paper curling, and detail loss. The automatic density reduction feature fixes this problem by intelligently reducing black pixel density while preserving image structure.

```bash
# Automatically reduce density if too high (basic usage)
fabric-access image-to-piaf dense-floor-plan.jpg --auto-reduce-density --verbose

# Custom target density (default is 30%)
fabric-access image-to-piaf complex-drawing.png --auto-reduce-density --target-density 0.25

# Allow more iterations for heavily dense images (default is 10)
fabric-access image-to-piaf very-dense-sketch.jpg --auto-reduce-density --max-reduction-iterations 15

# Combine with other features for best results
fabric-access image-to-piaf scan.jpg --enhance s_curve --auto-reduce-density --verbose
```

How it works:
- Detects when density exceeds 45% (unsafe threshold)
- Applies morphological erosion iteratively to reduce density
- Targets optimal density range (less than 30% by default)
- Preserves image structure and important details
- Provides detailed progress feedback

Batch processing with automatic density reduction:
```bash
# Apply to all images in a directory
fabric-access batch ./drawings ./output --auto-reduce-density --verbose

# With custom settings
fabric-access batch ./plans ./output --auto-reduce-density --target-density 0.28 --preset floor_plan
```

When to use:
- Images with high black pixel density (greater than 40%)
- Complex floor plans with heavy line work
- Scanned documents with dark backgrounds
- When you get density warnings during conversion

Note: If density reduction is disabled (default), the tool will warn you about high density and suggest using this feature.

#### Image Tiling for Large Images

When images exceed paper dimensions, use tiling to split them into multiple pages:

```bash
# Enable automatic tiling for oversized images
fabric-access image-to-piaf large-floor-plan.jpg --enable-tiling --verbose

# Custom tile overlap (default is 10%)
fabric-access image-to-piaf huge-drawing.png --enable-tiling --tile-overlap 0.15

# Disable registration marks if not needed
fabric-access image-to-piaf large-map.tif --enable-tiling --no-registration-marks

# Combine with other features
fabric-access image-to-piaf oversized-plan.jpg --enable-tiling --preset floor_plan --paper-size tabloid
```

Tiling features:
- Automatic detection of oversized images
- Configurable overlap between tiles (default 10%)
- Registration marks at tile corners for alignment
- Assembly instructions included on first page
- Tile position labels on each page
- Works with both letter and tabloid paper sizes

## Text Detection & Braille Conversion

Detect text and dimensions on architectural drawings and automatically add Braille labels to PDFs.

**Status:** ✅ FULLY OPERATIONAL (Updated Dec 17, 2025)

### Basic Usage

```bash
# Detect text and add Braille labels
fabric-access image-to-piaf floor-plan.jpg --detect-text --verbose

# Use Grade 2 Braille (contracted)
fabric-access image-to-piaf plan.png --detect-text --braille-grade 2

# Combined with other features
fabric-access image-to-piaf large-plan.jpg --detect-text --auto-reduce-density --enable-tiling
```

**Note:** Braille labels now render as proper Unicode Braille dots (⠠⠅⠊⠞⠉⠓⠑⠝) using DejaVu Sans font. See `BRAILLE_STATUS.md` for complete details.

### Supported Dimension Formats

Text detection recognizes the following architectural dimension formats:

- **Feet**: `10'`, `24'`
- **Inches**: `6"`, `120"`
- **Combined**: `10'-6"`, `3'-4"`
- **Meters**: `3m`, `5.5m`
- **Millimeters**: `120mm`, `2400mm`
- **Centimeters**: `50cm`, `100cm`

### Requirements

Text detection requires Tesseract OCR (✅ Installed):

```bash
# Ubuntu/Debian/WSL
sudo apt-get install tesseract-ocr
```

Braille conversion requires Liblouis (✅ Configured):

```bash
# Ubuntu/Debian/WSL
sudo apt-get install liblouis-dev python3-louis liblouis-data

# Create symlink for venv access (already done):
ln -s /usr/lib/python3/dist-packages/louis venv/lib/python3.12/site-packages/louis
```

**Current Setup:** Both Tesseract OCR 5.3.4 and liblouis 3.29.0 are installed and working.

### Batch Processing with Text Detection

```bash
# Detect text on all floor plans
fabric-access batch ./plans ./output --detect-text --preset floor_plan --verbose
```

## Supported File Formats

Input formats:
- JPG/JPEG
- PNG
- TIFF/TIF
- BMP
- GIF
- PDF

Output format:
- PDF (300 DPI, pure black and white)

## Paper Sizes

- **letter**: 8.5 x 11 inches (2550 x 3300 pixels at 300 DPI)
- **tabloid**: 11 x 17 inches (3300 x 5100 pixels at 300 DPI)

Images larger than these dimensions will require tiling (use --enable-tiling)

## Command Reference

### image-to-piaf

Convert an image to PIAF-ready PDF format.

Options:
- `--output, -o PATH`: Output PDF file path (auto-generated if not specified)
- `--threshold, -t INT`: Black/white threshold 0-255 (default: 128)
- `--paper-size, -p SIZE`: Paper size: letter or tabloid (default: letter)
- `--preset NAME`: Use a preset configuration (see `list-presets`)
- `--enhance, -e METHOD`: Enhancement method: s_curve, auto_contrast, clahe, histogram
- `--enhance-strength FLOAT`: S-curve strength 0.0-2.0 (default: 1.0)
- `--auto-reduce-density`: Automatically reduce density if too high (default: off)
- `--target-density FLOAT`: Target density percentage 0.0-1.0 (default: 0.30)
- `--max-reduction-iterations INT`: Maximum erosion iterations (default: 10)
- `--enable-tiling`: Enable automatic tiling for oversized images
- `--tile-overlap FLOAT`: Overlap percentage between tiles 0.0-1.0 (default: 0.1)
- `--no-registration-marks`: Disable registration marks on tiles
- `--detect-text`: Enable OCR-based text and dimension detection
- `--braille-grade GRADE`: Braille grade (1 or 2, default: 1)
- `--braille-placement PLACEMENT`: Label placement (overlay or margin, default: overlay)
- `--verbose, -v`: Show detailed progress messages
- `--interactive, -i`: Interactive mode with step-by-step prompts
- `--config PATH`: Path to custom tactile_standards.yaml configuration

### batch

Batch convert multiple images to PIAF-ready PDFs.

```bash
fabric-access batch INPUT_DIR OUTPUT_DIR [OPTIONS]
```

Options:
- `--pattern TEXT`: File patterns to process, comma-separated (default: *.jpg,*.jpeg,*.png,*.tiff,*.tif)
- `--preset NAME`: Apply preset to all images
- `--threshold, -t INT`: Threshold for all images (overrides preset)
- `--enhance, -e METHOD`: Enhancement method for all images (overrides preset)
- `--paper-size, -p SIZE`: Paper size for all outputs
- `--auto-reduce-density`: Automatically reduce density for all images if too high
- `--target-density FLOAT`: Target density percentage for all images (0.0-1.0, default: 0.30)
- `--max-reduction-iterations INT`: Maximum erosion iterations for density reduction (default: 10)
- `--detect-text`: Enable OCR-based text and dimension detection for all images
- `--braille-grade GRADE`: Braille grade (1 or 2, default: 1)
- `--braille-placement PLACEMENT`: Label placement (overlay or margin, default: overlay)
- `--recursive, -r`: Process subdirectories recursively
- `--verbose, -v`: Show detailed progress for each file

### list-presets

List all available conversion presets:

```bash
fabric-access list-presets
```

### version

Display version information:

```bash
fabric-access version
```

### info

Display toolkit information and supported formats:

```bash
fabric-access info
```

## Understanding Threshold Values

The threshold determines which pixels become black vs white:

- **Lower values (80-120)**: More white, less black - good for dark images
- **Default (128)**: Balanced conversion
- **Higher values (140-180)**: More black, less white - good for light sketches

## Density Warnings

The toolkit automatically checks black pixel density to prevent excessive swelling during PIAF printing:

- **Target**: Less than 30% black pixels (optimal)
- **Warning**: 40-45% black pixels
- **Error**: Above 45% black pixels

If you get density warnings, you have several options:
- **Use automatic density reduction** (recommended): Add `--auto-reduce-density` to automatically fix the problem
- Increase the threshold value (makes more pixels white): `--threshold 150`
- Use a different input image with less dense content
- Simplify the original drawing before conversion

Example with automatic density reduction:
```bash
fabric-access image-to-piaf dense-image.jpg --auto-reduce-density --verbose
```

## Accessibility Features

This toolkit is designed for screen-reader users:

- Clear, descriptive status messages
- No emoji or visual-only symbols
- Consistent message formatting
- Real-time output (no buffering)
- Interactive mode for guided workflow
- Detailed error messages with solutions

## Configuration

Advanced users can customize processing settings by editing:

```
src/fabric_access/data/tactile_standards.yaml
```

Settings include:
- Default threshold
- Output DPI
- Density limits and automatic reduction settings
- Paper sizes
- Line thickness standards (for future features)
- Automatic density reduction parameters (target density, max iterations, kernel size)

## Troubleshooting

### File Not Found Error

Make sure the file path is correct and the file exists:

```bash
ls -l your-file.jpg
```

### Unsupported Format Error

Check that your file is in a supported format (JPG, PNG, TIFF, BMP, GIF, or PDF).

### Density Too High Warning

Try increasing the threshold value:

```bash
fabric-access image-to-piaf plan.jpg --threshold 150
```

### Permission Denied Error

Make sure you have write permissions in the output directory:

```bash
ls -ld /path/to/output/directory
```

## Development Roadmap

### Phase 1 (Completed - MVP)
- Basic image to PIAF conversion
- Threshold-based B&W conversion
- Density checking
- Screen-reader accessible CLI

### Phase 2 (Completed)
- Image tiling for large drawings (>11x17")
- Contrast enhancement (S-curve, CLAHE, etc.)
- Batch processing
- Preset system for different image types
- Automatic density reduction
- Registration marks and assembly instructions

### Phase 3 (Completed)
- Text and dimension detection with Tesseract OCR
- Braille conversion with Liblouis (Grade 1 and 2)
- Unicode Braille label overlays on PDFs
- Support for 6 dimension formats (feet, inches, meters, mm, cm)

### Phase 4 (Future)
- AI-powered image description
- Pattern chaining with other tools
- Advanced tactile pattern optimization
- Smart label positioning to avoid image features

## Contributing

This toolkit is designed for accessibility and educational use. Feedback and contributions are welcome.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feedback, please open an issue on the project repository.

## Acknowledgments

Developed for accessible architecture education, enabling blind and low-vision students to access visual materials through tactile graphics.
