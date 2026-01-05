#!/usr/bin/env python3
"""
Demonstration of text detection feature in the processing pipeline.

This script demonstrates how to use the text detection module with
the ImageProcessor to detect dimensions and other text in architectural drawings.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fabric_access.core.processor import ImageProcessor
from fabric_access.config.standards_loader import StandardsLoader
from fabric_access.utils.logger import AccessibleLogger


def demo_text_detection(image_path: str):
    """
    Demonstrate text detection on an architectural drawing.

    Args:
        image_path: Path to image file
    """
    print("=" * 70)
    print("FABRIC ACCESSIBLE GRAPHICS - TEXT DETECTION DEMONSTRATION")
    print("=" * 70)
    print()

    # Initialize logger with verbose output
    logger = AccessibleLogger(verbose=True)

    # Load configuration
    print("Step 1: Loading configuration")
    print("-" * 70)
    loader = StandardsLoader()
    config = loader.get_all_config()

    # Enable text detection
    config['text_detection']['enabled'] = True
    print("Text detection: ENABLED")
    print(f"Language: {config['text_detection']['language']}")
    print(f"Minimum confidence: {config['text_detection']['min_confidence']}%")
    print(f"Filter dimensions: {config['text_detection']['filter_dimensions']}")
    print()

    # Initialize processor
    print("Step 2: Initializing image processor")
    print("-" * 70)
    processor = ImageProcessor(config=config, logger=logger)
    print()

    # Process image with text detection
    print("Step 3: Processing image with text detection")
    print("-" * 70)
    print(f"Input: {Path(image_path).name}")
    print()

    try:
        # Process with text detection enabled
        processed_image, metadata = processor.process(
            input_path=image_path,
            threshold=128,
            detect_text=True,  # Enable text detection
            enhance='s_curve',  # Apply enhancement for better image quality
            enhance_strength=1.0
        )

        # Display results
        print()
        print("=" * 70)
        print("TEXT DETECTION RESULTS")
        print("=" * 70)

        detected_texts = metadata.get('detected_texts', [])
        dimensions = [dt for dt in detected_texts if dt.is_dimension]
        other_text = [dt for dt in detected_texts if not dt.is_dimension]

        print(f"\nTotal text elements detected: {len(detected_texts)}")
        print(f"Dimensions detected: {len(dimensions)}")
        print(f"Other text detected: {len(other_text)}")

        if dimensions:
            print("\n" + "-" * 70)
            print("DIMENSIONS FOUND:")
            print("-" * 70)
            for i, dt in enumerate(dimensions, 1):
                print(f"{i:3d}. '{dt.text}'")
                print(f"     Location: ({dt.x}, {dt.y})")
                print(f"     Size: {dt.width}x{dt.height} pixels")
                print(f"     Confidence: {dt.confidence:.1f}%")
                print()

        if other_text:
            print("-" * 70)
            print(f"OTHER TEXT FOUND (showing first 20 of {len(other_text)}):")
            print("-" * 70)
            for i, dt in enumerate(other_text[:20], 1):
                print(f"{i:3d}. '{dt.text}' at ({dt.x}, {dt.y}) - "
                      f"confidence: {dt.confidence:.1f}%")

        # Display processing metadata
        print()
        print("=" * 70)
        print("PROCESSING METADATA")
        print("=" * 70)
        print(f"Source file: {metadata['source_file']}")
        print(f"Original size: {metadata['original_size']}")
        print(f"Threshold: {metadata['threshold']}")
        print(f"Enhancement: {metadata['enhancement']}")
        if metadata['density_percentage']:
            print(f"Black pixel density: {metadata['density_percentage']:.1f}%")
        print()

        print("=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run demonstration."""
    # Check for command line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use default test image
        test_images = [
            "/mnt/c/Users/ethan/fabric-accessible-graphics/ANNEX-PLANS-OFFICIAL_Page_1.jpg",
            "/mnt/c/Users/ethan/fabric-accessible-graphics/test-floor-plan.png",
            "/mnt/c/Users/ethan/fabric-accessible-graphics/Plan_Test.png"
        ]

        # Find first available image
        image_path = None
        for path in test_images:
            if Path(path).exists():
                image_path = path
                break

        if not image_path:
            print("Error: No test images found")
            print("Usage: python demo_text_detection.py <image_path>")
            sys.exit(1)

    # Run demonstration
    demo_text_detection(image_path)


if __name__ == '__main__':
    main()
