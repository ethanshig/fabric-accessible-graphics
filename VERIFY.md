# Radical Accessibility - Installation Verification

Use this checklist to verify your installation is complete and working.

## Core Installation

- [ ] Python 3.10+ installed
  ```bash
  python3 --version
  ```

- [ ] Virtual environment created and activated
  ```bash
  which python  # Should show venv path
  ```

- [ ] tactile-core library installed
  ```bash
  pip show tactile-core
  ```

- [ ] CLI available
  ```bash
  tact --version
  # Expected: tact, version 1.0.0
  ```

## System Dependencies

- [ ] Tesseract OCR installed (optional fallback, EasyOCR is primary)
  ```bash
  tesseract --version
  ```

- [ ] Poppler installed (optional, for multi-page PDF input)
  ```bash
  pdftoppm -v
  ```

- [ ] Liblouis installed (optional, for Grade 2 Braille)
  ```bash
  python3 -c "import louis; print(louis.version())"
  ```

## Functional Tests

### Basic Conversion

- [ ] Can list presets
  ```bash
  tact presets
  # Should show 10 presets
  ```

- [ ] Can convert an image
  ```bash
  tact convert samples/Sketch_Test.jpg --verbose
  # Should create samples/Sketch_Test_piaf.pdf
  ```

- [ ] Output PDF exists and has content
  ```bash
  ls -la samples/Sketch_Test_piaf.pdf
  # Should show file with size > 0
  ```

### Text Detection

- [ ] Can detect text and add Braille
  ```bash
  tact convert samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --detect-text --verbose
  ```

### Presets

- [ ] Can use presets
  ```bash
  tact convert samples/Sketch_Test.jpg --preset sketch --verbose
  ```

## MCP Server (Optional)

- [ ] MCP server starts without errors
  ```bash
  python mcp/server.py &
  # Should start without errors (Ctrl+C to stop)
  ```

## Quick Validation Script

Run all checks at once:

```bash
#!/bin/bash
echo "=== Radical Accessibility Verification ==="

echo -n "Python version: "
python3 --version

echo -n "tact version: "
tact --version 2>/dev/null || echo "NOT INSTALLED"

echo -n "Tesseract: "
tesseract --version 2>/dev/null | head -1 || echo "NOT INSTALLED"

echo -n "Poppler: "
pdftoppm -v 2>&1 | head -1 || echo "NOT INSTALLED"

echo -n "Liblouis: "
python3 -c "import louis; print(louis.version())" 2>/dev/null || echo "NOT INSTALLED (optional)"

echo ""
echo "Testing conversion..."
tact convert samples/Sketch_Test.jpg -o /tmp/test_verify.pdf --verbose 2>&1 | tail -5

if [ -f /tmp/test_verify.pdf ]; then
    echo "SUCCESS: Test PDF created"
    rm /tmp/test_verify.pdf
else
    echo "FAILED: Test PDF not created"
fi

echo ""
echo "=== Verification Complete ==="
```

## Troubleshooting Failed Checks

| Check | If Failed |
|-------|-----------|
| Python version | Install Python 3.10+ |
| tact version | Run `pip install -e ./lib/tactile-core` |
| Tesseract | See INSTALL.md Step 3 |
| Poppler | See INSTALL.md Step 3 |
| Liblouis | Optional - see INSTALL.md Step 3 |
| Conversion test | Check error messages, verify dependencies |

---

## All Checks Passed?

If all checks pass, your installation is complete. You can now:

1. Convert images: `tact convert your-image.jpg`
2. Use with Claude Code: Say "convert to tactile" or "describe this image"
3. Configure MCP: See [docs/MCP_SETUP.md](docs/MCP_SETUP.md)

See [README.md](README.md) for full usage documentation.
