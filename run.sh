#!/bin/bash
# Quick start script for WSL

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Environment activated! You can now use:"
echo "  tact info"
echo "  tact convert [IMAGE]"
echo "  tasc version"
echo ""
echo "To deactivate when done, type: deactivate"
echo ""

# Keep shell open with activated environment
exec bash
