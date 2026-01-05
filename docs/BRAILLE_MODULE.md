# Braille Conversion Module Documentation

## Overview

The Braille Conversion module (Phase 3) provides functionality to convert text labels to Unicode Braille and render them in tactile graphics PDFs. This is designed for architectural drawings and technical diagrams where dimension labels and room names need to be accessible to blind/low-vision users.

## Features

- Grade 1 Braille (uncontracted) conversion
- Grade 2 Braille (contracted) conversion
- Unicode Braille output (U+2800-U+28FF) for PDF rendering
- Configurable label positioning
- Automatic label truncation for long text
- Basic overlap detection
- Integration with PIAF PDF generator
- YAML-based configuration

## Dependencies

### Liblouis Installation

The module uses **Liblouis**, the industry-standard Braille translation library.

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install liblouis-dev python3-louis
pip install liblouis
```

#### macOS

```bash
brew install liblouis
pip install liblouis
```

#### Windows

1. Download liblouis from https://github.com/liblouis/liblouis/releases
2. Install the binary package
3. Install Python bindings:
   ```
   pip install liblouis
   ```

#### Verify Installation

```python
import louis
print(louis.version())
```

## Module Components

### 1. BrailleConfig

Configuration dataclass for Braille conversion settings.

```python
from fabric_access.core.braille_converter import BrailleConfig

config = BrailleConfig(
    enabled=True,           # Enable Braille conversion
    grade=1,                # 1 = Grade 1, 2 = Grade 2
    font_name="DejaVu Sans",  # Font supporting Unicode Braille
    font_size=10,           # Point size for PDF
    placement="overlay",    # 'overlay' or 'margin'
    offset_x=5,             # Horizontal offset (pixels)
    offset_y=-10,           # Vertical offset (pixels, negative = above)
    max_label_length=30,    # Maximum characters per label
    truncate_suffix="...",  # Suffix for truncated labels
    detect_overlaps=True,   # Check for overlapping labels
    min_label_spacing=6     # Minimum spacing (pixels)
)
```

### 2. BrailleConverter

Main converter class for text-to-Braille conversion.

```python
from fabric_access.core.braille_converter import BrailleConverter
from fabric_access.utils.logger import AccessibleLogger

logger = AccessibleLogger(verbose=True)
converter = BrailleConverter(config, logger)

# Convert single text
braille_text = converter.convert_text("10'-6\"")
print(braille_text)  # Unicode Braille output

# Convert multiple detected texts
from fabric_access.core.braille_converter import DetectedText

detected_texts = [
    DetectedText(text="Kitchen", x=100, y=200, width=80, height=20),
    DetectedText(text="10'-6\"", x=300, y=150, width=60, height=20),
]

labels = converter.create_braille_labels(detected_texts)
```

### 3. BrailleLabel

Container for Braille text with positioning information.

```python
@dataclass
class BrailleLabel:
    braille_text: str        # Unicode Braille string
    x: int                   # X coordinate (pixels)
    y: int                   # Y coordinate (pixels)
    original_text: str       # Original text before conversion
    width: Optional[int]     # Estimated width (pixels)
```

### 4. DetectedText

Input structure for text detection results.

```python
@dataclass
class DetectedText:
    text: str       # Detected text
    x: int          # X coordinate (left)
    y: int          # Y coordinate (top)
    width: int      # Bounding box width
    height: int     # Bounding box height
```

## PDF Integration

The Braille labels integrate seamlessly with the PIAF PDF generator.

```python
from fabric_access.core.pdf_generator import PIAFPDFGenerator
from PIL import Image

# Create PDF generator with Braille config
pdf_config = {
    'braille': {
        'font_name': 'Helvetica',
        'font_size': 10
    }
}

pdf_gen = PIAFPDFGenerator(logger=logger, config=pdf_config)

# Generate PDF with Braille labels
pdf_gen.generate(
    image=your_image,
    output_path="output.pdf",
    paper_size='letter',
    metadata={'source_file': 'floorplan.png'},
    braille_labels=labels  # Pass Braille labels here
)
```

## Configuration (YAML)

Configure Braille settings in `src/fabric_access/data/tactile_standards.yaml`:

```yaml
braille:
  enabled: false           # Opt-in feature
  grade: 1                 # 1 = Grade 1, 2 = Grade 2
  font_name: "DejaVu Sans"
  font_size: 10
  font_color: "black"
  placement: "overlay"
  offset_x: 5
  offset_y: -10
  max_label_length: 30
  truncate_suffix: "..."
  detect_overlaps: true
  min_label_spacing: 6
```

Load configuration:

```python
from fabric_access.config.standards_loader import load_standards

standards = load_standards()
braille_config_dict = standards.get('braille', {})

config = BrailleConfig(
    enabled=braille_config_dict.get('enabled', False),
    grade=braille_config_dict.get('grade', 1),
    # ... other settings
)
```

## Grade 1 vs Grade 2 Braille

### Grade 1 (Uncontracted)

- One-to-one character mapping
- Easier to read for beginners
- Longer output
- Best for dimensions and technical labels
- Default setting

Example:
```
Text:    "Kitchen"
Grade 1: "⠅⠊⠞⠉⠓⠑⠝"
```

### Grade 2 (Contracted)

- Uses contractions and abbreviations
- More compact
- Standard for literary Braille
- May be harder for technical content
- Optional setting

Example:
```
Text:    "Kitchen"
Grade 2: "⠅⠊⠞⠡⠝" (using contractions)
```

## Coordinate Systems

### Image Coordinates

- Origin: Top-left corner
- X increases to the right
- Y increases downward
- Units: Pixels

### PDF Coordinates

- Origin: Bottom-left corner
- X increases to the right
- Y increases upward
- Units: Points (1/72 inch)

### Conversion

The module handles coordinate conversion automatically:

```python
# Formula used internally
pdf_y = (image_height - image_y) * scale_factor
```

## Label Positioning

Labels are positioned relative to detected text with configurable offsets:

```
Original Text Position: (x, y)
                        ↓
Label Position: (x + offset_x, y + offset_y)

Example with offset_x=5, offset_y=-10:
  ⠅⠊⠞⠉⠓⠑⠝  ← Braille label (10 pixels above)
   Kitchen      ← Original text
```

## Truncation

Long labels are automatically truncated:

```python
config = BrailleConfig(
    max_label_length=15,
    truncate_suffix="..."
)

# Input:  "This is a very long dimension label"
# Output: "This is a ve..."  (truncated to 15 chars including suffix)
```

## Overlap Detection

Basic overlap detection warns about overlapping labels:

```python
config = BrailleConfig(
    detect_overlaps=True,
    min_label_spacing=6  # pixels
)

# Overlaps are logged but labels are still created
# Future enhancement: Automatic repositioning
```

## Error Handling

### BrailleConversionError

Raised when conversion fails:

```python
from fabric_access.core.braille_converter import BrailleConversionError

try:
    converter = BrailleConverter(config, logger)
    braille = converter.convert_text("Sample")
except BrailleConversionError as e:
    print(f"Conversion failed: {e}")
```

### Common Issues

1. **Liblouis Not Installed**
   ```
   Error: Liblouis not installed
   Solution: pip install liblouis
   ```

2. **Invalid Grade Setting**
   ```
   Error: Invalid Braille grade: 3
   Solution: Use grade=1 or grade=2
   ```

3. **Empty Text**
   - Returns empty string
   - No error raised
   - Normal behavior

## Examples

### Example 1: Simple Conversion

```python
from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig
from fabric_access.utils.logger import AccessibleLogger

logger = AccessibleLogger(verbose=True)
config = BrailleConfig(enabled=True, grade=1)
converter = BrailleConverter(config, logger)

# Convert dimension
dimension = "24'-0\""
braille = converter.convert_text(dimension)
print(f"{dimension} -> {braille}")
```

### Example 2: Full Pipeline

```python
from fabric_access.core.braille_converter import (
    BrailleConverter, BrailleConfig, DetectedText
)
from fabric_access.core.pdf_generator import PIAFPDFGenerator
from fabric_access.utils.logger import AccessibleLogger
from PIL import Image

# Setup
logger = AccessibleLogger(verbose=True)
config = BrailleConfig(enabled=True, grade=1)
converter = BrailleConverter(config, logger)

# Simulate text detection (would come from OCR in real use)
detected_texts = [
    DetectedText(text="24'-0\"", x=100, y=50, width=60, height=20),
    DetectedText(text="Kitchen", x=200, y=150, width=80, height=20),
]

# Convert to Braille
labels = converter.create_braille_labels(detected_texts)

# Load image
image = Image.open("floorplan.png").convert('1')

# Generate PDF with Braille
pdf_config = {'braille': {'font_name': 'Helvetica', 'font_size': 10}}
pdf_gen = PIAFPDFGenerator(logger=logger, config=pdf_config)

pdf_gen.generate(
    image=image,
    output_path="output_with_braille.pdf",
    braille_labels=labels
)
```

### Example 3: Grade 2 Braille

```python
config = BrailleConfig(enabled=True, grade=2)  # Grade 2
converter = BrailleConverter(config, logger)

room_labels = ["Kitchen", "Bathroom", "Bedroom", "Living Room"]
for label in room_labels:
    braille = converter.convert_text(label)
    print(f"{label:15} -> {braille}")
```

## Testing

Run the test suite:

```bash
python tests/test_braille_conversion.py
```

Tests cover:
- Liblouis installation
- Grade 1 and Grade 2 conversion
- Label positioning
- Truncation
- Overlap detection
- PDF integration
- Unicode Braille validation
- Error handling

## Demonstration

Run the demo script:

```bash
python examples/braille_demo.py
```

Demonstrates:
- Grade 1 and Grade 2 conversion
- PDF generation with Braille labels
- Configuration loading
- Comparison of Braille grades

## Font Support

### Unicode Braille Range

- Start: U+2800 (⠀ - blank Braille pattern)
- End: U+28FF (⣿ - all dots filled)
- Total: 256 patterns (2^8 combinations)

### Recommended Fonts

1. **DejaVu Sans** (recommended)
   - Excellent Braille support
   - Open source
   - Cross-platform

2. **Helvetica** (fallback)
   - Built into ReportLab
   - Basic Braille support
   - May not render all patterns

3. **Arial Unicode MS**
   - Good Braille support
   - Wide availability on Windows

### Font Installation

DejaVu Sans is usually pre-installed. If needed:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-dejavu

# macOS
brew install --cask font-dejavu

# Windows
Download from https://dejavu-fonts.github.io/
```

## Performance Considerations

- Braille conversion is fast (microseconds per label)
- PDF rendering adds minimal overhead
- Overlap detection scales O(n²) with label count
- For large documents (>1000 labels), consider disabling overlap detection

## Accessibility Notes

This module follows accessibility-first design:

- Clear, descriptive status messages
- No emojis or visual-only symbols
- Screen-reader friendly output
- Logging format: `[STATUS]: Message`
- Verbose mode for detailed progress

## Future Enhancements

Planned features:

1. **Automatic Label Repositioning**
   - Avoid overlaps by adjusting positions
   - Smart placement algorithms

2. **Margin Placement Mode**
   - Place labels in document margins
   - Avoid obscuring graphics

3. **Custom Translation Tables**
   - Support for specialized Braille codes
   - Mathematics and technical notation

4. **Multi-line Labels**
   - Wrap long labels across multiple lines
   - Configurable line breaks

5. **Braille Font Embedding**
   - Embed Braille fonts in PDF
   - Ensure consistent rendering

## References

- [Liblouis Documentation](https://liblouis.io/)
- [Unicode Braille Patterns](https://en.wikipedia.org/wiki/Braille_Patterns)
- [Braille Authority of North America](http://www.brailleauthority.org/)
- [Grade 1 vs Grade 2 Braille](https://www.afb.org/blindness-and-low-vision/braille/what-braille)

## License

This module is part of the Fabric Accessible Graphics Toolkit and follows the same license as the main project.

## Support

For issues or questions:
1. Check the test suite for examples
2. Review this documentation
3. Examine the demo script
4. Check the module source code comments

## Version History

- **Phase 3 (Current)**: Initial Braille conversion implementation
  - Grade 1 and Grade 2 Braille
  - Unicode output
  - PDF integration
  - YAML configuration
