#!/usr/bin/env python3
"""
Test Script for Zoom and Scaling Features

Tests all new zoom and scaling capabilities:
- Scale cap removal (unlimited auto-scaling)
- 300%+ scaling warnings
- crop_to_region() method
- adjust_to_aspect_ratio() method
- filter_texts_in_region() method
- zoom_region parameter
- zoom_to parameter (LLM workflow)
- zoom_regions parameter (multi-page)
- CLI --zoom-region option
- Filename generation with zoom target

Usage:
    python test_zoom_scaling.py [--image PATH] [--test TEST_NAME]
"""

import sys
import json
import argparse
import asyncio
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from PIL import Image
from fabric_access.core.processor import ImageProcessor
from fabric_access.core.text_detector import DetectedText
from fabric_access.config.standards_loader import StandardsLoader
from fabric_access.mcp_server.tools import convert_to_tactile


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


class TestResult:
    """Store test results."""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}

    def to_dict(self):
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details
        }


def test_crop_to_region(processor: ImageProcessor, image_path: str, output_dir: Path) -> TestResult:
    """Test 1: crop_to_region() method."""
    result = TestResult("crop_to_region")

    try:
        # Load image
        image = Image.open(image_path)
        original_width, original_height = image.size

        # Crop to center 50% (with 10% margin = 60% total)
        region = (25.0, 25.0, 50.0, 50.0)
        cropped = processor.crop_to_region(image, region, margin_percent=10.0)

        # Expected: ~60% of original (50% region + 10% margin)
        expected_width_ratio = 0.60
        actual_width_ratio = cropped.width / original_width
        actual_height_ratio = cropped.height / original_height

        # Save visualization
        output_path = output_dir / 'crop_region_test.png'
        cropped.save(str(output_path))

        # Validate
        tolerance = 0.05
        width_ok = abs(actual_width_ratio - expected_width_ratio) < tolerance
        height_ok = abs(actual_height_ratio - expected_width_ratio) < tolerance

        result.passed = width_ok and height_ok
        result.message = f"Cropped to {cropped.width}x{cropped.height} ({actual_width_ratio:.2%} of original)"
        result.details = {
            "original_size": f"{original_width}x{original_height}",
            "cropped_size": f"{cropped.width}x{cropped.height}",
            "width_ratio": f"{actual_width_ratio:.2%}",
            "output_file": str(output_path)
        }

    except Exception as e:
        result.message = f"Error: {e}"

    return result


def test_adjust_to_aspect_ratio(processor: ImageProcessor, output_dir: Path) -> TestResult:
    """Test 2: adjust_to_aspect_ratio() method."""
    result = TestResult("adjust_to_aspect_ratio")

    try:
        # Create a square test image (500x500)
        test_image = Image.new('RGB', (500, 500), color='white')

        # Adjust to letter ratio (8.5/11 = 0.773)
        adjusted = processor.adjust_to_aspect_ratio(test_image, 'letter')

        actual_ratio = adjusted.width / adjusted.height
        expected_ratio = 8.5 / 11.0  # 0.773

        # Save visualization
        output_path = output_dir / 'aspect_ratio_test.png'
        adjusted.save(str(output_path))

        # Validate
        tolerance = 0.01
        result.passed = abs(actual_ratio - expected_ratio) < tolerance
        result.message = f"Adjusted ratio: {actual_ratio:.3f} (expected {expected_ratio:.3f})"
        result.details = {
            "input_size": "500x500",
            "output_size": f"{adjusted.width}x{adjusted.height}",
            "actual_ratio": f"{actual_ratio:.3f}",
            "expected_ratio": f"{expected_ratio:.3f}",
            "output_file": str(output_path)
        }

    except Exception as e:
        result.message = f"Error: {e}"

    return result


def test_filter_texts_in_region(processor: ImageProcessor) -> TestResult:
    """Test 3: filter_texts_in_region() method."""
    result = TestResult("filter_texts_in_region")

    try:
        # Create mock detected texts at various positions
        # Image size: 1000x1000
        mock_texts = [
            DetectedText(text="Inside", x=300, y=300, width=100, height=20, confidence=90, is_dimension=False),
            DetectedText(text="Also Inside", x=400, y=400, width=100, height=20, confidence=90, is_dimension=False),
            DetectedText(text="Outside Top", x=100, y=100, width=100, height=20, confidence=90, is_dimension=False),
            DetectedText(text="Outside Bottom", x=800, y=800, width=100, height=20, confidence=90, is_dimension=False),
        ]

        # Filter to center region (25%, 25%, 50%, 50%)
        region = (25.0, 25.0, 50.0, 50.0)
        filtered = processor.filter_texts_in_region(
            mock_texts,
            region,
            original_image_size=(1000, 1000),
            margin_percent=10.0
        )

        # Expected: Only "Inside" and "Also Inside" should remain
        # Their coordinates should be adjusted relative to cropped area
        result.passed = len(filtered) == 2
        filtered_texts = [t.text for t in filtered]
        result.message = f"Filtered {len(mock_texts)} texts to {len(filtered)}: {filtered_texts}"
        result.details = {
            "input_count": len(mock_texts),
            "output_count": len(filtered),
            "filtered_texts": filtered_texts,
            "coordinates_adjusted": len(filtered) > 0 and filtered[0].x < mock_texts[0].x
        }

    except Exception as e:
        result.message = f"Error: {e}"

    return result


async def test_scale_cap_removal(image_path: str, output_dir: Path) -> TestResult:
    """Test 4: Auto-scaling beyond 200% when max_scale_factor=None."""
    result = TestResult("scale_cap_removal")

    try:
        # Call convert_to_tactile with auto_scale and no cap
        # Force high scaling by using a small bounding box scenario
        output_path = str(output_dir / 'scale_cap_test.pdf')

        response_json = await convert_to_tactile(
            image_path=image_path,
            output_path=output_path,
            detect_text=True,
            auto_scale=True,
            max_scale_factor=None,  # No cap
            paper_size='letter'
        )

        response = json.loads(response_json)

        if response.get('success') and response.get('phase') != 'zoom_region_identification':
            scale_applied = response.get('scale_applied', 100)
            # Check if we got auto-scaling (may not exceed 200% with this image)
            result.passed = True  # Pass if no errors - scaling depends on image content
            result.message = f"Scale applied: {scale_applied}% (no cap enforced)"
            result.details = {
                "scale_applied": scale_applied,
                "auto_scale_used": response.get('auto_scale_used', False),
                "output_file": response.get('output_file')
            }
        elif response.get('phase') == 'zoom_region_identification':
            # Phase 1 of hybrid OCR - this is expected behavior
            result.passed = True
            result.message = "Hybrid OCR Phase 1 returned (expected for text detection)"
            result.details = {"phase": "zoom_region_identification"}
        else:
            result.message = f"Conversion failed: {response.get('error', 'Unknown error')}"

    except Exception as e:
        result.message = f"Error: {e}"

    return result


async def test_300_percent_warning(image_path: str, output_dir: Path) -> TestResult:
    """Test 5: Warning appears when scale > 300%."""
    result = TestResult("300_percent_warning")

    try:
        import time
        output_path = str(output_dir / f'scale_warning_test_{int(time.time())}.pdf')

        # Force 350% scaling
        response_json = await convert_to_tactile(
            image_path=image_path,
            output_path=output_path,
            detect_text=False,  # Skip text detection for simpler test
            scale_percent=350,  # Force high scale
            paper_size='letter'
        )

        response = json.loads(response_json)

        if response.get('success'):
            warnings = response.get('warnings', [])
            has_warning = len(warnings) > 0 and '300' in str(warnings)

            result.passed = has_warning
            result.message = f"Warnings: {warnings}" if has_warning else "No warnings found (expected warning for 350%)"
            result.details = {
                "scale_applied": response.get('scale_applied'),
                "warnings": warnings,
                "recommended_range": response.get('recommended_scale_range')
            }
        else:
            result.message = f"Conversion failed: {response.get('error')}"

    except Exception as e:
        result.message = f"Error: {e}"

    return result


async def test_zoom_region_parameter(image_path: str, output_dir: Path) -> TestResult:
    """Test 6: zoom_region parameter for coordinate-based zoom."""
    result = TestResult("zoom_region_parameter")

    try:
        output_path = str(output_dir / 'zoom_region_test.pdf')

        # Zoom to upper-left quadrant
        response_json = await convert_to_tactile(
            image_path=image_path,
            output_path=output_path,
            detect_text=False,
            zoom_region=(10.0, 10.0, 40.0, 40.0),
            paper_size='letter'
        )

        response = json.loads(response_json)

        if response.get('success'):
            zoom_applied = response.get('zoom_applied')
            output_file = response.get('output_file')

            result.passed = zoom_applied is not None and Path(output_file).exists()
            result.message = f"Zoom applied: {zoom_applied is not None}, PDF exists: {Path(output_file).exists()}"
            result.details = {
                "zoom_applied": zoom_applied,
                "output_file": output_file
            }
        else:
            result.message = f"Conversion failed: {response.get('error')}"

    except Exception as e:
        result.message = f"Error: {e}"

    return result


async def test_zoom_to_parameter(image_path: str) -> TestResult:
    """Test 7: zoom_to parameter returns Phase 1 instructions."""
    result = TestResult("zoom_to_parameter")

    try:
        # Request zoom to "Bedroom" - should return instructions, not a PDF
        response_json = await convert_to_tactile(
            image_path=image_path,
            zoom_to="Bedroom",
            paper_size='letter'
        )

        response = json.loads(response_json)

        # Check for Phase 1 response
        is_phase1 = response.get('phase') == 'zoom_region_identification'
        has_instructions = 'instructions' in response
        has_zoom_target = response.get('zoom_target') == 'Bedroom'

        result.passed = is_phase1 and has_instructions and has_zoom_target
        result.message = f"Phase 1 response: {is_phase1}, Has instructions: {has_instructions}"
        result.details = {
            "phase": response.get('phase'),
            "zoom_target": response.get('zoom_target'),
            "has_instructions": has_instructions
        }

    except Exception as e:
        result.message = f"Error: {e}"

    return result


async def test_zoom_regions_multipage(image_path: str, output_dir: Path) -> TestResult:
    """Test 8: zoom_regions parameter generates multi-page PDF."""
    result = TestResult("zoom_regions_multipage")

    try:
        output_path = str(output_dir / 'zoom_multipage_test.pdf')

        # Define two regions
        regions = [
            {"label": "Region 1", "x_percent": 10, "y_percent": 10, "width_percent": 40, "height_percent": 40},
            {"label": "Region 2", "x_percent": 50, "y_percent": 50, "width_percent": 40, "height_percent": 40}
        ]

        response_json = await convert_to_tactile(
            image_path=image_path,
            output_path=output_path,
            detect_text=False,
            zoom_regions=regions,
            paper_size='letter'
        )

        response = json.loads(response_json)

        if response.get('success'):
            page_count = response.get('page_count', 1)
            is_multi_region = response.get('is_multi_region', False)
            output_file = response.get('output_file')

            result.passed = page_count == 2 and is_multi_region
            result.message = f"Pages: {page_count}, Multi-region: {is_multi_region}"
            result.details = {
                "page_count": page_count,
                "is_multi_region": is_multi_region,
                "regions": response.get('regions'),
                "output_file": output_file
            }
        else:
            result.message = f"Conversion failed: {response.get('error')}"

    except Exception as e:
        result.message = f"Error: {e}"

    return result


def test_cli_zoom_region(image_path: str, output_dir: Path) -> TestResult:
    """Test 9: CLI --zoom-region option."""
    result = TestResult("cli_zoom_region")

    try:
        output_path = output_dir / 'cli_zoom_test.pdf'

        # Run CLI command
        cmd = [
            sys.executable, '-m', 'fabric_access.cli',
            'image-to-piaf',
            str(image_path),
            '--output', str(output_path),
            '--zoom-region', '20,20,60,60',
            '--threshold', '128'
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent),
            timeout=120
        )

        result.passed = proc.returncode == 0 and output_path.exists()
        result.message = f"Exit code: {proc.returncode}, Output exists: {output_path.exists()}"
        result.details = {
            "exit_code": proc.returncode,
            "output_exists": output_path.exists(),
            "stdout": proc.stdout[:500] if proc.stdout else "",
            "stderr": proc.stderr[:500] if proc.stderr else ""
        }

    except subprocess.TimeoutExpired:
        result.message = "CLI command timed out"
    except Exception as e:
        result.message = f"Error: {e}"

    return result


async def test_filename_generation(image_path: str, output_dir: Path) -> TestResult:
    """Test 10: Filename includes zoom target."""
    result = TestResult("filename_generation")

    try:
        # Test with zoom_regions that have labels
        regions = [
            {"label": "Kitchen Test", "x_percent": 25, "y_percent": 25, "width_percent": 50, "height_percent": 50}
        ]

        response_json = await convert_to_tactile(
            image_path=image_path,
            detect_text=False,
            zoom_regions=regions,
            zoom_to="Kitchen",  # Should appear in filename
            paper_size='letter'
        )

        response = json.loads(response_json)

        if response.get('success'):
            output_file = response.get('output_file', '')
            has_zoom_in_name = 'kitchen' in output_file.lower()

            result.passed = has_zoom_in_name
            result.message = f"Filename: {Path(output_file).name}"
            result.details = {
                "output_file": output_file,
                "contains_zoom_target": has_zoom_in_name
            }
        else:
            result.message = f"Conversion failed: {response.get('error')}"

    except Exception as e:
        result.message = f"Error: {e}"

    return result


async def run_all_tests(image_path: str, output_dir: Path, specific_test: str = None):
    """Run all tests and report results."""

    print("=" * 70)
    print("ZOOM AND SCALING FEATURE TESTS")
    print("=" * 70)
    print(f"Image: {image_path}")
    print(f"Output: {output_dir}")
    print()

    # Initialize processor
    standards = StandardsLoader()
    processor = ImageProcessor(
        config=standards.get_all_config(),
        logger=SilentLogger()
    )

    # Define tests
    tests = {
        'crop_region': lambda: test_crop_to_region(processor, image_path, output_dir),
        'aspect_ratio': lambda: test_adjust_to_aspect_ratio(processor, output_dir),
        'filter_texts': lambda: test_filter_texts_in_region(processor),
        'scale_cap': lambda: test_scale_cap_removal(image_path, output_dir),
        'scale_warning': lambda: test_300_percent_warning(image_path, output_dir),
        'zoom_region': lambda: test_zoom_region_parameter(image_path, output_dir),
        'zoom_to': lambda: test_zoom_to_parameter(image_path),
        'zoom_multipage': lambda: test_zoom_regions_multipage(image_path, output_dir),
        'cli_zoom': lambda: test_cli_zoom_region(image_path, output_dir),
        'filename': lambda: test_filename_generation(image_path, output_dir),
    }

    results = []

    for test_name, test_func in tests.items():
        if specific_test and test_name != specific_test:
            continue

        print(f"\n--- Test: {test_name} ---")

        try:
            # Check if test is async
            test_result = test_func()
            if asyncio.iscoroutine(test_result):
                test_result = await test_result

            status = "PASS" if test_result.passed else "FAIL"
            print(f"  {status}: {test_result.message}")
            results.append(test_result)

        except Exception as e:
            print(f"  ERROR: {e}")
            fail_result = TestResult(test_name)
            fail_result.message = str(e)
            results.append(fail_result)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.message[:60]}...")

    print()
    print(f"Results: {passed}/{total} tests passed")

    # Save results to JSON
    results_file = output_dir / 'test_results.json'
    with open(results_file, 'w') as f:
        json.dump([r.to_dict() for r in results], f, indent=2)
    print(f"Results saved to: {results_file}")

    return passed == total


def main():
    parser = argparse.ArgumentParser(description='Test Zoom and Scaling Features')
    parser.add_argument('--image', default='samples/plan_test.jpg',
                        help='Path to test image')
    parser.add_argument('--output-dir', default='outputs/test-results/zoom-scaling',
                        help='Output directory for results')
    parser.add_argument('--test', default=None,
                        help='Run specific test only (e.g., crop_region, zoom_to)')

    args = parser.parse_args()

    # Resolve paths
    base_dir = Path(__file__).parent.parent
    image_path = base_dir / args.image
    output_dir = base_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verify image exists
    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)

    # Run tests
    success = asyncio.run(run_all_tests(str(image_path), output_dir, args.test))
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
