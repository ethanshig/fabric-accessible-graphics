# Fabric Accessible Graphics - User Walkthrough

This guide walks you through using the toolkit step-by-step.

## IMPORTANT: Windows Users Start Here

This toolkit runs in **WSL (Windows Subsystem for Linux)**, not in PowerShell or Command Prompt.

### Option A: Easy Start (Recommended)

**From PowerShell or Command Prompt:**

1. Navigate to the project folder in Windows Explorer:
   ```
   C:\Users\ethan\fabric-accessible-graphics
   ```

2. Double-click `run.ps1` or run in PowerShell:
   ```powershell
   cd C:\Users\ethan\fabric-accessible-graphics
   .\run.ps1
   ```

This automatically opens WSL with the environment activated.

### Option B: Manual WSL Start

1. **Open WSL** (any of these methods):
   - Type `wsl` in PowerShell or Command Prompt
   - Click Start menu → Search for "Ubuntu" or "WSL"
   - Open Windows Terminal and select Ubuntu/WSL

2. **Navigate to project:**
   ```bash
   cd /mnt/c/Users/ethan/fabric-accessible-graphics
   ```

3. **Run the start script:**
   ```bash
   ./run.sh
   ```

   **OR activate manually:**
   ```bash
   source venv/bin/activate
   ```

You'll see `(venv)` appear at the start of your command prompt, indicating the environment is active.

## Setup (One-Time Verification)

### Verify installation

Once in WSL with the environment activated:

```bash
fabric-access --version
```

You should see: `fabric-access, version 0.1.0`

## Basic Usage

### Step 1: Check what the tool can do

```bash
fabric-access info
```

This displays:
- Supported input formats
- Output format specifications
- Paper sizes available
- Accessibility features

### Step 2: Get help for a specific command

```bash
fabric-access image-to-piaf --help
```

This shows all available options and examples.

## Converting Your First Image

### Scenario 1: Basic Conversion (Simplest)

Convert an image with all default settings:

```bash
fabric-access image-to-piaf my-floor-plan.jpg
```

**What happens:**
- Loads `my-floor-plan.jpg`
- Converts to black and white using default threshold (128)
- Checks density to prevent paper swelling
- Creates `my-floor-plan_piaf.pdf` in the same directory
- Displays success message

### Scenario 2: Verbose Mode (Recommended for learning)

See detailed progress as the tool works:

```bash
fabric-access image-to-piaf my-floor-plan.jpg --verbose
```

**You'll see:**
```
Configuration loaded successfully
Input file: my-floor-plan.jpg
Output will be saved to: my-floor-plan_piaf.pdf
Loading: my-floor-plan.jpg
Image loaded: 2400x1800 pixels, mode: RGB
Processing: Converting to grayscale
Processing: Applying threshold: 128
Checking: Density analysis
Black pixel density: 38.2%
Status: Within acceptable range (target: <40.0%)
Success: Image processing complete

Generating: Creating PDF output
Image size: 8.0 inches x 6.0 inches
Fits on: letter size paper (8.5" x 11.0")
Success: PDF saved to my-floor-plan_piaf.pdf

Complete: Processing finished successfully
Ready to print on PIAF machine
```

### Scenario 3: Interactive Mode (Best for new users)

Get prompted step-by-step:

```bash
fabric-access image-to-piaf my-floor-plan.jpg --interactive
```

**Interactive flow:**
```
============================================================
Fabric Accessible Graphics - Image to PIAF Converter
============================================================

Input file: my-floor-plan.jpg

Settings:
  Threshold: 128
  Paper size: letter

Continue with these settings? [Y/n]: y

[Processing happens with detailed output]
```

### Scenario 4: Custom Settings

Adjust the black/white threshold:

```bash
fabric-access image-to-piaf sketch.png --threshold 140 --verbose
```

**When to adjust threshold:**
- **Image too light** (lots of white space, faint lines): Lower threshold (100-120)
- **Image too dark** (lots of black areas): Raise threshold (140-170)
- **Default not working well**: Experiment in increments of 10

### Scenario 5: Specify Output Location

Choose where to save the PDF:

```bash
fabric-access image-to-piaf drawing.jpg --output /path/to/output/final-print.pdf
```

### Scenario 6: Large Format (Tabloid)

For larger drawings that need 11x17" paper:

```bash
fabric-access image-to-piaf large-elevation.png --paper-size tabloid --verbose
```

## Phase 2 Features - Advanced Conversion

Phase 2 adds powerful features that simplify usage and improve image quality.

### Using Presets (Easiest Method - Recommended!)

Presets provide optimized settings for common image types. Instead of guessing threshold and enhancement settings, use a preset that matches your image.

#### Step 1: See All Available Presets

```bash
fabric-access list-presets
```

**You'll see:**
```
Available Presets:
==================

detail_drawing
  Description: Detailed architectural drawings with fine linework
  Threshold: 145
  Enhancement: s_curve (strength: 1.1)
  Paper Size: letter
  Max Density: 40%

diagram
  Description: Technical diagrams and schematics
  Threshold: 135
  Enhancement: auto_contrast
  Paper Size: letter
  Max Density: 40%

elevation
  Description: Architectural elevations
  Threshold: 135
  Enhancement: s_curve (strength: 1.0)
  Paper Size: letter
  Max Density: 40%

floor_plan
  Description: Architectural floor plans with walls and dimensions
  Threshold: 140
  Enhancement: s_curve (strength: 1.0)
  Paper Size: letter
  Max Density: 40%

photograph
  Description: Photographs of models or buildings
  Threshold: 120
  Enhancement: clahe
  Paper Size: letter
  Max Density: 30%

presentation
  Description: Presentation boards and large format images
  Threshold: 125
  Enhancement: clahe
  Paper Size: tabloid
  Max Density: 35%

section
  Description: Architectural section drawings
  Threshold: 145
  Enhancement: s_curve (strength: 1.2)
  Paper Size: letter
  Max Density: 40%

site_plan
  Description: Site plans and master plans
  Threshold: 140
  Enhancement: s_curve (strength: 1.0)
  Paper Size: tabloid
  Max Density: 40%

sketch
  Description: Hand-drawn sketches and conceptual drawings
  Threshold: 130
  Enhancement: s_curve (strength: 1.3)
  Paper Size: letter
  Max Density: 40%

technical_drawing
  Description: Technical drawings and CAD exports
  Threshold: 150
  Enhancement: none
  Paper Size: letter
  Max Density: 40%
```

#### Step 2: Use a Preset

```bash
# For a floor plan
fabric-access image-to-piaf my-floor-plan.jpg --preset floor_plan --verbose

# For a hand sketch
fabric-access image-to-piaf my-sketch.png --preset sketch --verbose

# For a photograph
fabric-access image-to-piaf model-photo.jpg --preset photograph --verbose

# For a site plan (automatically uses tabloid paper)
fabric-access image-to-piaf site.png --preset site_plan --verbose
```

**What happens:**
- The preset automatically sets the best threshold
- Applies appropriate contrast enhancement
- Chooses optimal paper size
- Sets density limits
- You get great results without guessing settings!

#### Step 3: Override Preset Settings (Optional)

If a preset is almost perfect but you want to tweak one setting:

```bash
# Use floor_plan preset but change threshold
fabric-access image-to-piaf plan.jpg --preset floor_plan --threshold 150 --verbose

# Use sketch preset but disable enhancement
fabric-access image-to-piaf sketch.png --preset sketch --enhance none
```

**Preset recommendations by image type:**
- **CAD floor plans** → `floor_plan` or `technical_drawing`
- **Hand sketches** → `sketch`
- **Elevations/facades** → `elevation`
- **Section cuts** → `section`
- **Detail drawings** → `detail_drawing`
- **Site/master plans** → `site_plan`
- **Photos of models** → `photograph`
- **Presentation boards** → `presentation`
- **Technical diagrams** → `diagram`

### S-Curve Enhancement

S-curve boosts midtone contrast, making lines crisper and more defined - like using Photoshop curves.

#### When to Use S-Curve

**Good for:**
- Faint or low-contrast images
- Scanned architectural drawings
- Images that look "flat" or "washed out"
- Clean drawings that need a contrast boost

**Not needed for:**
- Already high-contrast CAD exports
- Very dark or very light images (use auto_contrast or histogram instead)

#### Using S-Curve Enhancement

```bash
# Standard S-curve (strength 1.0)
fabric-access image-to-piaf plan.jpg --enhance s_curve --verbose

# Stronger enhancement for very faint images
fabric-access image-to-piaf faint-sketch.jpg --enhance s_curve --enhance-strength 1.5 --verbose

# Subtle enhancement
fabric-access image-to-piaf drawing.jpg --enhance s_curve --enhance-strength 0.7 --verbose
```

**Strength guide:**
- **0.5-0.8**: Subtle enhancement, preserves original tones
- **1.0**: Standard enhancement (default, recommended)
- **1.2-1.5**: Strong enhancement for faint images
- **1.6-2.0**: Very aggressive (may over-enhance)

#### Other Enhancement Methods

```bash
# Auto-contrast: Stretches histogram to full range
fabric-access image-to-piaf scan.jpg --enhance auto_contrast --verbose

# CLAHE: Good for photographs with uneven lighting
fabric-access image-to-piaf photo.jpg --enhance clahe --verbose

# Histogram equalization: For very dark or light images
fabric-access image-to-piaf dark-image.jpg --enhance histogram --verbose

# No enhancement
fabric-access image-to-piaf crisp-cad.jpg --enhance none --verbose
```

**Method comparison:**
- **s_curve**: Best for most architectural drawings (RECOMMENDED)
- **auto_contrast**: Good for scanned images with limited tonal range
- **clahe**: Best for photographs with shadows and highlights
- **histogram**: Aggressive adjustment for extreme images
- **none**: For already high-contrast CAD exports

### Batch Processing

Convert entire folders of images at once - perfect for processing assignment sets or project archives.

#### Basic Batch Conversion

```bash
# Process all images in a folder using a preset
fabric-access batch ./my-drawings ./output-pdfs --preset floor_plan --verbose
```

**What happens:**
```
Found 5 image files to process
Creating output directory: output-pdfs

[1/5] Processing: plan-floor1.jpg
Black pixel density: 36.2%
Success: plan-floor1_piaf.pdf

[2/5] Processing: plan-floor2.jpg
Black pixel density: 38.1%
Success: plan-floor2_piaf.pdf

[3/5] Processing: elevation-north.png
Black pixel density: 32.5%
Success: elevation-north_piaf.pdf

[4/5] Processing: section-aa.jpg
Black pixel density: 40.2%
Success: section-aa_piaf.pdf

[5/5] Processing: site-plan.png
Black pixel density: 35.8%
Success: site-plan_piaf.pdf

Batch Processing Summary:
========================
Total files: 5
Successful: 5
Failed: 0

All files processed successfully!
```

#### Recursive Processing

Process images in subdirectories too:

```bash
# Process entire project folder with nested folders
fabric-access batch ./semester-project ./output --preset floor_plan --recursive --verbose
```

**Example folder structure:**
```
semester-project/
├── phase1/
│   ├── sketches/
│   │   ├── concept1.jpg
│   │   └── concept2.jpg
│   └── floor-plans/
│       ├── plan1.jpg
│       └── plan2.jpg
└── phase2/
    ├── elevations/
    │   ├── north.png
    │   └── south.png
    └── sections/
        └── section-a.png
```

All images in all subdirectories will be processed and saved to the output folder with preserved names.

#### Custom Settings for Batch

Apply specific settings to all files:

```bash
# Custom threshold for all images
fabric-access batch ./sketches ./output --threshold 130 --enhance s_curve --verbose

# Use photograph preset with enhanced strength
fabric-access batch ./model-photos ./output --preset photograph --enhance-strength 1.2 --verbose

# Tabloid paper for all
fabric-access batch ./large-plans ./output --paper-size tabloid --verbose
```

#### File Pattern Filtering

Process only specific file types:

```bash
# Only PNG files
fabric-access batch ./mixed-files ./output --pattern "*.png" --preset floor_plan

# Only JPG and JPEG
fabric-access batch ./photos ./output --pattern "*.jpg,*.jpeg" --preset photograph

# Multiple types with specific preset
fabric-access batch ./drawings ./output --pattern "*.png,*.jpg,*.tiff" --preset sketch
```

**Default patterns:** `*.jpg,*.jpeg,*.png,*.tiff,*.tif` (all supported image formats)

#### Handling Failed Files

If some files fail during batch processing, you'll see a detailed report:

```
Batch Processing Summary:
========================
Total files: 10
Successful: 8
Failed: 2

Failed files:
  corrupted-image.jpg - Error: Unable to load image file
  too-dense.png - Error: Density too high: 52.3% (maximum: 45%)

Review failed files and try processing them individually with adjusted settings.
```

You can then process failed files individually with custom settings.

## Understanding Output Messages

### Success Messages

```
Success: Image processing complete
Success: PDF saved to [filename]
Complete: Processing finished successfully
Ready to print on PIAF machine
```

**Action:** Your file is ready to print!

### Density Warnings

```
Warning: Density is 42%, target is 40%
```

**What it means:** Your image has a lot of black pixels, which might cause excessive swelling on PIAF.

**Action:**
1. Try increasing the threshold:
   ```bash
   fabric-access image-to-piaf plan.jpg --threshold 150
   ```
2. Or simplify the original image (remove unnecessary detail)

### Density Errors

```
Error: Density too high: 48.5% (maximum: 45%)
```

**What it means:** Too much black in the image - it will not print well on PIAF.

**Action:**
1. Significantly increase threshold:
   ```bash
   fabric-access image-to-piaf plan.jpg --threshold 170
   ```
2. Or edit the original image to remove dense patterns

### File Not Found Errors

```
Error: File not found: plan.jpg
Details: Could not locate 'plan.jpg' in current directory
Solution: Check the file path and try again
```

**Action:** Verify the file exists and you're in the right directory:
```bash
ls -l plan.jpg
```

## Common Workflows

### Workflow 1: Converting Multiple Images (Phase 2 - Batch Method)

**Easiest way - use batch processing:**

```bash
# Activate environment once
source venv/bin/activate

# Process entire folder with one command
fabric-access batch ./my-drawings ./output --preset floor_plan --verbose
```

**Old way - convert each file individually:**

```bash
# Activate environment once
source venv/bin/activate

# Convert each file
fabric-access image-to-piaf floor-plan-1.jpg --verbose
fabric-access image-to-piaf floor-plan-2.jpg --verbose
fabric-access image-to-piaf elevation.png --threshold 140 --verbose
```

### Workflow 2: Testing Different Presets

```bash
# Try different presets to find the best result
fabric-access image-to-piaf sketch.png --preset sketch --output test-sketch-preset.pdf
fabric-access image-to-piaf sketch.png --preset floor_plan --output test-floor-preset.pdf
fabric-access image-to-piaf sketch.png --preset technical_drawing --output test-technical-preset.pdf

# Review the PDFs and choose the best one
```

### Workflow 3: Testing Different Enhancement Strengths

```bash
# Try different S-curve strengths
fabric-access image-to-piaf faint-drawing.jpg --enhance s_curve --enhance-strength 0.8 --output test-08.pdf
fabric-access image-to-piaf faint-drawing.jpg --enhance s_curve --enhance-strength 1.0 --output test-10.pdf
fabric-access image-to-piaf faint-drawing.jpg --enhance s_curve --enhance-strength 1.3 --output test-13.pdf

# Review and choose the clearest one
```

### Workflow 4: Class Assignment Workflow (Phase 2 - Preset Method)

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Convert your assignment drawing with appropriate preset
fabric-access image-to-piaf my-floor-plan.jpg --preset floor_plan --verbose

# 3. Review the output
# Check my-floor-plan_piaf.pdf

# 4. If needed, adjust and reconvert
fabric-access image-to-piaf my-floor-plan.jpg --preset floor_plan --threshold 145 --output my-floor-plan-v2.pdf --verbose

# 5. Print the best version on PIAF machine
```

### Workflow 5: Entire Project Batch Conversion

```bash
# Process a complete project with multiple drawing types
source venv/bin/activate

# Create organized output
mkdir -p project-output

# Process all floor plans
fabric-access batch ./project/plans ./project-output --preset floor_plan --verbose

# Process all elevations
fabric-access batch ./project/elevations ./project-output --preset elevation --verbose

# Process all sections
fabric-access batch ./project/sections ./project-output --preset section --verbose

# Or process everything at once recursively
fabric-access batch ./project ./project-output --preset floor_plan --recursive --verbose
```

### Workflow 6: Processing Scanned Hand Drawings

```bash
# Scanned sketches often need enhancement
source venv/bin/activate

# Use sketch preset with S-curve enhancement (automatically applied)
fabric-access batch ./scanned-sketches ./output --preset sketch --verbose

# Or apply stronger enhancement if scans are very faint
fabric-access batch ./scanned-sketches ./output --preset sketch --enhance-strength 1.5 --verbose
```

## Tips for Best Results

### Phase 2 Tip: Use Presets First! (Easiest)

**Before manually adjusting settings, try the appropriate preset:**

```bash
# Let the preset handle all settings automatically
fabric-access image-to-piaf YOUR-IMAGE.jpg --preset PRESET-NAME --verbose
```

Choose preset based on your image type (see preset list above in Phase 2 section).

### For Floor Plans (Clean CAD Drawings)

**Phase 2 Method (Recommended):**
```bash
fabric-access image-to-piaf plan.jpg --preset floor_plan --verbose
```

**Manual Method:**
```bash
fabric-access image-to-piaf plan.jpg --threshold 140
```
- Higher threshold works well for crisp, clean lines
- Usually low density

### For Hand Sketches

**Phase 2 Method (Recommended):**
```bash
fabric-access image-to-piaf sketch.jpg --preset sketch --verbose
```

**Manual Method:**
```bash
fabric-access image-to-piaf sketch.jpg --threshold 120 --enhance s_curve --enhance-strength 1.3 --verbose
```
- S-curve enhancement helps boost faint pencil lines
- Lower threshold preserves lighter lines
- Monitor density warnings

### For Photographs of Models

**Phase 2 Method (Recommended):**
```bash
fabric-access image-to-piaf model-photo.jpg --preset photograph --verbose
```

**Manual Method:**
```bash
fabric-access image-to-piaf model-photo.jpg --threshold 110 --enhance clahe --verbose
```
- CLAHE enhancement handles shadows and highlights
- Lower threshold to capture details
- Expect higher density - may need adjustment

### For Technical Drawings with Hatching

**Phase 2 Method (Recommended):**
```bash
fabric-access image-to-piaf section.png --preset section --verbose
```

**Manual Method:**
```bash
fabric-access image-to-piaf section.png --threshold 145 --verbose
```
- Higher threshold reduces hatching density
- Watch for density warnings on heavy hatching

### For Faint or Low-Contrast Scans

**Phase 2 Enhancement:**
```bash
# Use S-curve to boost contrast
fabric-access image-to-piaf faint-scan.jpg --enhance s_curve --enhance-strength 1.5 --verbose

# Or use auto-contrast for scans with narrow tonal range
fabric-access image-to-piaf scan.jpg --enhance auto_contrast --verbose
```

This makes faint lines more visible without manually editing the image.

## Checking Your Results

After conversion, you should:

1. **Check file size**: The PDF should be created
   ```bash
   ls -lh *_piaf.pdf
   ```

2. **Review processing summary**: Look at the density percentage
   - **Under 30%**: Excellent, optimal for tactile output
   - **30-40%**: Good, should print well
   - **40-45%**: Acceptable but approaching limit
   - **Over 45%**: Too dense, reconvert with higher threshold

3. **Verify dimensions**: Make sure it fits on your paper size
   - Letter: 8.5" x 11"
   - Tabloid: 11" x 17"

## Phase 3: Text Detection & Braille Conversion

Phase 3 adds optical character recognition (OCR) to detect text and dimensions on architectural drawings, then converts them to Braille labels.

### What is Text Detection?

Text detection uses Tesseract OCR to automatically find and read text on your images, with special attention to architectural dimensions like:
- Feet and inches: 10', 6", 10'-6"
- Metric: 3m, 120mm, 50cm

### What is Braille Conversion?

After detecting text, the toolkit can automatically convert it to Unicode Braille using Liblouis and overlay the Braille labels on the PDF. This makes dimensions and labels readable tactilely.

### Requirements

Before using text detection and Braille features, install the required dependencies:

#### Installing Tesseract OCR

**Ubuntu/Debian (WSL):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

#### Installing Liblouis (for Braille)

**Ubuntu/Debian (WSL):**
```bash
sudo apt-get install liblouis-dev
pip install liblouis
```

**macOS:**
```bash
brew install liblouis
pip install liblouis
```

**Windows:**
```bash
pip install liblouis
```

### Basic Text Detection Usage

#### Detect Text and Add Braille Labels

```bash
# Activate environment
source venv/bin/activate

# Detect text and convert to Braille
fabric-access image-to-piaf floor-plan.jpg --detect-text --verbose
```

**What you'll see:**
```
Detecting text and dimensions
Found 8 dimension(s)
Found 3 other text element(s)
Converting 11 text items to Braille
Created 11 Braille labels (Grade 1)
Generated 11 Braille label(s)
Adding 11 Braille labels to PDF
```

#### Using Grade 2 Braille

Grade 2 Braille is contracted (shorter), while Grade 1 is uncontracted (letter-by-letter):

```bash
# Grade 1 (default - uncontracted)
fabric-access image-to-piaf plan.jpg --detect-text --braille-grade 1 --verbose

# Grade 2 (contracted - more compact)
fabric-access image-to-piaf plan.jpg --detect-text --braille-grade 2 --verbose
```

### Combined Usage Examples

#### Text Detection with Presets

```bash
# Floor plan with text detection
fabric-access image-to-piaf floor-plan.jpg --detect-text --preset floor_plan --verbose

# Sketch with text detection
fabric-access image-to-piaf sketch.png --detect-text --preset sketch --verbose
```

#### Text Detection with Other Features

```bash
# With automatic density reduction
fabric-access image-to-piaf dense-plan.jpg --detect-text --auto-reduce-density --verbose

# With tiling for large images
fabric-access image-to-piaf large-drawing.jpg --detect-text --enable-tiling --verbose

# All features combined
fabric-access image-to-piaf complex-plan.jpg \
  --detect-text \
  --braille-grade 2 \
  --preset floor_plan \
  --auto-reduce-density \
  --enable-tiling \
  --verbose
```

### Batch Processing with Text Detection

Process entire folders with text detection:

```bash
# Detect text on all floor plans
fabric-access batch ./plans ./output --detect-text --preset floor_plan --verbose

# With Grade 2 Braille
fabric-access batch ./drawings ./output --detect-text --braille-grade 2 --verbose

# Recursive processing with text detection
fabric-access batch ./project ./output --detect-text --recursive --preset floor_plan --verbose
```

### Understanding Text Detection Output

When text detection is enabled, you'll see detailed information:

```
Detecting text and dimensions
Found 5 dimension(s)
Found 2 other text element(s)
```

This tells you:
- **Dimensions**: Text matching architectural dimension patterns (10'-6", 3m, etc.)
- **Other text**: Labels, room names, notes, etc.

### Workflow: Floor Plan with Dimensions

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Process floor plan with text detection
fabric-access image-to-piaf my-floor-plan.jpg --detect-text --preset floor_plan --verbose

# 3. Review the output
# The PDF will have:
# - High contrast black and white image
# - Braille labels overlaid on detected text
# - Proper density for tactile printing

# 4. Print on PIAF machine
# The Braille labels will be embossed along with the image
```

### Workflow: Batch Processing Architectural Drawings

```bash
# Process multiple drawings with dimensions
source venv/bin/activate

# Process all plans with text detection
fabric-access batch ./semester-project/plans ./output \
  --detect-text \
  --preset floor_plan \
  --recursive \
  --verbose
```

### Tips for Best Results

#### For Clean CAD Drawings
- Text detection works best on clear, high-resolution drawings
- Use `--preset floor_plan` for optimal image processing
- Grade 1 Braille is easier to read for dimensions

#### For Hand-Drawn Sketches
- Use enhancement to improve text clarity:
  ```bash
  fabric-access image-to-piaf sketch.jpg --detect-text --enhance s_curve --enhance-strength 1.3 --verbose
  ```

#### For Scanned Documents
- Higher resolution scans improve text detection accuracy
- Use auto-contrast enhancement:
  ```bash
  fabric-access image-to-piaf scan.jpg --detect-text --enhance auto_contrast --verbose
  ```

### Troubleshooting Text Detection

#### Problem: No text detected

**Possible causes:**
- Image resolution too low
- Text too small or blurry
- Tesseract not installed

**Solutions:**
```bash
# Verify Tesseract is installed
tesseract --version

# Try enhancing the image first
fabric-access image-to-piaf plan.jpg --detect-text --enhance s_curve --enhance-strength 1.5 --verbose
```

#### Problem: Incorrect text detection

**Possible causes:**
- Poor image quality
- Unusual fonts
- Rotated text

**Solutions:**
- Use higher resolution source images
- Pre-process images to improve clarity
- Verify dimensions are in supported formats

#### Problem: Braille conversion fails

**Possible causes:**
- Liblouis not installed

**Solution:**
```bash
# Verify Liblouis is installed
pip show liblouis

# If not installed
pip install liblouis
```

### Advanced Configuration

Text detection and Braille settings can be customized in the configuration file:

`src/fabric_access/data/tactile_standards.yaml`

Key settings:
```yaml
text_detection:
  enabled: false  # Set to true to enable by default
  min_confidence: 60  # OCR confidence threshold
  dimension_patterns:  # Patterns for detecting dimensions
    - "\\d+['\"]"  # Feet and inches

braille:
  grade: 1  # Default grade (1 or 2)
  font_size: 10  # Label size in points
  placement: "overlay"  # overlay or margin
  offset_x: 5  # Horizontal offset from text
  offset_y: -10  # Vertical offset (negative = above)
```

## Deactivating the Environment

When you're done working:

```bash
deactivate
```

The `(venv)` prefix will disappear from your prompt.

## Troubleshooting

### Problem: Command not found

```
bash: fabric-access: command not found
```

**Solution:** Activate the virtual environment:
```bash
source venv/bin/activate
```

### Problem: Image appears blank or all black/white

**Cause:** Threshold is set too high or too low

**Solution:** Try the opposite direction:
- If all white: Lower threshold (try 100)
- If all black: Raise threshold (try 160)

### Problem: Module import errors

```
ModuleNotFoundError: No module named 'click'
```

**Solution:** Reinstall dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Permission denied writing PDF

**Solution:** Check you have write permissions:
```bash
ls -ld .
# Make sure directory is writable
```

## Getting Help

### Within the tool:
```bash
fabric-access --help                    # General help
fabric-access image-to-piaf --help      # Command-specific help
fabric-access info                      # Tool information
```

### Documentation:
- README.md - Installation and overview
- This file (WALKTHROUGH.md) - Detailed usage guide
- .claude.md - Project context for AI assistance

## Quick Reference Card

### Phase 1 Commands (Basic)

```bash
# Activate environment
source venv/bin/activate

# Basic conversion
fabric-access image-to-piaf IMAGE.jpg

# Verbose (see details)
fabric-access image-to-piaf IMAGE.jpg --verbose

# Interactive (step-by-step)
fabric-access image-to-piaf IMAGE.jpg --interactive

# Custom threshold
fabric-access image-to-piaf IMAGE.jpg --threshold 140

# Custom output
fabric-access image-to-piaf IMAGE.jpg --output result.pdf

# Large paper
fabric-access image-to-piaf IMAGE.jpg --paper-size tabloid

# Combined
fabric-access image-to-piaf IMAGE.jpg --threshold 140 --verbose --output result.pdf
```

### Phase 2 Commands (Advanced - Recommended!)

```bash
# List all available presets
fabric-access list-presets

# Use a preset (EASIEST METHOD)
fabric-access image-to-piaf IMAGE.jpg --preset floor_plan --verbose
fabric-access image-to-piaf IMAGE.jpg --preset sketch --verbose
fabric-access image-to-piaf IMAGE.jpg --preset photograph --verbose

# S-curve enhancement
fabric-access image-to-piaf IMAGE.jpg --enhance s_curve --verbose
fabric-access image-to-piaf IMAGE.jpg --enhance s_curve --enhance-strength 1.5 --verbose

# Other enhancements
fabric-access image-to-piaf IMAGE.jpg --enhance auto_contrast --verbose
fabric-access image-to-piaf IMAGE.jpg --enhance clahe --verbose
fabric-access image-to-piaf IMAGE.jpg --enhance histogram --verbose

# Batch processing (convert entire folder)
fabric-access batch ./input-folder ./output-folder --preset floor_plan --verbose

# Batch with recursive subdirectories
fabric-access batch ./project ./output --preset floor_plan --recursive --verbose

# Batch with custom settings
fabric-access batch ./drawings ./output --threshold 140 --enhance s_curve --verbose

# Batch with file filtering
fabric-access batch ./images ./output --pattern "*.png,*.jpg" --preset sketch

# Override preset settings
fabric-access image-to-piaf IMAGE.jpg --preset floor_plan --threshold 150 --verbose
```

### Phase 3 Commands (Text Detection & Braille - NEW!)

```bash
# Detect text and add Braille labels (Grade 1)
fabric-access image-to-piaf floor-plan.jpg --detect-text --verbose

# Use Grade 2 Braille (contracted)
fabric-access image-to-piaf plan.png --detect-text --braille-grade 2 --verbose

# Combined with presets
fabric-access image-to-piaf drawing.jpg --detect-text --preset floor_plan --verbose

# Combined with other features
fabric-access image-to-piaf large-plan.jpg --detect-text --auto-reduce-density --enable-tiling

# Batch processing with text detection
fabric-access batch ./plans ./output --detect-text --preset floor_plan --verbose
```

### Environment Management

```bash
# Deactivate when done
deactivate
```
