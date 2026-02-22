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

## Step 4: Install the Python Libraries

```bash
# Install TACT (image-to-tactile conversion)
pip install -e ./lib/tactile-core

# Install TASC (programmatic Rhino design)
pip install -e ./lib/tasc-core

# Or with MCP server support for TACT
pip install -e "./lib/tactile-core[mcp]"
```

## Step 5: Verify Installation

```bash
# Check TACT CLI
tact --version
# Expected: tact, version 1.0.0

# Check TASC CLI
tasc version
# Expected: TASC - Tactile Architecture Scripting Console v0.1.0

# List TACT presets
tact presets

# Test TACT conversion with a sample image
tact samples/Sketch_Test.jpg --verbose

# Test TASC site creation
tasc site 200 150
tasc describe
tasc reset
```

If all commands work, you're ready to go!

## Step 5b: Install RhinoMCP (Optional - for live Rhino connection)

TASC can send geometry directly to Rhino in real-time via the RhinoMCP plugin. Additionally, the `rhinomcp` Python package provides an MCP server bridge so Claude Code can control Rhino directly with native tools (create/modify objects, booleans, viewport capture, etc.).

### Install the Rhino plugin

1. Open **Rhino** (7 or newer)
2. Go to **Tools > Package Manager**
3. Search for **rhinomcp** (by Jingcheng Chen)
4. Click **Install**, restart Rhino
5. In Rhino's command line, type `MCPStart` to start the socket server (TCP port 1999)

### Install the MCP server bridge

```bash
# Option A: Install directly in your venv (recommended)
pip install rhinomcp

# Option B: Use uvx (no install needed)
# Requires uv: curl -LsSf https://astral.sh/uv/install.sh | sh
uvx rhinomcp
```

### Configure the MCP server (for Claude Code)

Add to your project's `.mcp.json` or Claude Code settings:

**Standard (Rhino on same machine):**
```json
{
    "mcpServers": {
        "rhinomcp": {
            "command": "/path/to/venv/bin/rhinomcp"
        }
    }
}
```

**WSL2 (Rhino on Windows, Claude Code in WSL2):**

The RhinoMCP plugin binds to `127.0.0.1:1999` on Windows, which is unreachable from WSL2. Set the `RHINO_MCP_HOST` env var to the WSL2 gateway IP:

```json
{
    "mcpServers": {
        "rhinomcp": {
            "command": "/path/to/venv/bin/rhinomcp",
            "env": {
                "RHINO_MCP_HOST": "172.28.208.1",
                "RHINO_MCP_PORT": "1999"
            }
        }
    }
}
```

> **Finding your WSL2 gateway IP:** Run `ip route show default` in WSL2. The IP after "via" is your gateway (e.g., `172.28.208.1`).

> **One-time Windows setup:** Run these in an admin PowerShell to allow WSL2 to reach Rhino's port:
> ```powershell
> netsh interface portproxy add v4tov4 listenport=1999 listenaddress=0.0.0.0 connectport=1999 connectaddress=127.0.0.1
> netsh advfirewall firewall add rule name="RhinoMCP" dir=in action=allow protocol=TCP localport=1999
> ```

### Verify the connection

```bash
# From your terminal (with venv active):
tasc connect
# Expected: Connected to Rhino via MCP socket at 127.0.0.1:1999
# (or via WSL2 gateway: Connected to Rhino via MCP socket at 172.28.208.1:1999)
```

Without RhinoMCP, TASC still works fully offline -- text feedback, `.3dm` file export, and PIAF export all work without a Rhino connection.

## Step 6: Configure MCP Server (Non-PAI Users)

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

### "tact: command not found" or "tasc: command not found"

Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

Or reinstall:
```bash
pip install -e ./lib/tactile-core   # for tact
pip install -e ./lib/tasc-core      # for tasc
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

1. Try converting a sample: `tact samples/Sketch_Test.jpg`
2. Explore presets: `tact presets`
3. Try TASC: `tasc site 200 150 && tasc zone living 50 40 --at 10,10 && tasc describe`
4. Read the [README](README.md) for full feature documentation
5. Read [lib/tasc-core/README.md](lib/tasc-core/README.md) for TASC command reference
6. Check [VERIFY.md](VERIFY.md) to confirm everything works

## Getting Help

- Check [docs/](docs/) for detailed documentation
- Open an issue on GitHub for bugs or questions
- See the troubleshooting section above for common issues
