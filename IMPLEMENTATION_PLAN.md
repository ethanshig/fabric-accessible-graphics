# Fabric-Access Refinements Plan

## Overview
Four enhancements to improve tactile graphics conversion quality and workflow.

---

## 1. Multi-page PDF Combining

### Current State
- Tiling splits ONE large image across pages
- Batch processing creates SEPARATE PDFs per image
- No multi-page PDF input handling

### Requirements
- Combine all pages from a multi-page PDF into a single tactile output
- Maintain shared context (recurring labels/symbols) across pages

### Implementation

**File: `src/fabric_access/mcp_server/tools.py`**

1. Add multi-page detection in `convert_to_tactile()`:
```python
# After line 130 (image validation)
from pdf2image import convert_from_path

if image_file.suffix.lower() == '.pdf':
    pages = convert_from_path(str(image_file), dpi=300)
    # Process each page, collect results
else:
    pages = [Image.open(image_file)]
```

2. Loop processing for each page, accumulate:
   - `detected_texts` per page (with page number)
   - `braille_labels` per page
   - Shared symbol key across all pages

**File: `src/fabric_access/core/pdf_generator.py`**

3. New method `generate_multipage()`:
   - Accept list of `(processed_image, braille_labels)` tuples
   - Add each as a page to single PDF
   - Shared symbol key on final page

**File: `src/fabric_access/core/text_detector.py`**

4. Add `page_number` field to `DetectedText` dataclass for context tracking

---

## 2. Rotated Braille for Sideways Text

### Current State
- `DetectedText` has no rotation field
- Braille always rendered horizontally
- No transform methods in PDF generator

### Requirements
- Claude Vision detects text rotation angle
- Braille placed at matching angles

### Implementation

**File: `src/fabric_access/core/text_detector.py`** (lines 42-58)

1. Add rotation to `DetectedText`:
```python
@dataclass
class DetectedText:
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    is_dimension: bool = False
    rotation_degrees: float = 0.0  # NEW: 0=horizontal, 90=vertical, etc.
```

**File: `src/fabric_access/core/braille_converter.py`** (lines 75-91)

2. Add rotation to `BrailleLabel`:
```python
@dataclass
class BrailleLabel:
    braille_text: str
    x: int
    y: int
    original_text: str
    width: Optional[int] = None
    rotation_degrees: float = 0.0  # NEW
```

3. Propagate rotation in `create_braille_labels()` (line 539):
```python
label = BrailleLabel(
    braille_text=braille_text,
    x=label_x, y=label_y,
    original_text=text,
    width=estimated_width,
    rotation_degrees=detected.rotation_degrees  # NEW
)
```

**File: `src/fabric_access/core/pdf_generator.py`** (lines 380-391)

4. Render rotated Braille using ReportLab transforms:
```python
def _add_braille_labels(self, canvas_obj, braille_labels, ...):
    for label in braille_labels:
        x, y = ... # calculate position

        if label.rotation_degrees != 0:
            canvas_obj.saveState()
            canvas_obj.translate(x, y)
            canvas_obj.rotate(label.rotation_degrees)
            canvas_obj.drawString(0, 0, label.braille_text)
            canvas_obj.restoreState()
        else:
            canvas_obj.drawString(x, y, label.braille_text)
```

**File: `src/fabric_access/mcp_server/tools.py`** (Phase 1 instructions)

5. Update Claude Vision prompt (around line 192) to request rotation:
```
"rotation_degrees": 0,  // 0=horizontal, 90=rotated clockwise, -90=counter-clockwise
```

**File: `src/fabric_access/core/hybrid_text_detector.py`**

6. Handle rotation in `_handle_unmatched()` - map Claude's rotation to DetectedText

---

## 3. Grid Overlay for Precise Text Positioning

### Current State
- Claude estimates x_percent/y_percent (0-100)
- No visual reference for positioning

### Requirements
- Overlay grid on image for Claude to reference
- Adaptive density: larger images get denser grids
- Grid enhances Claude's coordinate accuracy

### Implementation

**New File: `src/fabric_access/core/grid_overlay.py`**

```python
from PIL import Image, ImageDraw, ImageFont

def calculate_grid_density(width: int, height: int) -> tuple[int, int]:
    """Adaptive grid: larger images get denser grids."""
    # Base: 10x10 for small images (< 1000px)
    # Scale up for larger images
    base_size = 100  # pixels per cell minimum
    cols = max(10, min(30, width // base_size))
    rows = max(10, min(30, height // base_size))
    return rows, cols

def create_grid_overlay(image: Image.Image,
                        rows: int = None,
                        cols: int = None) -> Image.Image:
    """Create image copy with grid overlay and cell labels."""
    img_copy = image.copy().convert('RGB')
    draw = ImageDraw.Draw(img_copy)
    width, height = img_copy.size

    if rows is None or cols is None:
        rows, cols = calculate_grid_density(width, height)

    cell_width = width / cols
    cell_height = height / rows

    # Draw grid lines
    for i in range(1, cols):
        x = int(i * cell_width)
        draw.line([(x, 0), (x, height)], fill='red', width=1)

    for i in range(1, rows):
        y = int(i * cell_height)
        draw.line([(0, y), (width, y)], fill='red', width=1)

    # Label cells (A1, A2, ... B1, B2, ...)
    font = ImageFont.load_default()
    for row in range(rows):
        for col in range(cols):
            label = f"{chr(65 + row)}{col + 1}"  # A1, A2, B1, etc.
            x = int(col * cell_width + 5)
            y = int(row * cell_height + 5)
            draw.text((x, y), label, fill='red', font=font)

    return img_copy, rows, cols

def grid_cell_to_percent(cell: str, rows: int, cols: int) -> tuple[float, float]:
    """Convert cell reference (e.g., 'B3') to x_percent, y_percent."""
    row_letter = cell[0].upper()
    col_num = int(cell[1:])

    row_idx = ord(row_letter) - ord('A')
    col_idx = col_num - 1

    x_percent = (col_idx + 0.5) * (100 / cols)  # Center of cell
    y_percent = (row_idx + 0.5) * (100 / rows)

    return x_percent, y_percent
```

**File: `src/fabric_access/mcp_server/tools.py`**

2. Add `use_grid_overlay: bool = False` parameter (line 67)

3. In Phase 1 (lines 158-214), if grid enabled:
   - Create grid overlay image
   - Save to temp file
   - Include grid image path in instructions
   - Tell Claude to reference cell labels (e.g., "Kitchen is in cell C4")

4. In Phase 2, parse cell references and convert to percentages

**Updated Claude prompt for grid mode:**
```
"For each text element, provide the grid cell (e.g., 'C4') where it's located:
[
  {
    \"text\": \"Kitchen\",
    \"grid_cell\": \"C4\",
    \"type\": \"printed\",
    \"confidence\": \"high\"
  }
]"
```

---

## 4. Quality Assessment Loop

### Current State
- No visual comparison of input vs output
- No parameter suggestions
- Density checking exists but doesn't suggest fixes

### Requirements
- On-request (`assess_quality=True`)
- Claude compares original vs processed image
- Suggests parameter adjustments
- Criteria: structure preserved, not too dense, context-dependent

### Implementation

**File: `src/fabric_access/mcp_server/tools.py`**

1. Add parameter (line 67):
```python
assess_quality: bool = False
```

2. New tool function `assess_tactile_quality()`:
```python
async def assess_tactile_quality(
    original_image_path: str,
    processed_image_path: str,
    image_type: str = "floor_plan",  # floor_plan, site_plan, section, etc.
    current_params: Optional[Dict] = None
) -> str:
    """
    Assess tactile output quality by comparing original and processed images.

    Returns JSON with:
    - quality_score: 1-10 rating
    - issues: List of identified problems
    - suggestions: Parameter adjustments to try
    - explanation: Why changes are recommended
    """
```

3. In `convert_to_tactile()`, after PDF generation (around line 385):
```python
if assess_quality:
    # Save processed image to temp file for comparison
    processed_path = save_temp_image(processed_image)

    return json.dumps({
        "success": True,
        "phase": "quality_assessment_needed",
        "original_image": str(image_file.absolute()),
        "processed_image": processed_path,
        "current_params": {
            "threshold": effective_threshold,
            "density": density_percentage,
            "enhance": enhance,
            ...
        },
        "instructions": (
            "Please compare the original and processed images:\n"
            f"1. Original: {image_file.absolute()}\n"
            f"2. Processed: {processed_path}\n\n"
            "Evaluate based on image type '{image_type}':\n"
            "- For floor plans: Are walls, doors, windows clearly defined?\n"
            "- For site plans: Are key features (buildings, paths) distinguishable?\n"
            "- General: Is density appropriate? Too much black = paper swelling\n\n"
            "If adjustments needed, call convert_to_tactile again with:\n"
            "- threshold: increase (more white) or decrease (more black)\n"
            "- auto_reduce_density: True if too dense\n"
            "- enhance: 's_curve' or 'clahe' for more contrast"
        )
    })
```

**Assessment criteria by image type:**

| Image Type | Primary Criteria | Secondary Criteria |
|------------|------------------|-------------------|
| floor_plan | Wall boundaries clear, room labels readable | Doors/windows visible |
| site_plan | Building footprints distinct, paths visible | Landscaping not overwhelming |
| section | Vertical structure clear, levels distinct | Materials differentiated |
| elevation | Building profile clear, openings visible | Details not lost |

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/fabric_access/mcp_server/tools.py` | Add parameters, multi-page logic, grid prompt, assessment loop |
| `src/fabric_access/core/text_detector.py` | Add `rotation_degrees` and `page_number` to DetectedText |
| `src/fabric_access/core/braille_converter.py` | Add `rotation_degrees` to BrailleLabel, propagate in creation |
| `src/fabric_access/core/pdf_generator.py` | Rotated Braille rendering, `generate_multipage()` method |
| `src/fabric_access/core/hybrid_text_detector.py` | Handle rotation field in merge |
| `src/fabric_access/core/grid_overlay.py` | **NEW FILE** - Grid generation and cell-to-coordinate conversion |

---

## Implementation Order

1. **Grid Overlay** (isolated, enables better testing of other features)
2. **Rotated Braille** (enhances text detection quality)
3. **Multi-page PDF** (builds on existing tiling infrastructure)
4. **Quality Assessment** (final polish, uses all other features)

---

## Testing

Each feature needs test cases:
- Grid: Various image sizes, verify adaptive density
- Rotation: 0°, 90°, -90°, 45° text angles
- Multi-page: 2-page PDF, 5-page PDF, mixed orientations
- Assessment: Floor plan that's too dense, section with lost detail
