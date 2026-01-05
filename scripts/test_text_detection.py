#!/usr/bin/env python3
"""
Test script for text detection module.

This script tests the text detection functionality on sample architectural drawings.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fabric_access.core.text_detector import TextDetector, TextDetectionConfig, TextDetectionError
from fabric_access.utils.logger import AccessibleLogger
from PIL import Image


def test_tesseract_installation():
    """Test if Tesseract is installed and accessible."""
    print("=" * 60)
    print("TEST 1: Tesseract Installation Check")
    print("=" * 60)

    logger = AccessibleLogger(verbose=True)

    try:
        config = TextDetectionConfig(
            enabled=True,
            language='eng',
            page_segmentation_mode=3,
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
        print("\nResult: Tesseract is properly installed and accessible")
        print("Status: PASS")
        return True, detector

    except TextDetectionError as e:
        print(f"\nResult: {e}")
        print("Status: FAIL")
        print("\nInstallation Instructions:")
        print("  - Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  - macOS: brew install tesseract")
        print("  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False, None


def test_text_detection_on_image(detector, image_path):
    """Test text detection on a specific image."""
    print("\n" + "=" * 60)
    print(f"TEST 2: Text Detection on {Path(image_path).name}")
    print("=" * 60)

    logger = AccessibleLogger(verbose=True)

    try:
        # Load image
        print(f"\nLoading: {image_path}")
        image = Image.open(image_path)

        # Convert to grayscale if needed
        if image.mode not in ('L', 'RGB'):
            image = image.convert('L')
        elif image.mode == 'RGB':
            print("Converting to grayscale for better OCR accuracy")
            image = image.convert('L')

        print(f"Image size: {image.size[0]}x{image.size[1]} pixels")
        print(f"Image mode: {image.mode}")

        # Detect text
        print("\nRunning OCR (this may take a few seconds)...")
        detected_texts = detector.detect_text(image)

        # Display results
        print(f"\nTotal text elements detected: {len(detected_texts)}")

        dimensions = [dt for dt in detected_texts if dt.is_dimension]
        other_text = [dt for dt in detected_texts if not dt.is_dimension]

        print(f"Dimensions detected: {len(dimensions)}")
        print(f"Other text detected: {len(other_text)}")

        if dimensions:
            print("\nDimensions found:")
            for i, dt in enumerate(dimensions, 1):
                print(f"  {i}. '{dt.text}' at ({dt.x}, {dt.y}) - confidence: {dt.confidence:.1f}%")

        if other_text:
            print("\nOther text found:")
            for i, dt in enumerate(other_text[:10], 1):  # Limit to first 10
                print(f"  {i}. '{dt.text}' at ({dt.x}, {dt.y}) - confidence: {dt.confidence:.1f}%")
            if len(other_text) > 10:
                print(f"  ... and {len(other_text) - 10} more")

        print("\nStatus: PASS")
        return True

    except Exception as e:
        print(f"\nError: {e}")
        print("Status: FAIL")
        import traceback
        traceback.print_exc()
        return False


def test_dimension_pattern_matching(detector):
    """Test dimension pattern matching."""
    print("\n" + "=" * 60)
    print("TEST 3: Dimension Pattern Matching")
    print("=" * 60)

    test_cases = [
        ("10'", True, "Feet"),
        ('6"', True, "Inches"),
        ("10'-6\"", True, "Feet and inches"),
        ("3.5'", True, "Decimal feet"),
        ("120mm", True, "Millimeters"),
        ("3m", True, "Meters"),
        ("50cm", True, "Centimeters"),
        ("ABC", False, "Random text"),
        ("Room A", False, "Room label"),
        ("123", False, "Plain number"),
    ]

    passed = 0
    failed = 0

    print("\nTesting pattern matching:")
    for text, should_match, description in test_cases:
        is_dimension = detector._is_dimension(text)
        status = "PASS" if is_dimension == should_match else "FAIL"
        result = "dimension" if is_dimension else "not dimension"

        print(f"  '{text}' ({description}): {result} - {status}")

        if is_dimension == should_match:
            passed += 1
        else:
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    print(f"Status: {'PASS' if failed == 0 else 'FAIL'}")

    return failed == 0


def test_integration_with_processor():
    """Test integration with ImageProcessor."""
    print("\n" + "=" * 60)
    print("TEST 4: Integration with ImageProcessor")
    print("=" * 60)

    try:
        from fabric_access.core.processor import ImageProcessor
        from fabric_access.config.standards_loader import StandardsLoader

        # Load configuration with text detection enabled
        loader = StandardsLoader()
        config = loader.get_all_config()
        config['text_detection']['enabled'] = True

        logger = AccessibleLogger(verbose=True)
        processor = ImageProcessor(config=config, logger=logger)

        # Check that text detector was initialized
        if processor.text_detector is None:
            print("\nResult: Text detector not initialized")
            print("Status: FAIL")
            return False

        print("\nResult: ImageProcessor successfully initialized with text detector")
        print("Status: PASS")
        return True

    except Exception as e:
        print(f"\nError: {e}")
        print("Status: FAIL")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("FABRIC ACCESSIBLE GRAPHICS - TEXT DETECTION TEST SUITE")
    print("=" * 60)

    # Test 1: Installation check
    tesseract_ok, detector = test_tesseract_installation()

    if not tesseract_ok:
        print("\n" + "=" * 60)
        print("OVERALL RESULT: FAIL")
        print("Tesseract is not installed. Please install it to continue.")
        print("=" * 60)
        return

    # Test 2: Text detection on actual image
    test_images = [
        "/mnt/c/Users/ethan/fabric-accessible-graphics/ANNEX-PLANS-OFFICIAL_Page_1.jpg",
        "/mnt/c/Users/ethan/fabric-accessible-graphics/test-floor-plan.png",
        "/mnt/c/Users/ethan/fabric-accessible-graphics/Plan_Test.png"
    ]

    image_test_passed = False
    for image_path in test_images:
        if Path(image_path).exists():
            image_test_passed = test_text_detection_on_image(detector, image_path)
            break  # Only test first available image

    if not image_test_passed:
        print("\nWarning: No test images found or text detection failed")

    # Test 3: Pattern matching
    pattern_test_passed = test_dimension_pattern_matching(detector)

    # Test 4: Integration test
    integration_test_passed = test_integration_with_processor()

    # Overall results
    print("\n" + "=" * 60)
    print("OVERALL TEST RESULTS")
    print("=" * 60)
    print(f"Tesseract Installation: {'PASS' if tesseract_ok else 'FAIL'}")
    print(f"Text Detection: {'PASS' if image_test_passed else 'SKIP/FAIL'}")
    print(f"Pattern Matching: {'PASS' if pattern_test_passed else 'FAIL'}")
    print(f"Processor Integration: {'PASS' if integration_test_passed else 'FAIL'}")

    all_passed = tesseract_ok and pattern_test_passed and integration_test_passed
    print(f"\nOVERALL STATUS: {'PASS' if all_passed else 'PARTIAL/FAIL'}")
    print("=" * 60)


if __name__ == '__main__':
    main()
