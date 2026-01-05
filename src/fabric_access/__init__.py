"""
Fabric Accessible Graphics Toolkit

A command-line toolkit for converting images to high-contrast, tactile-ready formats
for PIAF (Picture In A Flash) machines. Designed for accessibility and screen-reader compatibility.
"""

__version__ = "0.1.0"
__author__ = "Fabric Accessible Graphics Project"

from fabric_access.core.processor import ImageProcessor
from fabric_access.core.pdf_generator import PIAFPDFGenerator

__all__ = ["ImageProcessor", "PIAFPDFGenerator"]
