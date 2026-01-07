# Fabric-Access Toolkit Consolidation Plan

## Goals
1. **Naming consistency**: Rename MCP `convert_to_tactile` → `image_to_piaf`
2. **Feature parity**: Add MCP-only features to CLI (scaling, abbreviation key, multi-page PDF)
3. **Architecture**: Shared Core + Thin Wrappers (eliminate duplication)

---

## Architecture Overview

```
src/fabric_access/
├── core/
│   └── converter.py      # NEW: TactileConverter, ConversionParams, ConversionResult
├── cli.py                # Thin wrapper (~400 lines, down from 896)
└── mcp_server/
    ├── server.py         # Tool registration (rename tool)
    └── tools.py          # Thin wrapper (~600 lines, down from 1875)
```

**Key principle**: Core returns structured `ConversionResult` dataclass. CLI formats for terminal, MCP formats as JSON.

---

## Phase 1: Create Shared Core Module

**Create**: `src/fabric_access/core/converter.py`

### ConversionParams dataclass
```python
@dataclass
class ConversionParams:
    # Required
    input_path: str

    # Output
    output_path: Optional[str] = None
    paper_size: str = "letter"

    # Preset/threshold
    preset: Optional[str] = None
    threshold: Optional[int] = None

    # Enhancement
    enhance: Optional[str] = None
    enhance_strength: float = 1.0

    # Text/Braille
    detect_text: bool = True
    braille_grade: int = 2
    braille_placement: str = "overlay"

    # Scaling (NEW for CLI)
    scale_percent: Optional[float] = None
    auto_scale: bool = True
    max_scale_factor: Optional[float] = None

    # Abbreviation key (NEW for CLI)
    use_abbreviation_key: bool = True
    force_abbreviation_key: bool = False

    # Density
    auto_reduce_density: bool = False
    target_density: Optional[float] = None
    max_reduction_iterations: Optional[int] = None

    # Tiling
    enable_tiling: bool = False
    tile_overlap: float = 0.0
    add_registration_marks: bool = True

    # Zoom
    zoom_region: Optional[Tuple[float, float, float, float]] = None
    zoom_regions: Optional[List[Dict[str, Any]]] = None

    # MCP-only (not exposed in CLI)
    zoom_to: Optional[str] = None
    claude_text_json: Optional[Union[str, List]] = None
    use_grid_overlay: bool = False
    assess_quality: bool = False

    # CLI-only
    verbose: bool = False
    interactive: bool = False
    config_path: Optional[str] = None
```

### ConversionResult dataclass
```python
@dataclass
class ConversionResult:
    success: bool
    output_file: Optional[str] = None
    density_percentage: Optional[float] = None
    braille_labels_count: int = 0
    key_entries_count: int = 0
    detected_text_count: int = 0
    scale_applied: float = 100.0
    auto_scale_used: bool = False
    needs_tiling: bool = False
    page_count: int = 1
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None
    error_type: Optional[str] = None
    # ... additional metadata fields
```

### TactileConverter class
- `convert(params: ConversionParams) -> ConversionResult`
- `convert_with_predetected_text(params, texts) -> ConversionResult` (for MCP hybrid OCR)
- Internal methods: `_load_configuration()`, `_apply_preset()`, `_process_image()`, `_handle_scaling()`, `_create_braille_labels()`, `_generate_pdf()`

---

## Phase 2: Add New CLI Options

**Modify**: `src/fabric_access/cli.py`

### New Scaling Options
| Option | Type | Default | Help |
|--------|------|---------|------|
| `--scale-percent` | float | None | Manual zoom/scale percentage (100=no change, 200=2x) |
| `--auto-scale/--no-auto-scale` | bool | True | Auto-scale so Braille fits in bounding boxes |
| `--max-scale-factor` | float | None | Cap auto-scale (e.g., 2.0 = 200% max) |

### New Abbreviation Key Options
| Option | Type | Default | Help |
|--------|------|---------|------|
| `--abbreviation-key/--no-abbreviation-key` | bool | True | Auto-abbreviate labels that don't fit |
| `--force-abbreviation-key` | flag | False | Abbreviate ALL labels |

### Multi-page PDF
- Auto-detect multi-page PDF input (no flag needed)
- Process each page, combine output with shared key

### Batch Command (full parity)
Add same options to `batch` command:
- `--scale-percent`, `--auto-scale/--no-auto-scale`, `--max-scale-factor`
- `--abbreviation-key/--no-abbreviation-key`, `--force-abbreviation-key`

---

## Phase 3: Refactor MCP Tools

**Modify**: `src/fabric_access/mcp_server/tools.py`

1. Rename function `convert_to_tactile` → `image_to_piaf` (no backward compat alias)
2. Extract common logic to call `TactileConverter.convert()`
3. Keep MCP-only phases in wrapper:
   - `_handle_zoom_to_phase()` (natural language zoom)
   - `_handle_hybrid_ocr_phase1()` (Tesseract + Claude instructions)
   - `_merge_hybrid_ocr()` (merge Claude text with Tesseract positions)
   - `_handle_quality_assessment_phase()` (Claude visual comparison)

**Modify**: `src/fabric_access/mcp_server/server.py`
- Update tool registration: `mcp.tool()(image_to_piaf)`

---

## Phase 4: Refactor CLI to Use Core

**Modify**: `src/fabric_access/cli.py`

1. Import `TactileConverter`, `ConversionParams`
2. Build `ConversionParams` from Click options
3. Call `converter.convert(params)`
4. Format `ConversionResult` for terminal output
5. Keep CLI-specific logic: interactive mode, verbose logging

---

## Phase 5: Update Documentation

**Modify**:
- `docs/COMMAND_REFERENCE.md` - Add new CLI options, update MCP tool name
- `README.md` - Update examples
- CLI `--help` docstrings

---

## Files to Modify

| File | Action | Lines (before→after) |
|------|--------|---------------------|
| `src/fabric_access/core/converter.py` | CREATE | 0 → ~600 |
| `src/fabric_access/cli.py` | MODIFY | 896 → ~400 |
| `src/fabric_access/mcp_server/tools.py` | MODIFY | 1875 → ~600 |
| `src/fabric_access/mcp_server/server.py` | MODIFY | minor (rename) |
| `docs/COMMAND_REFERENCE.md` | MODIFY | update |

---

## MCP-Only Features (Require Claude Vision)

These stay in `tools.py` wrapper, not in core:
- `zoom_to` - natural language zoom target
- `claude_text_json` - hybrid OCR phase 2
- `use_grid_overlay` - grid cell positioning
- `assess_quality` - returns instructions for Claude
- `describe_image` tool
- `extract_text_with_vision` tool
- `assess_tactile_quality` tool

---

## Implementation Order

1. **Phase 1**: Create `core/converter.py` with dataclasses and TactileConverter (non-breaking)
2. **Phase 2**: Add new CLI options to `cli.py` (non-breaking, uses existing logic)
3. **Phase 3**: Refactor MCP `tools.py` to use TactileConverter + rename tool
4. **Phase 4**: Refactor CLI `cli.py` to use TactileConverter
5. **Phase 5**: Update documentation
