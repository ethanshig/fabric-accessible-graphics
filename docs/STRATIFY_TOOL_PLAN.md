# Stratify Image Tool - Implementation Plan

## Overview

The `stratify_image` tool separates complex, multi-layered architectural drawings into individual tactile-friendly pages. Each layer focuses on a specific category of information (e.g., circulation, structure, water features), making dense drawings accessible for PIAF printing.

**Example**: A California site map with roads, railroads, and aqueducts becomes three separate tactile pages - one for each system - with Braille labels and optimized patterns.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     stratify_image MCP Tool                      │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: Analysis & Proposal                                    │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │ Load Image  │───▶│ Claude Analysis  │───▶│ Propose Layers │ │
│  └─────────────┘    │ (semantic review)│    │ (text descrip) │ │
│                     └──────────────────┘    └────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Phase 2: User Confirmation                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ User approves/modifies proposed stratification              ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Phase 3: Layer Generation (via Nano Banana Pro)                 │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │ Original    │───▶│ Gemini generates │───▶│ Isolated layer │ │
│  │ Image       │    │ each layer       │    │ images         │ │
│  └─────────────┘    └──────────────────┘    └────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Phase 4: PIAF Processing (existing code)                        │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │ Layer image │───▶│ image_to_piaf    │───▶│ Multi-page PDF │ │
│  │             │    │ (threshold,      │    │ with Braille,  │ │
│  │             │    │  Braille, etc.)  │    │ keys, reg marks│ │
│  └─────────────┘    └──────────────────┘    └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Setup Requirements

### 1. Gemini API Key Security

**CRITICAL**: The API key must never be committed to GitHub.

#### Protection Methods:

```bash
# Option A: Environment variable (recommended)
export GEMINI_API_KEY="your-key-here"

# Option B: .env file in home directory
echo "GEMINI_API_KEY=your-key-here" >> ~/.gemini/.env

# Option C: Claude Code MCP config (stored in user settings)
claude mcp add nano-banana-pro -s user -- env GEMINI_API_KEY=$GEMINI_API_KEY npx @rafarafarafa/nano-banana-pro-mcp
```

#### .gitignore additions:
```gitignore
# API Keys - NEVER commit
.env
.env.*
*.env
.gemini/
secrets/
**/credentials*.json
```

#### Pre-commit hook (optional but recommended):
```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached | grep -iE "(api[_-]?key|secret|password|credential)" | grep -v "\.gitignore"; then
    echo "WARNING: Possible API key detected in commit!"
    exit 1
fi
```

### 2. Gemini CLI Installation

```bash
# Install Gemini CLI globally
npm install -g @google/gemini-cli

# Authenticate (browser-based, recommended)
gemini
# Select "Login with Google" when prompted

# OR use API key
export GEMINI_API_KEY="your-key-here"
gemini
```

**Free tier limits**: 60 requests/minute, 1,000 requests/day

### 3. Nano Banana Pro MCP Server

```bash
# Add to Claude Code
claude mcp add nano-banana-pro -s user -- env GEMINI_API_KEY=$GEMINI_API_KEY npx @rafarafarafa/nano-banana-pro-mcp

# Verify installation
claude mcp list
```

---

## Tool Specification

### Tool Name
`stratify_image`

### Parameters

```python
async def stratify_image(
    image_path: str,                    # Required: Path to source image
    output_path: str = None,            # Optional: Output PDF path

    # Layer specification (Phase 1 - user-specified)
    layers: list[str] = None,           # Optional: User-defined layer names
                                        # e.g., ["Roads", "Water features", "Buildings"]

    # AI assistance
    auto_analyze: bool = True,          # Let AI propose stratification

    # Output options
    paper_size: str = "letter",         # "letter" or "tabloid"
    max_layers: int = 5,                # Maximum layers to generate (aim for 2-3)

    # PIAF processing options (passed to image_to_piaf)
    braille_grade: int = 2,             # 1 or 2 (Grade 2 recommended)
    auto_scale: bool = True,            # Auto-scale for Braille fitting
    use_abbreviation_key: bool = True,  # Generate abbreviation key page

    # Generation options
    generation_backend: str = "nano-banana-pro",  # or "gemini-cli"
    preserve_proportions: bool = True,  # Maintain original layout
    optimize_tactile: bool = True,      # Allow AI to recompose for clarity
) -> dict:
```

### Return Value

```python
{
    "status": "success" | "awaiting_confirmation" | "error",

    # Phase 1 response (awaiting_confirmation)
    "proposed_layers": [
        {
            "name": "Transportation Infrastructure",
            "description": "Roads, highways, and railroad lines",
            "estimated_elements": ["Highway 99", "Railroad tracks", "Local roads"],
            "page_order": 1
        },
        # ... more layers
    ],
    "requires_confirmation": True,
    "instructions": "Review proposed layers and call again with confirmed layers",

    # Phase 3 response (success)
    "output_path": "/path/to/stratified_output.pdf",
    "pages_generated": 3,
    "layers": [
        {"name": "Transportation", "page": 1, "element_count": 12},
        {"name": "Water Systems", "page": 2, "element_count": 8},
        {"name": "Topography", "page": 3, "element_count": 5}
    ],
    "key_page_included": True,
    "total_braille_labels": 25,
    "warnings": []
}
```

---

## Workflow Phases

### Phase 1: Analysis & Proposal

When user calls `stratify_image(image_path, auto_analyze=True)`:

1. **Load and validate image**
2. **Claude analyzes image semantically**:
   - Identify distinct information categories
   - Count approximate elements per category
   - Assess separability (can layers be cleanly isolated?)
   - Check if stratification is beneficial (vs. single-page output)
3. **Return proposed stratification** as text descriptions
4. **Set status to "awaiting_confirmation"**

Example response:
```
I've analyzed this California site map and identified 3 distinct layers:

1. **Transportation Infrastructure** (Page 1)
   - Highway 99 and connecting roads
   - Railroad tracks running north-south
   - Approximately 15 labeled routes

2. **Water Systems** (Page 2)
   - California Aqueduct
   - Delta-Mendota Canal
   - Rivers and natural waterways
   - Approximately 8 labeled features

3. **Agricultural Regions** (Page 3)
   - Farm boundaries
   - Irrigation districts
   - Crop type indicators
   - Approximately 10 labeled areas

Would you like me to proceed with this stratification, or would you like to modify it?
```

### Phase 2: User Confirmation

User reviews and either:
- **Approves**: Calls `stratify_image(image_path, layers=["Transportation", "Water Systems", "Agriculture"])`
- **Modifies**: Specifies different layers or combines some
- **Rejects**: Suggests using regular `image_to_piaf` instead

### Phase 3: Layer Generation

For each confirmed layer:

1. **Construct Gemini prompt**:
   ```
   Original image attached. Generate a clean, high-contrast black and white
   drawing containing ONLY the following elements from this image:

   Layer: "Water Systems"
   Include: California Aqueduct, Delta-Mendota Canal, rivers, waterways
   Exclude: Roads, buildings, text labels (will be added separately)

   Requirements:
   - Maintain exact proportions and positions from original
   - Use bold, solid lines (minimum 2.5mm spacing between elements)
   - Pure black lines on white background
   - No gray tones or gradients
   - Simplify complex details while preserving essential information
   ```

2. **Send to Nano Banana Pro** (via MCP or Gemini CLI)
3. **Receive generated layer image**
4. **Validate output** (check dimensions, content)

### Phase 4: PIAF Processing

For each generated layer image:

1. **Call existing `image_to_piaf` internally**:
   ```python
   await image_to_piaf(
       image_path=layer_image_path,
       preset="floor_plan",  # or appropriate preset
       detect_text=True,
       braille_grade=2,
       auto_scale=True,
       use_abbreviation_key=True,
       # ... other params
   )
   ```

2. **Collect processed pages**

3. **Combine into multi-page PDF**:
   - Page 1: Layer 1 (title at top)
   - Page 2: Layer 2 (title at top)
   - Page N: Layer N
   - Final page: Shared abbreviation key/legend

4. **Add registration marks** to each page (bottom-right corner)

---

## Tactile Guidelines Integration

Based on [heardutchhere.net guidelines](https://www.heardutchhere.net/grbl/grbl3.html):

### Spacing & Sizing
- **Minimum 2.5mm** between distinguishable elements
- **Draw as large as possible** within paper constraints
- Design within Braille cell-sized perception window

### Line Quality
- Bold, solid lines with strong contrast
- Varying line weights (thick vs thin)
- No similar-density hatchings
- No gray tones

### Content Strategy
- Simplify to essential elements only
- Remove competing text/keys from graphic area
- Consistent symbol vocabulary across layers
- Maintain symbol consistency across entire output

### Prompt Engineering for Gemini
Include these requirements in every generation prompt:
```
Tactile requirements:
- Minimum 2.5mm spacing between all elements
- Bold solid lines, no fine details under 1.5mm
- Pure black on white, no gray tones
- Simplify hatching patterns to distinct textures
- Remove text (will be added as Braille separately)
- Maintain consistent line weights: walls=3px, details=2px
```

---

## File Structure

```
src/tactile_core/
├── core/
│   └── stratifier.py          # NEW: Stratification logic
├── mcp_server/
│   └── tools.py               # ADD: stratify_image function
└── integrations/
    └── gemini.py              # NEW: Gemini/Nano Banana integration
```

### New Files

#### `src/tactile_core/core/stratifier.py`
- `LayerProposal` dataclass
- `StratificationAnalyzer` class (Claude-based analysis)
- `LayerGenerator` class (Gemini integration)
- `StratifiedOutputBuilder` class (combines layers into PDF)

#### `src/tactile_core/integrations/gemini.py`
- `GeminiClient` class (abstraction over MCP/CLI)
- `NanoBananaGenerator` class (image generation)
- Prompt templates for layer generation
- Response parsing and validation

---

## Implementation Phases

### Phase 1: Foundation (User-Specified Layers)
- [ ] Create `stratifier.py` with basic structure
- [ ] Implement `gemini.py` integration layer
- [ ] Add `stratify_image` to MCP tools
- [ ] Support user-specified layer names
- [ ] Manual layer isolation via Gemini prompts
- [ ] Multi-page PDF assembly
- [ ] Registration marks on each page

### Phase 2: AI-Assisted Analysis
- [ ] Claude semantic analysis of source image
- [ ] Layer proposal generation (text descriptions)
- [ ] Confirmation workflow (awaiting_confirmation status)
- [ ] Layer count optimization (aim for 2-3)
- [ ] "Cannot stratify" detection with fallback suggestion

### Phase 3: Advanced Generation
- [ ] Refined Gemini prompts with tactile guidelines
- [ ] Quality validation of generated layers
- [ ] Iterative refinement if generation fails
- [ ] Support for both Nano Banana Pro and Gemini CLI
- [ ] Tactile clarity optimization (allow AI recomposition)

### Phase 4: Polish & Testing
- [ ] Edge case handling
- [ ] Error messages and recovery
- [ ] Performance optimization
- [ ] Documentation
- [ ] User testing with actual architectural drawings

---

## Example Usage

### Basic (User-Specified Layers)
```
User: Stratify this site plan into roads, buildings, and landscape

Claude: I'll stratify the image into 3 layers. Let me generate each one...

[Calls stratify_image with layers=["Roads", "Buildings", "Landscape"]]

Result: 4-page PDF created:
- Page 1: "Roads" - highways, streets, paths
- Page 2: "Buildings" - structures, footprints
- Page 3: "Landscape" - trees, water, terrain
- Page 4: Abbreviation key
```

### AI-Assisted Analysis
```
User: Please stratify this floor plan

Claude: Let me analyze this drawing to propose a stratification...

[Calls stratify_image with auto_analyze=True]

I've identified 3 potential layers in this floor plan:

1. **Structural Elements** - Walls, columns, stairs
2. **MEP Systems** - Ductwork, plumbing lines, electrical
3. **Furniture & Equipment** - Desks, fixtures, appliances

Would you like me to proceed with this stratification, or would you
prefer different groupings?

User: Combine furniture with structural, and split MEP into mechanical
and electrical

Claude: Got it. I'll create 3 layers: Structure+Furniture, Mechanical,
Electrical...

[Proceeds with modified layers]
```

### Fallback to Regular Processing
```
User: Stratify this simple diagram

Claude: [After analysis] This diagram shows a single system (electrical
circuit) without distinct separable layers. I recommend using the
regular image_to_piaf tool for this - would you like me to do that
instead?
```

---

## Testing Checklist

- [ ] Single-layer fallback works correctly
- [ ] 2-3 layer stratification produces clear output
- [ ] 5-layer maximum is enforced
- [ ] Registration marks align across pages
- [ ] Braille labels appear on correct layers
- [ ] Shared key page includes all abbreviations
- [ ] Gemini generation produces tactile-appropriate output
- [ ] Error handling for Gemini failures
- [ ] API key is never exposed in logs/output

---

## Open Questions

1. **Gemini rate limiting**: How to handle 60 req/min limit with multiple layers?
   - Proposal: Sequential generation with progress updates

2. **Generation quality validation**: How to detect if Gemini output is unusable?
   - Proposal: Check for minimum black pixel density, proper dimensions

3. **Layer overlap handling**: When same element should appear in multiple layers?
   - Proposal: Include in both as specified, note in output metadata

4. **Caching**: Should we cache Gemini responses for iterative refinement?
   - Proposal: Yes, similar to existing Tesseract cache

---

## Security Checklist

- [ ] API key loaded from environment variable only
- [ ] .gitignore updated with all key-related patterns
- [ ] No API key in error messages or logs
- [ ] Pre-commit hook recommended in setup docs
- [ ] MCP config uses `-s user` (user scope, not project)
