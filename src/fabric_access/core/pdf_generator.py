"""
PDF generation module for PIAF-compatible output.

Generates high-contrast PDFs optimized for tactile printing on PIAF machines.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image
import io

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from fabric_access.utils.logger import AccessibleLogger
from fabric_access.utils.validators import validate_output_path
from fabric_access.core.braille_converter import BrailleConverter, BrailleConfig, KeyEntry


class PDFGeneratorError(Exception):
    """Custom exception for PDF generation errors."""
    pass


class PIAFPDFGenerator:
    """
    PDF generator optimized for PIAF (Picture In A Flash) machines.

    Features:
    - 300 DPI output
    - Pure black & white (no grayscale)
    - Precise dimensions
    - Embedded metadata
    """

    # Paper sizes in inches
    SIZES = {
        'letter': (8.5, 11.0),
        'tabloid': (11.0, 17.0)
    }

    # Target DPI for PIAF printing
    TARGET_DPI = 300

    def __init__(self, logger: Optional[AccessibleLogger] = None, config: Optional[dict] = None):
        """
        Initialize PDF generator.

        Args:
            logger: Optional AccessibleLogger instance
            config: Optional configuration dictionary
        """
        self.logger = logger or AccessibleLogger(verbose=False)
        self.config = config or {}
        self.image_height = 0  # Track image height for coordinate conversion
        self._braille_font_available = False  # Track if Braille font is registered

        # Register Unicode Braille-compatible font
        self._register_braille_font()

        # Create internal Braille converter for dual-text rendering
        self._internal_braille_converter = self._create_internal_braille_converter()

    def _register_braille_font(self):
        """
        Register TrueType font with Unicode Braille support.

        Attempts to register DejaVu Sans which has full Unicode Braille
        character support (U+2800-U+28FF). Sets _braille_font_available flag.
        """
        # Check if font is already registered (prevent duplicate registration errors)
        if 'DejaVu Sans' in pdfmetrics.getRegisteredFontNames():
            # Font already registered, mark as available
            self._braille_font_available = True
            return

        # Font paths in priority order - bundled font first for reliability
        font_paths = [
            # 1. Bundled font (most reliable)
            Path(__file__).parent.parent / 'data' / 'fonts' / 'DejaVuSans.ttf',
            # 2. Linux/WSL system paths
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
            Path('/usr/share/fonts/truetype/dejavu-sans/DejaVuSans.ttf'),
            # 3. macOS
            Path('/System/Library/Fonts/Supplemental/DejaVuSans.ttf'),
            Path('/Library/Fonts/DejaVuSans.ttf'),
            # 4. Windows
            Path('C:/Windows/Fonts/DejaVuSans.ttf'),
        ]

        for font_path in font_paths:
            try:
                if font_path.exists():
                    # Register with space to match config: "DejaVu Sans"
                    dejavu_font = TTFont('DejaVu Sans', str(font_path))
                    try:
                        pdfmetrics.registerFont(dejavu_font)
                        self._braille_font_available = True
                        self.logger.info(f"Registered DejaVu Sans font from: {font_path}")
                    except KeyError as e:
                        # Font already registered in this session, which is fine
                        if "already registered" in str(e) or "redefining" in str(e):
                            self._braille_font_available = True
                            self.logger.debug(f"DejaVu Sans already registered: {e}")
                        else:
                            raise
                    return
            except Exception as e:
                self.logger.debug(f"Failed to register font from {font_path}: {e}")
                continue

        # If we get here, no font was registered - this is critical
        self._braille_font_available = False
        self.logger.error(
            "CRITICAL: DejaVu Sans font not found. Braille characters will NOT render. "
            "Install with: sudo apt-get install fonts-dejavu"
        )

    def _create_internal_braille_converter(self) -> Optional[BrailleConverter]:
        """
        Create a BrailleConverter for tool-generated text (labels, instructions).

        Returns:
            BrailleConverter instance or None if creation fails
        """
        if not self._braille_font_available:
            return None

        try:
            braille_config = BrailleConfig(
                enabled=True,
                grade=2,  # Use Grade 2 (contracted) for shorter output
                font_name=self.config.get('braille', {}).get('font_name', 'DejaVu Sans'),
                font_size=12
            )
            return BrailleConverter(braille_config, self.logger)
        except Exception as e:
            self.logger.debug(f"Failed to create internal BrailleConverter: {e}")
            return None

    def calculate_dimensions(self, image: Image.Image, dpi: int = 300) -> Tuple[float, float]:
        """
        Calculate physical dimensions of image in inches.

        Args:
            image: PIL Image
            dpi: Dots per inch

        Returns:
            Tuple of (width_inches, height_inches)
        """
        width_px, height_px = image.size
        width_inches = width_px / dpi
        height_inches = height_px / dpi

        return width_inches, height_inches

    def fits_on_page(self, image: Image.Image, paper_size: str = 'letter',
                     dpi: int = 300) -> Tuple[bool, Tuple[float, float]]:
        """
        Check if image fits on specified paper size.

        Args:
            image: PIL Image
            paper_size: Paper size name ('letter' or 'tabloid')
            dpi: Dots per inch

        Returns:
            Tuple of (fits, (image_width, image_height))
        """
        if paper_size not in self.SIZES:
            raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

        page_width, page_height = self.SIZES[paper_size]
        img_width, img_height = self.calculate_dimensions(image, dpi)

        fits = img_width <= page_width and img_height <= page_height

        return fits, (img_width, img_height)

    def generate(self, image: Image.Image, output_path: str,
                 paper_size: str = 'letter',
                 metadata: Optional[dict] = None,
                 braille_labels: Optional[list] = None,
                 symbol_key_entries: Optional[list] = None,
                 braille_converter=None,
                 key_entries: Optional[List[KeyEntry]] = None) -> str:
        """
        Generate PDF optimized for PIAF printing.

        Args:
            image: Processed B&W PIL Image
            output_path: Path for output PDF
            paper_size: Paper size ('letter' or 'tabloid')
            metadata: Optional metadata dictionary to embed
            braille_labels: Optional list of BrailleLabel objects to render
            symbol_key_entries: Optional list of SymbolKeyEntry objects for key page
            braille_converter: Optional BrailleConverter for rendering Braille on key page
            key_entries: Optional list of KeyEntry objects for abbreviation key page

        Returns:
            Path to generated PDF file

        Raises:
            PDFGeneratorError: If PDF generation fails
        """
        # Validate output path
        is_valid, error_msg = validate_output_path(output_path)
        if not is_valid:
            raise PDFGeneratorError(error_msg)

        self.logger.generating("Creating PDF output")

        try:
            # Get paper dimensions
            if paper_size not in self.SIZES:
                raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

            page_width, page_height = self.SIZES[paper_size]
            page_width_pts = page_width * inch
            page_height_pts = page_height * inch

            # Store image height for coordinate conversion
            self.image_height = image.size[1]

            # Check if image fits
            fits, (img_width, img_height) = self.fits_on_page(image, paper_size, self.TARGET_DPI)

            if not fits:
                self.logger.warning(
                    f"Image size ({img_width:.1f}\" x {img_height:.1f}\") "
                    f"exceeds {paper_size} paper ({page_width}\" x {page_height}\")"
                )
                self.logger.info("Image will be scaled to fit")
                # Calculate scaling factor
                scale_w = page_width / img_width
                scale_h = page_height / img_height
                scale = min(scale_w, scale_h) * 0.95  # 5% margin

                img_width *= scale
                img_height *= scale
            else:
                self.logger.info(
                    f"Image size: {img_width:.1f} inches x {img_height:.1f} inches"
                )
                self.logger.info(f"Fits on: {paper_size} size paper ({page_width}\" x {page_height}\")")

            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))

            # Set metadata
            c.setTitle(metadata.get('source_file', 'PIAF Image') if metadata else 'PIAF Image')
            c.setAuthor("Fabric Accessible Graphics Toolkit")
            c.setSubject("Tactile graphics for PIAF printing")
            c.setCreator("fabric-access")

            # Center image on page
            x_offset = (page_width - img_width) / 2 * inch
            y_offset = (page_height - img_height) / 2 * inch

            # Convert PIL Image to format reportlab can use
            img_buffer = io.BytesIO()
            # Save as PNG to preserve 1-bit format
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_reader = ImageReader(img_buffer)

            # Draw image
            c.drawImage(
                img_reader,
                x_offset,
                y_offset,
                width=img_width * inch,
                height=img_height * inch,
                preserveAspectRatio=True
            )

            # Add Braille labels if provided
            if braille_labels:
                # Calculate scale factor from image pixels to PDF inches
                scale_factor = img_width / image.size[0]
                self._add_braille_labels(c, braille_labels, scale_factor, x_offset, y_offset)

            # Add processing metadata as PDF info
            if metadata:
                timestamp = datetime.now().isoformat()

                # Add custom metadata
                density = metadata.get('density_percentage', 'N/A')
                density_str = f"{density:.1f}%" if isinstance(density, (int, float)) else str(density)

                c.setKeywords(
                    f"threshold:{metadata.get('threshold', 'N/A')}, "
                    f"density:{density_str}, "
                    f"timestamp:{timestamp}"
                )

            # Add key page if there are symbol entries
            if symbol_key_entries:
                c.showPage()
                self.add_key_page(c, symbol_key_entries, page_width_pts, page_height_pts,
                                 braille_converter)

            # Add abbreviation key page if there are key entries
            if key_entries:
                c.showPage()
                self.add_abbreviation_key_page(c, key_entries, page_width_pts, page_height_pts)

            # Save PDF
            c.save()

            self.logger.success(f"PDF saved to {Path(output_path).name}")
            self.logger.blank_line()
            self.logger.complete("Processing finished successfully")
            self.logger.info("Ready to print on PIAF machine")

            return output_path

        except PDFGeneratorError:
            raise
        except Exception as e:
            raise PDFGeneratorError(f"Failed to generate PDF: {str(e)}") from e

    def _add_braille_labels(self, canvas_obj: canvas.Canvas, labels: list,
                          scale_factor: float, x_offset: float, y_offset: float):
        """
        Render Braille labels on PDF.

        Args:
            canvas_obj: ReportLab canvas object
            labels: List of BrailleLabel objects
            scale_factor: Scale factor for coordinates (image pixels to PDF inches)
            x_offset: X offset for centering image on page (in points)
            y_offset: Y offset for centering image on page (in points)
        """
        if not labels:
            return

        # Check if Braille font is available - critical for rendering
        if not self._braille_font_available:
            self.logger.error(
                "Cannot render Braille labels: No Braille-compatible font available. "
                "Braille characters require DejaVu Sans or similar Unicode font. "
                "Install with: sudo apt-get install fonts-dejavu"
            )
            return

        self.logger.progress(f"Adding {len(labels)} Braille labels to PDF")

        # Get Braille font settings from config
        braille_config = self.config.get('braille', {})
        font_name = braille_config.get('font_name', 'DejaVu Sans')
        font_size = braille_config.get('font_size', 10)

        # Set font for Braille text - must use Braille-compatible font
        try:
            canvas_obj.setFont(font_name, font_size)
        except Exception as e:
            self.logger.error(
                f"Failed to set Braille font '{font_name}': {e}. "
                "Braille labels will not render correctly."
            )
            return

        # Convert font size from points to pixels for baseline calculation
        # 1 point = 1/72 inch, at 300 DPI: 1 point = 300/72 ≈ 4.17 pixels
        DPI = 300
        POINTS_PER_INCH = 72
        font_size_px = font_size * (DPI / POINTS_PER_INCH)

        # Set fill color to black for Braille text
        # This is critical - without explicit color, text may not render visibly
        canvas_obj.setFillColorRGB(0, 0, 0)

        # Render each label
        for label in labels:
            # Scale coordinates from image pixels to PDF inches
            x = label.x * scale_factor

            # Convert Y coordinate: PDF origin is bottom-left, image origin is top-left
            # label.y is the TOP of where text should appear (in image space, in pixels)
            # drawString expects the BASELINE position
            # Baseline is approximately at (top + ascent), where ascent ≈ 0.8 * font_size_px
            # So: baseline_image_y = label.y + (0.8 * font_size_px)
            # Then convert to PDF space: PDF_y = (image_height - baseline_image_y) * scale_factor
            baseline_offset = 0.8 * font_size_px
            y = (self.image_height - label.y - baseline_offset) * scale_factor

            # Add offsets for image centering
            x = x * inch + x_offset
            y = y * inch + y_offset

            # Get rotation (default to 0 if not present)
            rotation = getattr(label, 'rotation_degrees', 0.0)

            # Draw Braille text with rotation if needed
            if rotation != 0:
                # Use canvas transforms for rotated text
                canvas_obj.saveState()
                canvas_obj.translate(x, y)
                canvas_obj.rotate(rotation)
                canvas_obj.drawString(0, 0, label.braille_text)
                canvas_obj.restoreState()
            else:
                canvas_obj.drawString(x, y, label.braille_text)

        self.logger.success(f"Added {len(labels)} Braille labels")

    def add_text_page(self, canvas_obj: canvas.Canvas, text: str,
                     page_width: float, page_height: float):
        """
        Add a text page to the PDF (for assembly instructions).

        Renders each line in dual format: Braille above, print below.
        This ensures both blind and sighted users can read the content.

        Args:
            canvas_obj: ReportLab canvas object
            text: Text content to add
            page_width: Page width in points
            page_height: Page height in points
        """
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        margin = 0.5 * inch
        y_position = page_height - margin
        line_height = 28  # Space for Braille + print lines

        for line in text.split('\n'):
            if y_position < margin:
                # New page needed
                canvas_obj.showPage()
                y_position = page_height - margin

            # Draw Braille version first (if converter available and line not empty)
            if line.strip() and self._internal_braille_converter and self._braille_font_available:
                try:
                    braille_line = self._internal_braille_converter.convert_text(line)
                    canvas_obj.setFont(braille_font, 10)
                    canvas_obj.drawString(margin, y_position, braille_line)
                    y_position -= 14  # Move down for print line
                except Exception:
                    pass  # If Braille fails, just show print

            # Draw print version
            canvas_obj.setFont("Courier", 10)
            canvas_obj.drawString(margin, y_position, line)
            y_position -= line_height

    def add_tile_label(self, canvas_obj: canvas.Canvas, label: str,
                      page_width: float, page_height: float):
        """
        Add tile label to bottom of page in dual format (Braille + print).

        Args:
            canvas_obj: ReportLab canvas object
            label: Tile label text
            page_width: Page width in points
            page_height: Page height in points
        """
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        y_base = 0.25 * inch

        # Draw Braille version first (above print)
        if self._internal_braille_converter and self._braille_font_available:
            try:
                braille_label = self._internal_braille_converter.convert_text(label)
                canvas_obj.setFont(braille_font, 12)
                braille_width = canvas_obj.stringWidth(braille_label, braille_font, 12)
                x_braille = (page_width - braille_width) / 2
                canvas_obj.drawString(x_braille, y_base + 15, braille_label)
            except Exception:
                pass  # If Braille fails, just show print

        # Draw print version below Braille
        canvas_obj.setFont("Helvetica-Bold", 12)
        text_width = canvas_obj.stringWidth(label, "Helvetica-Bold", 12)
        x = (page_width - text_width) / 2
        canvas_obj.drawString(x, y_base, label)

    def add_abbreviation_key_page(self, canvas_obj: canvas.Canvas,
                                   key_entries: List[KeyEntry],
                                   page_width: float, page_height: float) -> None:
        """
        Add an abbreviation key page at the current position in the PDF.

        Renders each key entry in dual format:
          ⠠⠁ = ⠠⠅⠊⠞⠉⠓⠑⠝
          A = Kitchen

        This should be called BEFORE adding drawing pages so the key appears first.

        Args:
            canvas_obj: ReportLab canvas object
            key_entries: List of KeyEntry objects to include in the key
            page_width: Page width in points
            page_height: Page height in points
        """
        if not key_entries:
            return

        # Layout constants
        margin = 0.75 * inch
        braille_line_height = 18  # Points for Braille line
        print_line_height = 16   # Points for print line
        entry_spacing = 12       # Extra spacing between entries
        total_entry_height = braille_line_height + print_line_height + entry_spacing

        # Get font settings
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        braille_font_size = 14
        print_font_size = 12
        title_font_size = 18

        # Start position
        y_position = page_height - margin

        # Add title in dual format: Braille and print
        title_text = "ABBREVIATION KEY"

        # Title in Braille
        if self._internal_braille_converter and self._braille_font_available:
            try:
                braille_title = self._internal_braille_converter.convert_text(title_text)
                canvas_obj.setFont(braille_font, title_font_size)
                canvas_obj.setFillColorRGB(0, 0, 0)
                canvas_obj.drawString(margin, y_position, braille_title)
                y_position -= title_font_size + 4
            except Exception as e:
                self.logger.debug(f"Failed to render Braille title: {e}")

        # Title in print
        canvas_obj.setFont("Helvetica-Bold", title_font_size)
        canvas_obj.setFillColorRGB(0, 0, 0)
        canvas_obj.drawString(margin, y_position, title_text)
        y_position -= title_font_size + 8

        # Draw horizontal line under title
        canvas_obj.setStrokeColorRGB(0, 0, 0)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(margin, y_position, page_width - margin, y_position)
        y_position -= 20

        # Render each key entry
        for idx, entry in enumerate(key_entries):
            # Check if we need a new page
            if y_position < margin + total_entry_height:
                canvas_obj.showPage()
                y_position = page_height - margin

                # Add continuation header in dual format
                if self._internal_braille_converter and self._braille_font_available:
                    try:
                        cont_braille = self._internal_braille_converter.convert_text("KEY (continued)")
                        canvas_obj.setFont(braille_font, 14)
                        canvas_obj.setFillColorRGB(0, 0, 0)
                        canvas_obj.drawString(margin, y_position, cont_braille)
                        y_position -= 18
                    except Exception:
                        pass

                canvas_obj.setFont("Helvetica-Bold", 14)
                canvas_obj.setFillColorRGB(0, 0, 0)
                canvas_obj.drawString(margin, y_position, "KEY (continued)")
                y_position -= 30

            # Line 1 (Braille): letter_braille = braille_full
            if self._internal_braille_converter and self._braille_font_available:
                try:
                    # Convert the letter to Braille
                    letter_braille = self._internal_braille_converter.convert_text(entry.letter)
                    equals_braille = self._internal_braille_converter.convert_text("=")

                    # Construct Braille line: letter_braille = braille_full
                    braille_line = f"{letter_braille} {equals_braille} {entry.braille_full}"

                    canvas_obj.setFont(braille_font, braille_font_size)
                    canvas_obj.setFillColorRGB(0, 0, 0)
                    canvas_obj.drawString(margin, y_position, braille_line)
                except Exception as e:
                    self.logger.debug(f"Failed to render Braille entry for {entry.letter}: {e}")

            y_position -= braille_line_height

            # Line 2 (Print): letter = original_text
            print_line = f"{entry.letter} = {entry.original_text}"

            # Truncate if too long
            max_chars = 60
            if len(print_line) > max_chars:
                print_line = print_line[:max_chars - 3] + "..."

            canvas_obj.setFont("Helvetica", print_font_size)
            canvas_obj.setFillColorRGB(0, 0, 0)
            canvas_obj.drawString(margin, y_position, print_line)

            y_position -= print_line_height + entry_spacing

        self.logger.info(f"Added abbreviation key page with {len(key_entries)} entries")

    def add_key_page(self, canvas_obj: canvas.Canvas, symbol_key_entries: list,
                    page_width: float, page_height: float,
                    braille_converter=None):
        """
        Add a key page listing symbol-to-text mappings.

        Each entry shows the Braille symbol, print symbol, and original text.
        Format: ⠁ a = Original Text Here

        Args:
            canvas_obj: ReportLab canvas object
            symbol_key_entries: List of SymbolKeyEntry objects
            page_width: Page width in points
            page_height: Page height in points
            braille_converter: Optional BrailleConverter for converting symbols to Braille
        """
        if not symbol_key_entries:
            return

        margin = 0.5 * inch
        line_height = 18  # Points between lines
        max_text_width = page_width - (2 * margin) - 100  # Leave room for symbol

        # Title
        y_position = page_height - margin

        # Draw title "KEY" in print
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawString(margin, y_position, "KEY")

        # Draw Braille title next to it if converter available
        if braille_converter:
            try:
                braille_title = braille_converter.convert_text("KEY")
                # Get Braille font settings
                braille_config = self.config.get('braille', {})
                font_name = braille_config.get('font_name', 'DejaVu Sans')
                try:
                    canvas_obj.setFont(font_name, 14)
                except:
                    canvas_obj.setFont('Helvetica', 14)
                canvas_obj.drawString(margin + 60, y_position, braille_title)
            except:
                pass  # Skip Braille title if conversion fails

        y_position -= line_height * 2  # Space after title

        # Horizontal line under title
        canvas_obj.setStrokeColorRGB(0, 0, 0)
        canvas_obj.line(margin, y_position + 10, page_width - margin, y_position + 10)

        y_position -= line_height

        # Get fonts ready
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        braille_font_size = 12

        entries_per_page = int((y_position - margin) / line_height)
        current_entry = 0

        for entry in symbol_key_entries:
            # Each entry takes 2 lines: Braille on top, print below
            lines_needed = 2

            # Check if we need a new page
            if y_position < margin + (line_height * lines_needed):
                canvas_obj.showPage()
                y_position = page_height - margin

                # Add continuation header
                canvas_obj.setFont("Helvetica-Bold", 12)
                canvas_obj.drawString(margin, y_position, "KEY (continued)")
                y_position -= line_height * 2

            # Line 1: Full Braille line (symbol = original_text)
            if braille_converter:
                try:
                    braille_symbol = braille_converter.convert_text(entry.symbol)
                    braille_equals = braille_converter.convert_text("=")
                    braille_text = braille_converter.convert_text(entry.original_text)

                    # Truncate if too long
                    if len(braille_text) > 35:
                        braille_text = braille_text[:32] + "..."

                    braille_line = f"{braille_symbol} {braille_equals} {braille_text}"

                    try:
                        canvas_obj.setFont(braille_font, braille_font_size)
                    except:
                        canvas_obj.setFont('Helvetica', braille_font_size)
                    canvas_obj.drawString(margin, y_position, braille_line)
                except:
                    pass

            y_position -= line_height

            # Line 2: Print line (symbol = original_text)
            text = entry.original_text
            # Truncate very long text
            max_chars = 50
            if len(text) > max_chars:
                text = text[:max_chars-3] + "..."

            canvas_obj.setFont("Helvetica", 11)
            canvas_obj.drawString(margin, y_position, f"{entry.symbol} = {text}")

            y_position -= line_height * 1.5  # Extra space between entries
            current_entry += 1

        self.logger.info(f"Added key page with {len(symbol_key_entries)} entries")

    def generate_with_tiling(self, image: Image.Image, output_path: str,
                            paper_size: str = 'letter',
                            tile_overlap: float = 0.1,
                            add_registration_marks: bool = True,
                            metadata: Optional[dict] = None,
                            braille_labels: Optional[list] = None,
                            key_entries: Optional[List[KeyEntry]] = None,
                            braille_converter=None) -> str:
        """
        Generate multi-page tiled PDF for large images.

        Args:
            image: Large B&W PIL Image
            output_path: Path for output PDF
            paper_size: Paper size to use for tiles
            tile_overlap: Overlap percentage between tiles (0.0-1.0)
            add_registration_marks: Whether to add registration marks
            metadata: Optional metadata dictionary
            braille_labels: Optional list of BrailleLabel objects to render
            key_entries: Optional list of KeyEntry objects for abbreviation key page
            braille_converter: Optional BrailleConverter for key page rendering

        Returns:
            Path to generated PDF file

        Raises:
            PDFGeneratorError: If PDF generation fails
        """
        from fabric_access.core.tiler import ImageTiler, TilerConfig

        # Validate output path
        is_valid, error_msg = validate_output_path(output_path)
        if not is_valid:
            raise PDFGeneratorError(error_msg)

        self.logger.generating("Creating multi-page tiled PDF")

        try:
            # Get paper dimensions
            if paper_size not in self.SIZES:
                raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

            page_width, page_height = self.SIZES[paper_size]
            page_width_pts = page_width * inch
            page_height_pts = page_height * inch

            # Calculate max dimensions in pixels at 300 DPI
            max_width_px = int(page_width * self.TARGET_DPI)
            max_height_px = int(page_height * self.TARGET_DPI)

            # Create tiler config
            tiler_config = TilerConfig(
                max_width_px=max_width_px,
                max_height_px=max_height_px,
                overlap_percentage=tile_overlap,
                add_registration_marks=add_registration_marks,
                paper_size=paper_size
            )

            # Create tiler and generate tiles
            tiler = ImageTiler(config=tiler_config, logger=self.logger)
            tiles = tiler.tile_image(image, tiler_config)

            # Calculate grid dimensions for assembly instructions
            num_cols, num_rows, _, _ = tiler.calculate_tile_grid(image, tiler_config)

            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))

            # Set metadata
            c.setTitle(metadata.get('source_file', 'PIAF Tiled Image') if metadata else 'PIAF Tiled Image')
            c.setAuthor("Fabric Accessible Graphics Toolkit")
            c.setSubject("Tiled tactile graphics for PIAF printing")
            c.setCreator("fabric-access")

            # Add abbreviation key page if there are key entries (at the beginning)
            if key_entries:
                self.logger.info(f"Adding abbreviation key page with {len(key_entries)} entries")
                self.add_abbreviation_key_page(c, key_entries, page_width_pts, page_height_pts)
                c.showPage()

            # Add assembly instructions as first page
            self.logger.info("Adding assembly instructions page")
            assembly_text = tiler.create_assembly_instructions(num_rows, num_cols, tile_overlap)
            self.add_text_page(c, assembly_text, page_width_pts, page_height_pts)
            c.showPage()

            # Store original image height for Braille coordinate conversion
            self.image_height = image.size[1]

            # Add each tile as a page
            for idx, (tile, label) in enumerate(tiles, 1):
                self.logger.progress(f"Adding page {idx + 1} of {len(tiles) + 1}: {label}")

                # Convert PIL Image to format reportlab can use
                img_buffer = io.BytesIO()
                tile.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)

                # Calculate dimensions
                tile_width_in, tile_height_in = self.calculate_dimensions(tile, self.TARGET_DPI)

                # Center tile on page (leave room for label at bottom)
                label_space = 0.5 * inch
                available_height = page_height - (label_space / inch)

                # Check if tile needs scaling
                scale = 1.0
                if tile_width_in > page_width or tile_height_in > available_height:
                    scale_w = page_width / tile_width_in
                    scale_h = available_height / tile_height_in
                    scale = min(scale_w, scale_h) * 0.95

                tile_width_in *= scale
                tile_height_in *= scale

                # Center horizontally, top-align vertically (with margin)
                x_offset = (page_width - tile_width_in) / 2 * inch
                y_offset = (page_height - tile_height_in - 0.5) * inch

                # Draw tile
                c.drawImage(
                    img_reader,
                    x_offset,
                    y_offset,
                    width=tile_width_in * inch,
                    height=tile_height_in * inch,
                    preserveAspectRatio=True
                )

                # Add tile label at bottom
                self.add_tile_label(c, label, page_width_pts, page_height_pts)

                # New page for next tile
                if idx < len(tiles):
                    c.showPage()

            # Save PDF
            c.save()

            self.logger.success(f"Multi-page PDF saved to {Path(output_path).name}")
            self.logger.info(f"Total pages: {len(tiles) + 1} (1 instruction page + {len(tiles)} tile pages)")
            self.logger.blank_line()
            self.logger.complete("Tiled output generation finished successfully")
            self.logger.info("Ready to print on PIAF machine")

            return output_path

        except PDFGeneratorError:
            raise
        except Exception as e:
            raise PDFGeneratorError(f"Failed to generate tiled PDF: {str(e)}") from e
    def generate_multipage(self, pages_data: List[Tuple[Image.Image, list]], 
                          output_path: str, paper_size: str = "letter",
                          shared_symbol_key: list = None,
                          braille_converter=None) -> str:
        """
        Generate multi-page PDF from list of (processed_image, braille_labels) tuples.
        
        This method is used for combining multiple pages from a multi-page PDF input
        into a single tactile output with shared context (symbol key) across all pages.

        Args:
            pages_data: List of (processed_image, braille_labels) tuples, one per page
            output_path: Path for output PDF
            paper_size: Paper size ('letter' or 'tabloid')
            shared_symbol_key: Optional list of SymbolKeyEntry objects shared across all pages
            braille_converter: Optional BrailleConverter for rendering Braille on key page

        Returns:
            Path to generated PDF file

        Raises:
            PDFGeneratorError: If PDF generation fails
        """
        from fabric_access.utils.validators import validate_output_path
        
        # Validate output path
        is_valid, error_msg = validate_output_path(output_path)
        if not is_valid:
            raise PDFGeneratorError(error_msg)

        self.logger.generating(f"Creating multi-page PDF with {len(pages_data)} pages")

        try:
            # Get paper dimensions
            if paper_size not in self.SIZES:
                raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

            page_width, page_height = self.SIZES[paper_size]
            page_width_pts = page_width * inch
            page_height_pts = page_height * inch

            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))

            # Set metadata
            c.setTitle("Multi-page PIAF Document")
            c.setAuthor("Fabric Accessible Graphics Toolkit")
            c.setSubject("Multi-page tactile graphics for PIAF printing")
            c.setCreator("fabric-access")

            # Process each page
            for page_idx, (processed_image, braille_labels) in enumerate(pages_data, 1):
                self.logger.progress(f"Adding page {page_idx} of {len(pages_data)}")

                # Store image height for coordinate conversion
                self.image_height = processed_image.size[1]

                # Check if image fits
                fits, (img_width, img_height) = self.fits_on_page(
                    processed_image, paper_size, self.TARGET_DPI
                )

                if not fits:
                    # Calculate scaling factor
                    scale_w = page_width / img_width
                    scale_h = page_height / img_height
                    scale = min(scale_w, scale_h) * 0.95  # 5% margin
                    img_width *= scale
                    img_height *= scale

                # Center image on page
                x_offset = (page_width - img_width) / 2 * inch
                y_offset = (page_height - img_height) / 2 * inch

                # Convert PIL Image to format reportlab can use
                img_buffer = io.BytesIO()
                processed_image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)

                # Draw image
                c.drawImage(
                    img_reader,
                    x_offset,
                    y_offset,
                    width=img_width * inch,
                    height=img_height * inch,
                    preserveAspectRatio=True
                )

                # Add Braille labels if provided
                if braille_labels:
                    scale_factor = img_width / processed_image.size[0]
                    self._add_braille_labels(c, braille_labels, scale_factor, x_offset, y_offset)

                # Add page number label at bottom
                page_label = f"Page {page_idx} of {len(pages_data)}"
                self.add_tile_label(c, page_label, page_width_pts, page_height_pts)

                # New page for next image (but not after the last one)
                if page_idx < len(pages_data):
                    c.showPage()

            # Add shared symbol key page at the end if provided
            if shared_symbol_key:
                c.showPage()
                self.add_key_page(c, shared_symbol_key, page_width_pts, page_height_pts,
                                 braille_converter)

            # Save PDF
            c.save()

            self.logger.success(f"Multi-page PDF saved to {Path(output_path).name}")
            total_pages = len(pages_data) + (1 if shared_symbol_key else 0)
            self.logger.info(f"Total pages: {total_pages}")
            self.logger.blank_line()
            self.logger.complete("Multi-page output generation finished successfully")
            self.logger.info("Ready to print on PIAF machine")

            return output_path

        except PDFGeneratorError:
            raise
        except Exception as e:
            raise PDFGeneratorError(f"Failed to generate multi-page PDF: {str(e)}") from e

