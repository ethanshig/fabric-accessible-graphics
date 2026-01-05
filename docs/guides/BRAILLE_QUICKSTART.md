# Braille Module Quick Start Guide

## Installation

### 1. Install Liblouis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install liblouis-dev python3-louis
```

**macOS:**
```bash
brew install liblouis
```

**Windows:**
Download from https://github.com/liblouis/liblouis/releases

### 2. Install Python Bindings

```bash
pip install liblouis
```

### 3. Verify Installation

```bash
python -c "import louis; print('Liblouis version:', louis.version())"
```

## Basic Usage

### Convert Text to Braille

```python
from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig
from fabric_access.utils.logger import AccessibleLogger

# Setup
logger = AccessibleLogger(verbose=True)
config = BrailleConfig(enabled=True, grade=1)
converter = BrailleConverter(config, logger)

# Convert
braille = converter.convert_text("10'-6\"")
print(braille)  # Unicode Braille output
```

### Generate PDF with Braille Labels

```python
from fabric_access.core.braille_converter import DetectedText
from fabric_access.core.pdf_generator import PIAFPDFGenerator
from PIL import Image

# Create detected texts
detected = [
    DetectedText(text="Kitchen", x=100, y=200, width=80, height=20),
    DetectedText(text="24'-0\"", x=300, y=150, width=60, height=20),
]

# Convert to Braille
labels = converter.create_braille_labels(detected)

# Generate PDF
image = Image.open("floorplan.png").convert('1')
pdf_config = {'braille': {'font_name': 'Helvetica', 'font_size': 10}}
pdf_gen = PIAFPDFGenerator(logger=logger, config=pdf_config)

pdf_gen.generate(
    image=image,
    output_path="output.pdf",
    braille_labels=labels
)
```

## Configuration

Edit `src/fabric_access/data/tactile_standards.yaml`:

```yaml
braille:
  enabled: true        # Enable Braille conversion
  grade: 1             # 1 = Grade 1, 2 = Grade 2
  font_size: 10        # Font size in points
  offset_x: 5          # Horizontal offset (pixels)
  offset_y: -10        # Vertical offset (pixels, negative = above)
  max_label_length: 30 # Max characters
```

## Testing

```bash
# Run test suite
python tests/test_braille_conversion.py

# Run demonstration
python examples/braille_demo.py
```

## Common Issues

### Liblouis Not Found

**Error:** `ModuleNotFoundError: No module named 'louis'`

**Solution:** Install Liblouis system package and Python bindings

### Font Not Rendering

**Error:** Braille characters show as boxes in PDF

**Solution:** Install DejaVu Sans font or use Helvetica (built-in)

### Invalid Grade

**Error:** `Invalid Braille grade: 3`

**Solution:** Use `grade=1` or `grade=2`

## Grade 1 vs Grade 2

**Grade 1 (Uncontracted):**
- Default setting
- One-to-one character mapping
- Best for dimensions and technical labels
- Easier to read

**Grade 2 (Contracted):**
- Uses abbreviations
- More compact
- Standard for literary text
- Set `grade=2` in config

## Key Features

- Industry-standard Liblouis translation
- Unicode Braille output (U+2800-U+28FF)
- Configurable label positioning
- Automatic truncation
- Overlap detection
- PDF integration
- Screen-reader friendly

## Documentation

- **Full Documentation:** `docs/BRAILLE_MODULE.md`
- **Implementation Summary:** `BRAILLE_IMPLEMENTATION.md`
- **Test Suite:** `tests/test_braille_conversion.py`
- **Demo Script:** `examples/braille_demo.py`

## Support

For issues:
1. Check test suite for examples
2. Review full documentation
3. Run demo script
4. Check source code comments
