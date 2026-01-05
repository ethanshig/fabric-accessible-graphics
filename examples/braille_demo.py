"""
Braille Conversion Demonstration Script

This script demonstrates how to use the Braille conversion module
to add Braille labels to tactile graphics PDFs.

Usage:
    python braille_demo.py
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fabric_access.core.braille_converter import (
    BrailleConverter,
    BrailleConfig,
    DetectedText
)
from fabric_access.core.pdf_generator import PIAFPDFGenerator
from fabric_access.utils.logger import AccessibleLogger
from fabric_access.config.standards_loader import load_standards
from PIL import Image, ImageDraw, ImageFont


def create_sample_image_with_text():
    """
    Create a sample architectural drawing with dimension labels.

    This simulates a simple floor plan with dimensions.
    """
    # Create a white background
    width, height = 2550, 3300  # Letter size at 300 DPI
    image = Image.new('1', (width, height), color=1)
    draw = ImageDraw.Draw(image)

    # Draw a simple floor plan outline
    # Room outline
    draw.rectangle([300, 500, 2200, 2800], outline=0, width=5)

    # Door opening
    draw.line([300, 1600, 300, 1800], fill=1, width=5)
    draw.arc([280, 1600, 320, 1800], start=0, end=90, fill=0, width=3)

    # Window
    draw.rectangle([1000, 500, 1500, 520], outline=0, width=3)

    # Interior wall
    draw.line([1200, 500, 1200, 2800], fill=0, width=5)

    return image


def create_sample_detected_texts():
    """
    Create sample detected text positions.

    In a real application, these would come from OCR or
    text detection systems.
    """
    detected_texts = [
        # Room dimensions
        DetectedText(text="24'-0\"", x=1100, y=450, width=100, height=30),
        DetectedText(text="18'-0\"", x=200, y=1600, width=100, height=30),

        # Room labels
        DetectedText(text="Kitchen", x=600, y=1200, width=150, height=30),
        DetectedText(text="Living Room", x=1500, y=1600, width=200, height=30),

        # Door dimension
        DetectedText(text="3'-0\"", x=150, y=1700, width=80, height=25),

        # Window dimension
        DetectedText(text="5'-0\"", x=1150, y=400, width=80, height=25),

        # Directional label
        DetectedText(text="North", x=2300, y=300, width=100, height=30),
    ]

    return detected_texts


def demo_grade1_braille():
    """Demonstrate Grade 1 Braille conversion."""
    print("\n" + "="*60)
    print("DEMO 1: Grade 1 Braille Conversion")
    print("="*60)

    logger = AccessibleLogger(verbose=True)

    # Configure for Grade 1 Braille
    config = BrailleConfig(
        enabled=True,
        grade=1,
        font_size=10,
        offset_x=5,
        offset_y=-15,
        max_label_length=30
    )

    # Create converter
    converter = BrailleConverter(config, logger)

    # Sample architectural text
    sample_texts = [
        "10'-6\"",
        "3.5m",
        "Kitchen",
        "North",
        "Bedroom",
        "24'-0\"",
    ]

    print("\nConverting sample dimension and room labels:")
    for text in sample_texts:
        braille = converter.convert_text(text)
        print(f"  {text:15} -> {braille}")


def demo_grade2_braille():
    """Demonstrate Grade 2 Braille conversion."""
    print("\n" + "="*60)
    print("DEMO 2: Grade 2 Braille Conversion")
    print("="*60)

    logger = AccessibleLogger(verbose=True)

    # Configure for Grade 2 Braille (contracted)
    config = BrailleConfig(
        enabled=True,
        grade=2,
        font_size=10
    )

    converter = BrailleConverter(config, logger)

    sample_texts = [
        "Kitchen",
        "Bathroom",
        "Living Room",
        "Bedroom",
        "Hallway",
    ]

    print("\nConverting room labels with Grade 2 Braille:")
    for text in sample_texts:
        braille = converter.convert_text(text)
        print(f"  {text:15} -> {braille}")


def demo_pdf_generation_with_braille():
    """Demonstrate PDF generation with Braille labels."""
    print("\n" + "="*60)
    print("DEMO 3: PDF Generation with Braille Labels")
    print("="*60)

    logger = AccessibleLogger(verbose=True)

    # Load standards
    standards = load_standards()
    braille_config_dict = standards.get('braille', {})

    # Create Braille config from standards
    braille_config = BrailleConfig(
        enabled=True,
        grade=braille_config_dict.get('grade', 1),
        font_name=braille_config_dict.get('font_name', 'Helvetica'),
        font_size=braille_config_dict.get('font_size', 10),
        offset_x=braille_config_dict.get('offset_x', 5),
        offset_y=braille_config_dict.get('offset_y', -10),
        max_label_length=braille_config_dict.get('max_label_length', 30)
    )

    # Create sample image
    logger.info("Creating sample floor plan image")
    image = create_sample_image_with_text()

    # Create sample detected texts
    detected_texts = create_sample_detected_texts()
    logger.info(f"Created {len(detected_texts)} sample text detections")

    # Convert to Braille labels
    converter = BrailleConverter(braille_config, logger)
    braille_labels = converter.create_braille_labels(detected_texts)

    # Generate PDF with Braille labels
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "braille_demo_output.pdf"

    pdf_config = {
        'braille': {
            'font_name': braille_config.font_name,
            'font_size': braille_config.font_size
        }
    }

    pdf_gen = PIAFPDFGenerator(logger=logger, config=pdf_config)

    logger.generating("PDF with Braille labels")
    result_path = pdf_gen.generate(
        image=image,
        output_path=str(output_path),
        paper_size='letter',
        metadata={
            'source_file': 'braille_demo_floorplan',
            'braille_grade': braille_config.grade,
            'label_count': len(braille_labels)
        },
        braille_labels=braille_labels
    )

    print(f"\nOutput saved to: {result_path}")
    print(f"Braille labels added: {len(braille_labels)}")
    print(f"Braille grade: {braille_config.grade}")


def demo_label_comparison():
    """Compare Grade 1 and Grade 2 Braille for same text."""
    print("\n" + "="*60)
    print("DEMO 4: Grade 1 vs Grade 2 Comparison")
    print("="*60)

    logger = AccessibleLogger(verbose=False)

    sample_texts = [
        "Kitchen",
        "Bathroom",
        "Living Room",
        "Hallway",
        "and",
        "the",
    ]

    print(f"\n{'Text':<15} {'Grade 1':<30} {'Grade 2':<30}")
    print("-" * 75)

    for text in sample_texts:
        # Grade 1
        config_g1 = BrailleConfig(enabled=True, grade=1)
        converter_g1 = BrailleConverter(config_g1, logger)
        braille_g1 = converter_g1.convert_text(text)

        # Grade 2
        config_g2 = BrailleConfig(enabled=True, grade=2)
        converter_g2 = BrailleConverter(config_g2, logger)
        braille_g2 = converter_g2.convert_text(text)

        print(f"{text:<15} {braille_g1:<30} {braille_g2:<30}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("BRAILLE CONVERSION MODULE DEMONSTRATION")
    print("Fabric Accessible Graphics Toolkit - Phase 3")
    print("="*60)

    try:
        # Check if liblouis is installed
        import louis
        print(f"\nLiblouis version: {louis.version()}")

    except ImportError:
        print("\nError: Liblouis not installed")
        print("Please install with: pip install liblouis")
        print("\nSkipping demonstrations...")
        return 1

    try:
        # Run demonstrations
        demo_grade1_braille()
        demo_grade2_braille()
        demo_label_comparison()
        demo_pdf_generation_with_braille()

        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60)
        print("\nKey features demonstrated:")
        print("  - Grade 1 and Grade 2 Braille conversion")
        print("  - Unicode Braille output (U+2800-U+28FF)")
        print("  - Label positioning with configurable offsets")
        print("  - PDF integration with Braille labels")
        print("  - YAML configuration support")
        print("\nFor more information, see:")
        print("  - src/fabric_access/core/braille_converter.py")
        print("  - src/fabric_access/data/tactile_standards.yaml")

        return 0

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
