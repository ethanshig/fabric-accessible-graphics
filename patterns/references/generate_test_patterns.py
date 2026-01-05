#!/usr/bin/env python3
"""
Generate test pattern sheets for tactile graphics evaluation.

This script generates three PDF test sheets:
1. HATCH_TEST_SHEET_TACTILE.pdf - 6 tactile patterns optimized for PIAF
2. HATCH_TEST_SHEET_TRADITIONAL.pdf - Traditional architectural hatch patterns
3. HATCH_COMPARISON.pdf - Side-by-side comparison of traditional vs tactile

All patterns are generated at 300 DPI for PIAF printing quality.
"""

import sys
import os
import math
import random

# Add the project src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import io

# Import Braille converter from the project
from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig
from fabric_access.utils.logger import AccessibleLogger


# Constants
DPI = 300
LETTER_WIDTH_IN = 8.5
LETTER_HEIGHT_IN = 11.0
LETTER_WIDTH_PX = int(LETTER_WIDTH_IN * DPI)
LETTER_HEIGHT_PX = int(LETTER_HEIGHT_IN * DPI)

# Pattern cell size (75mm x 75mm at 300 DPI)
CELL_SIZE_MM = 75
CELL_SIZE_PX = int(CELL_SIZE_MM * DPI / 25.4)  # Convert mm to pixels at 300 DPI

# Line weight for PIAF compatibility (in pixels at 300 DPI)
LINE_WEIGHT = 3  # ~0.25mm at 300 DPI, good for swell paper


def register_braille_font():
    """Register DejaVu Sans font for Braille rendering."""
    font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux/WSL
        '/System/Library/Fonts/Supplemental/DejaVuSans.ttf',  # macOS
        'C:\\Windows\\Fonts\\DejaVuSans.ttf',  # Windows
    ]

    if 'DejaVu Sans' not in pdfmetrics.getRegisteredFontNames():
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('DejaVu Sans', font_path))
                    print(f"Registered DejaVu Sans from: {font_path}")
                    return True
                except Exception as e:
                    print(f"Failed to register font: {e}")
    else:
        return True

    print("Warning: DejaVu Sans font not found. Braille may not render correctly.")
    return False


def create_braille_converter():
    """Create a Braille converter instance using Grade 2 Braille."""
    config = BrailleConfig(
        enabled=True,
        grade=2,  # Grade 2 (contracted) Braille
        font_name="DejaVu Sans",
        font_size=12,
        offset_x=0,
        offset_y=0
    )
    logger = AccessibleLogger(verbose=False)
    return BrailleConverter(config, logger)


# Pattern generation functions

def create_solid_fill(draw, x, y, width, height):
    """P1: Solid black fill (STEEL)"""
    draw.rectangle([x, y, x + width, y + height], fill='black')


def create_stipple_dots(draw, x, y, width, height, spacing_mm=3, dot_diameter_mm=1.5):
    """P2: Stipple/dots pattern (CONCRETE)"""
    spacing_px = int(spacing_mm * DPI / 25.4)
    radius_px = int((dot_diameter_mm / 2) * DPI / 25.4)

    # Draw regular dot grid
    for row_y in range(y + spacing_px // 2, y + height, spacing_px):
        for col_x in range(x + spacing_px // 2, x + width, spacing_px):
            draw.ellipse([
                col_x - radius_px, row_y - radius_px,
                col_x + radius_px, row_y + radius_px
            ], fill='black')


def create_diagonal_lines(draw, x, y, width, height, spacing_mm=4, angle=45):
    """P3: Diagonal lines at specified angle (MASONRY)"""
    spacing_px = int(spacing_mm * DPI / 25.4)

    # Draw diagonal lines from bottom-left to top-right
    # For 45 degree lines, we need to cover the full diagonal extent
    max_extent = width + height

    for offset in range(-max_extent, max_extent, spacing_px):
        # Line endpoints
        x1 = x + offset
        y1 = y + height
        x2 = x + offset + height
        y2 = y

        # Clip line to rectangle bounds
        # This is a simplified approach - draw and let PIL clip
        draw.line([(x1, y1), (x2, y2)], fill='black', width=LINE_WEIGHT)


def create_horizontal_lines(draw, x, y, width, height, spacing_mm=4):
    """P4: Horizontal lines (WOOD)"""
    spacing_px = int(spacing_mm * DPI / 25.4)

    for line_y in range(y + spacing_px // 2, y + height, spacing_px):
        draw.line([(x, line_y), (x + width, line_y)], fill='black', width=LINE_WEIGHT)


def create_crosshatch_grid(draw, x, y, width, height, spacing_mm=10):
    """P5: Crosshatch grid pattern (EARTH)"""
    spacing_px = int(spacing_mm * DPI / 25.4)

    # Vertical lines
    for line_x in range(x + spacing_px // 2, x + width, spacing_px):
        draw.line([(line_x, y), (line_x, y + height)], fill='black', width=LINE_WEIGHT)

    # Horizontal lines
    for line_y in range(y + spacing_px // 2, y + height, spacing_px):
        draw.line([(x, line_y), (x + width, line_y)], fill='black', width=LINE_WEIGHT)


def create_vertical_lines(draw, x, y, width, height, spacing_mm=4):
    """P6: Vertical lines (GLASS)"""
    spacing_px = int(spacing_mm * DPI / 25.4)

    for line_x in range(x + spacing_px // 2, x + width, spacing_px):
        draw.line([(line_x, y), (line_x, y + height)], fill='black', width=LINE_WEIGHT)


# Traditional architectural pattern functions

def create_random_stipple(draw, x, y, width, height, density=0.02):
    """Traditional concrete: Random irregular stipple (more organic)"""
    # Calculate number of dots based on density
    area = width * height
    num_dots = int(area * density / 100)

    random.seed(42)  # For reproducibility

    for _ in range(num_dots):
        dot_x = random.randint(x + 5, x + width - 5)
        dot_y = random.randint(y + 5, y + height - 5)
        radius = random.randint(2, 5)
        draw.ellipse([
            dot_x - radius, dot_y - radius,
            dot_x + radius, dot_y + radius
        ], fill='black')


def create_concentric_arcs(draw, x, y, width, height, spacing_mm=4):
    """Traditional wood: Concentric arcs (end grain view)"""
    spacing_px = int(spacing_mm * DPI / 25.4)
    center_x = x + width // 2
    center_y = y + height + spacing_px * 2  # Center below the rectangle

    max_radius = int(math.sqrt((width/2)**2 + height**2)) + spacing_px * 3

    for radius in range(spacing_px, max_radius, spacing_px):
        # Draw arc from 0 to 180 degrees (top half)
        bbox = [
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius
        ]
        # Only draw if arc would be visible in the cell
        draw.arc(bbox, start=200, end=340, fill='black', width=LINE_WEIGHT)


def create_earth_with_triangles(draw, x, y, width, height, spacing_mm=8):
    """Traditional earth: Dots plus small triangles"""
    spacing_px = int(spacing_mm * DPI / 25.4)
    triangle_size = spacing_px // 3

    for row_idx, row_y in enumerate(range(y + spacing_px // 2, y + height, spacing_px)):
        for col_idx, col_x in enumerate(range(x + spacing_px // 2, x + width, spacing_px)):
            # Alternate between dots and triangles
            if (row_idx + col_idx) % 2 == 0:
                # Draw dot
                draw.ellipse([
                    col_x - 3, row_y - 3,
                    col_x + 3, row_y + 3
                ], fill='black')
            else:
                # Draw small triangle pointing up
                points = [
                    (col_x, row_y - triangle_size),
                    (col_x - triangle_size, row_y + triangle_size // 2),
                    (col_x + triangle_size, row_y + triangle_size // 2)
                ]
                draw.polygon(points, fill='black')


def create_glass_border(draw, x, y, width, height, border_mm=2):
    """Traditional glass: Clear rectangle with thick border"""
    border_px = int(border_mm * DPI / 25.4)

    # Draw thick border rectangle
    draw.rectangle([x, y, x + width, y + height], outline='black', width=border_px * 2)


def create_pattern_image(width, height, pattern_func, **kwargs):
    """Create a PIL image with a pattern."""
    img = Image.new('1', (width, height), color=1)  # 1-bit white background
    draw = ImageDraw.Draw(img)
    pattern_func(draw, 0, 0, width, height, **kwargs)
    return img


def generate_tactile_test_sheet(output_path, braille_converter):
    """Generate HATCH_TEST_SHEET_TACTILE.pdf with 6 tactile patterns."""
    print("Generating HATCH_TEST_SHEET_TACTILE.pdf...")

    # Pattern definitions: (name, function, kwargs)
    patterns = [
        ("STEEL", create_solid_fill, {}),
        ("CONCRETE", create_stipple_dots, {"spacing_mm": 3, "dot_diameter_mm": 1.5}),
        ("MASONRY", create_diagonal_lines, {"spacing_mm": 4, "angle": 45}),
        ("WOOD", create_horizontal_lines, {"spacing_mm": 4}),
        ("EARTH", create_crosshatch_grid, {"spacing_mm": 10}),
        ("GLASS", create_vertical_lines, {"spacing_mm": 4}),
    ]

    _generate_pattern_sheet(output_path, patterns, braille_converter, "Tactile Patterns")


def generate_traditional_test_sheet(output_path, braille_converter):
    """Generate HATCH_TEST_SHEET_TRADITIONAL.pdf with traditional architectural patterns."""
    print("Generating HATCH_TEST_SHEET_TRADITIONAL.pdf...")

    patterns = [
        ("STEEL", create_solid_fill, {}),
        ("CONCRETE", create_random_stipple, {"density": 0.015}),
        ("BRICK", create_diagonal_lines, {"spacing_mm": 4, "angle": 45}),
        ("WOOD", create_concentric_arcs, {"spacing_mm": 4}),
        ("EARTH", create_earth_with_triangles, {"spacing_mm": 8}),
        ("GLASS", create_glass_border, {"border_mm": 2}),
    ]

    _generate_pattern_sheet(output_path, patterns, braille_converter, "Traditional Patterns")


def _generate_pattern_sheet(output_path, patterns, braille_converter, title):
    """Generate a 2x3 pattern sheet PDF."""
    # Create canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    page_width, page_height = letter

    # Calculate layout
    margin = 0.5 * inch
    cols = 2
    rows = 3

    # Available space
    available_width = page_width - 2 * margin
    available_height = page_height - 2 * margin - 0.5 * inch  # Title space

    cell_width = available_width / cols
    cell_height = available_height / rows

    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, page_height - margin, title)

    # Generate each pattern
    for idx, (name, pattern_func, kwargs) in enumerate(patterns):
        row = idx // cols
        col = idx % cols

        # Calculate cell position
        cell_x = margin + col * cell_width
        cell_y = page_height - margin - 0.5 * inch - (row + 1) * cell_height

        # Pattern area (smaller than cell to leave room for labels)
        pattern_margin = 10
        label_space = 40  # Space for Braille and print labels below pattern

        pattern_width = cell_width - 2 * pattern_margin
        pattern_height = cell_height - label_space - pattern_margin

        # Create pattern image
        pattern_img = Image.new('1', (int(pattern_width * DPI / 72), int(pattern_height * DPI / 72)), color=1)
        draw = ImageDraw.Draw(pattern_img)
        pattern_func(draw, 0, 0, pattern_img.width, pattern_img.height, **kwargs)

        # Convert to image buffer
        img_buffer = io.BytesIO()
        pattern_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Draw pattern on PDF
        pattern_x = cell_x + pattern_margin
        pattern_y = cell_y + label_space

        c.drawImage(ImageReader(img_buffer), pattern_x, pattern_y,
                   width=pattern_width, height=pattern_height)

        # Draw border around pattern
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
        c.rect(pattern_x, pattern_y, pattern_width, pattern_height)

        # Add Braille label
        try:
            braille_text = braille_converter.convert_text(name)
            try:
                c.setFont("DejaVu Sans", 12)
            except:
                c.setFont("Helvetica", 12)

            label_y = cell_y + label_space - 15
            c.drawCentredString(cell_x + cell_width / 2, label_y, braille_text)
        except Exception as e:
            print(f"Warning: Could not create Braille for {name}: {e}")

        # Add print label below Braille
        c.setFont("Helvetica", 10)
        print_label_y = cell_y + 5
        c.drawCentredString(cell_x + cell_width / 2, print_label_y, name)

    c.save()
    print(f"  Saved: {output_path}")


def generate_comparison_sheet(output_path, braille_converter):
    """Generate HATCH_COMPARISON.pdf with side-by-side comparison."""
    print("Generating HATCH_COMPARISON.pdf...")

    # Material pairs: (name, traditional_func, traditional_kwargs, tactile_func, tactile_kwargs)
    materials = [
        ("STEEL", create_solid_fill, {}, create_solid_fill, {}),
        ("CONCRETE", create_random_stipple, {"density": 0.015},
         create_stipple_dots, {"spacing_mm": 3, "dot_diameter_mm": 1.5}),
        ("MASONRY", create_diagonal_lines, {"spacing_mm": 4},
         create_diagonal_lines, {"spacing_mm": 4}),
        ("WOOD", create_concentric_arcs, {"spacing_mm": 4},
         create_horizontal_lines, {"spacing_mm": 4}),
        ("EARTH", create_earth_with_triangles, {"spacing_mm": 8},
         create_crosshatch_grid, {"spacing_mm": 10}),
        ("GLASS", create_glass_border, {"border_mm": 2},
         create_vertical_lines, {"spacing_mm": 4}),
    ]

    c = canvas.Canvas(output_path, pagesize=letter)
    page_width, page_height = letter

    margin = 0.5 * inch

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, page_height - margin, "Pattern Comparison: Traditional vs Tactile")

    # Column headers
    c.setFont("Helvetica-Bold", 12)
    col_width = (page_width - 2 * margin - 0.5 * inch) / 2  # Split available width
    left_col_center = margin + 0.25 * inch + col_width / 2
    right_col_center = margin + 0.25 * inch + col_width + 0.5 * inch + col_width / 2

    header_y = page_height - margin - 0.3 * inch
    c.drawCentredString(left_col_center, header_y, "Traditional")
    c.drawCentredString(right_col_center, header_y, "Tactile")

    # Available space for patterns
    available_height = page_height - 2 * margin - 0.8 * inch
    row_height = available_height / 6
    pattern_size = min(col_width - 20, row_height - 35)  # Leave room for labels

    for idx, (name, trad_func, trad_kwargs, tact_func, tact_kwargs) in enumerate(materials):
        row_y = page_height - margin - 0.8 * inch - (idx + 1) * row_height

        # Material name on the left
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, row_y + row_height / 2, name)

        # Generate and draw traditional pattern
        trad_img = Image.new('1', (int(pattern_size * DPI / 72), int(pattern_size * DPI / 72)), color=1)
        trad_draw = ImageDraw.Draw(trad_img)
        trad_func(trad_draw, 0, 0, trad_img.width, trad_img.height, **trad_kwargs)

        trad_buffer = io.BytesIO()
        trad_img.save(trad_buffer, format='PNG')
        trad_buffer.seek(0)

        trad_x = margin + 0.6 * inch
        c.drawImage(ImageReader(trad_buffer), trad_x, row_y + 25,
                   width=pattern_size, height=pattern_size)
        c.rect(trad_x, row_y + 25, pattern_size, pattern_size)

        # Generate and draw tactile pattern
        tact_img = Image.new('1', (int(pattern_size * DPI / 72), int(pattern_size * DPI / 72)), color=1)
        tact_draw = ImageDraw.Draw(tact_img)
        tact_func(tact_draw, 0, 0, tact_img.width, tact_img.height, **tact_kwargs)

        tact_buffer = io.BytesIO()
        tact_img.save(tact_buffer, format='PNG')
        tact_buffer.seek(0)

        tact_x = margin + 0.6 * inch + col_width + 0.3 * inch
        c.drawImage(ImageReader(tact_buffer), tact_x, row_y + 25,
                   width=pattern_size, height=pattern_size)
        c.rect(tact_x, row_y + 25, pattern_size, pattern_size)

        # Braille label below
        try:
            braille_text = braille_converter.convert_text(name)
            try:
                c.setFont("DejaVu Sans", 10)
            except:
                c.setFont("Helvetica", 10)
            c.drawString(trad_x, row_y + 10, braille_text)
            c.drawString(tact_x, row_y + 10, braille_text)
        except Exception as e:
            print(f"Warning: Could not create Braille for {name}: {e}")

    c.save()
    print(f"  Saved: {output_path}")


def main():
    """Generate all test pattern sheets."""
    print("=" * 60)
    print("Test Pattern Sheet Generator for Tactile Graphics")
    print("=" * 60)
    print()

    # Get output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = script_dir  # Output to the same directory as the script

    # Register Braille font
    register_braille_font()

    # Create Braille converter
    braille_converter = create_braille_converter()

    # Generate test sheets
    generate_tactile_test_sheet(
        os.path.join(output_dir, "HATCH_TEST_SHEET_TACTILE.pdf"),
        braille_converter
    )

    generate_traditional_test_sheet(
        os.path.join(output_dir, "HATCH_TEST_SHEET_TRADITIONAL.pdf"),
        braille_converter
    )

    generate_comparison_sheet(
        os.path.join(output_dir, "HATCH_COMPARISON.pdf"),
        braille_converter
    )

    print()
    print("=" * 60)
    print("All test pattern sheets generated successfully!")
    print(f"Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
