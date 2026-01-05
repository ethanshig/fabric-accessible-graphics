#!/usr/bin/env python3
"""
OCR Comparison Test Script

Compares Tesseract OCR results with Claude Vision text extraction.
Creates separate visualization images showing bounding boxes for each method.

Output:
- tesseract_ocr_boxes.png - Tesseract detections with red boxes
- claude_vision_boxes.png - Claude Vision detections with blue boxes
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from PIL import Image, ImageDraw, ImageFont
from fabric_access.core.text_detector import TextDetector, TextDetectionConfig
from fabric_access.utils.logger import AccessibleLogger


def run_tesseract_ocr(image_path: str):
    """Run Tesseract OCR and return detected texts."""
    print("Running Tesseract OCR...")

    logger = AccessibleLogger(verbose=False)

    config = TextDetectionConfig(
        enabled=True,
        language='eng',
        page_segmentation_mode=3,  # Fully automatic
        min_confidence=60,
        filter_dimensions=True,
        dimension_patterns=[
            r"\d+['\"]",
            r"\d+\.\d+['\"]",
            r"\d+-\d+['\"]",
            r"\d+m",
            r"\d+mm",
            r"\d+cm"
        ]
    )

    detector = TextDetector(config=config, logger=logger)

    image = Image.open(image_path)
    if image.mode == 'RGB' or image.mode == 'RGBA':
        gray_image = image.convert('L')
    else:
        gray_image = image

    detected_texts = detector.detect_text(gray_image)

    print(f"  Tesseract found {len(detected_texts)} text regions")
    return detected_texts, image


def create_tesseract_visualization(image: Image.Image, detected_texts: list, output_path: str):
    """Create visualization with Tesseract bounding boxes."""
    print(f"Creating Tesseract visualization...")

    # Convert to RGB for colored boxes
    vis_image = image.convert('RGB')
    draw = ImageDraw.Draw(vis_image)

    # Red color for Tesseract boxes
    box_color = (255, 0, 0)  # Red
    text_color = (255, 0, 0)
    box_width = 3

    # Try to load a font for confidence labels
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    except:
        font = ImageFont.load_default()

    for dt in detected_texts:
        x1, y1 = dt.x, dt.y
        x2, y2 = dt.x + dt.width, dt.y + dt.height

        # Draw bounding box
        draw.rectangle([x1, y1, x2, y2], outline=box_color, width=box_width)

        # Draw confidence score above the box
        conf_text = f"{dt.confidence:.0f}%"
        draw.text((x1, y1 - 20), conf_text, fill=text_color, font=font)

    vis_image.save(output_path)
    print(f"  Saved: {output_path}")
    return vis_image


def create_claude_visualization(image: Image.Image, claude_texts: list, output_path: str):
    """Create visualization with Claude Vision bounding boxes."""
    print(f"Creating Claude Vision visualization...")

    # Convert to RGB for colored boxes
    vis_image = image.convert('RGB')
    draw = ImageDraw.Draw(vis_image)

    # Blue color for Claude boxes
    box_color = (0, 100, 255)  # Blue
    text_color = (0, 100, 255)
    box_width = 3

    # Try to load a font
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    except:
        font = ImageFont.load_default()

    for item in claude_texts:
        x = item.get('x', 0)
        y = item.get('y', 0)
        width = item.get('width', 50)
        height = item.get('height', 20)
        confidence = item.get('confidence', 'medium')

        x1, y1 = x, y
        x2, y2 = x + width, y + height

        # Draw bounding box
        draw.rectangle([x1, y1, x2, y2], outline=box_color, width=box_width)

        # Draw confidence label
        draw.text((x1, y1 - 20), confidence, fill=text_color, font=font)

    vis_image.save(output_path)
    print(f"  Saved: {output_path}")
    return vis_image


def print_tesseract_results(detected_texts: list):
    """Print Tesseract results for analysis."""
    print("\n" + "=" * 70)
    print("TESSERACT OCR RESULTS")
    print("=" * 70)

    # Group by type
    dimensions = [dt for dt in detected_texts if dt.is_dimension]
    other = [dt for dt in detected_texts if not dt.is_dimension]

    print(f"\nDimensions detected: {len(dimensions)}")
    for i, dt in enumerate(dimensions[:20], 1):
        print(f"  {i}. '{dt.text}' at ({dt.x}, {dt.y}) size {dt.width}x{dt.height} conf={dt.confidence:.0f}%")
    if len(dimensions) > 20:
        print(f"  ... and {len(dimensions) - 20} more")

    print(f"\nOther text detected: {len(other)}")
    for i, dt in enumerate(other[:30], 1):
        print(f"  {i}. '{dt.text}' at ({dt.x}, {dt.y}) size {dt.width}x{dt.height} conf={dt.confidence:.0f}%")
    if len(other) > 30:
        print(f"  ... and {len(other) - 30} more")


def main():
    """Run OCR comparison test."""
    print("=" * 70)
    print("OCR COMPARISON TEST")
    print("=" * 70)

    # Paths
    image_path = "/mnt/c/Users/ethan/fabric-accessible-graphics/samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg"
    output_dir = Path("/mnt/c/Users/ethan/fabric-accessible-graphics/outputs/test-results")
    output_dir.mkdir(parents=True, exist_ok=True)

    tesseract_output = output_dir / "tesseract_ocr_boxes.png"
    claude_output = output_dir / "claude_vision_boxes.png"

    # Run Tesseract OCR
    detected_texts, image = run_tesseract_ocr(image_path)
    print_tesseract_results(detected_texts)

    # Create Tesseract visualization
    create_tesseract_visualization(image, detected_texts, str(tesseract_output))

    # Check for Claude Vision results file
    claude_json_path = output_dir / "claude_vision_results.json"

    if claude_json_path.exists():
        print(f"\nLoading Claude Vision results from {claude_json_path}")
        with open(claude_json_path, 'r') as f:
            claude_texts = json.load(f)
        print(f"  Claude found {len(claude_texts)} text regions")
        create_claude_visualization(image, claude_texts, str(claude_output))
    else:
        print(f"\n[INFO] Claude Vision results not found at: {claude_json_path}")
        print("To generate Claude Vision visualization:")
        print("1. Have Claude view the image and extract text with bounding boxes")
        print("2. Save the results as JSON to the path above")
        print("3. Re-run this script")

    print("\n" + "=" * 70)
    print("COMPARISON COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  - Tesseract: {tesseract_output}")
    if claude_json_path.exists():
        print(f"  - Claude:    {claude_output}")
    print("\nCompare the images to evaluate OCR accuracy.")


if __name__ == '__main__':
    main()
