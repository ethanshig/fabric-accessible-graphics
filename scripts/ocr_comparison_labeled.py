#!/usr/bin/env python3
"""
OCR Comparison with Labeled Boxes

Creates visualizations where each detected text region is:
- Numbered with a visible label
- Shows the detected text next to the box
- Outputs a legend showing all detections

This makes it easy to see exactly what each OCR method found.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from PIL import Image, ImageDraw, ImageFont
from fabric_access.core.text_detector import TextDetector, TextDetectionConfig


def get_font(size=20):
    """Get a font, with fallback."""
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size)
    except:
        try:
            return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
        except:
            return ImageFont.load_default()


def create_labeled_visualization(image: Image.Image, detections: list, output_path: str,
                                  box_color: tuple, title: str):
    """
    Create a visualization with numbered, labeled boxes.

    Each detection gets:
    - A numbered circle at the box corner
    - The detected text displayed near the box
    """
    vis_image = image.convert('RGB')
    draw = ImageDraw.Draw(vis_image)

    font_large = get_font(24)
    font_small = get_font(16)
    font_number = get_font(20)

    box_width = 3

    # Draw all boxes with numbers
    for i, det in enumerate(detections, 1):
        if isinstance(det, dict):
            x, y = det.get('x', 0), det.get('y', 0)
            w, h = det.get('width', 50), det.get('height', 20)
            text = det.get('text', '')
            conf = det.get('confidence', 'N/A')
        else:
            # DetectedText object
            x, y, w, h = det.x, det.y, det.width, det.height
            text = det.text
            conf = f"{det.confidence:.0f}%"

        x1, y1 = x, y
        x2, y2 = x + w, y + h

        # Draw bounding box
        draw.rectangle([x1, y1, x2, y2], outline=box_color, width=box_width)

        # Draw number circle at top-left corner
        circle_radius = 18
        cx, cy = x1 - circle_radius, y1 - circle_radius
        draw.ellipse([cx - circle_radius, cy - circle_radius,
                      cx + circle_radius, cy + circle_radius],
                     fill=box_color, outline='white', width=2)

        # Draw number in circle
        num_text = str(i)
        draw.text((cx - 8, cy - 12), num_text, fill='white', font=font_number)

        # Draw detected text below the box (with white background for readability)
        label = f"{text[:25]}{'...' if len(text) > 25 else ''}"
        text_bbox = draw.textbbox((0, 0), label, font=font_small)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        label_x = x1
        label_y = y2 + 5

        # White background for label
        draw.rectangle([label_x - 2, label_y - 2,
                        label_x + text_w + 4, label_y + text_h + 4],
                       fill='white', outline=box_color)
        draw.text((label_x, label_y), label, fill=box_color, font=font_small)

    # Add title at top
    draw.rectangle([0, 0, vis_image.width, 60], fill='white')
    draw.text((20, 15), f"{title} - {len(detections)} items detected",
              fill=box_color, font=font_large)

    vis_image.save(output_path)
    print(f"Saved: {output_path}")
    return vis_image


def create_legend(detections: list, output_path: str, title: str):
    """Create a text legend listing all detections."""
    lines = [f"{'='*70}", f"{title}", f"{'='*70}", ""]

    for i, det in enumerate(detections, 1):
        if isinstance(det, dict):
            text = det.get('text', '')
            x, y = det.get('x', 0), det.get('y', 0)
            w, h = det.get('width', 0), det.get('height', 0)
            conf = det.get('confidence', 'N/A')
            dtype = det.get('type', 'unknown')
        else:
            text = det.text
            x, y, w, h = det.x, det.y, det.width, det.height
            conf = f"{det.confidence:.0f}%"
            dtype = "dimension" if det.is_dimension else "text"

        lines.append(f"{i:3}. \"{text}\"")
        lines.append(f"     Position: ({x}, {y}) Size: {w}x{h}")
        lines.append(f"     Confidence: {conf}, Type: {dtype}")
        lines.append("")

    legend_text = "\n".join(lines)

    with open(output_path, 'w') as f:
        f.write(legend_text)

    print(f"Saved legend: {output_path}")
    return legend_text


def run_tesseract(image_path: str):
    """Run Tesseract OCR."""
    from fabric_access.utils.logger import AccessibleLogger

    config = TextDetectionConfig(
        enabled=True, language='eng', page_segmentation_mode=3,
        min_confidence=60, filter_dimensions=True
    )

    detector = TextDetector(config=config, logger=AccessibleLogger(verbose=False))
    image = Image.open(image_path)
    gray = image.convert('L')

    detected = detector.detect_text(gray)
    return detected, image


def main():
    print("=" * 70)
    print("OCR COMPARISON WITH LABELED BOXES")
    print("=" * 70)

    image_path = "/mnt/c/Users/ethan/fabric-accessible-graphics/samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg"
    output_dir = Path("/mnt/c/Users/ethan/fabric-accessible-graphics/outputs/test-results")

    # Run Tesseract
    print("\nRunning Tesseract OCR...")
    tesseract_results, image = run_tesseract(image_path)
    print(f"  Found {len(tesseract_results)} items")

    # Filter Tesseract to remove obvious noise (single chars, pipes, etc.)
    meaningful_tesseract = [
        dt for dt in tesseract_results
        if len(dt.text.strip()) > 2 and dt.text.strip() not in ['|', '\\', '/', '-', '_', '||']
    ]
    print(f"  After filtering noise: {len(meaningful_tesseract)} items")

    # Create Tesseract visualization (filtered)
    create_labeled_visualization(
        image, meaningful_tesseract,
        str(output_dir / "tesseract_labeled.png"),
        (255, 0, 0),  # Red
        "TESSERACT OCR (filtered)"
    )

    # Create Tesseract legend
    create_legend(
        meaningful_tesseract,
        str(output_dir / "tesseract_legend.txt"),
        "TESSERACT OCR RESULTS (filtered)"
    )

    # Load Claude Vision results
    claude_json = output_dir / "claude_vision_results.json"
    if claude_json.exists():
        with open(claude_json) as f:
            claude_results = json.load(f)
        print(f"\nLoaded {len(claude_results)} Claude Vision results")

        # Create Claude visualization
        create_labeled_visualization(
            image, claude_results,
            str(output_dir / "claude_labeled.png"),
            (0, 100, 255),  # Blue
            "CLAUDE VISION"
        )

        # Create Claude legend
        create_legend(
            claude_results,
            str(output_dir / "claude_legend.txt"),
            "CLAUDE VISION RESULTS"
        )

    print("\n" + "=" * 70)
    print("OUTPUT FILES:")
    print("=" * 70)
    print(f"  tesseract_labeled.png  - Tesseract boxes with numbers and text labels")
    print(f"  tesseract_legend.txt   - Full list of Tesseract detections")
    print(f"  claude_labeled.png     - Claude boxes with numbers and text labels")
    print(f"  claude_legend.txt      - Full list of Claude detections")
    print("\nCompare the images to see exactly what each method detected!")


if __name__ == '__main__':
    main()
