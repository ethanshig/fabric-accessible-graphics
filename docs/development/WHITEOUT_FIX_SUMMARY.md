# Braille Whiteout Coordinate System Fix

## Problem Summary

The Braille whiteout feature had two critical issues:

1. **In test-annex-whiteout-v2.pdf**: Whiteout wasn't showing up at all or was too small
2. **In test-whiteout-v2.pdf**: Whiteout appeared too small and misaligned

## Root Cause

The fundamental issue was a **units mismatch**: font sizes were specified in **points** but were being treated as **pixels** throughout the codebase.

### Typography Units
- Font size is specified in **points** (pt)
- 1 point = 1/72 inch
- At 300 DPI: 1 point = 300/72 ≈ 4.17 pixels

### The Bug
When `font_size = 10` points:
- **Expected**: 10 × 4.17 ≈ **42 pixels**
- **Actual (buggy)**: **10 pixels** (treating points as pixels)

This caused whiteout rectangles to be approximately **4× smaller** than they should be, making them appear tiny or invisible.

## Files Modified

### 1. `/src/fabric_access/core/braille_converter.py`
**Issue**: Width and height calculations used font_size directly as pixels

**Fixed methods**:
- `_estimate_label_width()`: Now converts font_size from points to pixels before calculating character width
- `_check_overlap()`: Now converts font_size to pixels for bounding box height calculations

**Changes**:
```python
# Before (WRONG):
char_width = self.config.font_size * 0.6  # Treating points as pixels

# After (CORRECT):
DPI = 300
POINTS_PER_INCH = 72
font_size_px = self.config.font_size * (DPI / POINTS_PER_INCH)
char_width = font_size_px * 0.6  # Using actual pixels
```

### 2. `/src/fabric_access/core/processor.py`
**Issue**: `whiteout_braille_regions()` used font_size in points to calculate pixel dimensions

**Fixed**:
- Added conversion from points to pixels at 300 DPI
- Properly sized whiteout rectangles based on actual pixel dimensions

**Changes**:
```python
# Before (WRONG):
label_height = font_size  # Treating points as pixels

# After (CORRECT):
DPI = 300
POINTS_PER_INCH = 72
pixels_per_point = DPI / POINTS_PER_INCH
font_size_px = int(font_size * pixels_per_point)
label_height = font_size_px  # Using actual pixels
```

### 3. `/src/fabric_access/core/pdf_generator.py`
**Issue**: PDF baseline calculation used font_size in points for pixel-based coordinate transformation

**Fixed**:
- Converts font_size to pixels before calculating baseline offset
- Ensures Braille text appears at the exact position where whiteout was applied

**Changes**:
```python
# Before (WRONG):
baseline_offset = 0.8 * font_size  # Mixing points with pixel coordinates

# After (CORRECT):
DPI = 300
POINTS_PER_INCH = 72
font_size_px = font_size * (DPI / POINTS_PER_INCH)
baseline_offset = 0.8 * font_size_px  # Using actual pixels
```

## Coordinate System Details

### Image Space (used by whiteout)
- Origin: Top-left corner
- Y-axis: Increases downward
- Units: Pixels
- `label.y` = TOP of text bounding box

### PDF Space (used by reportlab)
- Origin: Bottom-left corner
- Y-axis: Increases upward
- Units: Points (converted from pixels via scale_factor)
- `drawString(x, y)` expects y = BASELINE position

### Transformation Formula
```python
# For a text box starting at label.y (top) in image space:
# 1. Calculate baseline position in image space
baseline_image_y = label.y + (0.8 * font_size_px)

# 2. Convert to PDF space (flip Y-axis)
baseline_pdf_y = (image_height - baseline_image_y) * scale_factor

# 3. Apply centering offsets
final_y = baseline_pdf_y * inch + y_offset
```

## Testing

### Test Commands
```bash
# Test with Plan_Test.png
python -m fabric_access.cli image-to-piaf Plan_Test.png --detect-text -o test-whiteout-FINAL.pdf

# Test with ANNEX image
python -m fabric_access.cli image-to-piaf ANNEX-PLANS-OFFICIAL_Page_1.jpg --detect-text -o test-annex-whiteout-FINAL.pdf
```

### Expected Results
- Whiteout rectangles should be approximately 42 pixels tall (for 10pt font)
- Whiteout rectangles should match the width of the Braille text
- Braille labels should appear centered within the whiteout regions
- No visible misalignment between whiteout and Braille text

### File Size Verification
The fix significantly increases whiteout coverage:

**Before (v2 - buggy)**:
- test-whiteout-v2.pdf: 42 KB (tiny whiteouts)
- test-annex-whiteout-v2.pdf: 1.4 MB

**After (FINAL - fixed)**:
- test-whiteout-FINAL.pdf: 138 KB (proper whiteouts, 3× larger)
- test-annex-whiteout-FINAL.pdf: 1.3 MB (more whiteout, smaller file)

## Impact

### Fixed
- Whiteout regions now properly clear space for Braille labels
- Size calculations are accurate for all font sizes
- Coordinate transformations correctly handle units conversion
- Overlap detection works with proper dimensions

### Unchanged
- Braille text conversion (already working)
- Text detection (already working)
- PDF structure and layout (already working)

## Technical Notes

### DPI Consistency
All calculations assume **300 DPI** output, which matches:
- PIAF machine requirements
- PDF generation settings (PIAFPDFGenerator.TARGET_DPI = 300)
- Image processing pipeline

### Font Size Handling
- Config files specify font_size in **points** (standard typography)
- Internal calculations convert to **pixels** at 300 DPI
- PDF rendering uses **points** directly (reportlab native units)

### Baseline Approximation
The baseline offset uses `0.8 * font_size_px` as an approximation:
- Typical fonts: ascent ≈ 0.75-0.85 of font height
- 0.8 is a reasonable middle ground
- Exact metrics would require font file parsing (overkill for this use case)
