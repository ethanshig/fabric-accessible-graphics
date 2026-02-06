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
  tactile --version
  # Expected: tactile, version 1.0.0
  ```

## System Dependencies

- [ ] Tesseract OCR installed
  ```bash
  tesseract --version
  ```

- [ ] Poppler installed
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
  tactile list-presets
  # Should show 10 presets
  ```

- [ ] Can convert an image
  ```bash
  tactile image-to-piaf samples/Sketch_Test.jpg --verbose
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
  tactile image-to-piaf samples/ANNEX-PLANS-OFFICIAL_Page_1.jpg --detect-text --verbose
  ```

### Presets

- [ ] Can use presets
  ```bash
  tactile image-to-piaf samples/Sketch_Test.jpg --preset sketch --verbose
  ```

## MCP Server (Optional)

- [ ] MCP server starts without errors
  ```bash
  python mcp/server.py &
  # Should start without errors (Ctrl+C to stop)
  ```

## PAI Integration (Optional)

If using PAI, verify skills are discoverable:

- [ ] TactileConversion skill exists
  ```bash
  ls src/skills/TactileConversion/
  ```

- [ ] TactileGeneration skill exists
  ```bash
  ls src/skills/TactileGeneration/
  ```

- [ ] AccessibleDescription skill exists
  ```bash
  ls src/skills/AccessibleDescription/
  ```

## Quick Validation Script

Run all checks at once:

```bash
#!/bin/bash
echo "=== Radical Accessibility Verification ==="

echo -n "Python version: "
python3 --version

echo -n "tactile version: "
tactile --version 2>/dev/null || echo "NOT INSTALLED"

echo -n "Tesseract: "
tesseract --version 2>/dev/null | head -1 || echo "NOT INSTALLED"

echo -n "Poppler: "
pdftoppm -v 2>&1 | head -1 || echo "NOT INSTALLED"

echo -n "Liblouis: "
python3 -c "import louis; print(louis.version())" 2>/dev/null || echo "NOT INSTALLED (optional)"

echo ""
echo "Testing conversion..."
tactile image-to-piaf samples/Sketch_Test.jpg -o /tmp/test_verify.pdf --verbose 2>&1 | tail -5

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
| tactile version | Run `pip install -e ./lib/tactile-core` |
| Tesseract | See INSTALL.md Step 3 |
| Poppler | See INSTALL.md Step 3 |
| Liblouis | Optional - see INSTALL.md Step 3 |
| Conversion test | Check error messages, verify dependencies |

## Phase 6: Hooks and Memory Integration (Optional)

These optional features enable proactive image detection and learning from usage.

### Hooks Structure

- [ ] ImageDetector hook exists
  ```bash
  ls src/hooks/ImageDetector.ts
  ```

- [ ] ConversionTracker hook exists
  ```bash
  ls src/hooks/ConversionTracker.ts
  ```

- [ ] FeedbackCapture hook exists
  ```bash
  ls src/hooks/FeedbackCapture.ts
  ```

- [ ] Memory module exists
  ```bash
  ls src/hooks/lib/memory.ts
  ```

### Hook Functionality

- [ ] ImageDetector parses input correctly
  ```bash
  echo '{"message": "here is a floor plan", "attachments": [{"type": "image"}]}' | bun src/hooks/ImageDetector.ts
  # Should output JSON with detected: true, category: floor_plan
  ```

- [ ] Memory directory creation works
  ```bash
  bun -e "import m from './src/hooks/lib/memory'; m.ensureMemorySetup(); console.log('OK')"
  # Should create ~/.radical-accessibility/memory/
  ```

### Memory Integration

- [ ] Conversion recording works
  ```bash
  bun -e "
    import m from './src/hooks/lib/memory';
    const id = m.recordConversion({
      session_id: 'test',
      image_type: 'floor_plan',
      preset_used: 'floor_plan',
      settings: {},
      success: true
    });
    console.log('Recorded:', id);
  "
  ```

- [ ] Feedback recording works
  ```bash
  bun -e "
    import m from './src/hooks/lib/memory';
    m.recordFeedback({
      conversion_id: 'test-123',
      rating: 4,
      comment: 'Good conversion',
      tags: ['clear']
    });
    console.log('OK');
  "
  ```

- [ ] Memory stats available
  ```bash
  bun -e "
    import m from './src/hooks/lib/memory';
    console.log(m.getMemoryStats());
  "
  ```

### Hook Installation (PAI Users)

If using PAI, add hooks to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__tactile__*",
        "hooks": [
          { "type": "command", "command": "bun /path/to/src/hooks/ConversionTracker.ts" }
        ]
      }
    ]
  }
}
```

---

## All Checks Passed?

If all checks pass, your installation is complete. You can now:

1. Convert images: `tactile image-to-piaf your-image.jpg`
2. Use with PAI: Just say "convert to tactile" or "describe this image"
3. Use with MCP: Configure in Claude Code settings

See [README.md](README.md) for full usage documentation.
