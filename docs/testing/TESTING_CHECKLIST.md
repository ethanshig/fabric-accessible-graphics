# tactile Testing Checklist

Comprehensive feature-by-feature testing guide. Work through each section, running the commands and recording results in [TEST_LOG.md](TEST_LOG.md).

**Test images location:** `samples/` directory
- `plan_test.jpg` - Floor plan with rooms (primary test image)
- `ANNEX-PLANS-OFFICIAL_Page_1.jpg` - Large dense floor plan
- `Sketch_Test.jpg` - Hand-drawn sketch
- `IMG_2732.JPG` - Photograph
- `ElCroquis-test.pdf` - PDF input
- `test-floor-plan.png` - Simple PNG floor plan

---

## Section 1: Core Conversion

Basic image-to-PIAF conversion functionality.

### Basic Format Support

- [ ] **JPG conversion**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --verbose
  ```
  **Look for:** PDF created, density percentage shown, no errors

- [ ] **PNG conversion**
  ```bash
  tactile image-to-piaf samples/test-floor-plan.png --verbose
  ```
  **Look for:** PNG handled correctly, output PDF created

- [ ] **PDF input**
  ```bash
  tactile image-to-piaf samples/ElCroquis-test.pdf --verbose
  ```
  **Look for:** PDF processed, may report multi-page handling

### Threshold Control

- [ ] **Default threshold (128)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --verbose
  ```
  **Look for:** Balanced black/white output

- [ ] **Low threshold (100) - more white**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --threshold 100 --verbose
  ```
  **Look for:** Lighter output, faint lines may disappear

- [ ] **High threshold (180) - more black**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --threshold 180 --verbose
  ```
  **Look for:** Darker output, density increases

- [ ] **Extreme low threshold (50)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --threshold 50 --verbose
  ```
  **Look for:** Very light output, handles without error

- [ ] **Extreme high threshold (220)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --threshold 220 --verbose
  ```
  **Look for:** Very dark output, may trigger density warning

### Paper Size

- [ ] **Letter size (default)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --paper-size letter --verbose
  ```
  **Look for:** 8.5x11" output dimensions

- [ ] **Tabloid size**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --paper-size tabloid --verbose
  ```
  **Look for:** 11x17" output, better fit for large images

### Output Path

- [ ] **Auto-generated output name**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --verbose
  ```
  **Look for:** Creates `plan_test_piaf.pdf` in same directory

- [ ] **Custom output path**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --output /tmp/my_custom_output.pdf --verbose
  ```
  **Look for:** File created at specified path

### Enhancement Methods

- [ ] **S-curve enhancement**
  ```bash
  tactile image-to-piaf samples/Sketch_Test.jpg --enhance s_curve --verbose
  ```
  **Look for:** Improved contrast, faint lines more visible

- [ ] **S-curve with high strength**
  ```bash
  tactile image-to-piaf samples/Sketch_Test.jpg --enhance s_curve --enhance-strength 1.5 --verbose
  ```
  **Look for:** Stronger contrast effect

- [ ] **CLAHE enhancement (for photos)**
  ```bash
  tactile image-to-piaf samples/IMG_2732.JPG --enhance clahe --verbose
  ```
  **Look for:** Better local contrast, good for uneven lighting

- [ ] **Auto-contrast enhancement**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --enhance auto_contrast --verbose
  ```
  **Look for:** Automatic contrast adjustment applied

### Density Management

- [ ] **Density check (observe warning)**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --threshold 180 --verbose
  ```
  **Look for:** May show density warning if >40%

- [ ] **Auto-reduce density**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --auto-reduce-density --verbose
  ```
  **Look for:** "Reducing density" message, final density in target range

- [ ] **Auto-reduce with custom target**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --auto-reduce-density --target-density 0.25 --verbose
  ```
  **Look for:** Density reduced to ~25%

### Error Handling

- [ ] **Missing file**
  ```bash
  tactile image-to-piaf nonexistent_file.jpg
  ```
  **Look for:** Clear error message, no crash

- [ ] **Invalid threshold (out of range)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --threshold 300
  ```
  **Look for:** Error about invalid threshold

---

## Section 2: Presets

Testing all 10 conversion presets.

- [ ] **floor_plan preset**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --preset floor_plan --verbose
  ```
  **Look for:** threshold 140, s_curve enhancement applied

- [ ] **sketch preset**
  ```bash
  tactile image-to-piaf samples/Sketch_Test.jpg --preset sketch --verbose
  ```
  **Look for:** threshold 130, strong s_curve (1.3), faint lines captured

- [ ] **photograph preset**
  ```bash
  tactile image-to-piaf samples/IMG_2732.JPG --preset photograph --verbose
  ```
  **Look for:** threshold 120, CLAHE enhancement

- [ ] **elevation preset**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --preset elevation --verbose
  ```
  **Look for:** threshold 135, s_curve applied

- [ ] **section preset**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --preset section --verbose
  ```
  **Look for:** threshold 145, s_curve 1.2

- [ ] **site_plan preset**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --preset site_plan --verbose
  ```
  **Look for:** threshold 140, tabloid paper size

- [ ] **technical_drawing preset**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --preset technical_drawing --verbose
  ```
  **Look for:** threshold 150, no enhancement (clean CAD lines)

- [ ] **detail_drawing preset**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --preset detail_drawing --verbose
  ```
  **Look for:** threshold 145, s_curve 1.1

- [ ] **diagram preset**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --preset diagram --verbose
  ```
  **Look for:** threshold 135, auto_contrast enhancement

- [ ] **presentation preset**
  ```bash
  tactile image-to-piaf samples/IMG_2732.JPG --preset presentation --verbose
  ```
  **Look for:** threshold 125, CLAHE, tabloid size

- [ ] **Preset with threshold override**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --preset floor_plan --threshold 160 --verbose
  ```
  **Look for:** CLI threshold (160) overrides preset (140)

- [ ] **List presets command**
  ```bash
  tactile list-presets
  ```
  **Look for:** All 10 presets listed with descriptions

---

## Section 3: Text and Braille

OCR text detection and Braille label generation.

### Text Detection

- [ ] **Basic text detection**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --verbose
  ```
  **Look for:** "Detected X text regions", labels visible in PDF

- [ ] **Text detection on sketch**
  ```bash
  tactile image-to-piaf samples/Sketch_Test.jpg --detect-text --verbose
  ```
  **Look for:** Handwritten text detected (if any)

- [ ] **Text detection disabled (default)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --verbose
  ```
  **Look for:** No text detection messages, no Braille labels

### Braille Grades

- [ ] **Grade 1 Braille (uncontracted)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --braille-grade 1 --verbose
  ```
  **Look for:** Full spelling in Braille labels

- [ ] **Grade 2 Braille (contracted)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --braille-grade 2 --verbose
  ```
  **Look for:** Contracted Braille (shorter labels)

### Braille Rendering

- [ ] **Braille appears as dots (not squares)**
  - Open output PDF from text detection test
  **Look for:** Braille characters render as dot patterns, not black squares or missing characters

- [ ] **Text whiteout**
  - Open output PDF from text detection test
  **Look for:** Original text removed/whited out, Braille in its place

- [ ] **Label positioning**
  - Open output PDF from text detection test
  **Look for:** Labels positioned near original text location, not overlapping major drawing elements

---

## Section 4: Zoom and Scaling

Region zoom and image scaling features.

### Zoom Region (Manual Coordinates)

- [ ] **Basic zoom region**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --zoom-region 25,30,50,40 --verbose
  ```
  **Look for:** Cropped to region starting at 25% from left, 30% from top, 50% wide, 40% tall

- [ ] **Zoom to top-left corner**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --zoom-region 0,0,40,40 --verbose
  ```
  **Look for:** Top-left quadrant captured and scaled to fill page

- [ ] **Zoom to bottom-right corner**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --zoom-region 60,60,40,40 --verbose
  ```
  **Look for:** Bottom-right quadrant captured

- [ ] **Zoom with text detection**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --zoom-region 25,30,50,40 --detect-text --verbose
  ```
  **Look for:** Text detected only within zoomed region

### Manual Scaling

- [ ] **Scale 150%**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --scale-percent 150 --verbose
  ```
  **Look for:** Image enlarged 1.5x, may trigger tiling

- [ ] **Scale 200%**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --scale-percent 200 --verbose
  ```
  **Look for:** Image doubled, likely needs tiling

- [ ] **Scale 50% (reduction)**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --scale-percent 50 --verbose
  ```
  **Look for:** Image reduced to half size

### Auto-Scaling

- [ ] **Auto-scale with text detection**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --verbose
  ```
  **Look for:** "Scale applied: X%" if Braille labels needed more space

- [ ] **Auto-scale with max cap**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --max-scale-factor 1.5 --verbose
  ```
  **Look for:** Scaling capped at 150%, labels that don't fit get abbreviated

- [ ] **Auto-scale disabled**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --no-auto-scale --verbose
  ```
  **Look for:** No auto-scaling applied, labels may overflow

### Abbreviation Key

- [ ] **Abbreviation key enabled (default with text detection)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --verbose
  ```
  **Look for:** Key page generated if any labels abbreviated (A=Kitchen, B=Bedroom, etc.)

- [ ] **Force abbreviation key (all labels)**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --force-abbreviation-key --verbose
  ```
  **Look for:** ALL labels abbreviated with comprehensive key page

- [ ] **Abbreviation key disabled**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --detect-text --no-abbreviation-key --verbose
  ```
  **Look for:** No key page, long labels may overflow bounding boxes

---

## Section 5: Tiling

Large image handling and multi-page output.

- [ ] **Tiling for oversized image**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --enable-tiling --verbose
  ```
  **Look for:** Image split into multiple pages if larger than paper

- [ ] **Tiling triggered by scaling**
  ```bash
  tactile image-to-piaf samples/plan_test.jpg --scale-percent 250 --enable-tiling --verbose
  ```
  **Look for:** Scaled image tiled across multiple pages

- [ ] **Tile overlap**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --enable-tiling --tile-overlap 0.15 --verbose
  ```
  **Look for:** 15% overlap between adjacent tiles

- [ ] **Tiling without registration marks**
  ```bash
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --enable-tiling --no-registration-marks --verbose
  ```
  **Look for:** No alignment marks on tile corners

---

## Section 6: MCP Tools

Testing via Claude conversation (requires MCP server configured).

### Basic MCP Conversion

- [ ] **image_to_piaf via Claude**
  - Say to Claude: "Convert samples/plan_test.jpg to tactile"
  **Look for:** Tool called, PDF generated, success response

- [ ] **Conversion with preset via Claude**
  - Say to Claude: "Convert samples/Sketch_Test.jpg using the sketch preset"
  **Look for:** Preset applied correctly

### MCP Zoom Features

- [ ] **Natural language zoom (zoom_to)**
  - Say to Claude: "Convert samples/plan_test.jpg and zoom to the Kitchen"
  **Look for:** Phase 0 returns region identification instructions, then conversion

- [ ] **Multi-region zoom via MCP**
  - Test with zoom_regions parameter for multi-page output
  **Look for:** Multiple pages generated, one per region

### MCP Hybrid OCR

- [ ] **Phase 1: Tesseract detection**
  - Call image_to_piaf with detect_text=True
  **Look for:** Returns instructions for Claude to extract text with vision

- [ ] **Phase 2: Claude text merge**
  - Provide claude_text_json with extracted text
  **Look for:** Merged results, Braille labels generated

### Other MCP Tools

- [ ] **list_presets**
  - Call via Claude or directly
  **Look for:** All 10 presets returned with descriptions

- [ ] **analyze_image**
  - Call with image path
  **Look for:** Recommendations, suggested preset, density estimate

- [ ] **describe_image**
  - Call with image path
  **Look for:** Arch-Alt-Text format instructions for accessibility description

---

## Batch Processing

- [ ] **Batch convert folder**
  ```bash
  tactile batch samples/ /tmp/batch_output --verbose
  ```
  **Look for:** All images processed, summary at end

- [ ] **Batch with preset**
  ```bash
  tactile batch samples/ /tmp/batch_output --preset floor_plan --verbose
  ```
  **Look for:** Preset applied to all images

- [ ] **Batch with text detection**
  ```bash
  tactile batch samples/ /tmp/batch_output --detect-text --verbose
  ```
  **Look for:** Text detected on each image

---

## Quick Smoke Test (10 Critical Tests)

Run these 10 tests for quick validation before any release:

1. [ ] Basic JPG conversion works
2. [ ] Preset applies correctly
3. [ ] Text detection finds text
4. [ ] Braille renders as dots (not squares)
5. [ ] Auto-scaling applies when needed
6. [ ] Zoom region crops correctly
7. [ ] High density warning/auto-reduce works
8. [ ] MCP server starts without error
9. [ ] MCP basic conversion works
10. [ ] Missing file gives clear error

---

## Notes

[Space for testing notes, observations, questions]
