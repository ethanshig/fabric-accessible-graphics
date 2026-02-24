# ConvertImage Workflow

Step-by-step process for converting an image to tactile-ready PDF.

## Prerequisites

- Image file path provided by user
- `tact` CLI available (from tactile-core)
- Tesseract installed (if text detection needed)

## Workflow Steps

### Step 1: Analyze Source Image

Before conversion, understand the source:

1. **Identify image type**:
   - Floor plan, section, elevation, sketch, photograph?
   - This determines the best preset

2. **Assess quality**:
   - Is it high contrast already?
   - Are lines clean or fuzzy?
   - Is there text/dimensions visible?

3. **Check complexity**:
   - Single system or multiple overlapping?
   - If complex, consider TactileGeneration instead

**Tool call** (optional):
```bash
tact analyze IMAGE_PATH
```

### Step 2: Select Preset

Match image type to preset:

| Image Type | Recommended Preset |
|------------|-------------------|
| Architectural floor plan | `floor_plan` |
| Building section | `section` |
| Building elevation | `elevation` |
| Site/landscape plan | `site_plan` |
| Hand-drawn sketch | `sketch` |
| Conceptual diagram | `diagram` |
| CAD output | `technical_drawing` |
| Photo of building | `photograph` |
| Presentation board | `presentation` |
| Construction detail | `detail_drawing` |

If unsure, ask user or use default (no preset).

### Step 3: Determine Options

Based on user needs:

**Text Detection**:
- Does image have labels/dimensions?
- User wants Braille? → Add `--detect-text --braille-grade 2`

**Paper Size**:
- Standard drawings → `letter` (default)
- Large plans → `tabloid`
- Very large → Add `--enable-tiling`

**Density Issues**:
- If source is dense/dark → Add `--auto-reduce-density`

**Region Focus**:
- User wants specific area? → Add `--zoom-region X,Y,W,H`

### Step 4: Execute Conversion

Build and run the command:

```bash
tact image-to-piaf IMAGE_PATH \
  --preset PRESET_NAME \
  --detect-text \
  --braille-grade 2 \
  --verbose
```

**Using the tool wrapper**:
```typescript
// Via TactileConvert.ts
bun run src/tools/TactileConvert.ts IMAGE_PATH --preset floor_plan --detect-text
```

### Step 5: Validate Output

Check the results:

1. **Density**: Should be < 40% (ideally < 30%)
2. **Dimensions**: Fits on selected paper size?
3. **Braille**: Labels present and readable?
4. **Key page**: Generated if abbreviations used?

If density too high:
```bash
tact image-to-piaf IMAGE_PATH --auto-reduce-density --verbose
```

### Step 6: Present Results

Report to user:
- Output file path
- Paper size used
- Density percentage
- Number of pages (if tiled)
- Braille labels added (if detected)

**Offer refinements**:
- Adjust threshold if too light/dark
- Try different preset
- Enable/disable text detection
- Zoom to specific region

## Example Execution

**User request**: "Convert this floor plan to tactile"

**Response**:
```
I'll convert the floor plan using the floor_plan preset with Braille labels.

Running: tact image-to-piaf floor-plan.jpg --preset floor_plan --detect-text --braille-grade 2 --verbose

Results:
- Output: floor-plan_piaf.pdf
- Paper size: letter (8.5" x 11")
- Density: 28% (good)
- Braille labels: 8 detected, Grade 2
- Key page: Not needed (all labels fit)

The PDF is ready for PIAF printing. Would you like me to:
1. Adjust the threshold for more/less contrast?
2. Zoom to a specific room?
3. Generate a description of the plan?
```

## Error Handling

| Error | Solution |
|-------|----------|
| "Density too high" | Add `--auto-reduce-density` |
| "Image too large" | Add `--enable-tiling` or `--paper-size tabloid` |
| "Tesseract not found" | Install Tesseract or skip `--detect-text` |
| "File not found" | Verify image path |
| "Unsupported format" | Convert to JPG/PNG first |

## Batch Processing

For multiple images:

```bash
tact batch INPUT_DIR OUTPUT_DIR --preset floor_plan --detect-text --verbose
```

Or with recursive subdirectories:

```bash
tact batch INPUT_DIR OUTPUT_DIR --preset floor_plan --recursive --verbose
```
