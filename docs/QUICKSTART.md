# Quick Start Guide

Get running in 5 minutes. Convert your first image to a tactile-ready PDF.

## Prerequisites

- **Python 3.8+**
- **Windows users:** You'll need WSL (Windows Subsystem for Linux). See [Windows Quick Start](guides/WINDOWS-QUICKSTART.md) first.
- **macOS/Linux:** You're ready to go.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/ethanshig/pai-radical-accessibility.git
cd pai-radical-accessibility

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows WSL: same command

# 3. Install dependencies
pip install -e ./lib/tactile-core

# 4. Verify it works
tact info
```

You should see toolkit information and "Ready to convert images!"

## Your First Conversion

```bash
tact convert samples/plan_test.jpg --preset floor_plan --verbose
```

This converts a sample floor plan to a PIAF-ready PDF. You'll see:
- Processing steps in the terminal
- Output file: `samples/plan_test_piaf.pdf`

Open the PDF to see the high-contrast black & white result.

## What Just Happened?

The toolkit:
1. Loaded the floor plan image
2. Converted it to grayscale
3. Applied a threshold to create pure black & white
4. Checked the density (prevents paper swelling on PIAF)
5. Generated a 300 DPI PDF ready for tactile printing

## Try These Next

### Add Braille Labels
Detect text in the image and convert to Braille:
```bash
tact convert samples/plan_test.jpg --detect-text --verbose
```

### Use Different Presets
Each preset is optimized for different image types:
```bash
# For hand-drawn sketches
tact convert your-sketch.jpg --preset sketch

# For photographs
tact convert photo.jpg --preset photograph

# See all presets
tact presets
```

### Enhance Low-Contrast Images
```bash
tact convert faint-drawing.jpg --enhance s_curve --verbose
```

### Process Multiple Files
```bash
tact batch ./input-folder ./output-folder --preset floor_plan
```

## Common Issues

**"Command not found: tact"**
- Make sure you activated the virtual environment: `source venv/bin/activate`

**Output is too dark/light**
- Adjust threshold: `--threshold 100` (lower = lighter) or `--threshold 160` (higher = darker)
- Default is 128

**Image has too much black (density warning)**
- Add `--auto-reduce-density` to automatically fix it

## Next Steps

- See all options: `tact convert --help`
- Full documentation: [README.md](../README.md)
- Text detection guide: [TEXT_DETECTION_QUICKSTART.md](guides/TEXT_DETECTION_QUICKSTART.md)
