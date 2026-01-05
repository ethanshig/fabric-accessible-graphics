# Text Detection Module - Phase 3

## Overview

The Text Detection module adds OCR (Optical Character Recognition) capability to the Fabric Accessible Graphics Toolkit, enabling automatic detection and localization of text and dimensions in architectural drawings.

## Features

- **Tesseract OCR Integration**: Uses industry-standard Tesseract OCR engine
- **Dimension Detection**: Automatically identifies architectural dimensions (feet, inches, meters, etc.)
- **Bounding Box Detection**: Returns exact position and size of detected text
- **Confidence Filtering**: Filters low-confidence OCR results
- **Pattern Matching**: Regex-based dimension pattern recognition
- **Pipeline Integration**: Seamlessly integrates into existing processing pipeline

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install `pytesseract>=0.3.10` along with other dependencies.

### 2. Install Tesseract OCR

The `pytesseract` package requires the Tesseract OCR engine to be installed on your system:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki

Verify installation:
```bash
tesseract --version
```

## Configuration

Text detection is configured in `src/fabric_access/data/tactile_standards.yaml`:

```yaml
text_detection:
  enabled: false  # Opt-in feature (default: disabled)

  # Tesseract OCR settings
  language: 'eng'  # Language code for OCR
  page_segmentation_mode: 3  # PSM 3 = Fully automatic
  min_confidence: 60  # Minimum confidence threshold (0-100)

  # Dimension detection
  filter_dimensions: true  # Identify dimension text separately
  dimension_patterns:
    - "\\d+['\"]"              # Feet and inches (10', 6")
    - "\\d+\\.\\d+['\"]"       # Decimal feet/inches (3.5')
    - "\\d+-\\d+['\"]"         # Range format (10'-6")
    - "\\d+m"                  # Meters (3m)
    - "\\d+mm"                 # Millimeters (120mm)
    - "\\d+cm"                 # Centimeters (50cm)
```

### Configuration Options

- **enabled**: Enable/disable text detection (default: `false`)
- **language**: Tesseract language code (default: `'eng'`)
- **page_segmentation_mode**: Tesseract PSM mode (default: `3` for automatic)
- **min_confidence**: Minimum OCR confidence to accept (0-100, default: `60`)
- **filter_dimensions**: Enable dimension pattern matching (default: `true`)
- **dimension_patterns**: List of regex patterns for dimension detection

## Usage

### Programmatic Usage

```python
from fabric_access.core.processor import ImageProcessor
from fabric_access.config.standards_loader import StandardsLoader
from fabric_access.utils.logger import AccessibleLogger

# Load configuration
loader = StandardsLoader()
config = loader.get_all_config()

# Enable text detection
config['text_detection']['enabled'] = True

# Initialize processor
logger = AccessibleLogger(verbose=True)
processor = ImageProcessor(config=config, logger=logger)

# Process image with text detection
processed_image, metadata = processor.process(
    input_path='floor-plan.jpg',
    threshold=128,
    detect_text=True  # Enable text detection for this image
)

# Access detected texts
detected_texts = metadata['detected_texts']

# Filter by type
dimensions = [dt for dt in detected_texts if dt.is_dimension]
other_text = [dt for dt in detected_texts if not dt.is_dimension]

# Access text properties
for dt in dimensions:
    print(f"Dimension: '{dt.text}'")
    print(f"  Location: ({dt.x}, {dt.y})")
    print(f"  Size: {dt.width}x{dt.height}")
    print(f"  Confidence: {dt.confidence}%")
```

### Using the Text Detector Directly

```python
from fabric_access.core.text_detector import TextDetector, TextDetectionConfig
from fabric_access.utils.logger import AccessibleLogger
from PIL import Image

# Configure text detector
config = TextDetectionConfig(
    enabled=True,
    language='eng',
    min_confidence=60,
    filter_dimensions=True,
    dimension_patterns=[r"\d+['\"]", r"\d+-\d+['\"]"]
)

# Initialize detector
logger = AccessibleLogger(verbose=True)
detector = TextDetector(config=config, logger=logger)

# Load and process image
image = Image.open('plan.jpg').convert('L')  # Grayscale
detected_texts = detector.detect_text(image)

# Process results
for dt in detected_texts:
    if dt.is_dimension:
        print(f"Found dimension: {dt.text}")
```

## Data Structures

### TextDetectionConfig

Configuration dataclass for text detection:

```python
@dataclass
class TextDetectionConfig:
    enabled: bool = False
    language: str = 'eng'
    page_segmentation_mode: int = 3
    min_confidence: int = 60
    filter_dimensions: bool = True
    dimension_patterns: List[str] = field(default_factory=list)
```

### DetectedText

Container for detected text with metadata:

```python
@dataclass
class DetectedText:
    text: str              # Detected text string
    x: int                 # X coordinate of bounding box
    y: int                 # Y coordinate of bounding box
    width: int             # Width of bounding box
    height: int            # Height of bounding box
    confidence: float      # OCR confidence (0-100)
    is_dimension: bool     # Whether text matches dimension pattern
```

## Testing

### Run the Test Suite

```bash
python test_text_detection.py
```

This will test:
1. Tesseract installation
2. Text detection on sample images
3. Dimension pattern matching
4. Integration with ImageProcessor

### Run the Demonstration

```bash
python demo_text_detection.py [image_path]
```

If no image path is provided, it will use the first available test image.

## Important Notes

### When to Use Text Detection

- **Opt-in Feature**: Text detection is disabled by default in config
- **Performance**: OCR can be slow on large images (6000x7000 pixels may take 10-30 seconds)
- **Best Results**: Run OCR on grayscale/enhanced image BEFORE thresholding
- **Use Cases**:
  - Identifying dimensions for Braille labels
  - Locating room labels for accessibility
  - Cataloging text elements in drawings

### Limitations

1. **OCR Accuracy**: Architectural drawings often have:
   - Small text that's hard to read
   - Stylized fonts
   - Text at angles
   - Low contrast text

2. **Dimension Detection**: Current patterns detect:
   - Imperial units (feet/inches): `10'`, `6"`, `10'-6"`
   - Metric units: `3m`, `120mm`, `50cm`
   - Does NOT detect: Decimal points without units, fractions, angled dimensions

3. **Performance**: Large images (>5000x5000px) may take significant time

### Best Practices

1. **Use Grayscale**: Convert to grayscale before OCR for better accuracy
2. **Apply Enhancement**: Use S-curve or CLAHE before OCR to improve contrast
3. **Filter Confidence**: Use `min_confidence >= 60` to reduce false positives
4. **Validate Results**: OCR on architectural drawings can have errors
5. **Check Tesseract**: Ensure Tesseract is installed and in PATH

## Architecture

### Processing Flow

```
1. Load Image (RGB/CMYK/etc)
2. Convert to Grayscale
3. Apply Enhancement (S-curve, CLAHE, etc.) - OPTIONAL
4. >>> TEXT DETECTION (OCR on enhanced grayscale) <<< NEW
5. Apply Threshold (B&W conversion)
6. Density Check
7. Output
```

Text detection runs BEFORE thresholding because:
- Grayscale images have more information than binary (B&W)
- Enhancement improves text contrast
- Tesseract works better on grayscale

### Module Structure

```
src/fabric_access/core/text_detector.py
  - TextDetectionError: Custom exception
  - TextDetectionConfig: Configuration dataclass
  - DetectedText: Result dataclass
  - TextDetector: Main detector class
    - detect_text(): Run OCR and return results
    - _preprocess_for_ocr(): Enhance image for better OCR
    - _is_dimension(): Pattern matching for dimensions
```

## Error Handling

The module includes graceful error handling:

```python
# If Tesseract not installed
TextDetectionError: "Tesseract OCR is not installed or not in PATH"

# If pytesseract module missing
TextDetectionError: "pytesseract module not installed"

# In ImageProcessor integration
# - Falls back gracefully if text detection fails
# - Logs warning and continues processing
# - Returns empty list for detected_texts
```

## Future Enhancements (Phase 4+)

Potential future improvements:

1. **Advanced Pattern Matching**: Support for more dimension formats
2. **Text Orientation**: Detect and handle rotated text
3. **Multi-Language**: Support for non-English text
4. **Text Removal**: Option to remove text for cleaner tactile output
5. **Braille Labels**: Convert detected dimensions to Braille overlays
6. **Room Label Detection**: Specific patterns for room names
7. **Performance**: Downsample large images for faster OCR
8. **Custom Training**: Fine-tune Tesseract for architectural drawings

## Accessibility

All status messages follow screen-reader friendly format:

```
Processing: Detecting text and dimensions
Found 5 dimension(s)
Found 23 other text element(s)
No text detected
```

- Clear, descriptive messages
- No emojis or visual symbols
- Consistent `[ACTION]: [Description]` format
- Real-time progress updates with verbose mode

## License & Credits

Part of the Fabric Accessible Graphics Toolkit.
Uses Tesseract OCR (Apache 2.0 License).
