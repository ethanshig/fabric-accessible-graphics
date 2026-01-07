"""
Label scaler module for analyzing Braille label fit within original text bounding boxes.

This module provides functionality to determine whether Braille conversions of detected
text will fit within the original text's bounding box dimensions, and calculates
scaling recommendations when they don't fit.
"""

import logging
from typing import Dict, List, Optional, Tuple

from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig
from fabric_access.core.text_detector import DetectedText


__all__ = ["analyze_label_fit"]


# Constants matching braille_converter.py rendering parameters
DPI = 300
FONT_SIZE_POINTS = 10
FONT_SIZE_PX = FONT_SIZE_POINTS * (DPI / 72)  # ~41.67 pixels
CHAR_WIDTH_PX = FONT_SIZE_PX * 0.6  # ~25 pixels per character


class _SilentLogger:
    """A silent logger that suppresses all output."""
    def debug(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def success(self, *args, **kwargs): pass
    def step(self, *args, **kwargs): pass
    def verbose(self, *args, **kwargs): pass


def _create_braille_converter(grade: int = 2) -> BrailleConverter:
    """Create a BrailleConverter with default config for label width estimation."""
    config = BrailleConfig(
        enabled=True,
        grade=grade,
        placement="overlay",
        font_name="DejaVu Sans",
        font_size=FONT_SIZE_POINTS,
        offset_x=5,
        offset_y=-10,
        max_label_length=30,
        truncate_suffix="...",
        font_color="black",
        detect_overlaps=True,
        min_label_spacing=6
    )
    return BrailleConverter(config, _SilentLogger())


def analyze_label_fit(
    detected_texts: List[DetectedText],
    image_size: Tuple[int, int],
    braille_grade: int = 2,
) -> Dict:
    """
    Analyze whether Braille labels will fit within their original text bounding boxes.

    For each detected text, this function converts the text to Braille and calculates
    whether the resulting Braille text width will fit within the original bounding box.
    Note that Braille text may be longer than the original due to Grade 2 contractions
    expanding certain characters.

    Args:
        detected_texts: List of DetectedText objects containing text and bounding box info.
        image_size: Tuple of (width, height) of the source image in pixels.
        braille_grade: Braille grade to use for conversion (1 or 2). Default is 2.

    Returns:
        A dictionary containing:
            - fits: List of DetectedText objects where Braille fits within original bounds.
            - needs_key: List of DetectedText objects where Braille won't fit.
            - fit_ratios: Dict mapping original text to its ratio (braille_width / original_width).
            - recommended_scale: The scale percentage that would make ALL labels fit
                                 (max of all ratios * 100). Returns 100 if all labels fit.

    Example:
        >>> from fabric_access.core.text_detector import DetectedText
        >>> texts = [
        ...     DetectedText(text="Room", x=100, y=100, width=80, height=20, confidence=0.95),
        ...     DetectedText(text="Kitchen", x=200, y=200, width=50, height=20, confidence=0.90),
        ... ]
        >>> result = analyze_label_fit(texts, image_size=(1000, 800))
        >>> print(f"Labels that fit: {len(result['fits'])}")
        >>> print(f"Labels needing key: {len(result['needs_key'])}")
        >>> print(f"Recommended scale: {result['recommended_scale']}%")
    """
    converter = _create_braille_converter(braille_grade)

    fits: List[DetectedText] = []
    needs_key: List[DetectedText] = []
    fit_ratios: Dict[str, float] = {}
    max_ratio: float = 1.0

    for detected in detected_texts:
        # Convert original text to Braille
        braille_text = converter.convert_text(detected.text)

        # Calculate Braille width using the standard formula
        braille_width = len(braille_text) * CHAR_WIDTH_PX

        # Get original text bounding box width
        original_width = detected.width

        # Calculate fit ratio (braille_width / original_width)
        # Avoid division by zero for zero-width bounding boxes
        if original_width > 0:
            ratio = braille_width / original_width
        else:
            # If original width is 0, Braille won't fit
            ratio = float("inf") if braille_width > 0 else 1.0

        # Store the ratio using original text as key
        fit_ratios[detected.text] = ratio

        # Track maximum ratio for recommended scale
        if ratio != float("inf"):
            max_ratio = max(max_ratio, ratio)

        # Categorize based on whether Braille fits
        if ratio <= 1.0:
            fits.append(detected)
        else:
            needs_key.append(detected)

    # Calculate recommended scale percentage
    # This is the scale that would make ALL labels fit
    recommended_scale = max_ratio * 100

    return {
        "fits": fits,
        "needs_key": needs_key,
        "fit_ratios": fit_ratios,
        "recommended_scale": recommended_scale,
    }
