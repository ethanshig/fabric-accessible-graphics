"""
Hybrid Text Detector Module

Combines Tesseract OCR's accurate position detection with Claude Vision's
accurate text reading for improved Braille conversion in architectural drawings.

The hybrid approach:
1. Tesseract finds WHERE text is located (bounding boxes)
2. Claude Vision reads WHAT the text says (accurate content)
3. Fuzzy matching pairs Claude's text with Tesseract's positions
4. Fallback to normalized coordinates for unmatched text
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional, Tuple
import logging

from .text_detector import DetectedText, TextDetector, TextDetectionConfig
from .grid_overlay import grid_cell_to_percent

logger = logging.getLogger("fabric-access.hybrid")


@dataclass
class MatchResult:
    """Result of matching Claude text to Tesseract detection."""
    claude_text: str
    tesseract_text: str
    similarity_score: float
    position: Tuple[int, int, int, int]  # x, y, width, height
    matched: bool


class HybridTextDetector:
    """
    Combines Tesseract positions with Claude Vision text reading.

    This detector merges results from two OCR approaches:
    - Tesseract: Good at finding text locations, poor at reading complex text
    - Claude Vision: Excellent at reading text, estimates positions as percentages

    The merge uses fuzzy string matching to pair Claude's accurate text
    with Tesseract's accurate bounding boxes.
    """

    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize hybrid detector.

        Args:
            similarity_threshold: Minimum similarity score (0-1) for matching.
                                  Default 0.6 (60% match required).
        """
        self.similarity_threshold = similarity_threshold
        self.logger = logger

    def merge(
        self,
        tesseract_results: List[DetectedText],
        claude_results: List[Dict[str, Any]],
        image_size: Tuple[int, int],
        grid_info: Optional[Dict[str, Any]] = None
    ) -> List[DetectedText]:
        """
        Merge Tesseract positions with Claude text readings.

        Args:
            tesseract_results: List of DetectedText from Tesseract OCR
            claude_results: List of dicts from Claude Vision with keys:
                - text: The text content
                - x_percent: X position as percentage (0-100) OR
                - grid_cell: Grid cell reference (e.g., "C4") when grid mode is enabled
                - width_percent: Width as percentage (optional)
                - height_percent: Height as percentage (optional)
                - type: 'printed', 'handwritten', or 'dimension'
                - confidence: 'high', 'medium', or 'low'
            image_size: Tuple of (width, height) in pixels
            grid_info: Optional dict with grid info (rows, cols) for grid_cell conversion

        Returns:
            List of DetectedText objects with merged data
        """
        width, height = image_size

        # Step 1: Match Claude's text to Tesseract's positions
        matched_results, used_tesseract_indices = self._match_texts(
            tesseract_results, claude_results
        )

        # Step 2: Handle unmatched Claude texts (use normalized coords or grid_cell)
        unmatched_results = self._handle_unmatched(
            claude_results, image_size, grid_info
        )

        # Combine results
        all_results = matched_results + unmatched_results

        # Log statistics
        self.logger.info(
            f"Hybrid merge: {len(matched_results)} matched, "
            f"{len(unmatched_results)} unmatched (using estimated coords)"
        )

        return all_results

    def _match_texts(
        self,
        tesseract: List[DetectedText],
        claude: List[Dict[str, Any]]
    ) -> Tuple[List[DetectedText], set]:
        """
        Use fuzzy matching to pair Claude's text with Tesseract's positions.

        Args:
            tesseract: Tesseract detection results
            claude: Claude Vision extraction results

        Returns:
            Tuple of (matched DetectedText list, set of used Tesseract indices)
        """
        matched = []
        used_tesseract = set()

        for claude_item in claude:
            claude_text = claude_item.get('text', '').strip()
            if not claude_text:
                continue

            best_match = None
            best_score = 0.0
            best_index = -1

            # Find best matching Tesseract result
            for i, tess_item in enumerate(tesseract):
                if i in used_tesseract:
                    continue

                # Calculate similarity score
                score = self._calculate_similarity(claude_text, tess_item.text)

                if score > best_score and score >= self.similarity_threshold:
                    best_score = score
                    best_match = tess_item
                    best_index = i

            if best_match is not None:
                # Create merged result: Claude's text + Tesseract's position
                # Use rotation from Claude's data (Claude can detect rotated text)
                rotation = float(claude_item.get('rotation_degrees', 0.0))
                merged = DetectedText(
                    text=claude_text,  # Use Claude's accurate reading
                    x=best_match.x,
                    y=best_match.y,
                    width=best_match.width,
                    height=best_match.height,
                    confidence=best_score * 100,  # Convert to percentage
                    is_dimension=claude_item.get('type') == 'dimension',
                    rotation_degrees=rotation
                )
                matched.append(merged)
                used_tesseract.add(best_index)

                # Mark Claude item as matched
                claude_item['_matched'] = True

                self.logger.debug(
                    f"Matched: '{claude_text}' <-> '{best_match.text}' "
                    f"(score: {best_score:.2f})"
                )

        return matched, used_tesseract

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.

        Uses SequenceMatcher for fuzzy matching, with normalization
        to handle case differences and whitespace.

        Args:
            text1: First text string
            text2: Second text string

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize: lowercase, strip whitespace
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()

        if not t1 or not t2:
            return 0.0

        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, t1, t2).ratio()

    def _handle_unmatched(
        self,
        claude_results: List[Dict[str, Any]],
        image_size: Tuple[int, int],
        grid_info: Optional[Dict[str, Any]] = None
    ) -> List[DetectedText]:
        """
        Convert unmatched Claude results using normalized coordinates.

        For text that Claude found but Tesseract missed, we use Claude's
        percentage-based position estimates OR grid_cell references converted to pixels.

        Args:
            claude_results: Claude Vision extraction results
            image_size: Tuple of (width, height) in pixels
            grid_info: Optional dict with grid info (rows, cols) for grid_cell conversion

        Returns:
            List of DetectedText for unmatched items
        """
        width, height = image_size
        unmatched = []

        for item in claude_results:
            # Skip if already matched
            if item.get('_matched'):
                continue

            text = item.get('text', '').strip()
            if not text:
                continue

            # Check for grid_cell first
            x_percent = item.get('x_percent', 0)
            y_percent = item.get('y_percent', 0)
            w_percent = item.get('width_percent', 5)  # Default 5% width
            h_percent = item.get('height_percent', 3)  # Default 3% height

            x = int(x_percent / 100 * width)
            y = int(y_percent / 100 * height)
            w = int(w_percent / 100 * width)
            h = int(h_percent / 100 * height)

            # Ensure minimum dimensions
            w = max(w, 20)
            h = max(h, 10)

            # Determine confidence based on Claude's assessment
            confidence_map = {'high': 70.0, 'medium': 50.0, 'low': 30.0}
            confidence = confidence_map.get(
                item.get('confidence', 'medium'), 50.0
            )

            # Get rotation from Claude's data (default to 0 for horizontal)
            rotation = float(item.get('rotation_degrees', 0.0))
            
            unmatched.append(DetectedText(
                text=text,
                x=x,
                y=y,
                width=w,
                height=h,
                confidence=confidence,
                is_dimension=item.get('type') == 'dimension',
                rotation_degrees=rotation
            ))

            self.logger.debug(
                f"Unmatched (using estimated coords): '{text}' "
                f"at ({x}, {y}) from ({x_percent}%, {y_percent}%), rotation={rotation}deg"
            )

        return unmatched

    def get_match_statistics(
        self,
        tesseract_results: List[DetectedText],
        claude_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about matching without actually merging.

        Useful for debugging and understanding match quality.

        Args:
            tesseract_results: Tesseract detection results
            claude_results: Claude Vision extraction results

        Returns:
            Dictionary with match statistics
        """
        matched_count = 0
        unmatched_claude = 0
        unused_tesseract = 0
        match_scores = []

        used_tesseract = set()

        for claude_item in claude_results:
            claude_text = claude_item.get('text', '').strip()
            if not claude_text:
                continue

            best_score = 0.0
            best_index = -1

            for i, tess_item in enumerate(tesseract_results):
                if i in used_tesseract:
                    continue

                score = self._calculate_similarity(claude_text, tess_item.text)
                if score > best_score:
                    best_score = score
                    best_index = i

            if best_score >= self.similarity_threshold:
                matched_count += 1
                used_tesseract.add(best_index)
                match_scores.append(best_score)
            else:
                unmatched_claude += 1

        unused_tesseract = len(tesseract_results) - len(used_tesseract)

        return {
            'tesseract_count': len(tesseract_results),
            'claude_count': len(claude_results),
            'matched_count': matched_count,
            'unmatched_claude': unmatched_claude,
            'unused_tesseract': unused_tesseract,
            'average_match_score': sum(match_scores) / len(match_scores) if match_scores else 0,
            'match_scores': match_scores
        }
