# Text Detection Quick Start Guide

## Installation (One-Time Setup)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Verify Installation
```bash
tesseract --version
# Should show: tesseract 4.x.x or 5.x.x
```

---

## Quick Test

### Run the test suite:
```bash
python test_text_detection.py
```

Expected output:
```
OVERALL STATUS: PASS
```

### Run the demo:
```bash
python demo_text_detection.py
# Or with specific image:
python demo_text_detection.py path/to/image.jpg
```

---

## Basic Usage (Python)

```python
from fabric_access.core.processor import ImageProcessor
from fabric_access.config.standards_loader import StandardsLoader
from fabric_access.utils.logger import AccessibleLogger

# Setup
loader = StandardsLoader()
config = loader.get_all_config()
config['text_detection']['enabled'] = True

logger = AccessibleLogger(verbose=True)
processor = ImageProcessor(config=config, logger=logger)

# Process with text detection
image, metadata = processor.process(
    input_path='floor-plan.jpg',
    detect_text=True
)

# Get results
detected_texts = metadata['detected_texts']
dimensions = [dt for dt in detected_texts if dt.is_dimension]

# Display
for dt in dimensions:
    print(f"{dt.text} at ({dt.x}, {dt.y})")
```

---

## Configuration (Optional)

Edit `src/fabric_access/data/tactile_standards.yaml`:

```yaml
text_detection:
  enabled: false          # Set to true to enable by default
  min_confidence: 60      # Lower = more detections (more false positives)
  filter_dimensions: true # Set to false to get all text
```

---

## What It Detects

### Dimension Patterns:
- Feet: `10'`, `3.5'`
- Inches: `6"`, `12.75"`
- Combined: `10'-6"`
- Metric: `3m`, `120mm`, `50cm`

### Returns:
- Text content
- Position (x, y, width, height)
- Confidence score (0-100)
- Is dimension flag

---

## Troubleshooting

### "Tesseract is not installed"
→ Install Tesseract (see Installation above)

### "pytesseract module not installed"
→ Run: `pip install pytesseract`

### No text detected
→ Common for simple drawings or low-resolution images
→ Try enhancing image first: `enhance='s_curve'`

### Low accuracy
→ Increase image quality
→ Lower min_confidence (try 50)
→ Use enhancement before OCR

---

## Performance Notes

- Small images (<1000x1000): ~1-2 seconds
- Medium images (2000x2000): ~5-10 seconds
- Large images (6000x7000): ~15-30 seconds

For faster processing, consider downsampling large images.

---

## Files Reference

| File | Purpose |
|------|---------|
| `src/fabric_access/core/text_detector.py` | Main OCR module |
| `test_text_detection.py` | Test suite |
| `demo_text_detection.py` | Demo script |
| `TEXT_DETECTION_README.md` | Full documentation |
| `IMPLEMENTATION_SUMMARY.md` | Technical details |

---

## Need Help?

See `TEXT_DETECTION_README.md` for complete documentation.
