#!/bin/bash
# Quick start script for WSL

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Environment activated! You can now use:"
echo "  tactile info"
echo "  tactile image-to-piaf [IMAGE]"
echo ""
echo "To deactivate when done, type: deactivate"
echo ""

# Keep shell open with activated environment
exec bash
