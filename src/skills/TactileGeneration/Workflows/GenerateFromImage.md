# GenerateFromImage Workflow

Generate simplified tactile graphics from complex source images.

## Prerequisites

- Source image provided by user
- PAI Art skill available (for image generation)
- API keys configured (GOOGLE_API_KEY for Nano Banana Pro)

## When to Use

- Source image is cluttered, low-contrast, or overly complex
- Multiple overlapping systems need separation
- Simplification would improve tactile readability
- TactileConversion produced poor results

## Workflow Steps

### Step 1: Analyze Source Image

Use Claude vision to understand the source:

1. **Identify drawing type**: Floor plan, section, elevation, etc.
2. **Catalog elements**:
   - Primary elements (walls, structure)
   - Secondary elements (doors, windows)
   - Tertiary elements (furniture, fixtures)
   - Systems present (structure, circulation, MEP)
3. **Assess complexity**:
   - How many overlapping systems?
   - What can be omitted?
   - Would stratification help?

**Output**: Element inventory and complexity assessment

### Step 2: Determine Strategy

Based on analysis:

| Scenario | Strategy |
|----------|----------|
| Single system, cluttered | Simplify and regenerate |
| Multiple systems, separable | Stratify into layers |
| Key details lost in noise | Focus on essentials |
| Low contrast source | Regenerate with high contrast |

**Ask user if unclear**:
- "This drawing has structure, circulation, and MEP. Should I stratify into separate layers?"
- "Should I include doors and windows, or just walls?"

### Step 3: Construct Prompt

Build the generation prompt:

**Part 1: Drawing Type + Style**
```
Architectural [floor plan/section/elevation], technical drawing style,
clean linework, orthographic projection, high contrast
```

**Part 2: Content Description**
Describe what to include based on source:
```
Recreate the essential spatial layout from the reference:
- [List primary elements to include]
- [Describe overall geometry]
- [Specify what to emphasize]

Omit: [List elements to exclude]
```

**Part 3: Reference Image** (optional)
If using model that supports reference images (Nano Banana Pro):
```
Use the provided image as reference for spatial layout,
but simplify all linework to meet tactile requirements.
```

**Part 4: Tactile Suffix**
Append the mandatory suffix from `TactilePromptGuide.md`

### Step 4: Generate Image

Execute using PAI's Art skill:

```bash
bun run ~/.claude/skills/Art/Tools/Generate.ts \
  --model nano-banana-pro \
  --prompt "[constructed prompt]" \
  --reference "[source image path]" \
  --size 2K \
  --aspect-ratio 17:22 \
  --output ~/Downloads/tactile-output.png
```

For stratified output, generate each layer separately:
```bash
# Layer 1: Structure
bun run Generate.ts --prompt "[structure prompt]" --output ~/Downloads/tactile-structure.png

# Layer 2: Circulation
bun run Generate.ts --prompt "[circulation prompt]" --output ~/Downloads/tactile-circulation.png

# Layer 3: Program
bun run Generate.ts --prompt "[program prompt]" --output ~/Downloads/tactile-program.png
```

### Step 5: Validate Output

Check generated image against requirements:

- [ ] Pure black and white only (no grays)
- [ ] Lines appear bold enough (>1.5mm at print size)
- [ ] Adequate spacing between elements (>2.5mm)
- [ ] No text or labels present
- [ ] No gradients or shading
- [ ] Essential elements preserved from source
- [ ] Unnecessary details removed

**If validation fails**:
- Adjust prompt (see `TactilePromptGuide.md` iteration tips)
- Try different model
- Regenerate

### Step 6: Post-Process (Optional)

If Braille labels needed:

```bash
tact image-to-piaf ~/Downloads/tactile-output.png \
  --detect-text \
  --braille-grade 2 \
  --verbose
```

Note: Since generated image has no text, this mainly formats for PIAF paper size.

### Step 7: Present Results

Report to user:

```
Generated tactile [drawing type] from your source image.

Simplifications made:
- Removed: [list omitted elements]
- Preserved: [list kept elements]
- Enhanced: [list improvements]

Output: ~/Downloads/tactile-output.png
[Stratified layers if applicable]

Would you like me to:
1. Add Braille labels to specific rooms?
2. Generate additional layers (structure, circulation)?
3. Adjust the simplification level?
4. Convert to PDF for PIAF printing?
```

## Stratification Workflow

When user requests stratification or analysis reveals multiple systems:

### Step 1: Identify Layers

Analyze source for separable systems:
- **Structure**: Walls, columns, cores
- **Circulation**: Doors, stairs, corridors
- **Program**: Room boundaries, zones
- **Systems**: MEP, furniture (usually omit)

### Step 2: Generate Each Layer

Create separate prompts for each layer (see `TactilePromptGuide.md` for templates).

Generate in sequence:
1. Structure layer first (provides context)
2. Circulation layer
3. Program layer

### Step 3: Package Output

Provide all layers:
```
Stratified tactile output:

1. Structure (tactile-structure.png)
   - Bearing walls, columns, building core

2. Circulation (tactile-circulation.png)
   - Doors, stairs, corridors

3. Program (tactile-program.png)
   - Room boundaries for Braille labeling

Each layer can be printed separately on PIAF paper.
Recommend starting with Structure for orientation,
then adding Circulation and Program as understanding builds.
```

## Error Handling

| Issue | Solution |
|-------|----------|
| Gray tones in output | Add "pure black and white, no gray" to prompt |
| Lines too thin | Add "bold, thick linework" |
| Too much detail | Add "simplified, essential elements only" |
| Missing key elements | Be more explicit in content description |
| API error | Try alternative model (GPT-Image-1) |
| Reference image not used | Verify model supports reference (Nano Banana Pro) |

## Example: Complex Floor Plan

**Source**: Dense architectural floor plan with furniture, dimensions, hatching, MEP

**Analysis**: Multiple systems, should stratify

**Strategy**: Generate 3 layers

**Structure Prompt**:
```
Structural floor plan showing only load-bearing elements, technical drawing style

Recreate from reference: exterior bearing walls as thick bold lines,
interior load-bearing partitions as medium lines, columns as filled circles.
Overall rectangular footprint approximately 60x40 feet.

Omit: furniture, dimensions, hatching, MEP, non-bearing partitions, doors, windows.

[TACTILE SUFFIX]
```

**Output**: Three PNG files ready for PIAF printing
