"""
MCP tool implementations for fabric-access.

These functions are exposed to Claude via MCP, enabling natural language
interaction for converting architectural images to tactile graphics.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

from fabric_access.core.processor import ImageProcessor, ImageProcessorError
from fabric_access.core.pdf_generator import PIAFPDFGenerator, PDFGeneratorError
from fabric_access.config.standards_loader import StandardsLoader, StandardsLoaderError
from fabric_access.config.presets import PresetManager, PresetError
from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig
from fabric_access.core.text_detector import TextDetector, TextDetectionConfig, DetectedText
from fabric_access.core.hybrid_text_detector import HybridTextDetector
from fabric_access.utils.cache import cache_tesseract_results, load_cached_tesseract

logger = logging.getLogger("fabric-access-mcp")


class SilentLogger:
    """A logger that doesn't output anything - for MCP server use."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def info(self, msg, *args): pass
    def warning(self, msg, *args): pass
    def error(self, msg, *args, **kwargs): pass
    def progress(self, msg, *args): pass
    def loading(self, msg, *args): pass
    def checking(self, msg, *args): pass
    def found(self, msg, *args): pass
    def success(self, msg, *args): pass
    def solution(self, msg, *args): pass
    def generating(self, msg, *args): pass
    def complete(self, msg, *args): pass
    def blank_line(self): pass


def _get_density_message(density: float) -> str:
    """Generate a human-readable message about density."""
    if density < 30:
        return f"Density {density:.1f}% - optimal for PIAF printing."
    elif density < 40:
        return f"Density {density:.1f}% - acceptable for PIAF."
    elif density < 45:
        return f"Density {density:.1f}% - slightly high, may cause some paper swelling."
    else:
        return f"Density {density:.1f}% - high, consider using auto_reduce_density option."


async def convert_to_tactile(
    image_path: str,
    output_path: Optional[str] = None,
    preset: Optional[str] = None,
    threshold: Optional[int] = None,
    paper_size: str = "letter",
    detect_text: bool = True,
    braille_grade: int = 2,
    auto_reduce_density: bool = False,
    tile_overlap: float = 0.0,
    claude_text_json: Optional[Union[str, List[Dict[str, Any]]]] = None
) -> str:
    """
    Convert an architectural image to a PIAF-ready tactile PDF.

    This tool processes images (floor plans, sections, diagrams, etc.) and
    creates high-contrast PDFs suitable for printing on PIAF tactile machines.

    When detect_text=True, this tool uses a two-phase hybrid OCR approach:
    - Phase 1: Runs Tesseract to find text positions, returns instructions for Claude
              to view the image and extract text with normalized coordinates
    - Phase 2: When called again with claude_text_json, merges Claude's accurate
              text with Tesseract's accurate positions for optimal Braille placement

    Args:
        image_path: Path to the input image file (JPG, PNG, TIFF, BMP, GIF, or PDF)
        output_path: Path for output PDF. If not specified, creates {input_name}_piaf.pdf
        preset: Preset configuration to use (floor_plan, section, sketch, etc.)
        threshold: Black/white threshold 0-255. Higher = more black. Default varies by preset.
        paper_size: Output paper size - "letter" (8.5x11") or "tabloid" (11x17")
        detect_text: Enable OCR to detect text/dimensions and convert to Braille (default: True)
        braille_grade: Braille grade - 1 (uncontracted) or 2 (contracted, recommended)
        auto_reduce_density: Automatically reduce density if too high for PIAF
        tile_overlap: Overlap between tiles for large images (0.0-1.0, default 0.0 for no overlap)
        claude_text_json: Claude's text extraction as JSON string or list of dicts (Phase 2 of hybrid OCR)

    Returns:
        JSON string with conversion results including output file path and metadata
    """
    try:
        silent_logger = SilentLogger()

        # Load configuration
        try:
            standards = StandardsLoader()
        except StandardsLoaderError as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to load configuration: {e}",
                "error_type": "configuration_error"
            })

        # Apply preset if specified
        effective_threshold = threshold
        enhance = None
        enhance_strength = 1.0
        effective_paper_size = paper_size

        if preset:
            try:
                preset_manager = PresetManager()
                preset_settings = preset_manager.get_preset_settings(preset)
                preset_info = preset_manager.get_preset_info(preset)

                # Apply preset settings (explicit parameters override preset)
                if effective_threshold is None:
                    effective_threshold = preset_settings.get('threshold', 128)
                if paper_size == "letter":  # Only override if using default
                    effective_paper_size = preset_settings.get('paper_size', 'letter')
                enhance = preset_settings.get('enhance')
                enhance_strength = preset_settings.get('enhance_strength', 1.0)

                logger.info(f"Using preset: {preset_info['name']}")
            except PresetError as e:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid preset '{preset}': {e}",
                    "error_type": "preset_error"
                })

        # Set default threshold if still not set
        if effective_threshold is None:
            effective_threshold = standards.get_default_threshold()

        # Validate image path
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Image file not found: {image_path}",
                "error_type": "file_not_found"
            })

        # Get image dimensions for hybrid OCR
        from PIL import Image
        with Image.open(image_file) as img:
            img_width, img_height = img.size

        # ============================================================
        # PHASE 1: Hybrid OCR - Run Tesseract, return instructions for Claude
        # ============================================================
        if detect_text and not claude_text_json:
            # Run Tesseract to get text positions
            text_config = TextDetectionConfig(
                enabled=True,
                language='eng',
                page_segmentation_mode=3,
                min_confidence=50,  # Lower threshold to catch more
                filter_dimensions=True
            )

            try:
                text_detector = TextDetector(config=text_config, logger=silent_logger)
                gray_image = Image.open(image_file).convert('L')
                tesseract_results = text_detector.detect_text(gray_image)

                # Cache Tesseract results for Phase 2
                cache_tesseract_results(
                    str(image_file.absolute()),
                    tesseract_results,
                    image_size=(img_width, img_height)
                )

                # Return instructions for Claude to view image and extract text
                return json.dumps({
                    "success": True,
                    "phase": "text_extraction_needed",
                    "tesseract_count": len(tesseract_results),
                    "image_path": str(image_file.absolute()),
                    "image_size": {"width": img_width, "height": img_height},
                    "instructions": (
                        f"HYBRID OCR PHASE 1 COMPLETE: Tesseract found {len(tesseract_results)} text regions.\n\n"
                        "NOW PLEASE:\n"
                        f"1. VIEW the image at: {image_file.absolute()}\n"
                        f"2. Image dimensions: {img_width}x{img_height} pixels\n\n"
                        "3. Extract ALL visible text and return a JSON array with this format:\n"
                        "[\n"
                        "  {\n"
                        '    "text": "exact text content",\n'
                        '    "x_percent": 25,  // horizontal position as % (0-100) from left\n'
                        '    "y_percent": 10,  // vertical position as % (0-100) from top\n'
                        '    "width_percent": 8,  // approximate width as % of image width\n'
                        '    "height_percent": 3,  // approximate height as % of image height\n'
                        '    "type": "printed|handwritten|dimension",\n'
                        '    "confidence": "high|medium|low"\n'
                        "  }\n"
                        "]\n\n"
                        "4. After extracting text, call convert_to_tactile AGAIN with:\n"
                        "   - Same image_path\n"
                        "   - claude_text_json parameter containing your JSON array\n\n"
                        "TIPS:\n"
                        "- Include room labels, dimensions, title block text, annotations\n"
                        "- For position, estimate: 'Kitchen' at center-left might be x_percent=30, y_percent=40\n"
                        "- Dimensions like '5,55 m' should have type='dimension'\n"
                        "- Your accurate text will be merged with Tesseract's accurate positions"
                    ),
                    "message": "Phase 1 complete. Please view the image, extract text, then call again with claude_text_json."
                })

            except Exception as e:
                logger.warning(f"Tesseract failed, falling back to Claude-only: {e}")
                # Continue without Tesseract - Claude will provide positions too

        # ============================================================
        # PHASE 2: Merge Claude's text with Tesseract's positions
        # ============================================================
        merged_detected_texts = None
        if detect_text and claude_text_json:
            try:
                # Normalize: accept both JSON string and list of dicts
                if isinstance(claude_text_json, str):
                    claude_results = json.loads(claude_text_json)
                else:
                    claude_results = claude_text_json  # Already a list

                # Load cached Tesseract results
                cached = load_cached_tesseract(str(image_file.absolute()))

                if cached and cached.get('results'):
                    # Reconstruct DetectedText objects from cache
                    tesseract_results = [
                        DetectedText(
                            text=r['text'],
                            x=r['x'],
                            y=r['y'],
                            width=r['width'],
                            height=r['height'],
                            confidence=r['confidence'],
                            is_dimension=r.get('is_dimension', False)
                        )
                        for r in cached['results']
                    ]

                    # Merge using hybrid detector
                    hybrid_detector = HybridTextDetector(similarity_threshold=0.6)
                    merged_detected_texts = hybrid_detector.merge(
                        tesseract_results,
                        claude_results,
                        image_size=(img_width, img_height)
                    )

                    logger.info(f"Hybrid OCR: Merged {len(merged_detected_texts)} text items")
                else:
                    # No cached Tesseract results - use Claude's positions directly
                    logger.warning("No cached Tesseract results, using Claude positions only")
                    hybrid_detector = HybridTextDetector()
                    merged_detected_texts = hybrid_detector._handle_unmatched(
                        claude_results, (img_width, img_height)
                    )

            except json.JSONDecodeError as e:
                logger.warning(f"Invalid claude_text_json: {e}")
            except Exception as e:
                logger.warning(f"Hybrid merge failed: {e}")

        # Generate output path if not specified
        if not output_path:
            output_path = str(image_file.parent / f"{image_file.stem}_piaf.pdf")

        # Process image
        processor = ImageProcessor(
            config=standards.get_all_config(),
            logger=silent_logger
        )

        # If we have merged results from hybrid OCR, skip text detection in processor
        # (we already have the text, just need image processing)
        should_run_tesseract = detect_text and not merged_detected_texts

        try:
            processed_image, metadata = processor.process(
                input_path=str(image_path),
                threshold=effective_threshold,
                check_density_flag=True,
                enhance=enhance,
                enhance_strength=enhance_strength,
                paper_size=effective_paper_size,
                auto_reduce_density=auto_reduce_density,
                detect_text=should_run_tesseract  # Skip if we have hybrid results
            )
        except ImageProcessorError as e:
            return json.dumps({
                "success": False,
                "error": f"Image processing failed: {e}",
                "error_type": "processing_error"
            })

        # Use merged results from hybrid OCR if available, otherwise use Tesseract results
        detected_texts_to_use = merged_detected_texts or metadata.get('detected_texts', [])

        # Convert detected text to Braille labels
        braille_labels = None
        symbol_key_entries = None
        braille_converter = None
        braille_labels_count = 0

        if detect_text and detected_texts_to_use:
            try:
                braille_config_dict = standards.get_all_config().get('braille', {})

                braille_config = BrailleConfig(
                    enabled=True,
                    grade=int(braille_grade),
                    placement="overlay",
                    font_name=braille_config_dict.get('font_name', 'DejaVu Sans'),
                    font_size=braille_config_dict.get('font_size', 10),
                    offset_x=braille_config_dict.get('offset_x', 5),
                    offset_y=braille_config_dict.get('offset_y', -10),
                    max_label_length=braille_config_dict.get('max_label_length', 30),
                    truncate_suffix=braille_config_dict.get('truncate_suffix', '...'),
                    font_color=braille_config_dict.get('font_color', 'black'),
                    detect_overlaps=braille_config_dict.get('detect_overlaps', True),
                    min_label_spacing=braille_config_dict.get('min_label_spacing', 6)
                )

                braille_converter = BrailleConverter(braille_config, silent_logger)
                braille_labels, symbol_key_entries = braille_converter.create_braille_labels(
                    detected_texts_to_use  # Use merged or Tesseract results
                )

                if braille_labels:
                    braille_labels_count = len(braille_labels)

                # White out original text regions
                whiteout_enabled = braille_config_dict.get('whiteout_original_text', True)
                whiteout_padding = braille_config_dict.get('whiteout_padding', 5)

                if whiteout_enabled and detected_texts_to_use:
                    processed_image = processor.whiteout_text_regions(
                        processed_image,
                        detected_texts_to_use,  # Use merged or Tesseract results
                        padding=whiteout_padding
                    )

            except Exception as e:
                logger.warning(f"Braille conversion failed: {e}")
                # Continue without Braille - don't fail the whole conversion

        # Generate PDF
        pdf_generator = PIAFPDFGenerator(
            logger=silent_logger,
            config=standards.get_all_config()
        )

        needs_tiling = metadata.get('needs_tiling', False)

        try:
            if needs_tiling:
                # Generate tiled PDF for oversized images
                final_output = pdf_generator.generate_with_tiling(
                    image=processed_image,
                    output_path=output_path,
                    paper_size=effective_paper_size,
                    tile_overlap=tile_overlap,
                    add_registration_marks=True,
                    metadata=metadata,
                    braille_labels=braille_labels
                )
            else:
                # Generate standard single-page PDF
                final_output = pdf_generator.generate(
                    image=processed_image,
                    output_path=output_path,
                    paper_size=effective_paper_size,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    symbol_key_entries=symbol_key_entries,
                    braille_converter=braille_converter
                )
        except PDFGeneratorError as e:
            return json.dumps({
                "success": False,
                "error": f"PDF generation failed: {e}",
                "error_type": "pdf_error"
            })

        # Build success response
        density = metadata.get('density_percentage', 0)
        density_message = _get_density_message(density)

        # Build human-readable message
        message_parts = ["Converted successfully."]
        if braille_labels_count > 0:
            message_parts.append(f"{braille_labels_count} Braille label(s) added.")
        message_parts.append(density_message)
        if needs_tiling:
            message_parts.append("Image was tiled across multiple pages.")
        message_parts.append("Ready for PIAF printing.")

        # Determine if hybrid OCR was used
        hybrid_ocr_used = merged_detected_texts is not None and len(merged_detected_texts) > 0

        return json.dumps({
            "success": True,
            "output_file": str(final_output),
            "density_percentage": round(density, 1),
            "braille_labels_count": braille_labels_count,
            "paper_size": effective_paper_size,
            "threshold_used": effective_threshold,
            "preset_used": preset,
            "needs_tiling": needs_tiling,
            "detected_text_count": len(detected_texts_to_use),
            "hybrid_ocr_used": hybrid_ocr_used,
            "message": " ".join(message_parts)
        })

    except Exception as e:
        logger.error(f"Unexpected error in convert_to_tactile: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


async def list_presets() -> str:
    """
    List all available conversion presets with their descriptions.

    Presets provide optimized settings for different types of architectural
    images. Using the right preset improves conversion quality.

    Returns:
        JSON string with list of presets and their settings
    """
    try:
        preset_manager = PresetManager()
        presets_list = []

        for name in preset_manager.list_presets():
            info = preset_manager.get_preset_info(name)
            settings = preset_manager.get_preset_settings(name)

            presets_list.append({
                "name": name,
                "description": info.get('description', ''),
                "threshold": settings.get('threshold', 128),
                "paper_size": settings.get('paper_size', 'letter'),
                "enhance": settings.get('enhance'),
                "notes": info.get('notes', '')
            })

        return json.dumps({
            "success": True,
            "presets": presets_list,
            "count": len(presets_list),
            "message": f"{len(presets_list)} presets available. Use preset name with convert_to_tactile."
        })

    except PresetError as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to load presets: {e}",
            "error_type": "preset_error"
        })
    except Exception as e:
        logger.error(f"Unexpected error in list_presets: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


async def analyze_image(image_path: str) -> str:
    """
    Analyze an image before conversion to provide recommendations.

    This tool performs a pre-flight check on an image, detecting its
    characteristics and recommending optimal conversion settings.

    Args:
        image_path: Path to the image file to analyze

    Returns:
        JSON string with image analysis and recommendations
    """
    try:
        silent_logger = SilentLogger()

        # Validate image path
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Image file not found: {image_path}",
                "error_type": "file_not_found"
            })

        # Load configuration
        try:
            standards = StandardsLoader()
        except StandardsLoaderError as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to load configuration: {e}",
                "error_type": "configuration_error"
            })

        # Process image with default settings to get metadata
        processor = ImageProcessor(
            config=standards.get_all_config(),
            logger=silent_logger
        )

        try:
            # Process with default threshold to analyze
            processed_image, metadata = processor.process(
                input_path=str(image_path),
                threshold=128,
                check_density_flag=True,
                detect_text=True
            )
        except ImageProcessorError as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to analyze image: {e}",
                "error_type": "processing_error"
            })

        # Get image info
        original_size = metadata.get('original_size', (0, 0))
        density = metadata.get('density_percentage', 0)
        detected_texts = metadata.get('detected_texts', [])
        needs_tiling = metadata.get('needs_tiling', False)

        # Determine recommended preset based on characteristics
        recommendations = []
        recommended_preset = "floor_plan"  # Default

        # Analyze text content for hints
        text_content = " ".join([t.text.lower() for t in detected_texts if hasattr(t, 'text')])

        if any(word in text_content for word in ['section', 'elevation', 'height']):
            recommended_preset = "section"
            recommendations.append("Detected section/elevation indicators - using 'section' preset")
        elif any(word in text_content for word in ['site', 'north', 'scale']):
            recommended_preset = "site_plan"
            recommendations.append("Detected site plan indicators - using 'site_plan' preset")
        elif len(detected_texts) > 30:
            recommended_preset = "floor_plan"
            recommendations.append("High text density suggests floor plan - using 'floor_plan' preset")
        elif len(detected_texts) < 5:
            recommended_preset = "sketch"
            recommendations.append("Low text density suggests sketch or diagram - using 'sketch' preset")
        else:
            recommendations.append("Using default 'floor_plan' preset")

        # Density recommendations
        if density > 45:
            recommendations.append(f"Density is high ({density:.1f}%). Recommend using --auto-reduce-density")
        elif density > 40:
            recommendations.append(f"Density is moderately high ({density:.1f}%). May cause some paper swelling")
        elif density < 20:
            recommendations.append(f"Density is low ({density:.1f}%). Consider lowering threshold for more detail")
        else:
            recommendations.append(f"Density is good ({density:.1f}%) - optimal for PIAF")

        # Size recommendations
        if needs_tiling:
            recommendations.append("Image is larger than paper size. Will require tiling or use tabloid paper")

        # Paper size recommendation
        if original_size[0] > 2550 or original_size[1] > 3300:
            recommendations.append("Consider using tabloid paper (11x17\") for better detail")

        return json.dumps({
            "success": True,
            "image_path": str(image_path),
            "format": image_file.suffix.upper().replace('.', ''),
            "dimensions": {
                "width": original_size[0],
                "height": original_size[1]
            },
            "estimated_density": round(density, 1),
            "detected_text_count": len(detected_texts),
            "needs_tiling": needs_tiling,
            "recommended_preset": recommended_preset,
            "recommendations": recommendations,
            "message": f"Analysis complete. Recommended preset: {recommended_preset}. {len(recommendations)} suggestion(s)."
        })

    except Exception as e:
        logger.error(f"Unexpected error in analyze_image: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


def _get_image_media_type(file_path: Path) -> str:
    """Get the media type for an image file."""
    suffix = file_path.suffix.lower()
    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.tif': 'image/tiff',
    }
    return media_types.get(suffix, 'image/jpeg')


async def describe_image(
    image_path: str,
    detail_level: str = "full"
) -> str:
    """
    Generate a detailed architectural description of an image for accessibility.

    Uses the Arch-Alt-Text system to create multi-sensory descriptions of
    architectural images (plans, sections, diagrams, photos, etc.) specifically
    designed for blind/low-vision architecture students.

    The description follows a structured format:
    - Title: Identifies the piece
    - Macro Layer: Medium, subject, purpose (3 sentences)
    - Meso Layer: Composition, materials, orientation, scale (4+ sentences)
    - Micro Layer: Details, textures, dimensions, analogies (8+ sentences)

    Args:
        image_path: Path to the image file to describe
        detail_level: "full" for complete description, "brief" for summary only

    Returns:
        JSON string with the structured description
    """
    try:
        # Validate image path
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Image file not found: {image_path}",
                "error_type": "file_not_found"
            })

        # Check supported formats
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
        if image_file.suffix.lower() not in supported_formats:
            return json.dumps({
                "success": False,
                "error": f"Unsupported image format: {image_file.suffix}. Supported: {', '.join(supported_formats)}",
                "error_type": "format_error"
            })

        # Get image metadata
        try:
            from PIL import Image
            with Image.open(image_file) as img:
                width, height = img.size
                mode = img.mode
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to read image metadata: {e}",
                "error_type": "file_error"
            })

        # Get media type
        media_type = _get_image_media_type(image_file)

        # Return success with instructions for Claude to use its native vision
        return json.dumps({
            "success": True,
            "image_path": str(image_file.absolute()),
            "image_info": {
                "format": image_file.suffix.upper().replace('.', ''),
                "media_type": media_type,
                "width": width,
                "height": height,
                "mode": mode
            },
            "detail_level": detail_level,
            "instructions": (
                "To describe this image using the Arch-Alt-Text system:\n"
                "1. Read the prompt from resource: arch-alt-text://prompt\n"
                "2. Use your vision capability to view the image at the path above\n"
                "3. Apply the Arch-Alt-Text format (Macro/Meso/Micro) to describe it\n\n"
                f"Detail level requested: {detail_level}"
            ),
            "message": f"Image validated. Use the arch-alt-text://prompt resource and view the image to generate description."
        })

    except Exception as e:
        logger.error(f"Unexpected error in describe_image: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


async def extract_text_with_vision(
    image_path: str,
    include_handwritten: bool = True,
    include_dimensions: bool = True
) -> str:
    """
    Extract text from an architectural image using Claude's vision capability.

    This tool validates the image and returns instructions for Claude to use
    its native vision capability to detect all text, including handwritten
    annotations, dimensions, and rotated text that Tesseract may miss.

    The extracted text can then be passed to convert_to_tactile() via the
    extracted_text_json parameter for Braille conversion.

    Args:
        image_path: Path to the image file to extract text from
        include_handwritten: Whether to include handwritten text/annotations
        include_dimensions: Whether to identify dimension annotations (e.g., 10'-6")

    Returns:
        JSON with image info and extraction instructions for Claude's vision
    """
    try:
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Image file not found: {image_path}",
                "error_type": "file_not_found"
            })

        # Validate format
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
        if image_file.suffix.lower() not in supported_formats:
            return json.dumps({
                "success": False,
                "error": f"Unsupported format: {image_file.suffix}",
                "error_type": "format_error"
            })

        # Get image metadata
        try:
            from PIL import Image
            with Image.open(image_file) as img:
                width, height = img.size
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to read image: {e}",
                "error_type": "file_error"
            })

        media_type = _get_image_media_type(image_file)

        return json.dumps({
            "success": True,
            "image_path": str(image_file.absolute()),
            "image_info": {
                "format": image_file.suffix.upper().replace('.', ''),
                "media_type": media_type,
                "width": width,
                "height": height
            },
            "extraction_settings": {
                "include_handwritten": include_handwritten,
                "include_dimensions": include_dimensions
            },
            "instructions": (
                "To extract text from this image for Braille conversion:\n\n"
                "1. Use your vision capability to view the image at the path above\n"
                f"2. Image dimensions: {width}x{height} pixels\n"
                "3. Identify ALL text including:\n"
                "   - Printed text and labels (room names, titles)\n"
                f"   - {'Handwritten annotations' if include_handwritten else '(skip handwritten)'}\n"
                f"   - {'Dimensions (e.g., 10 feet-6 inches, 3.5m, 5,55 m)' if include_dimensions else '(skip dimensions)'}\n"
                "   - Rotated or angled text\n\n"
                "4. Return a JSON array with NORMALIZED COORDINATES (percentages 0-100):\n"
                "[\n"
                "  {\n"
                '    "text": "Kitchen",\n'
                '    "x_percent": 35,      // horizontal position as % from left edge\n'
                '    "y_percent": 25,      // vertical position as % from top edge\n'
                '    "width_percent": 8,   // approximate width as % of image width\n'
                '    "height_percent": 3,  // approximate height as % of image height\n'
                '    "type": "printed",    // "printed", "handwritten", or "dimension"\n'
                '    "confidence": "high"  // "high", "medium", or "low"\n'
                "  }\n"
                "]\n\n"
                "TIPS:\n"
                "- Use percentages NOT pixels (easier to estimate visually)\n"
                "- Center of image is approximately x_percent=50, y_percent=50\n"
                "- Top-left corner is x_percent=0, y_percent=0\n"
                "- For dimensions like '5,55 m' use type='dimension'\n\n"
                "5. Pass this JSON to convert_to_tactile() via claude_text_json parameter"
            ),
            "message": "Image validated. View the image and extract text with normalized coordinates (percentages)."
        })

    except Exception as e:
        logger.error(f"Unexpected error in extract_text_with_vision: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })
