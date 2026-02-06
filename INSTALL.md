# Radical Accessibility - Installation Guide

This guide walks you through installing the Radical Accessibility pack step by step.

## Prerequisites Check

Before starting, verify you have:

- [ ] Python 3.10 or higher
- [ ] pip (Python package installer)
- [ ] Git (to clone the repository)

```bash
# Check Python version
python3 --version  # Should show 3.10 or higher

# Check pip
pip --version
```

## Step 1: Clone the Repository

```bash
git clone https://github.com/ethanshig/radical-accessibility.git
cd radical-accessibility
```

## Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

## Step 3: Install System Dependencies

### Tesseract OCR (Required for text detection)

**Ubuntu/Debian/WSL:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from https://github.com/UB-Mannheim/tesseract/wiki

### Poppler (Required for PDF processing)

**Ubuntu/Debian/WSL:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

**Windows:**
Download from https://github.com/oschwartz10612/poppler-windows/releases and add to PATH.

### Liblouis (Optional - for Grade 2 Braille)

**Ubuntu/Debian/WSL:**
```bash
sudo apt-get install liblouis-dev python3-louis liblouis-data

# If using venv, create symlink:
ln -s /usr/lib/python3/dist-packages/louis venv/lib/python3.*/site-packages/louis
```

**macOS:**
```bash
brew install liblouis
pip install liblouis
```

**Windows:**
Download from https://github.com/liblouis/liblouis/releases

> **Note**: If Liblouis is not available, the system uses a simple ASCII-to-Braille converter. For full Grade 2 (contracted) Braille, Liblouis is required.

## Step 4: Install the Python Library

```bash
# Install in development mode
pip install -e ./lib/tactile-core

# Or with MCP server support
pip install -e "./lib/tactile-core[mcp]"
```

## Step 5: Verify Installation

```bash
# Check CLI version
tactile --version
# Expected: tactile, version 1.0.0

# List available presets
tactile list-presets

# Test conversion with a sample image
tactile image-to-piaf samples/Sketch_Test.jpg --verbose
```

If all commands work, you're ready to go!

## Step 6: Configure for PAI (Optional)

If you're using PAI (Personal AI Infrastructure), the skills will auto-activate based on triggers:

- "convert to tactile" → TactileConversion
- "generate tactile" → TactileGeneration
- "describe this image" → AccessibleDescription

No additional configuration needed.

## Step 7: Configure MCP Server (Non-PAI Users)

If you're using Claude Code without PAI:

1. Open Claude Code settings:
   - macOS/Linux: `~/.config/claude-code/settings.json`
   - Windows: `%APPDATA%\claude-code\settings.json`

2. Add the MCP server:
```json
{
    "mcpServers": {
        "tactile": {
            "command": "python",
            "args": ["/full/path/to/radical-accessibility/mcp/server.py"]
        }
    }
}
```

3. Restart Claude Code.

## Troubleshooting

### "tactile: command not found"

Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

Or install globally:
```bash
pip install ./lib/tactile-core
```

### "tesseract is not installed or not in PATH"

Install Tesseract (see Step 3) and verify:
```bash
tesseract --version
```

### "Unable to get page count. Is poppler installed?"

Install Poppler (see Step 3) and verify:
```bash
pdftoppm -v
```

### Braille shows as boxes or question marks

This usually means the font doesn't support Braille Unicode. The library uses DejaVu Sans which includes Braille. If you see boxes in a PDF viewer, try printing - PIAF machines don't need the visual rendering.

### High density warning

If you see density warnings, use:
```bash
tactile image-to-piaf image.jpg --auto-reduce-density
```

## What's Next?

After installation:

1. Try converting a sample: `tactile image-to-piaf samples/Sketch_Test.jpg`
2. Explore presets: `tactile list-presets`
3. Read the [README](README.md) for full feature documentation
4. Check [VERIFY.md](VERIFY.md) to confirm everything works

## Getting Help

- Check [docs/](docs/) for detailed documentation
- Open an issue on GitHub for bugs or questions
- See the troubleshooting section above for common issues
