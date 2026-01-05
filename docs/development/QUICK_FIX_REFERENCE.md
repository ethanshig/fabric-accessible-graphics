# Quick Reference: Braille Whiteout Fix

## The Problem
Whiteout rectangles were **4× too small** because font sizes in **points** were being treated as **pixels**.

## The Solution
Convert font size from points to pixels at 300 DPI before any dimension calculations.

### Conversion Formula
```python
DPI = 300
POINTS_PER_INCH = 72
font_size_px = font_size * (DPI / POINTS_PER_INCH)
# Example: 10 points → 10 × 4.17 ≈ 42 pixels
```

## Files Changed

1. **braille_converter.py**
   - `_estimate_label_width()`: Fixed width calculation
   - `_check_overlap()`: Fixed height in overlap detection

2. **processor.py**
   - `whiteout_braille_regions()`: Fixed whiteout rectangle dimensions

3. **pdf_generator.py**
   - `_add_braille_labels()`: Fixed baseline calculation for coordinate transform

## Test Results

### Before Fix (v2)
- test-whiteout-v2.pdf: 42 KB (whiteout too small)
- test-annex-whiteout-v2.pdf: 1.4 MB (whiteout barely visible)

### After Fix (FINAL)
- FINAL-test-whiteout.pdf: 138 KB (proper whiteout)
- FINAL-test-annex-whiteout.pdf: 1.3 MB (proper whiteout)

## Verification
Run these commands to test:
```bash
python -m fabric_access.cli image-to-piaf Plan_Test.png --detect-text -o test1.pdf
python -m fabric_access.cli image-to-piaf ANNEX-PLANS-OFFICIAL_Page_1.jpg --detect-text -o test2.pdf
```

Expected output should include:
- "Cleared X region(s) for Braille labels"
- "Added X Braille labels"
- PDFs should show white rectangles where Braille appears
