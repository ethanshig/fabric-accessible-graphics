#!/usr/bin/env python3
"""
Manual Braille Placement Tool

Allows you to:
1. View Tesseract's detected regions (for position reference)
2. Manually specify text and coordinates for Braille placement
3. Generate a PDF with Braille at your specified locations

Usage:
  python manual_braille_placement.py <image_path> [--interactive]

The tool reads from a JSON file (manual_braille_entries.json) that you can edit.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from PIL import Image
from fabric_access.core.text_detector import TextDetector, TextDetectionConfig, DetectedText
from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig
from fabric_access.core.processor import ImageProcessor
from fabric_access.core.pdf_generator import PIAFPDFGenerator
from fabric_access.config.standards_loader import StandardsLoader


class SilentLogger:
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


def load_manual_entries(json_path: str) -> list:
    """Load manual Braille entries from JSON file."""
    if not Path(json_path).exists():
        return []

    with open(json_path, 'r') as f:
        return json.load(f)


def save_manual_entries(entries: list, json_path: str):
    """Save manual Braille entries to JSON file."""
    with open(json_path, 'w') as f:
        json.dump(entries, f, indent=2)


def create_template_json(image_path: str, output_path: str):
    """
    Create a template JSON with Tesseract detections that you can edit.

    This gives you position references - edit the 'text' field to correct
    what Tesseract got wrong, or add new entries.
    """
    print("Creating template from Tesseract detections...")

    logger = SilentLogger()
    config = TextDetectionConfig(
        enabled=True, language='eng', page_segmentation_mode=3,
        min_confidence=50,  # Lower threshold to catch more
        filter_dimensions=True
    )

    detector = TextDetector(config=config, logger=logger)
    image = Image.open(image_path)
    gray = image.convert('L')
    detected = detector.detect_text(gray)

    # Convert to editable format
    entries = []
    for dt in detected:
        # Skip obvious noise
        if len(dt.text.strip()) < 2:
            continue
        if dt.text.strip() in ['|', '\\', '/', '-', '_', '||', '—']:
            continue

        entries.append({
            "text": dt.text,  # Edit this to correct OCR errors
            "x": dt.x,
            "y": dt.y,
            "width": dt.width,
            "height": dt.height,
            "include": True,  # Set to false to skip this entry
            "tesseract_confidence": round(dt.confidence, 1),
            "notes": ""  # Add your notes here
        })

    # Sort by y position (top to bottom), then x (left to right)
    entries.sort(key=lambda e: (e['y'], e['x']))

    save_manual_entries(entries, output_path)
    print(f"Created template with {len(entries)} entries: {output_path}")
    print("\nEdit this file to:")
    print("  - Correct 'text' fields where Tesseract got it wrong")
    print("  - Set 'include': false for entries you don't want")
    print("  - Add new entries manually")
    print("  - Adjust coordinates if needed")

    return entries


def add_manual_entry(entries: list) -> dict:
    """Interactively add a manual entry."""
    print("\n--- Add Manual Entry ---")
    text = input("Text to convert to Braille: ").strip()
    if not text:
        return None

    try:
        x = int(input("X coordinate (pixels from left): "))
        y = int(input("Y coordinate (pixels from top): "))
        width = int(input("Width (approximate, default 100): ") or "100")
        height = int(input("Height (approximate, default 30): ") or "30")
    except ValueError:
        print("Invalid coordinates")
        return None

    entry = {
        "text": text,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "include": True,
        "notes": "manually added"
    }

    entries.append(entry)
    return entry


def generate_braille_pdf(image_path: str, entries: list, output_path: str):
    """Generate PDF with Braille at specified locations."""
    print(f"\nGenerating PDF with {len(entries)} Braille labels...")

    logger = SilentLogger()
    standards = StandardsLoader()
    config = standards.get_all_config()

    # Load and process image
    image = Image.open(image_path)
    gray = image.convert('L')
    processed = gray.point(lambda x: 255 if x > 128 else 0, mode='1')

    # Convert entries to DetectedText objects
    detected_texts = []
    for entry in entries:
        if not entry.get('include', True):
            continue

        dt = DetectedText(
            text=entry['text'],
            x=entry['x'],
            y=entry['y'],
            width=entry.get('width', 100),
            height=entry.get('height', 30),
            confidence=100.0,
            is_dimension=False
        )
        detected_texts.append(dt)

    print(f"  Processing {len(detected_texts)} text entries")

    # Create Braille labels
    braille_config = BrailleConfig(
        enabled=True, grade=2, placement='overlay',
        font_name='DejaVu Sans', font_size=10,
        offset_x=5, offset_y=-10, max_label_length=30,
        truncate_suffix='...', font_color='black',
        detect_overlaps=True, min_label_spacing=6
    )

    converter = BrailleConverter(braille_config, logger)
    labels, symbols = converter.create_braille_labels(detected_texts)
    print(f"  Created {len(labels)} Braille labels")

    # Whiteout original text regions
    processor = ImageProcessor(config=config, logger=logger)
    processed = processor.whiteout_text_regions(processed, detected_texts, padding=5)

    # Generate PDF
    pdf_generator = PIAFPDFGenerator(logger=logger, config=config)
    result = pdf_generator.generate(
        image=processed,
        output_path=output_path,
        paper_size='letter',
        metadata={'original_size': image.size},
        braille_labels=labels,
        symbol_key_entries=symbols,
        braille_converter=converter
    )

    print(f"  Saved: {result}")
    return result


def main():
    parser = argparse.ArgumentParser(description='Manual Braille Placement Tool')
    parser.add_argument('image', nargs='?',
                        default='/mnt/c/Users/ethan/fabric-accessible-graphics/samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg',
                        help='Path to image file')
    parser.add_argument('--create-template', action='store_true',
                        help='Create a template JSON from Tesseract detections')
    parser.add_argument('--interactive', action='store_true',
                        help='Interactively add entries')
    parser.add_argument('--generate', action='store_true',
                        help='Generate PDF from entries')
    parser.add_argument('--json', default='manual_braille_entries.json',
                        help='JSON file for entries')

    args = parser.parse_args()

    output_dir = Path('/mnt/c/Users/ethan/fabric-accessible-graphics/outputs/test-results')
    json_path = output_dir / args.json

    print("=" * 70)
    print("MANUAL BRAILLE PLACEMENT TOOL")
    print("=" * 70)
    print(f"Image: {args.image}")
    print(f"JSON file: {json_path}")

    if args.create_template:
        create_template_json(args.image, str(json_path))
        return

    if args.interactive:
        entries = load_manual_entries(str(json_path))
        print(f"\nLoaded {len(entries)} existing entries")

        while True:
            action = input("\n[a]dd entry, [l]ist entries, [g]enerate PDF, [q]uit: ").strip().lower()

            if action == 'a':
                entry = add_manual_entry(entries)
                if entry:
                    save_manual_entries(entries, str(json_path))
                    print(f"Added and saved. Total entries: {len(entries)}")

            elif action == 'l':
                for i, e in enumerate(entries, 1):
                    status = "✓" if e.get('include', True) else "✗"
                    print(f"{i}. [{status}] \"{e['text'][:30]}\" at ({e['x']}, {e['y']})")

            elif action == 'g':
                active = [e for e in entries if e.get('include', True)]
                pdf_path = output_dir / 'manual_braille_output.pdf'
                generate_braille_pdf(args.image, active, str(pdf_path))

            elif action == 'q':
                break

        return

    if args.generate:
        entries = load_manual_entries(str(json_path))
        if not entries:
            print("No entries found. Use --create-template first.")
            return

        active = [e for e in entries if e.get('include', True)]
        pdf_path = output_dir / 'manual_braille_output.pdf'
        generate_braille_pdf(args.image, active, str(pdf_path))
        return

    # Default: show help
    print("\nUsage:")
    print("  1. Create template from Tesseract: --create-template")
    print("  2. Edit the JSON file to correct text and set 'include' flags")
    print("  3. Generate PDF: --generate")
    print("")
    print("Or use --interactive for step-by-step entry")


if __name__ == '__main__':
    main()
