# Tactile Core MCP Server

This is a standalone MCP (Model Context Protocol) server for users who want to use the tactile conversion tools directly in Claude Code without the full PAI Pack infrastructure.

## Installation

1. Install the tactile-core library:
   ```bash
   cd /path/to/radical-accessibility
   pip install -e "./lib/tactile-core[mcp]"
   ```

2. Install system dependencies (see `lib/tactile-core/README.md`)

3. Add to Claude Code's MCP configuration:

   **macOS/Linux**: `~/.config/claude-code/settings.json`
   **Windows**: `%APPDATA%\claude-code\settings.json`

   ```json
   {
       "mcpServers": {
           "tactile": {
               "command": "python",
               "args": ["/path/to/radical-accessibility/mcp/server.py"]
           }
       }
   }
   ```

## Available Tools

The MCP server provides these tools:

- **image_to_piaf** - Convert images to tactile-ready PDFs
- **list_presets** - List available conversion presets
- **analyze_image** - Pre-flight analysis of images
- **describe_image** - Generate accessibility descriptions
- **extract_text_with_vision** - OCR text extraction
- **assess_tactile_quality** - Quality assessment

## Usage

Once configured, you can use natural language in Claude Code:

- "Convert this floor plan to a tactile PDF"
- "Analyze this image for tactile conversion"
- "Describe this architectural drawing for accessibility"

## PAI Pack Alternative

If you're using PAI (Personal AI Infrastructure), consider installing the full **Radical Accessibility** pack instead, which provides:

- Richer skill-based workflows
- AI-powered tactile generation
- Enhanced descriptions
- Memory and learning

See the main README for PAI Pack installation.
