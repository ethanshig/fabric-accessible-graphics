# Radical Accessibility - PAI Pack Implementation Plan

**Version**: 3.0
**Date**: January 2026
**Status**: Ready for Implementation
**Context**: This plan is designed to be loaded as context in a new Claude Code session.

---

## Executive Summary

Restructure the existing `fabric-accessible-graphics` project into a PAI Pack called **Radical Accessibility**. The pack provides three distinct skills for making architectural graphics accessible to blind/low-vision users:

1. **TactileConversion** - Code-based image processing (existing Python library)
2. **TactileGeneration** - AI-powered image creation (new, overcomes source limitations)
3. **AccessibleDescription** - Arch-Alt-Text verbal descriptions (existing, enhanced)

---

## Part 1: Architecture Overview

### 1.1 Pack Structure

```
radical-accessibility/
├── README.md                    # Pack overview with YAML frontmatter
├── INSTALL.md                   # Wizard-style installation guide
├── VERIFY.md                    # Completion checklist
├── LICENSE
│
├── lib/
│   └── tactile-core/            # Python library (pip-installable)
│       ├── pyproject.toml       # Modern Python packaging
│       ├── README.md            # Standalone library docs
│       └── src/
│           └── tactile_core/    # Renamed from fabric_access
│               ├── __init__.py
│               ├── cli.py
│               ├── core/
│               │   ├── converter.py
│               │   ├── contrast.py
│               │   ├── braille_converter.py
│               │   ├── hybrid_text_detector.py
│               │   └── ...
│               └── config/
│                   ├── presets.py
│                   └── standards_loader.py
│
├── src/
│   ├── skills/
│   │   ├── TactileConversion/
│   │   │   ├── SKILL.md
│   │   │   └── Workflows/
│   │   │       └── ConvertImage.md
│   │   │
│   │   ├── TactileGeneration/
│   │   │   ├── SKILL.md
│   │   │   ├── TactileGuidelines.md
│   │   │   └── Workflows/
│   │   │       ├── GenerateFromImage.md
│   │   │       └── GenerateFromDescription.md
│   │   │
│   │   └── AccessibleDescription/
│   │       ├── SKILL.md
│   │       ├── ArchAltText.md
│   │       └── Workflows/
│   │           └── DescribeImage.md
│   │
│   ├── tools/
│   │   ├── TactileConvert.ts    # Calls Python library via CLI
│   │   └── TactileGenerate.ts   # Calls AI APIs (Gemini/Flux)
│   │
│   ├── hooks/
│   │   └── ImageDetector.ts     # Optional: proactive image detection
│   │
│   └── shared/
│       ├── TactileGuidelines.md
│       └── ArchitecturalContext.md
│
├── mcp/                          # MCP server (kept for non-PAI users)
│   ├── server.py
│   └── README.md
│
├── samples/                      # Test images
│   └── ...
│
└── docs/
    ├── TACTILE_STANDARDS.md
    └── DEVELOPMENT.md
```

### 1.2 Naming Decisions

| Old Name | New Name | Reason |
|----------|----------|--------|
| `fabric-accessible-graphics` | `radical-accessibility` | Reflects mission, not implementation |
| `fabric_access` (Python) | `tactile_core` | Descriptive of what it does |
| `fabric-access` (CLI) | `tactile` | Shorter, clearer |

### 1.3 Python Library Strategy

The Python library (`tactile-core`) is:
- Located at `lib/tactile-core/` within the pack
- Pip-installable: `pip install -e ./lib/tactile-core`
- Importable by future RhinoPython skills
- Provides both Python API and CLI (`tactile` command)

---

## Part 2: Skill Specifications

### 2.1 TactileConversion Skill

**Purpose**: Process existing images into tactile-ready PDFs using code-based algorithms.

**When to Use**:
- Source image is clean and high-contrast
- Quick processing needed
- No AI API required
- Exact preservation of source matters

**Limitations**: Output quality limited by source quality.

**SKILL.md Frontmatter**:
```yaml
---
name: TactileConversion
description: Convert images to tactile-ready PDFs for PIAF printing
triggers:
  - convert to tactile
  - make tactile version
  - PIAF conversion
  - convert for printing
context: fork
---
```

**Workflow**: `ConvertImage.md`
1. Analyze source image (type detection, quality assessment)
2. Select appropriate preset (floor_plan, section, sketch, etc.)
3. Call `tactile` CLI with appropriate flags
4. Validate output (density check, dimensions)
5. Present results with options for refinement

### 2.2 TactileGeneration Skill

**Purpose**: Create NEW tactile images using AI, overcoming source image limitations.

**When to Use**:
- Source image is cluttered, low-contrast, or complex
- Simplification/stratification needed
- Creating from description (no source image)
- Source has overlapping systems that need separation

**Advantage**: AI can interpret and recreate, not just process.

**SKILL.md Frontmatter**:
```yaml
---
name: TactileGeneration
description: Generate tactile graphics using AI image generation
triggers:
  - generate tactile
  - create tactile image
  - simplify for tactile
  - stratify this drawing
  - tactile version of [building name]
context: fork
---
```

**Workflows**:

`GenerateFromImage.md`:
1. Analyze source with Claude vision (identify elements, systems, complexity)
2. Propose stratification if multiple systems detected
3. Construct tactile-optimized prompt with guidelines
4. Call AI generation (Gemini Imagen / Flux)
5. Post-process through tactile-core for Braille labels
6. Validate and present results

`GenerateFromDescription.md`:
1. Clarify requirements (building, drawing type, focus)
2. Research if specific building (use Research skill)
3. Construct generation prompt with architectural accuracy
4. Generate and validate
5. Post-process for Braille

**AI Generation Prompt Suffix** (always appended):
```
Technical requirements for tactile output:
- Pure black lines on pure white background
- Minimum 2.5mm spacing between all distinct elements
- Bold solid lines, no fine details smaller than 1.5mm
- No gray tones, gradients, or shading
- No text or labels (Braille added separately)
- Consistent line weights throughout
- High contrast suitable for PIAF swell paper printing
```

### 2.3 AccessibleDescription Skill

**Purpose**: Generate rich verbal descriptions of architectural images.

**When to Use**:
- Quick understanding without PIAF printing
- Supplementing tactile graphics with context
- Images that don't translate well to tactile
- Remote situations without PIAF access

**SKILL.md Frontmatter**:
```yaml
---
name: AccessibleDescription
description: Generate detailed accessibility descriptions of architectural images
triggers:
  - describe this image
  - what does this show
  - explain this drawing
  - accessibility description
context: fork
---
```

**Workflow**: `DescribeImage.md`
1. Load Arch-Alt-Text framework
2. Analyze image with Claude vision
3. Generate three-layer description:
   - **Macro**: Medium, subject, purpose (3 sentences)
   - **Meso**: Composition, materials, orientation, scale (4+ sentences)
   - **Micro**: Details, textures, dimensions, analogies (8+ sentences)
4. Offer follow-up options (more detail, tactile conversion, concept explanation)

---

## Part 3: Implementation Phases

### Phase 1: Repository Restructure (Foundation)

**Goal**: Reorganize files without breaking existing functionality.

**Tasks**:
- [ ] Create new directory structure per Section 1.1
- [ ] Move Python library to `lib/tactile-core/`
- [ ] Rename `fabric_access` to `tactile_core` (update all imports)
- [ ] Update `pyproject.toml` with new name and metadata
- [ ] Rename CLI from `fabric-access` to `tactile`
- [ ] Update all internal references
- [ ] Verify `pip install -e ./lib/tactile-core` works
- [ ] Verify `tactile --version` works
- [ ] Move samples, docs to new locations
- [ ] Update MCP server to use new library name

**Validation**:
```bash
cd radical-accessibility
pip install -e ./lib/tactile-core
tactile --version
tactile image-to-piaf samples/test.jpg --verbose
```

### Phase 2: Pack Scaffolding

**Goal**: Create PAI Pack structure with README, INSTALL, VERIFY.

**Tasks**:
- [ ] Write `README.md` with YAML frontmatter (see template below)
- [ ] Write `INSTALL.md` wizard-style installation guide
- [ ] Write `VERIFY.md` completion checklist
- [ ] Create `src/skills/` directory structure
- [ ] Create `src/tools/` directory structure
- [ ] Create `src/shared/` with guideline documents

**README.md Template**:
```yaml
---
name: Radical Accessibility
pack-id: ethanshig-radical-accessibility-v1.0.0
version: 1.0.0
author: ethanshig
description: Accessible architectural graphics for blind/low-vision students
type: skill-bundle
purpose-type: [accessibility, architecture, tactile-graphics, education]
platform: claude-code
dependencies: [pai-core-install, python3.10+, bun]
keywords: [accessibility, tactile, PIAF, braille, architecture, blind]
---
```

### Phase 3: TactileConversion Skill

**Goal**: Implement first skill wrapping existing Python library.

**Tasks**:
- [ ] Write `TactileConversion/SKILL.md`
- [ ] Write `Workflows/ConvertImage.md`
- [ ] Create `tools/TactileConvert.ts` (TypeScript wrapper)
- [ ] Test skill triggers in PAI
- [ ] Validate end-to-end workflow

**TactileConvert.ts Pseudocode**:
```typescript
#!/usr/bin/env bun
// Wrapper for tactile-core Python library

import { $ } from "bun";

const args = process.argv.slice(2);
const imagePath = args[0];
const options = parseOptions(args.slice(1));

// Build CLI command
const cmd = [
  "tactile", "image-to-piaf", imagePath,
  "--preset", options.preset || "floor_plan",
  options.detectText ? "--detect-text" : "",
  options.brailleGrade ? `--braille-grade ${options.brailleGrade}` : "",
  "--verbose"
].filter(Boolean).join(" ");

// Execute and stream output
const result = await $`${cmd}`;
console.log(result.stdout.toString());
```

### Phase 4: AccessibleDescription Skill

**Goal**: Implement description skill using Claude vision.

**Tasks**:
- [ ] Write `AccessibleDescription/SKILL.md`
- [ ] Write `ArchAltText.md` framework document
- [ ] Write `Workflows/DescribeImage.md`
- [ ] Test with various image types
- [ ] Refine description format based on feedback

### Phase 5: TactileGeneration Skill

**Goal**: Implement AI generation skill (requires API setup).

**Prerequisites**:
- Gemini API key configured
- Image generation model access (Imagen 3 or Flux)

**Tasks**:
- [ ] Write `TactileGeneration/SKILL.md`
- [ ] Write `TactileGuidelines.md` (shared)
- [ ] Write `Workflows/GenerateFromImage.md`
- [ ] Write `Workflows/GenerateFromDescription.md`
- [ ] Create `tools/TactileGenerate.ts`
- [ ] Implement stratification logic
- [ ] Test with complex multi-system drawings
- [ ] Integrate with tactile-core for post-processing

**AI Integration Options**:
1. **Gemini Imagen 3** via API
2. **Flux** via Replicate or local
3. **GPT-Image-1** via OpenAI API
4. **Nano Banana Pro MCP** (already configured)

### Phase 6: Optional Enhancements

**ImageDetector Hook**:
- Proactively detect images in conversation
- Offer tactile conversion when architectural images detected
- Log detections to memory for learning

**Memory Integration**:
- Track successful conversions by image type
- Learn preferred settings
- Capture student feedback

---

## Part 4: File Templates

### 4.1 TactileConversion/SKILL.md

```markdown
---
name: TactileConversion
description: Convert images to tactile-ready PDFs for PIAF printing
triggers:
  - convert to tactile
  - make tactile version
  - PIAF conversion
  - convert for printing
  - tactile PDF
context: fork
---

# TactileConversion

**Auto-loads when**: User wants to convert an existing image to tactile format for PIAF printing.

## When to Use This Skill

- Source image is already clean and high-contrast
- Quick processing without AI generation needed
- Exact preservation of source content matters
- No API calls required (works offline)

## When NOT to Use (Use TactileGeneration Instead)

- Source is cluttered or low-contrast
- Image has overlapping systems needing separation
- Simplification or reinterpretation needed
- Creating from description (no source image)

## Workflow

Execute: `Workflows/ConvertImage.md`

## Available Presets

| Preset | Best For |
|--------|----------|
| floor_plan | Architectural floor plans |
| section | Building sections |
| elevation | Building elevations |
| site_plan | Site and landscape plans |
| sketch | Hand-drawn sketches |
| diagram | Diagrams and charts |
| technical_drawing | CAD drawings |

## Tool

Uses: `tools/TactileConvert.ts` → `tactile` CLI → `tactile-core` library
```

### 4.2 TactileGeneration/SKILL.md

```markdown
---
name: TactileGeneration
description: Generate tactile graphics using AI image generation
triggers:
  - generate tactile
  - create tactile image
  - simplify for tactile
  - stratify drawing
  - tactile of [building]
context: fork
---

# TactileGeneration

**Auto-loads when**: User needs AI-powered tactile image creation, especially for complex or poor-quality sources.

## When to Use This Skill

- Source image is cluttered, low-contrast, or complex
- Multiple overlapping systems need stratification
- Simplification or reinterpretation needed
- Creating from description (no source image)
- Generating precedent study diagrams

## When NOT to Use (Use TactileConversion Instead)

- Source is already clean and high-contrast
- Quick processing needed without AI
- Exact source preservation required

## Context Files

Load before executing:
- `TactileGuidelines.md` - Tactile design rules
- `../shared/ArchitecturalContext.md` - Architecture knowledge

## Workflows

| Trigger | Workflow |
|---------|----------|
| Has source image | `Workflows/GenerateFromImage.md` |
| No source, description only | `Workflows/GenerateFromDescription.md` |

## Stratification

When an image contains multiple systems (structure, circulation, program, MEP), offer to stratify into separate layers/pages for clarity.

## Tool

Uses: `tools/TactileGenerate.ts` → AI API (Gemini/Flux) → post-process with `tactile-core`
```

### 4.3 AccessibleDescription/SKILL.md

```markdown
---
name: AccessibleDescription
description: Generate detailed accessibility descriptions of architectural images
triggers:
  - describe image
  - what does this show
  - explain drawing
  - accessibility description
context: fork
---

# AccessibleDescription

**Auto-loads when**: User needs a verbal/text description of an architectural image.

## When to Use This Skill

- Quick understanding without PIAF printing
- Supplementing tactile graphics with verbal context
- Images that don't translate well to tactile
- Remote/mobile situations without PIAF access
- Initial exploration before deciding on tactile conversion

## Context Files

Load before executing:
- `ArchAltText.md` - Description framework

## Workflow

Execute: `Workflows/DescribeImage.md`

## Output Format

Descriptions follow three layers:
1. **Macro** (Overview): Medium, subject, purpose - 3 sentences
2. **Meso** (Composition): Layout, relationships, orientation, scale - 4+ sentences
3. **Micro** (Details): Specific elements, dimensions, materials, analogies - 8+ sentences

## Follow-up Options

After description, offer:
- Describe specific area in more detail
- Generate tactile version (invoke TactileGeneration)
- Explain architectural concepts shown
```

---

## Part 5: Validation Checklist

### Repository Restructure Complete
- [ ] New directory structure in place
- [ ] Python library renamed and pip-installable
- [ ] CLI renamed and functional
- [ ] All imports updated
- [ ] MCP server updated (if keeping)

### Pack Structure Complete
- [ ] README.md with proper frontmatter
- [ ] INSTALL.md wizard-style guide
- [ ] VERIFY.md checklist
- [ ] All skill directories created

### TactileConversion Skill Working
- [ ] SKILL.md triggers correctly
- [ ] Workflow executes end-to-end
- [ ] Tool wrapper calls Python library
- [ ] Output PDF is valid for PIAF

### AccessibleDescription Skill Working
- [ ] SKILL.md triggers correctly
- [ ] Arch-Alt-Text format followed
- [ ] Three-layer descriptions generated
- [ ] Follow-up options presented

### TactileGeneration Skill Working
- [ ] SKILL.md triggers correctly
- [ ] AI generation produces tactile-ready output
- [ ] Stratification logic works
- [ ] Post-processing with tactile-core works
- [ ] GenerateFromDescription works without source

---

## Part 6: Session Context

**When starting a new session to implement this plan:**

1. Load this document as context
2. State current phase (1-6)
3. Reference specific tasks within phase
4. The implementing agent should:
   - Read this plan first
   - Check current file state
   - Execute tasks in order
   - Validate after each phase

**Example session start:**
```
Load context: /path/to/IMPLEMENTATION_PLAN_V3.md
Current phase: Phase 1 (Repository Restructure)
Starting task: Create new directory structure
```

---

## Appendix A: MCP Server Decision

**Keep the MCP server** in `mcp/` directory because:
- Serves non-PAI Claude Code users
- Already works and is tested
- Provides alternative interface
- Can be deprecated later if desired

Update MCP to use renamed library (`tactile_core` instead of `fabric_access`).

---

## Appendix B: Future RhinoPython Integration

When creating RhinoPython skills later, they can import the tactile library:

```python
# In a future RhinoPython skill
import sys
sys.path.append("/path/to/radical-accessibility/lib/tactile-core/src")
from tactile_core import ImageProcessor, PIAFPDFGenerator

# Or if pip-installed in Rhino's Python environment
from tactile_core import ImageProcessor
```

---

*End of Implementation Plan v3.0*
