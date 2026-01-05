# Architectural Tactile Graphics Guidelines - Project Status

DATE: 2025-12-26
STATUS: In Progress

---

## Project Goal

Create comprehensive guidelines that LLMs can use to convert architectural graphics into accessible tactile formats for a blind/low-vision architecture student. The LLM receives images and invokes the Image-to-PIAF tool with appropriate parameters.

---

## Student Context

- **Level**: Sophomore architecture student
- **Courses**: Structures, Design Studio
- **Vision**: Some residual, but goal is fully tactile (may deteriorate)
- **Braille**: Fluent in Grade 2 (contracted) - preferred
- **Assistance**: Has sighted help, but goal is self-sufficiency
- **Workflow**: Drop image in → LLM processes → Student prints on PIAF

---

## Key Requirements Established

1. **No overlapping information** - absolute rule
2. **Preserve original scale** - unless tiling required or user specifies otherwise
3. **Grade 2 Braille** - always
4. **Colors → patterns/textures** - describe in text until pattern detection implemented
5. **LLM explains simplification choices** - transparency required
6. **On-demand production** - minimal iteration cycles

---

## Completed Work

### 1. Symbol Key Feature (Code)
Added to Image-to-PIAF tool:
- When Braille labels overlap and can't be repositioned, replaced with symbols (a, b, c...)
- Automatic key page added to PDF with Braille + print for each symbol
- Format: Line 1 = Braille, Line 2 = Print text

Files modified:
- `src/fabric_access/core/braille_converter.py` - SymbolKeyEntry, _get_next_symbol(), modified create_braille_labels()
- `src/fabric_access/core/pdf_generator.py` - add_key_page(), updated generate()
- `src/fabric_access/cli.py` - Handle tuple return, pass to PDF generator

### 2. Main Guidelines Document
**Location**: `/patterns/ARCHITECTURAL_TACTILE_GUIDELINES.md`

Contains:
- Overview and user context
- Pattern integration (Image-Description-Machine → Guidelines → Image-to-PIAF)
- General principles (no overlap, scale preservation, Braille standards)
- 9 graphic categories with specific parameters
- Complete CLI syntax and examples
- Decision framework (when to simplify, tile, use symbols)
- Testing log structure
- Quick reference card
- Glossary

### 3. Floor Plans Guide
**Location**: `/patterns/graphic-types/floor-plans.md`

Contains:
- What floor plans are and when encountered
- Information hierarchy (essential/important/optional/omit)
- Common challenges with solutions
- Recommended CLI parameters
- Examples using ANNEX and plan_test images
- Testing checklist

### 4. Text Visualization
**Location**: `/annex-text-visualization.png`
- Red bounding boxes around 185 detected text elements in ANNEX floor plan
- Script saved: `create_annex_visualization.py`

---

## Remaining Work

### High Priority

1. **Test with Student**
   - Print ANNEX floor plan using guidelines
   - Record comprehension time, confusion points
   - Update guidelines based on feedback
   - Determine acceptable density thresholds

2. **Create Additional Graphic Type Guides**
   - `/patterns/graphic-types/sections.md`
   - `/patterns/graphic-types/elevations.md`
   - `/patterns/graphic-types/structural-diagrams.md` (important for structures class)
   - `/patterns/graphic-types/details.md`
   - `/patterns/graphic-types/diagrams.md`

### Medium Priority

3. **BANA Standards Reference**
   - Extract relevant sections from `Tactile Graphics Standards and Guidelines 2022_a11y.pdf`
   - PDF too large for automated extraction - do manually
   - Save to `/patterns/references/BANA_SUMMARY.md`

4. **Pattern/Texture Library**
   - Document which patterns work for which architectural elements
   - Create `/patterns/references/TEXTURE_PATTERNS.md`

### Future Enhancements

5. **Callout System**
   - For dense areas, create zoomed detail views
   - Link main drawing to detail with consistent labeling

6. **Color Detection**
   - Automatically detect color-coded information
   - Generate text description of what colors represent

---

## File Structure

```
/patterns/
├── ARCHITECTURAL_TACTILE_GUIDELINES.md    ✓ Created
├── graphic-types/
│   ├── floor-plans.md                     ✓ Created
│   ├── sections.md                        ○ To create
│   ├── elevations.md                      ○ To create
│   ├── structural-diagrams.md             ○ To create
│   ├── details.md                         ○ To create
│   └── diagrams.md                        ○ To create
├── decision-trees/
│   ├── simplification.md                  ○ To create
│   ├── labeling.md                        ○ To create
│   └── density.md                         ○ To create
├── references/
│   ├── BANA_SUMMARY.md                    ○ To create
│   └── TEXTURE_PATTERNS.md                ○ To create
└── examples/
    └── [before/after samples]             ○ To create
```

---

## How to Continue

### To test with student:
```bash
cd /mnt/c/Users/ethan/fabric-accessible-graphics
source venv/bin/activate

# Process ANNEX floor plan
fabric-access image-to-piaf ANNEX-PLANS-OFFICIAL_Page_1.jpg \
  --preset floor_plan \
  --detect-text \
  --braille-grade 2 \
  --paper-size tabloid \
  --verbose \
  -o annex-test-for-student.pdf
```

### To create next graphic type guide:
Ask Claude to create the sections.md or structural-diagrams.md guide following the same format as floor-plans.md.

### To review/edit guidelines:
Main document is at `/patterns/ARCHITECTURAL_TACTILE_GUIDELINES.md`

---

## Questions to Resolve Through Testing

1. What is the maximum acceptable tactile density?
2. How much simplification is too much for architectural understanding?
3. Which line weights/patterns are distinguishable?
4. Optimal Braille label size and spacing?
5. When does tiling help vs. hurt comprehension?
6. How to handle structural diagrams with tension/compression colors?

---

## Notes

- Image-Description-Machine pattern exists at `/patterns/image_description_machine/`
- Image-to-PIAF is the CLI tool: `fabric-access image-to-piaf`
- Student prefers self-sufficiency - minimize need for sighted assistance
- All prints should be at original scale unless specified
- Both 8.5x11 (letter) and 11x17 (tabloid) paper available
