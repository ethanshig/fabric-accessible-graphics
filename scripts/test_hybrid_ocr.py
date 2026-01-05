#!/usr/bin/env python3
"""
Test Script for Hybrid OCR Approach

Tests the combination of Tesseract position detection with Claude Vision
text reading for improved Braille conversion accuracy.

Usage:
    python test_hybrid_ocr.py [--image PATH] [--claude-json PATH]
"""

import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from PIL import Image, ImageDraw, ImageFont
from fabric_access.core.text_detector import TextDetector, TextDetectionConfig, DetectedText
from fabric_access.core.hybrid_text_detector import HybridTextDetector
from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig
from fabric_access.core.processor import ImageProcessor
from fabric_access.core.pdf_generator import PIAFPDFGenerator
from fabric_access.config.standards_loader import StandardsLoader
from fabric_access.utils.cache import cache_tesseract_results, load_cached_tesseract, get_cache_stats


class SilentLogger:
    """Silent logger for testing."""
    def info(self, *args): pass
    def warning(self, *args): pass
    def error(self, *args, **kwargs): pass
    def progress(self, *args): pass
    def success(self, *args): pass
    def loading(self, *args): pass
    def checking(self, *args): pass
    def found(self, *args): pass
    def generating(self, *args): pass
    def complete(self, *args): pass
    def blank_line(self): pass
    def solution(self, *args): pass


def convert_claude_coords_to_percent(claude_results, image_size):
    """
    Convert Claude Vision pixel coordinates to normalized percentages.

    The existing test data uses pixel coordinates - convert to percentages
    for the hybrid approach.
    """
    width, height = image_size
    converted = []

    for item in claude_results:
        converted.append({
            'text': item['text'],
            'x_percent': (item['x'] / width) * 100,
            'y_percent': (item['y'] / height) * 100,
            'width_percent': (item.get('width', 50) / width) * 100,
            'height_percent': (item.get('height', 20) / height) * 100,
            'type': item.get('type', 'printed'),
            'confidence': item.get('confidence', 'medium')
        })

    return converted


def run_tesseract_detection(image_path: str, logger) -> list:
    """Run Tesseract OCR on the image."""
    config = TextDetectionConfig(
        enabled=True,
        language='eng',
        page_segmentation_mode=3,
        min_confidence=50,
        filter_dimensions=True
    )

    detector = TextDetector(config=config, logger=logger)
    image = Image.open(image_path).convert('L')
    results = detector.detect_text(image)

    return results


def visualize_results(image_path: str, tesseract: list, claude: list,
                      merged: list, output_path: str):
    """Create a visualization showing all three detection methods."""
    image = Image.open(image_path).convert('RGB')
    draw = ImageDraw.Draw(image)

    # Colors for each source
    colors = {
        'tesseract': (255, 0, 0),    # Red
        'claude': (0, 255, 0),        # Green
        'merged': (0, 0, 255)         # Blue
    }

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        font = ImageFont.load_default()

    # Draw Tesseract results (red, offset up)
    for t in tesseract[:15]:  # Limit to avoid clutter
        x, y, w, h = t.x, t.y, t.width, t.height
        draw.rectangle([x, y-2, x+w, y+h-2], outline=colors['tesseract'], width=1)

    # Draw Claude results (green, offset down)
    width, height = image.size
    for c in claude:
        x = int(c['x_percent'] / 100 * width)
        y = int(c['y_percent'] / 100 * height)
        w = int(c.get('width_percent', 5) / 100 * width)
        h = int(c.get('height_percent', 3) / 100 * height)
        draw.rectangle([x, y+2, x+w, y+h+2], outline=colors['claude'], width=1)

    # Draw merged results (blue, dashed effect using dots)
    for m in merged:
        x, y, w, h = m.x, m.y, m.width, m.height
        draw.rectangle([x-1, y-1, x+w+1, y+h+1], outline=colors['merged'], width=2)

    # Add legend
    legend_y = 10
    draw.rectangle([10, legend_y, 200, legend_y + 70], fill=(255, 255, 255, 200))
    draw.text((15, legend_y + 5), "Red: Tesseract positions", fill=colors['tesseract'], font=font)
    draw.text((15, legend_y + 20), "Green: Claude Vision text", fill=colors['claude'], font=font)
    draw.text((15, legend_y + 35), "Blue: Merged (hybrid)", fill=colors['merged'], font=font)
    draw.text((15, legend_y + 50), f"Matched: {len(merged)} items", fill=(0, 0, 0), font=font)

    image.save(output_path)
    print(f"Visualization saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Test Hybrid OCR Approach')
    parser.add_argument('--image', default='samples/plan_test.jpg',
                        help='Path to test image')
    parser.add_argument('--claude-json',
                        default='outputs/test-results/plan_test_claude_vision.json',
                        help='Path to Claude Vision JSON results')
    parser.add_argument('--output-dir', default='outputs/test-results',
                        help='Output directory for results')

    args = parser.parse_args()

    # Resolve paths
    base_dir = Path(__file__).parent.parent
    image_path = base_dir / args.image
    claude_json_path = base_dir / args.claude_json
    output_dir = base_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    logger = SilentLogger()

    print("=" * 70)
    print("HYBRID OCR TEST")
    print("=" * 70)
    print(f"Image: {image_path}")
    print(f"Claude JSON: {claude_json_path}")
    print()

    # Verify files exist
    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return

    if not claude_json_path.exists():
        print(f"ERROR: Claude JSON not found: {claude_json_path}")
        print("Run OCR comparison test first to generate Claude Vision results.")
        return

    # Get image size
    with Image.open(image_path) as img:
        img_width, img_height = img.size
    print(f"Image size: {img_width}x{img_height}")

    # Step 1: Run Tesseract
    print("\n--- Step 1: Running Tesseract ---")
    tesseract_results = run_tesseract_detection(str(image_path), logger)
    print(f"Tesseract found: {len(tesseract_results)} text regions")

    # Filter out obvious noise
    filtered_tesseract = [t for t in tesseract_results
                         if len(t.text.strip()) >= 2
                         and t.text.strip() not in ['|', '\\', '/', '-', '_', '||']]
    print(f"After filtering noise: {len(filtered_tesseract)} regions")

    # Cache results (simulating Phase 1)
    cache_tesseract_results(str(image_path.absolute()), filtered_tesseract,
                           image_size=(img_width, img_height))
    print("Tesseract results cached.")

    # Step 2: Load Claude Vision results
    print("\n--- Step 2: Loading Claude Vision Results ---")
    with open(claude_json_path, 'r') as f:
        claude_raw = json.load(f)
    print(f"Claude Vision found: {len(claude_raw)} text items")

    # Convert pixel coords to percentages
    claude_results = convert_claude_coords_to_percent(claude_raw, (img_width, img_height))

    # Step 3: Run hybrid merge
    print("\n--- Step 3: Running Hybrid Merge ---")
    hybrid_detector = HybridTextDetector(similarity_threshold=0.6)

    # Get match statistics first
    stats = hybrid_detector.get_match_statistics(filtered_tesseract, claude_results)
    print(f"Match statistics:")
    print(f"  - Tesseract items: {stats['tesseract_count']}")
    print(f"  - Claude items: {stats['claude_count']}")
    print(f"  - Matched pairs: {stats['matched_count']}")
    print(f"  - Unmatched Claude: {stats['unmatched_claude']}")
    print(f"  - Unused Tesseract: {stats['unused_tesseract']}")
    if stats['match_scores']:
        print(f"  - Average match score: {stats['average_match_score']:.2f}")

    # Perform actual merge
    merged_results = hybrid_detector.merge(
        filtered_tesseract,
        claude_results,
        image_size=(img_width, img_height)
    )
    print(f"\nMerged results: {len(merged_results)} items")

    # Step 4: Show sample matches
    print("\n--- Step 4: Sample Merged Results ---")
    for i, result in enumerate(merged_results[:10]):
        print(f"  {i+1}. \"{result.text}\" at ({result.x}, {result.y}) "
              f"conf={result.confidence:.1f}% dim={result.is_dimension}")
    if len(merged_results) > 10:
        print(f"  ... and {len(merged_results) - 10} more")

    # Step 5: Create visualization
    print("\n--- Step 5: Creating Visualization ---")
    vis_path = output_dir / 'hybrid_ocr_comparison.png'
    visualize_results(str(image_path), filtered_tesseract, claude_results,
                     merged_results, str(vis_path))

    # Step 6: Generate test PDF with merged results
    print("\n--- Step 6: Generating Test PDF ---")
    try:
        standards = StandardsLoader()
        config = standards.get_all_config()

        # Process image
        processor = ImageProcessor(config=config, logger=logger)
        processed_image, metadata = processor.process(
            input_path=str(image_path),
            threshold=128,
            check_density_flag=True,
            detect_text=False  # We already have text
        )

        # Create Braille labels from merged results
        braille_config = BrailleConfig(
            enabled=True, grade=2, placement='overlay',
            font_name='DejaVu Sans', font_size=10,
            offset_x=5, offset_y=-10, max_label_length=30,
            truncate_suffix='...', font_color='black',
            detect_overlaps=True, min_label_spacing=6
        )

        converter = BrailleConverter(braille_config, logger)
        braille_labels, symbol_key = converter.create_braille_labels(merged_results)
        print(f"Created {len(braille_labels)} Braille labels")

        # Whiteout original text
        processed_image = processor.whiteout_text_regions(
            processed_image, merged_results, padding=5
        )

        # Generate PDF
        pdf_path = output_dir / 'hybrid_ocr_test.pdf'
        pdf_generator = PIAFPDFGenerator(logger=logger, config=config)
        result = pdf_generator.generate(
            image=processed_image,
            output_path=str(pdf_path),
            paper_size='letter',
            metadata={'original_size': (img_width, img_height)},
            braille_labels=braille_labels,
            symbol_key_entries=symbol_key,
            braille_converter=converter
        )
        print(f"PDF generated: {result}")

    except Exception as e:
        print(f"PDF generation failed: {e}")
        import traceback
        traceback.print_exc()

    # Step 7: Cache stats
    print("\n--- Cache Statistics ---")
    cache_stats = get_cache_stats()
    print(f"Cache directory: {cache_stats['cache_dir']}")
    print(f"Total entries: {cache_stats['total_entries']}")
    print(f"Active entries: {cache_stats['active_entries']}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  - Visualization: {vis_path}")
    print(f"  - PDF: {output_dir / 'hybrid_ocr_test.pdf'}")


if __name__ == '__main__':
    main()
