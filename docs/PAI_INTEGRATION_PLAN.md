# Accessible Architecture Infrastructure (AAI)
# PAI Bundle Integration Plan

**Version**: 2.0 Draft
**Date**: January 2026
**Status**: Planning/Review
**Parent Project**: Radical Accessibility

---

## Executive Summary

This document outlines the **Accessible Architecture Infrastructure (AAI)**—a PAI Bundle designed for blind/low-vision architecture students. AAI provides an AI-powered infrastructure for receiving, understanding, and eventually creating architectural information through non-visual means.

**Core Vision**: An infrastructure that enables blind/low-vision architecture students to practice and learn architecture with full access to visual information—starting with tools for receiving architectural content, and expanding to creation tools in the future.

### Bundle Structure

```
Radical Accessibility (umbrella organization)
└── Accessible Architecture Infrastructure (AAI) [Bundle]
    ├── aai-tactile-graphics [Pack]
    │   └── Workflows: GenerateFromImage, GenerateFromDescription, ConvertOnly
    ├── aai-image-description [Pack]
    │   └── Workflows: DescribeImage
    └── (future packs: 3D models, audio, course materials, etc.)
```

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Repository Structure](#2-repository-structure)
3. [Bundle Specification](#3-bundle-specification)
4. [Pack: aai-tactile-graphics](#4-pack-aai-tactile-graphics)
5. [Pack: aai-image-description](#5-pack-aai-image-description)
6. [Shared Components](#6-shared-components)
7. [TELOS Integration](#7-telos-integration)
8. [Hook System](#8-hook-system)
9. [Memory System](#9-memory-system)
10. [Gemini/Nano Banana Integration](#10-gemininano-banana-integration)
11. [tactile-conversion Library](#11-tactile-conversion-library)
12. [Implementation Phases](#12-implementation-phases)
13. [Testing Strategy](#13-testing-strategy)
14. [Open Questions](#14-open-questions)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ACCESSIBLE ARCHITECTURE INFRASTRUCTURE                    │
│                         (PAI Bundle for Architecture Students)               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────────────────────┐  │
│  │    TELOS     │     │              PACKS                               │  │
│  │ (Accessibility│     │                                                  │  │
│  │   Centered)  │     │  ┌─────────────────────────────────────────────┐ │  │
│  │              │     │  │  aai-tactile-graphics                       │ │  │
│  │  MISSION     │     │  │  ├─ GenerateFromImage (AI, primary)         │ │  │
│  │  GOALS       │◄────┤  │  ├─ GenerateFromDescription (AI)            │ │  │
│  │  BELIEFS     │     │  │  └─ ConvertOnly (code-based fallback)       │ │  │
│  │  STRATEGIES  │     │  └─────────────────────────────────────────────┘ │  │
│  │  ...         │     │                                                  │  │
│  └──────────────┘     │  ┌─────────────────────────────────────────────┐ │  │
│                       │  │  aai-image-description                      │ │  │
│                       │  │  └─ DescribeImage (Arch-Alt-Text)           │ │  │
│                       │  └─────────────────────────────────────────────┘ │  │
│                       │                                                  │  │
│                       │  ┌─────────────────────────────────────────────┐ │  │
│                       │  │  (PAI Core Skills: Research, TELOS, etc.)   │ │  │
│                       │  └─────────────────────────────────────────────┘ │  │
│                       └──────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────────────────────┐  │
│  │    HOOKS     │     │              MEMORY                              │  │
│  │              │     │  ┌────────────────────────────────────────────┐  │  │
│  │  ImageDetect │     │  │  LEARNING/AAI/                             │  │  │
│  │  (proactive) │◄────┤  │  ├─ image_type_preferences.jsonl           │  │  │
│  │              │     │  │  ├─ successful_generations.jsonl           │  │  │
│  │              │     │  │  ├─ student_feedback.jsonl                 │  │  │
│  │              │     │  │  └─ guidelines_refinements.md              │  │  │
│  └──────────────┘     │  └────────────────────────────────────────────┘  │  │
│                       └──────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    EXTERNAL INTEGRATIONS                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   Gemini    │  │  tactile-   │  │   Canvas    │  │    PIAF     │  │   │
│  │  │ Nano Banana │  │  conversion │  │    LMS      │  │   Printer   │  │   │
│  │  │ (generate)  │  │  (fallback) │  │  (future)   │  │  (output)   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Design Principles

1. **Generation-First**: AI-generated tactile images are the primary approach; code-based conversion (`tactile-conversion`) is a fallback
2. **Proactive Assistance**: PAI detects images and offers tactile conversion without explicit requests
3. **Dialogue-Driven Refinement**: When uncertain about what information matters, PAI consults the student
4. **Memory by Image Type**: System learns preferred settings for floor plans vs. sections vs. diagrams
5. **Modular Packs**: Each capability is a separate pack that can be installed independently
6. **Accessibility Throughout**: Every interaction designed for screen-reader compatibility

### 1.3 Naming Conventions

| Component | Naming Pattern | Example |
|-----------|---------------|---------|
| Bundle | Title Case | Accessible Architecture Infrastructure |
| Packs | aai-kebab-case | aai-tactile-graphics |
| Skills | TitleCase | TactileGraphics |
| Workflows | TitleCase.md | GenerateFromImage.md |
| Tools | TitleCase.ts | GeminiGenerate.ts |
| Hooks | TitleCase.hook.ts | ImageDetector.hook.ts |
| Python lib | kebab-case | tactile-conversion |

---

## 2. Repository Structure

The AAI bundle lives in a single repository, restructured from the original fabric-accessible-graphics project.

```
accessible-architecture-infrastructure/          # Repository root
├── README.md                                   # Bundle overview (displays on GitHub)
├── INSTALL.md                                  # Bundle installation guide
├── LICENSE
│
├── lib/
│   └── tactile-conversion/                     # Python library (standalone installable)
│       ├── README.md                           # Standalone usage docs
│       ├── pyproject.toml                      # pip installable
│       ├── src/
│       │   └── tactile_conversion/             # Python package
│       │       ├── __init__.py
│       │       ├── cli.py                      # CLI entry point
│       │       ├── processor.py                # Image processing
│       │       ├── pdf_generator.py            # PIAF PDF output
│       │       ├── braille_converter.py        # Braille conversion
│       │       ├── text_detector.py            # OCR integration
│       │       ├── contrast.py                 # Enhancement methods
│       │       ├── tiler.py                    # Multi-page tiling
│       │       └── config/
│       │           ├── presets.yaml
│       │           └── tactile_standards.yaml
│       └── tests/
│
├── aai-tactile-graphics/                       # Pack 1
│   ├── README.md                               # Pack overview
│   ├── INSTALL.md                              # Pack installation
│   ├── VERIFY.md                               # Verification checklist
│   └── src/
│       ├── skills/
│       │   └── TactileGraphics/
│       │       ├── SKILL.md                    # Skill routing
│       │       ├── TactileGuidelines.md        # Tactile design rules
│       │       ├── ArchitecturalContext.md     # Architecture knowledge
│       │       └── Workflows/
│       │           ├── GenerateFromImage.md    # AI generation from image
│       │           ├── GenerateFromDescription.md  # AI generation from text
│       │           └── ConvertOnly.md          # Code-based fallback
│       ├── hooks/
│       │   └── ImageDetector.hook.ts           # Proactive detection
│       └── tools/
│           ├── GeminiGenerate.ts               # AI image generation
│           ├── TactileConvert.ts               # Wrapper for tactile-conversion
│           └── GuidelinesCheck.ts              # Validation tool
│
├── aai-image-description/                      # Pack 2
│   ├── README.md
│   ├── INSTALL.md
│   ├── VERIFY.md
│   └── src/
│       └── skills/
│           └── ImageDescription/
│               ├── SKILL.md
│               ├── ArchAltText.md              # Description framework
│               └── Workflows/
│                   └── DescribeImage.md
│
├── shared/                                     # Shared resources
│   ├── TactileGuidelines.md                    # Master guidelines (copied to packs)
│   └── ArchitecturalContext.md                 # Master context (copied to packs)
│
└── docs/
    ├── PAI_INTEGRATION_PLAN.md                 # This document
    ├── TACTILE_STANDARDS.md                    # Full standards reference
    └── DEVELOPMENT.md                          # Development guide
```

### 2.1 Installation Paths

When installed via PAI, files are placed in:

```
~/.claude/                                      # PAI_DIR
├── skills/
│   ├── TactileGraphics/                        # From aai-tactile-graphics
│   │   ├── SKILL.md
│   │   ├── TactileGuidelines.md
│   │   ├── ArchitecturalContext.md
│   │   └── Workflows/
│   │       ├── GenerateFromImage.md
│   │       ├── GenerateFromDescription.md
│   │       └── ConvertOnly.md
│   └── ImageDescription/                       # From aai-image-description
│       ├── SKILL.md
│       ├── ArchAltText.md
│       └── Workflows/
│           └── DescribeImage.md
├── hooks/
│   └── ImageDetector.hook.ts                   # From aai-tactile-graphics
├── tools/
│   ├── GeminiGenerate.ts
│   ├── TactileConvert.ts
│   └── GuidelinesCheck.ts
└── MEMORY/
    └── LEARNING/
        └── AAI/                                # Shared memory for bundle
```

---

## 3. Bundle Specification

### 3.1 Bundle README.md

```markdown
# Accessible Architecture Infrastructure (AAI)

A PAI Bundle for blind/low-vision architecture students.

## Purpose

AAI provides an AI-powered infrastructure for architecture students to receive,
understand, and work with visual architectural information through non-visual means.

## Philosophy

Architecture is fundamentally about space, not just visual appearance. AAI enables
spatial understanding through multiple senses—tactile graphics, detailed descriptions,
and (in future) 3D models and audio representations.

## Packs Included

| Pack | Purpose | Install Order |
|------|---------|---------------|
| aai-tactile-graphics | Generate tactile-ready images for PIAF printing | 1 |
| aai-image-description | Create detailed accessibility descriptions | 2 |

## Dependencies

- PAI Core (pai-core-install)
- Python 3.10+ with pip (for tactile-conversion library)
- Gemini API key (for AI generation)

## Installation

See [INSTALL.md](./INSTALL.md) for step-by-step installation.

## Pack Relationships

```
aai-tactile-graphics
├── Uses: tactile-conversion (Python library)
├── Uses: Gemini/Nano Banana (AI generation)
├── Integrates with: PAI Research skill (for precedent studies)
└── Shares: TactileGuidelines.md, ArchitecturalContext.md

aai-image-description
├── Uses: Claude vision (image analysis)
├── Uses: Arch-Alt-Text framework
└── Shares: ArchitecturalContext.md
```

## What You Get

After installation:
- Proactive image detection with PIAF conversion offers
- AI-powered tactile image generation
- Code-based conversion fallback
- Detailed architectural image descriptions
- Memory system that learns your preferences
```

### 3.2 Bundle INSTALL.md

```markdown
# AAI Bundle Installation

## Prerequisites

Before installing AAI, ensure you have:
- [ ] PAI Core installed (`pai-core-install`)
- [ ] Python 3.10+ with pip
- [ ] Gemini API key

## Installation Steps

### Phase 1: Install tactile-conversion Library

```bash
# From repository root
cd lib/tactile-conversion
pip install -e .

# Verify installation
tactile-conversion --version
```

### Phase 2: Install aai-tactile-graphics Pack

```bash
# Navigate to pack
cd ../../aai-tactile-graphics

# Follow pack INSTALL.md
# (AI-assisted installation recommended)
```

### Phase 3: Install aai-image-description Pack

```bash
cd ../aai-image-description
# Follow pack INSTALL.md
```

### Phase 4: Configure API Keys

Add to `~/.claude/.env`:
```bash
GEMINI_API_KEY=your-gemini-api-key
```

### Phase 5: Verify Installation

Run verification for each pack:
```
"Verify aai-tactile-graphics installation"
"Verify aai-image-description installation"
```

## Post-Installation

1. Test with a sample image
2. Configure TELOS files for accessibility focus
3. Set up memory directory structure
```

---

## 4. Pack: aai-tactile-graphics

### 4.1 Pack Overview

The primary pack for generating tactile-ready images for PIAF printing.

**Capabilities:**
- AI-powered image generation from existing images (primary)
- AI-powered image generation from text descriptions
- Code-based conversion fallback (via tactile-conversion)
- Stratification of complex images into layers
- Braille label generation
- Proactive image detection

### 4.2 SKILL.md

```yaml
---
name: TactileGraphics
description: Generate tactile-ready images for PIAF printing
implements: Science
science_cycle_time: meso
context: fork
---

# TactileGraphics

**Auto-loads when:** User discusses images, graphics, drawings, diagrams, floor plans,
sections, elevations, site plans, or requests tactile/PIAF conversion.

## Customization

**Before executing, check for user customizations at:**
`~/.claude/skills/CORE/USER/SKILLCUSTOMIZATIONS/TactileGraphics/`

## Context Files

Load these files to understand tactile graphics principles:
- `TactileGuidelines.md` - Core tactile design rules
- `ArchitecturalContext.md` - Architecture-specific knowledge

## Workflow Routing

| Trigger | Description | Workflow |
|---------|-------------|----------|
| Image path provided, wants tactile version | Generate tactile from existing image | `Workflows/GenerateFromImage.md` |
| "create image of", "draw", "visualize", no source | Generate tactile from description | `Workflows/GenerateFromDescription.md` |
| "convert only", "just convert", explicit request | Code-based conversion only | `Workflows/ConvertOnly.md` |

## Decision Logic: Generate vs. Convert

**Default to Generation (AI) when:**
- Image is complex with multiple overlapping systems
- Image has low contrast or poor quality
- Student wants simplified/focused representation
- Creating from scratch (no source image)

**Use Conversion (code-based) when:**
- Student explicitly requests it
- AI generation is unavailable/failing
- Image is already clean and high-contrast
- Quick processing needed without refinement

## Voice Notification

Before executing workflows, announce:
- What workflow is being used
- Expected output type
- Whether stratification is recommended
```

### 4.3 Workflow: GenerateFromImage.md

```markdown
# GenerateFromImage Workflow

Generate a tactile-optimized image from an existing visual image using AI.

## Overview

This workflow uses Gemini/Nano Banana to generate a new tactile-optimized
image designed from scratch for tactile perception. This is the PRIMARY
approach for converting images.

## Prerequisites

- Source image path provided
- GEMINI_API_KEY configured
- Nano Banana Pro MCP server available

## Workflow Steps

### Step 1: Analyze Source Image

Use Claude vision to analyze:
1. Identify image type (floor plan, section, diagram, etc.)
2. Inventory elements present
3. Assess complexity (single-system vs. multi-system)
4. Identify text/labels needing Braille conversion
5. Note quality issues (low contrast, noise)

### Step 2: Propose Stratification (if needed)

If image contains multiple information systems:

```
I've analyzed this drawing and identified 3 potential layers:

1. Structure - Walls, columns, stairs (12 elements)
2. Circulation - Paths, doors, entries (8 elements)
3. Program - Furniture, equipment (15 elements)

Would you like me to proceed with this stratification, or would you
prefer different groupings?
```

Accept student modifications before proceeding.

### Step 3: Consult Memory for Preferences

Check `MEMORY/LEARNING/AAI/image_type_preferences.jsonl`:
- Look up preferences for this image type
- Apply learned settings
- Note relevant successful generations

### Step 4: Generate Tactile Image(s)

For each layer (or single image if not stratified):

1. **Construct generation prompt**:
   ```
   Generate a clean, high-contrast tactile graphic showing:
   [layer description]

   From source image: [attached]

   Requirements:
   - Pure black lines on white background
   - Minimum 2.5mm spacing between elements
   - Bold solid lines, no fine details under 1.5mm
   - Maintain spatial relationships and proportions
   - Remove all text (Braille added separately)
   - Simplify: [specific simplifications]
   - Preserve: [specific preservations]
   ```

2. **Call Gemini/Nano Banana** via GeminiGenerate.ts
3. **Validate output** (dimensions, density)
4. **Iterate if needed** (max 2 retries)

### Step 5: Apply Post-Processing

For each generated image, call tactile-conversion:
```bash
tactile-conversion [generated_image] \
  --detect-text \
  --braille-grade 2 \
  --auto-scale \
  --abbreviation-key
```

### Step 6: Assemble Output

1. Combine layers into multi-page PDF if stratified
2. Add key page with all abbreviations
3. Add registration marks if multi-page
4. Generate summary

### Step 7: Present to Student

```
Generation complete:
- [N] page PDF created at [path]
- Page 1: [layer name] - [element count] elements
- Page 2: [layer name] - [element count] elements
- Page [N]: Abbreviation key

Total Braille labels: [count]

Would you like me to describe any specific area, or make adjustments?
```

### Step 8: Capture Learning

Record to MEMORY/LEARNING/AAI/:
- Settings used for this image type
- Student feedback
- Refinements for future generations

## Error Handling

**Generation fails:**
1. Retry with simplified prompt (1 retry)
2. If still fails, offer ConvertOnly fallback:
   ```
   AI generation failed. Would you like me to try code-based
   conversion instead? It preserves the original image more
   directly but with less simplification.
   ```

**Student unsatisfied:**
1. Ask what's missing or incorrect
2. Regenerate with refined parameters
3. Update memory with feedback
```

### 4.4 Workflow: GenerateFromDescription.md

```markdown
# GenerateFromDescription Workflow

Generate a tactile image from scratch based on text description.

## Overview

Creates tactile graphics without a source image—useful for:
- Researching precedent studies ("Barcelona Pavilion floor plan")
- Visualizing concepts being discussed
- Creating study aids
- Generating diagrams during research

## Prerequisites

- Clear description of desired image
- GEMINI_API_KEY configured
- Nano Banana Pro MCP server available

## Workflow Steps

### Step 1: Clarify Requirements

Gather through dialogue:
1. **Subject**: Specific building, generic type, or abstract concept
2. **Drawing type**: Floor plan, section, elevation, site plan, diagram
3. **Key information**: What should it communicate?
4. **Detail level**: Overview, detailed, or focused area

### Step 2: Research Subject (if specific building)

For known buildings:
1. Use PAI Research skill to gather accurate information
2. Cross-reference sources for accuracy
3. Note uncertainties to communicate to student
4. Compile reference description

### Step 3: Construct Generation Prompt

```
Generate a tactile-ready floor plan of [subject].

Subject Information:
[Research findings or user description]

Drawing Type: [floor plan/section/etc.]

Key Elements to Include:
- [element 1]
- [element 2]

Tactile Requirements:
- Pure black lines on white background
- Minimum 2.5mm spacing between all elements
- Bold solid lines, no fine details under 1.5mm
- No text (Braille added separately)
- No gray tones or gradients

Accuracy Notes:
- Maintain correct proportions
- [specific requirements]
- [note uncertainties]
```

### Step 4: Generate and Verify

1. Call Gemini/Nano Banana
2. Validate output
3. Present to student with context:

```
I've generated a tactile floor plan of [subject] based on
documented sources. Key features:
- [feature 1]
- [feature 2]

Note: Generated from descriptions—some proportions may not
be exact. Would you like adjustments?
```

### Step 5: Apply Post-Processing

Process through tactile-conversion for Braille labels.

### Step 6: Capture Learning

Record subject, approach, and feedback for future reference.
```

### 4.5 Workflow: ConvertOnly.md

```markdown
# ConvertOnly Workflow

Code-based conversion using tactile-conversion library.

## Overview

This workflow uses the tactile-conversion Python library for direct
image processing WITHOUT AI generation. Use when:
- Student explicitly requests it
- AI generation is unavailable or failing
- Source image is already clean and high-contrast
- Quick processing needed

## When to Use

**Appropriate for:**
- Clean, high-contrast source images
- Technical drawings where exact accuracy matters
- Quick conversions
- Offline scenarios (no API needed)

**Less ideal for:**
- Complex, cluttered images
- Low-contrast photographs
- Images needing significant simplification

## Workflow Steps

### Step 1: Analyze Image

Quick assessment:
1. Image type detection
2. Quality check
3. Complexity assessment
4. Text detection preview

### Step 2: Select Preset

| Image Type | Preset | Settings |
|------------|--------|----------|
| Floor plan | `floor_plan` | threshold=128, enhance=auto_contrast |
| Section | `section` | threshold=140, enhance=clahe |
| Elevation | `elevation` | threshold=135, enhance=s_curve |
| Site plan | `site_plan` | threshold=120, enhance=auto_contrast |
| Sketch | `sketch` | threshold=100, enhance=s_curve |
| Diagram | `diagram` | threshold=150, enhance=auto_contrast |

### Step 3: Process Image

```bash
tactile-conversion [image_path] \
  --preset [selected_preset] \
  --detect-text \
  --braille-grade 2 \
  --auto-scale \
  --abbreviation-key \
  --auto-reduce-density
```

### Step 4: Present Results

```
Conversion complete. Output saved to [path].

Stats:
- Density: [X]%
- Braille labels: [N]
- Pages: [N]

If the result is too cluttered, I can try AI generation
for a simplified version. Would you like that?
```

## Fallback to Generation

If conversion produces poor results, offer AI generation:

```
The converted image has [issue]. AI generation could:
- Simplify cluttered areas
- Separate overlapping systems
- Enhance clarity

Would you like me to try generating instead?
```
```

---

## 5. Pack: aai-image-description

### 5.1 Pack Overview

Generates detailed accessibility descriptions of architectural images using the Arch-Alt-Text framework.

**Capabilities:**
- Multi-layered descriptions (Macro/Meso/Micro)
- Architecture-specific vocabulary
- Spatial relationship articulation
- Tactile analogies where helpful

### 5.2 SKILL.md

```yaml
---
name: ImageDescription
description: Generate detailed accessibility descriptions of architectural images
implements: Science
science_cycle_time: micro
context: fork
---

# ImageDescription

**Auto-loads when:** User asks to describe an image, explain what an image shows,
or needs text-based understanding of visual content.

## Customization

**Before executing, check for user customizations at:**
`~/.claude/skills/CORE/USER/SKILLCUSTOMIZATIONS/ImageDescription/`

## Context Files

- `ArchAltText.md` - Description framework and guidelines
- `ArchitecturalContext.md` - Architecture-specific knowledge (shared)

## Workflow Routing

| Trigger | Description | Workflow |
|---------|-------------|----------|
| "describe", "what does this show", "explain this image" | Generate accessibility description | `Workflows/DescribeImage.md` |

## When to Use

- Quick understanding without PIAF printing
- Supplementing tactile graphics with verbal context
- Images that don't translate well to tactile
- Remote/mobile situations without PIAF access
- Initial exploration before deciding on tactile conversion
```

### 5.3 Workflow: DescribeImage.md

```markdown
# DescribeImage Workflow

Generate detailed accessibility description using Arch-Alt-Text system.

## Overview

Creates multi-layered text descriptions of architectural images for
situations where tactile graphics aren't needed or as a supplement.

## Workflow Steps

### Step 1: Load Arch-Alt-Text Framework

Use the structured description system:
- **Macro Layer**: Medium, subject, purpose (3 sentences)
- **Meso Layer**: Composition, materials, orientation, scale (4+ sentences)
- **Micro Layer**: Details, textures, dimensions, analogies (8+ sentences)

### Step 2: Analyze Image

Using Claude vision, identify:
- Image type and subject
- Key architectural elements
- Spatial relationships
- Notable features

### Step 3: Generate Layered Description

```markdown
## [Image Title/Subject]

### Overview (Macro)
[Medium - what type of drawing/image this is]
[Subject - what building/space/concept is shown]
[Purpose - what information it communicates]

### Composition (Meso)
[Overall organization and layout]
[Major elements and their relationships]
[Orientation and viewpoint]
[Scale and proportions]

### Details (Micro)
[Specific elements, clockwise from entry or logical order]
[Dimensions and measurements if relevant]
[Materials and textures]
[Tactile analogies where helpful]
```

### Step 4: Offer Follow-up

```
Would you like me to:
- Describe a specific area in more detail?
- Generate a tactile version of this image?
- Explain any architectural concepts shown?
```

## Example

```
Student: What does this site plan show?

PAI: ## Campus Library Site Plan

### Overview
This is an architectural site plan showing a proposed library
building and its surrounding landscape. The drawing communicates
the building's footprint, circulation paths, and relationship
to adjacent campus buildings.

### Composition
The library is positioned center-drawing, oriented with its main
entrance facing south toward a large open quad. The building
footprint is roughly rectangular, approximately 200 feet east-west
by 150 feet north-south—about half a football field.

Three pathways converge on the main entrance: south (main approach),
east (science buildings), and west (student center).

### Details
Starting at the main entrance and moving clockwise:
- South facade: Main entrance with covered portico
- East side: Service entrance, loading area
- North side: Emergency exits, backs onto parking
- West side: Secondary entrance via covered walkway

Would you like me to describe any area in more detail, or
generate a tactile version for PIAF printing?
```
```

---

## 6. Shared Components

### 6.1 TactileGuidelines.md

Shared between both packs. Contains:
- Spacing rules (2.5mm minimum)
- Line weight standards
- Simplification principles
- Labeling guidelines
- Architecture-specific conventions

(Full content in Section 4 of original document)

### 6.2 ArchitecturalContext.md

Shared knowledge base:
- Drawing type purposes
- Common architectural elements
- Dimension formats
- Precedent study references

(Full content in Section 4 of original document)

---

## 7. TELOS Integration

The entire PAI identity centers on accessibility and architectural education.

### 7.1 MISSION.md (Draft)

```markdown
# Mission

Excel in architecture education with full access to visual information,
developing spatial understanding and design skills that prepare for
professional practice.

## Core Purpose
Learn, understand, and create architecture through non-visual means
that are equally rich and informative as visual approaches.

## Scope
- Academic success in architecture program
- Development of spatial reasoning and design intuition
- Preparation for professional architectural practice
- Contribution to making architecture education more accessible
```

### 7.2 GOALS.md (Draft)

```markdown
# Goals

## Immediate (This Semester)
- Master reading tactile floor plans for current studio projects
- Develop efficient workflow for processing course materials
- Build library of tactile precedent studies

## Short-Term (This Year)
- Complete design studios with full access to visual references
- Develop personal tactile notation system
- Create accessible versions of key precedent studies

## Long-Term (Career Preparation)
- Build portfolio demonstrating design capability
- Develop strategies for professional practice
- Contribute to accessibility knowledge in architecture
```

### 7.3 Additional TELOS Files

| File | Purpose | Priority |
|------|---------|----------|
| BELIEFS.md | About learning, architecture, technology, independence | High |
| STRATEGIES.md | For course materials, studio, research, time management | High |
| CHALLENGES.md | Current obstacles being addressed | High |
| PROJECTS.md | Active courses and design projects | Medium |

---

## 8. Hook System

### 8.1 ImageDetector.hook.ts

Proactively detects images and offers tactile conversion.

```typescript
#!/usr/bin/env bun
/**
 * ImageDetector.hook.ts - Proactive image detection for AAI
 *
 * TRIGGER: PostToolUse (matcher: Read, WebFetch, Bash)
 * PURPOSE: Detect images and offer PIAF conversion
 */

// Image extensions to detect
const IMAGE_EXTENSIONS = [
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.pdf', '.webp'
];

// Architecture keywords suggesting tactile conversion would help
const ARCHITECTURE_KEYWORDS = [
  'floor plan', 'floorplan', 'section', 'elevation', 'site plan',
  'diagram', 'drawing', 'blueprint', 'schematic', 'layout'
];

// Hook implementation detects images and logs to MEMORY/LEARNING/AAI/
// When architecture context detected, suggests tactile conversion
```

### 8.2 Hook Registration

Add to `~/.claude/settings.json`:
```json
{
  "PostToolUse": [
    {
      "matchers": ["Read", "WebFetch", "Bash"],
      "hooks": [{
        "type": "command",
        "command": "${PAI_DIR}/hooks/ImageDetector.hook.ts"
      }]
    }
  ]
}
```

---

## 9. Memory System

### 9.1 Directory Structure

```
MEMORY/LEARNING/AAI/
├── image_type_preferences.jsonl    # Learned settings by image type
├── successful_generations.jsonl    # What worked
├── student_feedback.jsonl          # Explicit feedback
├── generation_failures.jsonl       # What didn't work
├── detections.jsonl               # Hook-logged detections
└── guidelines_refinements.md       # Accumulated learnings
```

### 9.2 Memory Integration

Workflows should:
1. **Read preferences** before generation
2. **Write outcomes** after completion
3. **Capture explicit feedback** when provided

---

## 10. Gemini/Nano Banana Integration

### 10.1 Architecture

```
Generation Request
    ↓
Nano Banana Pro MCP Server
    ↓
Gemini API (Imagen 3)
    ↓
Generated Image (high-contrast, tactile)
    ↓
tactile-conversion (Braille, scaling, PDF)
    ↓
PIAF-Ready Output
```

### 10.2 GeminiGenerate.ts Tool

TypeScript tool for PAI that:
- Constructs tactile-optimized prompts
- Calls Nano Banana Pro MCP
- Handles retries and fallbacks
- Returns generated image path

### 10.3 Tactile Prompt Suffix

Automatically appended to all generation requests:
```
Technical requirements for tactile output:
- Pure black lines on pure white background
- Minimum 2.5mm spacing between all distinct elements
- Bold solid lines, no fine details smaller than 1.5mm
- No gray tones, gradients, or shading
- No text or labels (will be added separately as Braille)
- Consistent line weights throughout
- High contrast suitable for PIAF swell paper printing
```

---

## 11. tactile-conversion Library

### 11.1 Overview

The Python library (renamed from tactile) provides code-based image conversion as a fallback and for post-processing AI-generated images.

### 11.2 Installation

```bash
# From repository
cd lib/tactile-conversion
pip install -e .

# Verify
tactile-conversion --version
```

### 11.3 CLI Usage

```bash
# Basic conversion
tactile-conversion input.jpg -o output.pdf

# With options
tactile-conversion input.jpg \
  --preset floor_plan \
  --detect-text \
  --braille-grade 2 \
  --auto-scale \
  --abbreviation-key

# List presets
tactile-conversion --list-presets
```

### 11.4 Python API

```python
from tactile_conversion import ImageProcessor, PIAFPDFGenerator

processor = ImageProcessor()
image = processor.load_image("floor_plan.jpg")
processed = processor.apply_threshold(image, 128)

generator = PIAFPDFGenerator()
generator.generate_pdf(processed, "letter", "output.pdf")
```

---

## 12. Implementation Phases

### Phase 1: Repository Restructure (Week 1)

- [ ] Rename repository to accessible-architecture-infrastructure
- [ ] Restructure directories per this plan
- [ ] Rename tactile to tactile-conversion
- [ ] Update all imports and references
- [ ] Verify tactile-conversion installs standalone

### Phase 2: Pack Structure (Week 2)

- [ ] Create aai-tactile-graphics pack structure
- [ ] Create aai-image-description pack structure
- [ ] Write pack README, INSTALL, VERIFY files
- [ ] Write bundle README, INSTALL files

### Phase 3: TactileGraphics Skill (Weeks 3-4)

- [ ] Write SKILL.md with routing
- [ ] Implement ConvertOnly.md workflow (wrapping tactile-conversion)
- [ ] Create TactileConvert.ts tool wrapper
- [ ] Test basic PAI integration

### Phase 4: ImageDescription Skill (Week 5)

- [ ] Write SKILL.md
- [ ] Implement DescribeImage.md workflow
- [ ] Create ArchAltText.md framework document
- [ ] Test integration

### Phase 5: Proactive Detection (Week 6)

- [ ] Implement ImageDetector.hook.ts
- [ ] Register hook
- [ ] Test detection across tools
- [ ] Create memory directory structure

### Phase 6: AI Generation (Weeks 7-9)

- [ ] Set up Nano Banana Pro MCP
- [ ] Implement GeminiGenerate.ts
- [ ] Create GenerateFromImage.md workflow
- [ ] Create GenerateFromDescription.md workflow
- [ ] Implement stratification logic
- [ ] Test with various image types

### Phase 7: Memory & Learning (Week 10)

- [ ] Implement preference capture
- [ ] Implement feedback logging
- [ ] Build preference application in workflows
- [ ] Test learning cycle

### Phase 8: TELOS & Polish (Weeks 11-12)

- [ ] Draft TELOS files with student
- [ ] End-to-end testing
- [ ] Documentation
- [ ] Feedback iteration

---

## 13. Testing Strategy

### 13.1 Test Categories

| Category | Examples | Key Tests |
|----------|----------|-----------|
| Floor Plans | Studio projects, precedents | Stratification, labels, circulation |
| Sections | Building sections | Level relationships, structure |
| Site Plans | Campus, urban context | Layer separation, scale |
| Diagrams | Circulation, program | Concept clarity, legends |

### 13.2 Quality Metrics

- Generation success rate
- Student comprehension
- Fallback frequency
- Memory utilization

---

## 14. Open Questions

### Technical

1. **Gemini rate limits**: Sequential generation with progress updates
2. **Generation validation**: Density check, dimension validation
3. **Canvas integration**: Start manual, evaluate later
4. **Offline capability**: ConvertOnly works offline

### Process

5. **Feedback loop**: After each session, optional rating
6. **Human assistant coordination**: PAI handles routine; human handles judgment

### Future Packs

7. **3D model generation**: Major future capability
8. **Audio representations**: Spatial audio for navigation
9. **Course material processing**: Automated syllabus/handout handling

---

## Appendix A: Environment Setup

### Required Variables

```bash
# ~/.claude/.env
PAI_DIR=~/.claude
DA=AccessibilityAssistant
TIME_ZONE=America/New_York
GEMINI_API_KEY=your-key
```

### MCP Server Setup

```bash
# Nano Banana Pro
claude mcp add nano-banana-pro -s user -- \
  env GEMINI_API_KEY=$GEMINI_API_KEY \
  npx @rafarafarafa/nano-banana-pro-mcp
```

---

## Appendix B: File Checklist

### Repository Files
- [ ] `README.md` (bundle)
- [ ] `INSTALL.md` (bundle)
- [ ] `lib/tactile-conversion/` (Python library)
- [ ] `aai-tactile-graphics/` (pack)
- [ ] `aai-image-description/` (pack)
- [ ] `shared/` (shared resources)
- [ ] `docs/` (documentation)

### Pack: aai-tactile-graphics
- [ ] `README.md`, `INSTALL.md`, `VERIFY.md`
- [ ] `src/skills/TactileGraphics/SKILL.md`
- [ ] `src/skills/TactileGraphics/TactileGuidelines.md`
- [ ] `src/skills/TactileGraphics/ArchitecturalContext.md`
- [ ] `src/skills/TactileGraphics/Workflows/GenerateFromImage.md`
- [ ] `src/skills/TactileGraphics/Workflows/GenerateFromDescription.md`
- [ ] `src/skills/TactileGraphics/Workflows/ConvertOnly.md`
- [ ] `src/hooks/ImageDetector.hook.ts`
- [ ] `src/tools/GeminiGenerate.ts`
- [ ] `src/tools/TactileConvert.ts`
- [ ] `src/tools/GuidelinesCheck.ts`

### Pack: aai-image-description
- [ ] `README.md`, `INSTALL.md`, `VERIFY.md`
- [ ] `src/skills/ImageDescription/SKILL.md`
- [ ] `src/skills/ImageDescription/ArchAltText.md`
- [ ] `src/skills/ImageDescription/Workflows/DescribeImage.md`

---

*End of Plan Document*
