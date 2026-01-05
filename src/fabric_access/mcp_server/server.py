"""
FastMCP server for fabric-access tactile graphics conversion.

This server exposes the fabric-access toolkit to Claude via MCP,
allowing natural language interaction for image-to-PIAF conversion.
"""

import logging
import sys
from pathlib import Path

# Configure logging to stderr (never stdout for MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("fabric-access-mcp")

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logger.error("MCP library not installed. Run: pip install mcp")
    sys.exit(1)

from fabric_access.mcp_server.tools import (
    convert_to_tactile,
    list_presets,
    analyze_image,
    describe_image,
    extract_text_with_vision
)

# Initialize MCP server
mcp = FastMCP(
    name="fabric-access",
    instructions="Tools for accessible architectural graphics. Use convert_to_tactile to convert images to PIAF-ready PDFs, list_presets to see available presets, analyze_image for pre-conversion checks, and describe_image for detailed accessibility descriptions of architectural images."
)

# Register tools
mcp.tool()(convert_to_tactile)
mcp.tool()(list_presets)
mcp.tool()(analyze_image)
mcp.tool()(describe_image)
mcp.tool()(extract_text_with_vision)


# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("arch-alt-text://prompt")
def get_arch_alt_text_prompt() -> str:
    """
    The Arch-Alt-Text system prompt for describing architectural images.

    This prompt guides Claude to create multi-sensory descriptions of
    architectural images (plans, sections, diagrams, photos) specifically
    designed for blind/low-vision architecture students.

    Usage: Read this resource, then use Claude's vision capability to
    describe an image following the Macro/Meso/Micro format.
    """
    # Try to load from the patterns directory first
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "patterns" / "image_description_machine" / "image_description_machine.md",
        Path("/mnt/c/Users/ethan/fabric-accessible-graphics/patterns/image_description_machine/image_description_machine.md"),
    ]

    for prompt_path in possible_paths:
        if prompt_path.exists():
            return prompt_path.read_text(encoding='utf-8')

    # Fallback to embedded prompt if file not found
    logger.warning("Could not find image_description_machine.md, using embedded prompt")
    return _get_embedded_arch_alt_text_prompt()


def _get_embedded_arch_alt_text_prompt() -> str:
    """Fallback embedded prompt if file is not found."""
    return '''You are **Arch-Alt-Text**, an expert narrator and tutor for a blind architecture student. Your dual mission:

1) Translate ANY visual used in architecture education into a vivid, multi-sensory mental model.
2) Build architectural literacy—precision in vocabulary, spatial reasoning, representation conventions, and critical context—without lecturing.
3) Only describe what is in the image, do not embellish, interpret or contextualize. Do not ask questions in your answer.
4) Do not repeat yourself within the answer.

════════════════════════════════════════
MACRO • MESO • MICRO — OUTPUT FORMAT (STRICT)
════════════════════════════════════════

Title: <concise title. Say the title if known, OR "Unknown" if no source is evident>

<Macro Layer — exactly 3 sentences>
• Identify the medium (photo, drawing, plan, section, axonometric, diagram, etc).
• State the principal subject and the image's purpose/argument.
• Convey the dominant atmosphere or pedagogical intent.

<Meso Layer — at least 4 sentences>
• Decompose composition and hierarchy: main masses/forms, axes/grids, figure–ground.
• Name primary materials/assemblies or graphical conventions.
• Give orientation and viewpoint/projection.
• Describe scale cues and lighting qualities.

<Micro Layer — at least 8 sentences>
• Detail textures, assemblies, structural logic, and environmental strategies.
• Provide proportional/relative dimensions.
• Map visual traits to multi-sensory analogies (tactile, acoustic, thermal).
• State occlusions and limits.

════════════════════════════════════════
WRITING RULES
════════════════════════════════════════

• Present tense; American English; ≤25 words per sentence.
• Never refer to "this image/photo"; describe directly.
• Output only: Title + three paragraphs.'''


@mcp.resource("ocr-extraction://prompt")
def get_ocr_extraction_prompt() -> str:
    """
    OCR extraction prompt for Claude's vision to detect text in architectural images.

    This prompt guides text extraction for Braille conversion, with special
    attention to handwritten annotations, dimensions, and rotated text.

    Usage: Read this resource, then use Claude's vision to extract text
    and return a JSON array of detected text with positions.
    """
    return '''You are extracting text from an architectural drawing for Braille conversion.

Your task: Identify ALL visible text in the image, including text that traditional OCR often misses.

For EACH text element found, provide:
- text: The exact text content (preserve case)
- x: Left edge position in pixels (estimate from image dimensions)
- y: Top edge position in pixels (estimate from image dimensions)
- width: Approximate width in pixels
- height: Approximate height in pixels
- type: One of "printed", "handwritten", or "dimension"
- confidence: Your confidence level ("high", "medium", or "low")

SPECIAL ATTENTION TO:

1. DIMENSIONS: Architectural measurements in various formats:
   - Feet-inches: 10'-6", 12' 0", 8'-4 1/2"
   - Metric: 3.5m, 2500mm, 45cm
   - Plain numbers with context: 120, 2400

2. HANDWRITTEN TEXT: Annotations, notes, corrections, sketched labels
   - Often in margins or near specific features
   - May be harder to read than printed text

3. ROTATED TEXT: Labels that are not horizontal
   - Vertical text along walls
   - Angled dimension strings
   - Text following curved paths

4. SMALL TEXT: Fine print, scale indicators, stamps
   - Often in title blocks
   - May be low contrast

5. ROOM LABELS: Names of spaces
   - LIVING ROOM, KITCHEN, BEDROOM
   - Often centered in rooms

OUTPUT FORMAT:
Return ONLY a valid JSON array. Example:

[
  {"text": "LIVING ROOM", "x": 450, "y": 320, "width": 120, "height": 18, "type": "printed", "confidence": "high"},
  {"text": "12'-6\\"", "x": 200, "y": 500, "width": 45, "height": 12, "type": "dimension", "confidence": "high"},
  {"text": "add outlet here", "x": 180, "y": 620, "width": 100, "height": 15, "type": "handwritten", "confidence": "medium"},
  {"text": "N", "x": 50, "y": 50, "width": 20, "height": 20, "type": "printed", "confidence": "high"}
]

IMPORTANT:
- Coordinates are pixel positions from TOP-LEFT corner (not bottom-left)
- Estimate positions based on image dimensions provided
- Include ALL readable text, even if partially obscured
- For rotated text, use the bounding box that would contain it
- Do not include decorative elements or hatching patterns
- Return empty array [] if no text is found'''


def main():
    """Run the MCP server."""
    logger.info("Starting fabric-access MCP server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
