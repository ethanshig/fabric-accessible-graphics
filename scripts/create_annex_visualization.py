#!/usr/bin/env python3
"""
Create visualization of text detection on ANNEX-PLANS-OFFICIAL_Page_1.jpg
with bounding boxes drawn around all detected text.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PIL import Image, ImageDraw
from fabric_access.core.text_detector import TextDetector, TextDetectionConfig
from fabric_access.utils.logger import AccessibleLogger


def create_text_visualization(input_path: str, output_path: str):
    """
    Create a visualization with bounding boxes around detected text.

    Args:
        input_path: Path to input image
        output_path: Path to save the visualization
    """
    print("=" * 70)
    print("Creating Text Detection Visualization")
    print("=" * 70)

    # Initialize logger
    logger = AccessibleLogger(verbose=True)

    # Configure text detector
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

    # Create text detector
    print("\nInitializing text detector...")
    detector = TextDetector(config=config, logger=logger)

    # Load the image
    print(f"\nLoading image: {input_path}")
    image = Image.open(input_path)
    print(f"Image size: {image.size[0]}x{image.size[1]} pixels")
    print(f"Image mode: {image.mode}")

    # Convert to grayscale for OCR
    if image.mode == 'RGB' or image.mode == 'RGBA':
        grayscale_image = image.convert('L')
    else:
        grayscale_image = image

    # Detect text
    print("\nRunning text detection (this may take a few seconds)...")
    detected_texts = detector.detect_text(grayscale_image)

    print(f"\nTotal text elements detected: {len(detected_texts)}")

    dimensions = [dt for dt in detected_texts if dt.is_dimension]
    other_text = [dt for dt in detected_texts if not dt.is_dimension]

    print(f"Dimensions detected: {len(dimensions)}")
    print(f"Other text detected: {len(other_text)}")

    # Create RGB copy of image for drawing colored boxes
    if image.mode == 'L':
        vis_image = image.convert('RGB')
    elif image.mode == 'RGBA':
        vis_image = image.convert('RGB')
    else:
        vis_image = image.copy()

    # Draw bounding boxes on the image
    print("\nDrawing bounding boxes...")
    draw = ImageDraw.Draw(vis_image)

    # Red color for bounding boxes (matching example-visualization.png style)
    box_color = (255, 0, 0)  # Red
    box_width = 2  # Line thickness

    for dt in detected_texts:
        # Draw rectangle around detected text
        x1, y1 = dt.x, dt.y
        x2, y2 = dt.x + dt.width, dt.y + dt.height

        # Draw the bounding box
        draw.rectangle([x1, y1, x2, y2], outline=box_color, width=box_width)

    # Save the visualization
    print(f"\nSaving visualization to: {output_path}")
    vis_image.save(output_path)

    # Print summary of detected texts
    print("\n" + "=" * 70)
    print("DETECTED TEXT SUMMARY")
    print("=" * 70)

    if dimensions:
        print("\nDimensions found:")
        for i, dt in enumerate(dimensions[:20], 1):
            print(f"  {i}. '{dt.text}' at ({dt.x}, {dt.y}) - confidence: {dt.confidence:.1f}%")
        if len(dimensions) > 20:
            print(f"  ... and {len(dimensions) - 20} more")

    if other_text:
        print(f"\nOther text found (showing first 30 of {len(other_text)}):")
        for i, dt in enumerate(other_text[:30], 1):
            print(f"  {i}. '{dt.text}' at ({dt.x}, {dt.y}) - confidence: {dt.confidence:.1f}%")
        if len(other_text) > 30:
            print(f"  ... and {len(other_text) - 30} more")

    print("\n" + "=" * 70)
    print("VISUALIZATION COMPLETE")
    print(f"Output saved to: {output_path}")
    print("=" * 70)


def main():
    """Main entry point."""
    input_path = "/mnt/c/Users/ethan/fabric-accessible-graphics/ANNEX-PLANS-OFFICIAL_Page_1.jpg"
    output_path = "/mnt/c/Users/ethan/fabric-accessible-graphics/annex-text-visualization.png"

    create_text_visualization(input_path, output_path)


if __name__ == '__main__':
    main()
