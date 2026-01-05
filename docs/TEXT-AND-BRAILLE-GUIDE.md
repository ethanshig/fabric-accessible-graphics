# Text Detection and Braille Conversion Guide

A comprehensive guide to using OCR-based text detection and Braille conversion features in the Fabric Accessible Graphics Toolkit.

## Table of Contents

1. [Overview](#overview)
2. [What Text Detection Does](#what-text-detection-does)
3. [What Braille Conversion Does](#what-braille-conversion-does)
4. [Installation Requirements](#installation-requirements)
5. [Basic Usage](#basic-usage)
6. [Configuration Options](#configuration-options)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)
9. [Limitations and Best Practices](#limitations-and-best-practices)

## Overview

Phase 3 of the Fabric Accessible Graphics Toolkit adds two powerful features:

1. **Text Detection**: Uses Tesseract OCR to automatically detect and locate text on images
2. **Braille Conversion**: Uses Liblouis to convert detected text to Unicode Braille and overlay it on PDFs

Together, these features make architectural dimensions and labels accessible through tactile reading on PIAF machines.

## What Text Detection Does

Text detection uses optical character recognition (OCR) to find and read text on your images. It specifically looks for:

### Architectural Dimensions

The system recognizes six common dimension formats:

- **Feet**: `10'`, `24'`, `3'`
- **Inches**: `6"`, `120"`, `48"`
- **Combined Feet-Inches**: `10'-6"`, `3'-4"`, `12'-0"`
- **Meters**: `3m`, `5.5m`, `10m`
- **Millimeters**: `120mm`, `2400mm`, `300mm`
- **Centimeters**: `50cm`, `100cm`, `250cm`

### Other Text

In addition to dimensions, the system detects:
- Room labels ("Kitchen", "Bedroom", "Living Room")
- Notes and annotations
- Scale indicators
- Any other visible text

### How It Works

1. **Image Preprocessing**: Before OCR, the image is preprocessed to improve text clarity (median blur, noise reduction)
2. **Tesseract OCR**: The Tesseract engine scans the image and extracts text with bounding box coordinates
3. **Pattern Matching**: Detected text is checked against dimension patterns to identify measurements
4. **Confidence Filtering**: Only text with confidence above 60% is kept (configurable)

## What Braille Conversion Does

After text is detected, the Braille converter creates tactile labels:

### Conversion Process

1. **Text Preparation**: Long text is truncated to 30 characters (configurable)
2. **Braille Translation**: Text is converted to Unicode Braille using Liblouis
3. **Position Calculation**: Braille labels are positioned near the original text (with configurable offsets)
4. **Overlap Detection**: System checks for and warns about overlapping labels
5. **PDF Rendering**: Braille labels are added to the PDF using Unicode characters (U+2800 to U+28FF)

### Braille Grades

**Grade 1 (Uncontracted)**
- Letter-by-letter representation
- Easier to read for beginners
- Recommended for dimensions and measurements
- Default setting

**Grade 2 (Contracted)**
- Uses contractions and abbreviations
- More compact
- Requires more Braille literacy
- Good for longer text

### Label Placement

**Overlay Mode (Default)**
- Labels are positioned directly on the image
- Offset from original text position (5 pixels right, 10 pixels up by default)
- Best for most use cases

**Margin Mode (Future Feature)**
- Labels would be positioned in page margins
- Useful for dense images

## Installation Requirements

### Installing Tesseract OCR

Tesseract is required for text detection.

**Ubuntu/Debian (including WSL):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr

# Verify installation
tesseract --version
```

**macOS:**
```bash
brew install tesseract

# Verify installation
tesseract --version
```

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add Tesseract to your PATH
4. Verify installation in Command Prompt:
   ```
   tesseract --version
   ```

### Installing Liblouis

Liblouis is required for Braille conversion.

**Ubuntu/Debian (including WSL):**
```bash
# Install system library
sudo apt-get install liblouis-dev

# Install Python bindings (in your virtual environment)
source venv/bin/activate
pip install liblouis

# Verify installation
python -c "import louis; print('Liblouis installed successfully')"
```

**macOS:**
```bash
# Install system library
brew install liblouis

# Install Python bindings
pip install liblouis

# Verify installation
python -c "import louis; print('Liblouis installed successfully')"
```

**Windows:**
```bash
# Python bindings only (in your virtual environment)
pip install liblouis

# Verify installation
python -c "import louis; print('Liblouis installed successfully')"
```

### Troubleshooting Installation

**If Tesseract is not found:**
```bash
# Ubuntu/Debian
which tesseract

# If not found, check installation
sudo apt-get install --reinstall tesseract-ocr
```

**If Liblouis import fails:**
```bash
# Reinstall Python bindings
pip uninstall liblouis
pip install liblouis

# Or install development version
pip install git+https://github.com/liblouis/liblouis.git
```

## Basic Usage

### Simple Text Detection

Detect text and add Grade 1 Braille labels:

```bash
fabric-access image-to-piaf floor-plan.jpg --detect-text --verbose
```

**Output:**
```
Detecting text and dimensions
Found 8 dimension(s)
Found 3 other text element(s)
Converting 11 text items to Braille
Created 11 Braille labels (Grade 1)
Generated 11 Braille label(s)
Adding 11 Braille labels to PDF
```

### Using Grade 2 Braille

For contracted Braille:

```bash
fabric-access image-to-piaf floor-plan.jpg --detect-text --braille-grade 2 --verbose
```

### Batch Processing

Process multiple files with text detection:

```bash
fabric-access batch ./plans ./output --detect-text --preset floor_plan --verbose
```

### Combined with Other Features

```bash
# With automatic density reduction
fabric-access image-to-piaf plan.jpg --detect-text --auto-reduce-density --verbose

# With tiling for large images
fabric-access image-to-piaf large-plan.jpg --detect-text --enable-tiling --verbose

# With presets
fabric-access image-to-piaf drawing.jpg --detect-text --preset floor_plan --verbose

# All features
fabric-access image-to-piaf complex-plan.jpg \
  --detect-text \
  --braille-grade 2 \
  --preset floor_plan \
  --auto-reduce-density \
  --enable-tiling \
  --verbose
```

## Configuration Options

### Command-Line Options

**--detect-text**
- Type: Flag (no value)
- Enables text detection
- Default: Off (opt-in feature)

**--braille-grade**
- Type: Choice (1 or 2)
- Braille translation mode
- Default: 1 (uncontracted)
- Options:
  - `1`: Grade 1 (letter-by-letter)
  - `2`: Grade 2 (contracted)

**--braille-placement**
- Type: Choice (overlay or margin)
- Label placement strategy
- Default: overlay
- Options:
  - `overlay`: On the image
  - `margin`: In margins (future feature)

### Configuration File Settings

Advanced settings in `src/fabric_access/data/tactile_standards.yaml`:

#### Text Detection Settings

```yaml
text_detection:
  enabled: false  # Enable by default
  language: 'eng'  # OCR language
  page_segmentation_mode: 3  # Tesseract PSM
  min_confidence: 60  # Minimum OCR confidence (0-100)

  # Dimension detection
  filter_dimensions: true
  dimension_patterns:
    - "\\d+['\"]"              # Feet/inches: 10', 6"
    - "\\d+\\.\\d+['\"]"       # Decimal: 3.5'
    - "\\d+-\\d+['\"]"         # Range: 10'-6"
    - "\\d+m"                  # Meters: 3m
    - "\\d+mm"                 # Millimeters: 120mm
    - "\\d+cm"                 # Centimeters: 50cm
```

#### Braille Conversion Settings

```yaml
braille:
  enabled: false  # Enable by default
  grade: 1  # Default grade (1 or 2)

  # Font settings
  font_name: "DejaVu Sans"  # Font supporting Unicode Braille
  font_size: 10  # Point size
  font_color: "black"

  # Placement
  placement: "overlay"
  offset_x: 5  # Pixels right from text
  offset_y: -10  # Pixels up from text (negative = above)

  # Label constraints
  max_label_length: 30  # Maximum characters
  truncate_suffix: "..."  # Suffix for truncated text

  # Overlap handling
  detect_overlaps: true
  min_label_spacing: 6  # Pixels between labels
```

### Customizing Dimension Patterns

To detect custom dimension formats, add patterns to `dimension_patterns`:

```yaml
dimension_patterns:
  # Standard patterns
  - "\\d+['\"]"

  # Custom: Room dimensions in format "10x12"
  - "\\d+x\\d+"

  # Custom: Decimal meters "3.5m"
  - "\\d+\\.\\d+m"
```

Patterns use Python regular expression syntax.

### Adjusting Label Positioning

Fine-tune where Braille labels appear:

```yaml
braille:
  offset_x: 10  # Move labels further right
  offset_y: -15  # Move labels further up
  font_size: 12  # Larger text
```

## Advanced Usage

### Workflow: Annotated Floor Plans

For floor plans with dimensions and room labels:

```bash
# 1. Process with text detection and optimal settings
fabric-access image-to-piaf floor-plan.jpg \
  --detect-text \
  --preset floor_plan \
  --auto-reduce-density \
  --verbose

# 2. Review output for detected text count
# 3. Check PDF for Braille label placement
# 4. Adjust settings if needed and reprocess
```

### Workflow: Batch Processing Project Drawings

For entire project folders:

```bash
# Process all architectural drawings with text detection
fabric-access batch ./project-drawings ./output \
  --detect-text \
  --braille-grade 1 \
  --preset floor_plan \
  --recursive \
  --auto-reduce-density \
  --verbose
```

### Enhancing Text Detection Accuracy

For challenging images:

**Low Contrast Images:**
```bash
fabric-access image-to-piaf faint-scan.jpg \
  --detect-text \
  --enhance s_curve \
  --enhance-strength 1.5 \
  --verbose
```

**Scanned Documents:**
```bash
fabric-access image-to-piaf scan.jpg \
  --detect-text \
  --enhance auto_contrast \
  --verbose
```

**Hand-Drawn Sketches:**
```bash
fabric-access image-to-piaf sketch.jpg \
  --detect-text \
  --enhance s_curve \
  --enhance-strength 1.3 \
  --preset sketch \
  --verbose
```

### Testing Different Configurations

Compare Grade 1 vs Grade 2:

```bash
# Grade 1 (uncontracted)
fabric-access image-to-piaf plan.jpg \
  --detect-text \
  --braille-grade 1 \
  --output plan-grade1.pdf

# Grade 2 (contracted)
fabric-access image-to-piaf plan.jpg \
  --detect-text \
  --braille-grade 2 \
  --output plan-grade2.pdf

# Review both PDFs and choose the more readable version
```

## Troubleshooting

### No Text Detected

**Symptoms:**
```
Detecting text and dimensions
No text detected
```

**Possible Causes:**
1. Image resolution too low
2. Text too small or blurry
3. Poor image quality
4. Tesseract not properly installed

**Solutions:**

1. **Check Tesseract Installation:**
   ```bash
   tesseract --version
   ```
   Should output version information.

2. **Verify Image Quality:**
   - Ensure image is at least 300 DPI
   - Text should be clearly visible
   - Try enhancing the image:
     ```bash
     fabric-access image-to-piaf plan.jpg \
       --detect-text \
       --enhance s_curve \
       --enhance-strength 1.5 \
       --verbose
     ```

3. **Check Image Format:**
   - Use high-quality formats (PNG, TIFF)
   - Avoid heavily compressed JPEGs

4. **Lower OCR Confidence Threshold:**
   Edit `tactile_standards.yaml`:
   ```yaml
   text_detection:
     min_confidence: 50  # Lower from 60
   ```

### Incorrect Text Detection

**Symptoms:**
- Wrong characters detected
- Dimensions misread
- Random characters appearing

**Possible Causes:**
1. Image artifacts or noise
2. Unusual fonts
3. Rotated text
4. Poor contrast

**Solutions:**

1. **Improve Image Quality:**
   ```bash
   fabric-access image-to-piaf plan.jpg \
     --detect-text \
     --enhance auto_contrast \
     --verbose
   ```

2. **Use Higher Resolution Source:**
   - Scan at 600 DPI instead of 300 DPI
   - Export CAD drawings at higher resolution

3. **Clean Up Image:**
   - Remove noise and artifacts before processing
   - Ensure text is horizontal (OCR works best with upright text)

### Braille Conversion Fails

**Symptoms:**
```
Warning: Braille conversion failed: Liblouis not installed
Continuing with PDF generation without Braille labels
```

**Solution:**

1. **Install Liblouis:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install liblouis-dev
   pip install liblouis

   # macOS
   brew install liblouis
   pip install liblouis

   # Windows
   pip install liblouis
   ```

2. **Verify Installation:**
   ```bash
   python -c "import louis; print('Liblouis version:', louis.version())"
   ```

3. **Check Virtual Environment:**
   Ensure you're in the correct virtual environment:
   ```bash
   source venv/bin/activate
   pip list | grep liblouis
   ```

### Overlapping Braille Labels

**Symptoms:**
```
Overlap detected for label at (120, 340): 10'-6"
```

**This is an informational message.** The label is still added, but it may overlap with another label.

**Solutions:**

1. **Adjust Label Offsets:**
   Edit `tactile_standards.yaml`:
   ```yaml
   braille:
     offset_x: 10  # Increase horizontal offset
     offset_y: -20  # Increase vertical offset
   ```

2. **Reduce Font Size:**
   ```yaml
   braille:
     font_size: 8  # Smaller labels
   ```

3. **Manual Review:**
   - Check PDF to see if overlaps are problematic
   - If text is too dense, consider simplifying the source image

### Labels Not Visible in PDF

**Symptoms:**
- Text detection succeeds
- Braille conversion succeeds
- But labels don't appear in PDF

**Possible Causes:**
1. Font issue (font doesn't support Unicode Braille)
2. Label position outside image bounds

**Solutions:**

1. **Check Font Support:**
   The font must support Unicode Braille characters (U+2800-U+28FF).

   Edit `tactile_standards.yaml`:
   ```yaml
   braille:
     font_name: "DejaVu Sans"  # Known to support Braille
   ```

2. **Adjust Label Positioning:**
   Labels positioned outside image bounds won't appear:
   ```yaml
   braille:
     offset_x: 0  # Reset offsets
     offset_y: 0
   ```

3. **Check PDF Viewer:**
   Some PDF viewers may not render Unicode Braille correctly. Try:
   - Adobe Acrobat Reader
   - Chrome PDF viewer
   - Firefox PDF viewer

## Limitations and Best Practices

### Current Limitations

1. **Text Detection:**
   - Works best on horizontal, upright text
   - Rotated or curved text may not be detected accurately
   - Very small text (less than 8pt) may be missed
   - Handwritten text has lower accuracy than printed text

2. **Braille Conversion:**
   - Only English language Braille (en-us-g1, en-us-g2)
   - Label positioning is automatic (cannot manually adjust individual labels)
   - Margin placement not yet implemented
   - No automatic label repositioning to avoid overlaps

3. **OCR Accuracy:**
   - Depends heavily on image quality
   - May misread similar-looking characters (O vs 0, I vs l)
   - Background patterns can interfere with detection

### Best Practices

#### For Optimal Text Detection

1. **Use High-Resolution Images:**
   - Minimum 300 DPI
   - 600 DPI recommended for small text
   - Export CAD drawings at high resolution

2. **Clean, Clear Text:**
   - Use standard, readable fonts
   - Avoid overly decorative fonts
   - Ensure good contrast between text and background

3. **Preprocessing:**
   - Remove noise and artifacts
   - Ensure proper lighting (for scans)
   - Keep text horizontal

4. **Test and Iterate:**
   ```bash
   # First attempt
   fabric-access image-to-piaf plan.jpg --detect-text --verbose

   # If needed, enhance
   fabric-access image-to-piaf plan.jpg \
     --detect-text \
     --enhance s_curve \
     --enhance-strength 1.3 \
     --verbose
   ```

#### For Readable Braille Labels

1. **Choose Appropriate Grade:**
   - Use Grade 1 for dimensions and measurements
   - Use Grade 2 for longer text if readers are proficient

2. **Check Label Placement:**
   - Review generated PDFs
   - Ensure labels don't obscure important image features
   - Verify labels are positioned near their source text

3. **Avoid Overcrowding:**
   - If image has too much text, consider:
     - Simplifying the source image
     - Using larger paper size
     - Processing in sections with tiling

4. **Test on PIAF:**
   - Print test pages
   - Verify Braille embosses clearly
   - Adjust settings based on tactile readability

#### Workflow Recommendations

1. **Start Simple:**
   ```bash
   fabric-access image-to-piaf plan.jpg --detect-text --verbose
   ```

2. **Review Output:**
   - Check how many text items were detected
   - Verify detection accuracy
   - Check PDF for label placement

3. **Adjust Settings:**
   - If text missed: Use enhancement, lower confidence threshold
   - If too much noise: Raise confidence threshold, clean image
   - If labels overlap: Adjust offsets or font size

4. **Batch Process:**
   Once settings are optimized:
   ```bash
   fabric-access batch ./all-plans ./output \
     --detect-text \
     --preset floor_plan \
     --recursive \
     --verbose
   ```

### When NOT to Use Text Detection

Text detection may not be helpful for:

1. **Images with minimal text** - Overhead of OCR not needed
2. **Very low-quality scans** - OCR will produce unreliable results
3. **Artistic or decorative text** - OCR optimized for standard fonts
4. **Photographs** - Text in photos often at angles or with perspective
5. **Dense technical drawings** - Too many labels may create clutter

For these cases, use the standard conversion without `--detect-text`.

### Performance Considerations

**Processing Time:**
- Text detection adds 2-10 seconds per image (depending on image size)
- Braille conversion adds minimal time (less than 1 second)
- Batch processing benefits from parallelization

**Memory Usage:**
- OCR requires loading full-resolution image into memory
- Large images (greater than 10,000x10,000 pixels) may require more RAM

**Optimization Tips:**
```bash
# Process at optimal resolution (don't overscan)
# 300-600 DPI is sufficient for most cases

# Use batch processing for multiple files
# More efficient than processing individually
fabric-access batch ./plans ./output --detect-text --verbose
```

## Additional Resources

### Documentation
- Main README: Overview and quick start
- WALKTHROUGH.md: Step-by-step usage guide
- BRAILLE_MODULE.md: Technical details on Braille module
- BRAILLE_WORKFLOW.md: Braille workflow documentation

### External Resources
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- Liblouis: https://github.com/liblouis/liblouis
- Unicode Braille Patterns: https://unicode.org/charts/PDF/U2800.pdf
- Braille Standards: http://www.brl.org/

### Support

For issues, questions, or feedback:
- Check troubleshooting section above
- Review configuration settings
- Open an issue on the project repository
- Consult WALKTHROUGH.md for practical examples

---

**Version:** Phase 3
**Last Updated:** December 2024
**Maintained by:** Fabric Accessible Graphics Project
