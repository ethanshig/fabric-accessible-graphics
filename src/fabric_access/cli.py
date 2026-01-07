"""
Command-line interface for Fabric Accessible Graphics toolkit.

Provides accessible, screen-reader friendly commands for converting
images to tactile-ready formats.
"""

import sys
import click
from pathlib import Path

from fabric_access import __version__
from fabric_access.core.processor import ImageProcessor, ImageProcessorError
from fabric_access.core.pdf_generator import PIAFPDFGenerator, PDFGeneratorError
from fabric_access.config.standards_loader import StandardsLoader, StandardsLoaderError
from fabric_access.config.presets import PresetManager, PresetError
from fabric_access.utils.logger import AccessibleLogger
from fabric_access.utils.validators import (
    validate_image_file,
    validate_threshold,
    validate_paper_size,
    generate_output_filename
)
from fabric_access.core.text_detector import TextDetector, TextDetectionConfig
from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig


@click.group()
@click.version_option(version=__version__, prog_name="fabric-access")
def main():
    """
    Fabric Accessible Graphics Toolkit

    A command-line tool for converting images to high-contrast, tactile-ready
    formats for PIAF (Picture In A Flash) machines.

    Designed for accessibility and full screen-reader compatibility.
    """
    pass


@main.command(name="image-to-piaf")
@click.argument('input_path', type=click.Path(exists=True))
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output PDF file path (auto-generated if not specified)'
)
@click.option(
    '--threshold', '-t',
    type=int,
    default=None,
    help='Black/white threshold 0-255 (default: 128). Higher values produce more black.'
)
@click.option(
    '--paper-size', '-p',
    type=click.Choice(['letter', 'tabloid'], case_sensitive=False),
    default='letter',
    help='Paper size for output (default: letter)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed progress messages'
)
@click.option(
    '--interactive', '-i',
    is_flag=True,
    help='Interactive mode with step-by-step prompts'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Path to custom tactile_standards.yaml configuration'
)
@click.option(
    '--preset',
    type=str,
    default=None,
    help='Use a preset configuration (floor_plan, sketch, photograph, etc.). Use "list-presets" to see all.'
)
@click.option(
    '--enhance', '-e',
    type=click.Choice(['s_curve', 'auto_contrast', 'clahe', 'histogram'], case_sensitive=False),
    default=None,
    help='Apply contrast enhancement before thresholding (s_curve recommended, overrides preset)'
)
@click.option(
    '--enhance-strength',
    type=float,
    default=None,
    help='Enhancement strength for S-curve (0.0-2.0, default 1.0, only applies to s_curve, overrides preset)'
)
@click.option(
    '--enable-tiling',
    is_flag=True,
    help='Enable automatic tiling for images larger than paper size'
)
@click.option(
    '--tile-overlap',
    type=float,
    default=0.0,
    help='Overlap percentage between tiles (0.0-1.0, default 0.0 for no overlap)'
)
@click.option(
    '--no-registration-marks',
    is_flag=True,
    help='Disable registration marks on tiles'
)
@click.option(
    '--auto-reduce-density',
    is_flag=True,
    help='Automatically reduce density if too high (default: off, preserves warning behavior)'
)
@click.option(
    '--target-density',
    type=float,
    default=None,
    help='Target density percentage (0.0-1.0, default: 0.30 for 30 percent)'
)
@click.option(
    '--max-reduction-iterations',
    type=int,
    default=None,
    help='Maximum erosion iterations for density reduction (default: 10)'
)
@click.option(
    '--detect-text',
    is_flag=True,
    help='Detect text and dimensions using OCR'
)
@click.option(
    '--braille-grade',
    type=click.Choice(['1', '2'], case_sensitive=False),
    default='1',
    help='Braille grade: 1 (uncontracted) or 2 (contracted). Default: 1'
)
@click.option(
    '--braille-placement',
    type=click.Choice(['overlay', 'margin'], case_sensitive=False),
    default='overlay',
    help='Braille label placement: overlay on image or in margins. Default: overlay'
)
@click.option(
    '--zoom-region',
    type=str,
    default=None,
    help='Zoom to a region: "x%%,y%%,w%%,h%%" (e.g., "25,30,50,40" = start at 25%%,30%% with 50%%x40%% size). Includes 10%% margin.'
)
def image_to_piaf(input_path, output, threshold, paper_size, verbose, interactive, config, preset, enhance, enhance_strength, enable_tiling, tile_overlap, no_registration_marks, auto_reduce_density, target_density, max_reduction_iterations, detect_text, braille_grade, braille_placement, zoom_region):
    """
    Convert an image to PIAF-ready PDF format.

    INPUT_PATH: Path to the image file to convert

    Examples:

    Basic conversion:
        fabric-access image-to-piaf floor-plan.jpg

    Using a preset (easiest - optimized settings):
        fabric-access image-to-piaf floor-plan.jpg --preset floor_plan --verbose

    With S-curve enhancement:
        fabric-access image-to-piaf floor-plan.jpg --enhance s_curve --verbose

    Custom threshold and output:
        fabric-access image-to-piaf sketch.png --threshold 140 --output result.pdf

    Strong enhancement for faint images:
        fabric-access image-to-piaf faint-sketch.jpg --enhance s_curve --enhance-strength 1.5

    Interactive mode with detailed output:
        fabric-access image-to-piaf drawing.jpg --interactive --verbose

    Automatic density reduction (fixes high density issues):
        fabric-access image-to-piaf dense-image.jpg --auto-reduce-density --verbose

    Custom density reduction target:
        fabric-access image-to-piaf floor-plan.jpg --auto-reduce-density --target-density 0.25

    Density reduction with more iterations:
        fabric-access image-to-piaf complex-drawing.png --auto-reduce-density --max-reduction-iterations 15

    Enable tiling for large images:
        fabric-access image-to-piaf large-plan.jpg --enable-tiling --verbose

    Tiling with custom overlap:
        fabric-access image-to-piaf huge-drawing.png --enable-tiling --tile-overlap 0.15

    Tiling without registration marks:
        fabric-access image-to-piaf large-map.tif --enable-tiling --no-registration-marks

    Supported formats: JPG, PNG, TIFF, BMP, GIF, PDF

    Use 'fabric-access list-presets' to see all available presets.
    """
    # Initialize logger
    logger = AccessibleLogger(verbose=verbose or interactive)

    try:
        # Display welcome message for interactive mode
        if interactive:
            logger.info("=" * 60)
            logger.info("Fabric Accessible Graphics - Image to PIAF Converter")
            logger.info("=" * 60)
            logger.blank_line()

        # Load configuration
        try:
            standards = StandardsLoader(config_path=config)
            if verbose:
                logger.info("Configuration loaded successfully")
        except StandardsLoaderError as e:
            logger.error("Failed to load configuration", e)
            logger.solution("Check that tactile_standards.yaml exists and is valid")
            sys.exit(1)

        # Load presets
        try:
            preset_manager = PresetManager()
        except PresetError as e:
            logger.error("Failed to load presets", e)
            logger.solution("Check that presets.yaml exists and is valid")
            sys.exit(1)

        # Apply preset settings if specified
        if preset:
            try:
                preset_settings = preset_manager.get_preset_settings(preset)
                preset_info = preset_manager.get_preset_info(preset)

                if verbose:
                    logger.info(f"Using preset: {preset_info['name']}")
                    logger.info(f"  {preset_info['description']}")

                # Apply preset settings (CLI options override preset)
                if threshold is None:
                    threshold = preset_settings.get('threshold', standards.get_default_threshold())
                if paper_size == 'letter':  # Only override if still default
                    paper_size = preset_settings.get('paper_size', 'letter')
                if enhance is None:
                    enhance = preset_settings.get('enhance')
                if enhance_strength is None:
                    enhance_strength = preset_settings.get('enhance_strength', 1.0)

            except PresetError as e:
                logger.error("Invalid preset", e)
                logger.solution("Use 'fabric-access list-presets' to see available presets")
                sys.exit(1)

        # Get default threshold from config if still not specified
        if threshold is None:
            threshold = standards.get_default_threshold()

        # Set default enhance_strength if not set
        if enhance_strength is None:
            enhance_strength = 1.0

        # Validate threshold
        is_valid, error_msg = validate_threshold(threshold)
        if not is_valid:
            logger.error(error_msg)
            logger.solution("Use a threshold value between 0 and 255")
            sys.exit(1)

        # Validate paper size
        is_valid, error_msg = validate_paper_size(paper_size)
        if not is_valid:
            logger.error(error_msg)
            sys.exit(1)

        # Display input file
        logger.info(f"Input file: {Path(input_path).name}")

        # Validate tiling options
        if tile_overlap < 0.0 or tile_overlap > 1.0:
            logger.error("Invalid tile overlap value")
            logger.solution("Use a value between 0.0 and 1.0 (e.g., 0.1 for 10% overlap)")
            sys.exit(1)

        # Validate density reduction options
        if target_density is not None and (target_density < 0.0 or target_density > 1.0):
            logger.error("Invalid target density value")
            logger.solution("Use a value between 0.0 and 1.0 (e.g., 0.30 for 30% density)")
            sys.exit(1)

        if max_reduction_iterations is not None and max_reduction_iterations < 1:
            logger.error("Invalid max reduction iterations value")
            logger.solution("Use a positive integer (e.g., 10)")
            sys.exit(1)

        # Interactive confirmation
        if interactive:
            logger.blank_line()
            logger.info(f"Settings:")
            logger.info(f"  Threshold: {threshold}")
            logger.info(f"  Paper size: {paper_size}")
            if enhance:
                logger.info(f"  Enhancement: {enhance}")
                if enhance == 's_curve':
                    logger.info(f"  Enhancement strength: {enhance_strength}")
            if enable_tiling:
                logger.info(f"  Tiling: enabled")
                logger.info(f"  Tile overlap: {int(tile_overlap * 100)}%")
                logger.info(f"  Registration marks: {'disabled' if no_registration_marks else 'enabled'}")
            if auto_reduce_density:
                logger.info(f"  Automatic density reduction: enabled")
                if target_density is not None:
                    logger.info(f"  Target density: {int(target_density * 100)}%")
                if max_reduction_iterations is not None:
                    logger.info(f"  Max iterations: {max_reduction_iterations}")
            if zoom_region:
                logger.info(f"  Zoom region: {zoom_region}")
            logger.blank_line()

            if not click.confirm("Continue with these settings?", default=True):
                logger.info("Operation cancelled")
                sys.exit(0)

            logger.blank_line()

        # Generate output filename if not specified
        if not output:
            output = generate_output_filename(input_path)
            if verbose:
                logger.info(f"Output will be saved to: {Path(output).name}")

        # Process image
        processor = ImageProcessor(
            config=standards.get_all_config(),
            logger=logger
        )

        # Parse and apply zoom region if specified
        zoom_region_tuple = None
        zoomed_input_path = input_path
        if zoom_region:
            try:
                parts = [float(p.strip()) for p in zoom_region.split(',')]
                if len(parts) != 4:
                    raise ValueError("Expected 4 values")
                zoom_region_tuple = tuple(parts)

                # Validate percentages
                if not all(0 <= p <= 100 for p in zoom_region_tuple):
                    logger.error("Zoom region values must be between 0 and 100")
                    sys.exit(1)

                # Load and crop the image
                from PIL import Image as PILImage
                import tempfile

                with PILImage.open(input_path) as img:
                    cropped = processor.crop_to_region(img, zoom_region_tuple, margin_percent=10.0)
                    cropped = processor.adjust_to_aspect_ratio(cropped, paper_size)
                    # Scale up to fill the page
                    cropped = processor.scale_to_fill_page(cropped, paper_size, dpi=300)

                    # Save to temp file
                    zoom_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='zoom_')
                    cropped.save(zoom_temp.name, format='PNG')
                    zoomed_input_path = zoom_temp.name

                if verbose:
                    logger.info(f"Zoomed to region: {zoom_region}")

            except ValueError as e:
                logger.error(f"Invalid zoom-region format: {e}")
                logger.solution("Use format: x%,y%,width%,height% (e.g., 25,30,50,40)")
                sys.exit(1)

        try:
            processed_image, metadata = processor.process(
                input_path=zoomed_input_path,
                threshold=threshold,
                check_density_flag=True,
                enhance=enhance,
                enhance_strength=enhance_strength,
                paper_size=paper_size,
                auto_reduce_density=auto_reduce_density,
                target_density=target_density,
                max_reduction_iterations=max_reduction_iterations,
                detect_text=detect_text
            )
        except ImageProcessorError as e:
            logger.error("Image processing failed", e)
            logger.solution("Check that the input file is a valid image")
            sys.exit(1)

        logger.blank_line()

        # Convert detected text to Braille labels if text detection was enabled
        braille_labels = None
        symbol_key_entries = None
        braille_converter = None
        if detect_text and metadata.get('detected_texts'):
            try:
                # Get braille config from standards
                braille_config_dict = standards.get_all_config().get('braille', {})

                # Create Braille config with CLI overrides
                braille_config = BrailleConfig(
                    enabled=True,
                    grade=int(braille_grade),
                    placement=braille_placement,
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

                # Convert to Braille
                braille_converter = BrailleConverter(braille_config, logger)
                braille_labels, symbol_key_entries = braille_converter.create_braille_labels(
                    metadata['detected_texts']
                )

                if braille_labels:
                    logger.info(f"Generated {len(braille_labels)} Braille label(s)")
                if symbol_key_entries:
                    logger.info(f"Created {len(symbol_key_entries)} symbol key entries for key page")

                # White out original text regions using exact OCR bounding boxes
                # This removes text so Braille can sit on clean white space
                whiteout_enabled = braille_config_dict.get('whiteout_original_text', True)
                whiteout_padding = braille_config_dict.get('whiteout_padding', 5)

                if whiteout_enabled and metadata.get('detected_texts'):
                    processed_image = processor.whiteout_text_regions(
                        processed_image,
                        metadata['detected_texts'],
                        padding=whiteout_padding
                    )

            except Exception as e:
                logger.warning(f"Braille conversion failed: {e}")
                logger.info("Continuing with PDF generation without Braille labels")
                braille_labels = None
                symbol_key_entries = None
                braille_converter = None

        # Check if tiling is needed and enabled
        needs_tiling = metadata.get('needs_tiling', False)

        if needs_tiling and not enable_tiling:
            logger.warning("Image is too large for specified paper size")
            logger.info("Use --enable-tiling to split image into multiple pages")
            logger.info("Or use --paper-size tabloid for larger paper")
            logger.blank_line()

            if interactive:
                if click.confirm("Enable tiling automatically?", default=True):
                    enable_tiling = True
                else:
                    logger.info("Proceeding with scaled output")
                logger.blank_line()

        # Generate PDF
        pdf_generator = PIAFPDFGenerator(logger=logger, config=standards.get_all_config())

        try:
            if enable_tiling and needs_tiling:
                # Generate tiled PDF
                logger.blank_line()
                logger.info("Generating tiled output for oversized image")
                logger.blank_line()

                output_path = pdf_generator.generate_with_tiling(
                    image=processed_image,
                    output_path=output,
                    paper_size=paper_size,
                    tile_overlap=tile_overlap,
                    add_registration_marks=not no_registration_marks,
                    metadata=metadata,
                    braille_labels=braille_labels
                )
            else:
                # Generate standard single-page PDF
                output_path = pdf_generator.generate(
                    image=processed_image,
                    output_path=output,
                    paper_size=paper_size,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    symbol_key_entries=symbol_key_entries,
                    braille_converter=braille_converter
                )

            # Display final summary
            if verbose or interactive:
                logger.blank_line()
                logger.info("=" * 60)
                logger.info("Processing Summary:")
                logger.info(f"  Input: {Path(input_path).name}")
                logger.info(f"  Output: {Path(output_path).name}")
                logger.info(f"  Threshold: {threshold}")
                logger.info(f"  Paper size: {paper_size}")
                if metadata.get('density_percentage'):
                    logger.info(f"  Density: {metadata['density_percentage']:.1f}%")
                logger.info("=" * 60)

        except PDFGeneratorError as e:
            logger.error("PDF generation failed", e)
            logger.solution("Check that the output path is writable")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.blank_line()
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Unexpected error occurred", e)
        sys.exit(1)


@main.command(name="version")
def version():
    """Display version information."""
    click.echo(f"Fabric Accessible Graphics Toolkit v{__version__}")
    click.echo("A tool for creating tactile-ready graphics for PIAF machines")


@main.command(name="info")
def info():
    """Display toolkit information and supported formats."""
    logger = AccessibleLogger(verbose=True)

    logger.info("=" * 60)
    logger.info("Fabric Accessible Graphics Toolkit")
    logger.info(f"Version: {__version__}")
    logger.info("=" * 60)
    logger.blank_line()

    logger.info("Purpose:")
    logger.info("  Convert images to high-contrast, tactile-ready PDFs")
    logger.info("  Optimized for PIAF (Picture In A Flash) machines")
    logger.blank_line()

    logger.info("Supported Input Formats:")
    logger.info("  JPG, JPEG, PNG, TIFF, TIF, BMP, GIF, PDF")
    logger.blank_line()

    logger.info("Output Format:")
    logger.info("  PDF - 300 DPI, pure black and white")
    logger.blank_line()

    logger.info("Paper Sizes:")
    logger.info("  letter  - 8.5 x 11 inches")
    logger.info("  tabloid - 11 x 17 inches")
    logger.blank_line()

    logger.info("Accessibility Features:")
    logger.info("  - Full screen reader compatibility")
    logger.info("  - Clear, descriptive status messages")
    logger.info("  - Interactive mode with step-by-step guidance")
    logger.info("  - Verbose mode for detailed progress")
    logger.blank_line()

    logger.info("For help with commands, use: fabric-access --help")
    logger.info("=" * 60)


@main.command(name="list-presets")
def list_presets():
    """List all available conversion presets."""
    logger = AccessibleLogger(verbose=True)

    try:
        preset_manager = PresetManager()
        presets_info = preset_manager.get_all_presets_info()

        logger.info("=" * 60)
        logger.info("Available Conversion Presets")
        logger.info("=" * 60)
        logger.blank_line()

        for name in preset_manager.list_presets():
            info = presets_info[name]
            logger.info(f"{name}")
            logger.info(f"  {info['description']}")
            logger.blank_line()

        logger.info("=" * 60)
        logger.info("Usage:")
        logger.info("  fabric-access image-to-piaf IMAGE.jpg --preset PRESET_NAME")
        logger.blank_line()
        logger.info("Example:")
        logger.info("  fabric-access image-to-piaf floor-plan.jpg --preset floor_plan")
        logger.info("=" * 60)

    except PresetError as e:
        logger.error("Failed to load presets", e)
        sys.exit(1)


@main.command(name="batch")
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('output_dir', type=click.Path(file_okay=False, dir_okay=True))
@click.option(
    '--pattern',
    type=str,
    default='*.jpg,*.jpeg,*.png,*.tiff,*.tif',
    help='File patterns to process (comma-separated, default: *.jpg,*.jpeg,*.png,*.tiff,*.tif)'
)
@click.option(
    '--preset',
    type=str,
    default=None,
    help='Apply preset to all images'
)
@click.option(
    '--threshold', '-t',
    type=int,
    default=None,
    help='Black/white threshold for all images (overrides preset)'
)
@click.option(
    '--enhance', '-e',
    type=click.Choice(['s_curve', 'auto_contrast', 'clahe', 'histogram'], case_sensitive=False),
    default=None,
    help='Enhancement method for all images (overrides preset)'
)
@click.option(
    '--paper-size', '-p',
    type=click.Choice(['letter', 'tabloid'], case_sensitive=False),
    default='letter',
    help='Paper size for all outputs'
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help='Process subdirectories recursively'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed progress for each file'
)
@click.option(
    '--auto-reduce-density',
    is_flag=True,
    help='Automatically reduce density for all images if too high'
)
@click.option(
    '--target-density',
    type=float,
    default=None,
    help='Target density percentage for all images (0.0-1.0, default: 0.30)'
)
@click.option(
    '--max-reduction-iterations',
    type=int,
    default=None,
    help='Maximum erosion iterations for density reduction (default: 10)'
)
@click.option(
    '--detect-text',
    is_flag=True,
    help='Detect text and dimensions using OCR for all images'
)
@click.option(
    '--braille-grade',
    type=click.Choice(['1', '2'], case_sensitive=False),
    default='1',
    help='Braille grade: 1 (uncontracted) or 2 (contracted). Default: 1'
)
@click.option(
    '--braille-placement',
    type=click.Choice(['overlay', 'margin'], case_sensitive=False),
    default='overlay',
    help='Braille label placement: overlay on image or in margins. Default: overlay'
)
def batch(input_dir, output_dir, pattern, preset, threshold, enhance, paper_size, recursive, verbose, auto_reduce_density, target_density, max_reduction_iterations, detect_text, braille_grade, braille_placement):
    """
    Batch convert multiple images to PIAF-ready PDFs.

    INPUT_DIR: Directory containing images to convert
    OUTPUT_DIR: Directory for output PDFs

    Examples:

    Convert all JPGs in a folder with floor_plan preset:
        fabric-access batch ./drawings ./output --preset floor_plan

    Convert all images recursively:
        fabric-access batch ./all-drawings ./output --recursive --preset floor_plan

    Custom settings for all files:
        fabric-access batch ./sketches ./output --threshold 130 --enhance s_curve

    Process only PNG files:
        fabric-access batch ./images ./output --pattern "*.png" --preset photograph

    Batch with automatic density reduction:
        fabric-access batch ./drawings ./output --auto-reduce-density --verbose
    """
    import glob as glob_module
    from pathlib import Path as PathLib

    logger = AccessibleLogger(verbose=True)  # Always verbose for batch

    try:
        input_path = PathLib(input_dir)
        output_path = PathLib(output_dir)

        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 60)
        logger.info("Batch Processing")
        logger.info("=" * 60)
        logger.blank_line()

        # Load presets if needed
        preset_manager = None
        if preset:
            try:
                preset_manager = PresetManager()
                preset_info = preset_manager.get_preset_info(preset)
                logger.info(f"Using preset: {preset_info['name']}")
                logger.info(f"  {preset_info['description']}")
            except PresetError as e:
                logger.error("Invalid preset", e)
                sys.exit(1)

        # Find all matching files
        patterns = [p.strip() for p in pattern.split(',')]
        files = []

        for pat in patterns:
            if recursive:
                files.extend(input_path.rglob(pat))
            else:
                files.extend(input_path.glob(pat))

        # Filter to only image files
        image_files = [f for f in files if f.is_file()]

        if not image_files:
            logger.warning(f"No image files found matching pattern: {pattern}")
            logger.info(f"  Input directory: {input_dir}")
            if recursive:
                logger.info("  Recursive search: enabled")
            sys.exit(0)

        logger.info(f"Found {len(image_files)} image(s) to process")
        logger.info(f"Input directory: {input_dir}")
        logger.info(f"Output directory: {output_dir}")
        logger.blank_line()

        # Process each file
        successful = 0
        failed = 0
        failed_files = []

        for idx, input_file in enumerate(image_files, 1):
            logger.info(f"[{idx}/{len(image_files)}] Processing: {input_file.name}")

            try:
                # Generate output filename
                output_file = output_path / f"{input_file.stem}_piaf.pdf"

                # Determine settings (preset -> defaults)
                file_threshold = threshold
                file_enhance = enhance
                file_enhance_strength = 1.0
                file_paper_size = paper_size

                if preset and preset_manager:
                    preset_settings = preset_manager.get_preset_settings(preset)
                    if file_threshold is None:
                        file_threshold = preset_settings.get('threshold', 128)
                    if file_enhance is None:
                        file_enhance = preset_settings.get('enhance')
                    file_enhance_strength = preset_settings.get('enhance_strength', 1.0)
                    if paper_size == 'letter':
                        file_paper_size = preset_settings.get('paper_size', 'letter')

                if file_threshold is None:
                    file_threshold = 128

                # Process image
                standards = StandardsLoader()
                processor = ImageProcessor(
                    config=standards.get_all_config(),
                    logger=AccessibleLogger(verbose=verbose)
                )

                processed_image, metadata = processor.process(
                    input_path=str(input_file),
                    threshold=file_threshold,
                    check_density_flag=True,
                    enhance=file_enhance,
                    enhance_strength=file_enhance_strength,
                    paper_size=file_paper_size,
                    auto_reduce_density=auto_reduce_density,
                    target_density=target_density,
                    max_reduction_iterations=max_reduction_iterations,
                    detect_text=detect_text
                )

                # Convert detected text to Braille labels if text detection was enabled
                braille_labels = None
                symbol_key_entries = None
                braille_converter = None
                if detect_text and metadata.get('detected_texts'):
                    try:
                        # Get braille config from standards
                        braille_config_dict = standards.get_all_config().get('braille', {})

                        # Create Braille config with CLI overrides
                        braille_config = BrailleConfig(
                            enabled=True,
                            grade=int(braille_grade),
                            placement=braille_placement,
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

                        # Convert to Braille
                        braille_converter = BrailleConverter(braille_config, AccessibleLogger(verbose=verbose))
                        braille_labels, symbol_key_entries = braille_converter.create_braille_labels(
                            metadata['detected_texts']
                        )
                    except Exception:
                        # Silently skip braille conversion errors in batch mode
                        braille_labels = None
                        symbol_key_entries = None
                        braille_converter = None

                # Generate PDF
                pdf_generator = PIAFPDFGenerator(logger=AccessibleLogger(verbose=verbose), config=standards.get_all_config())
                pdf_generator.generate(
                    image=processed_image,
                    output_path=str(output_file),
                    paper_size=file_paper_size,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    symbol_key_entries=symbol_key_entries,
                    braille_converter=braille_converter
                )

                successful += 1
                logger.info(f"  Success: {output_file.name}")

            except Exception as e:
                failed += 1
                failed_files.append((input_file.name, str(e)))
                logger.error(f"  Failed: {input_file.name}", e)

            logger.blank_line()

        # Summary
        logger.info("=" * 60)
        logger.info("Batch Processing Complete")
        logger.info("=" * 60)
        logger.info(f"Total files: {len(image_files)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")

        if failed_files:
            logger.blank_line()
            logger.info("Failed files:")
            for filename, error in failed_files:
                logger.info(f"  {filename}: {error}")

        logger.info("=" * 60)

        if failed > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.blank_line()
        logger.info("Batch processing cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Batch processing failed", e)
        sys.exit(1)


if __name__ == '__main__':
    main()
