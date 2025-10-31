---
id: task-1
title: Add self-submitting notebook hooks
status: To Do
assignee: []
created_date: '2025-10-31 18:53'
labels: []
dependencies: []
---

## Overview

Enable Jupyter notebooks to self-submit HTCondor jobs by parsing HTCSS markup from notebook cells and extracting executable code directly from tagged code cells. This extends the existing HTCSS system to support notebook-first workflows.

## Goals

1. Parse HTCSS markup from notebook cells (both markdown and code comments)
2. Extract executable Python code from designated notebook cells
3. Provide IPython magic commands for in-notebook submission
4. Expose Python API for programmatic submission
5. Maintain compatibility with existing `.htpy` and `.py` file formats

## Technical Approach

### Markup Parsing
- Support HTCSS markers in **both** markdown cells and code cell comments
- Markdown cells: Direct `%HTCSS TEMPLATE` / `%HTCSS TABLE` markers
- Code comments: `#%HTCSS TEMPLATE` / `#%HTCSS TABLE` in comment lines
- Parser should check both locations and merge if found in multiple places

### Executable Code Extraction

**Inclusion Method**: Cell tags
- Include all cells by default
- If this default is overridden, then cells containing `#%HTCSS INCLUDE` comment anywhere in source will be included

**Exclusion Method**: Magic markers
- Cells containing `#%HTCSS EXCLUDE` comment will be skipped, even if tagged
- Provides quick override without modifying cell tags
- Visible in code, works in any editor
- Exclusion takes precedence over inclusion tags

**Processing Logic**:
1. If default is kept, use all cells.
1a. If default is changed to exclude all, find all cells with `#%HTCSS INCLUDE` tag in notebook metadata
2. Filter out cells containing `#%HTCSS EXCLUDE` comment anywhere in source
3. Extract source code from remaining cells in notebook order
4. Concatenate with newlines to create `_exec.py`
5. Preserve imports and function definitions across cells

**Example Workflow (Include All by Default)**:
```python
# Cell 1 (code) - Included automatically
import torch
import sys

# Cell 2 (code) - Included automatically
def load_model():
    return torch.load('model.pth')

# Cell 3 (code) - EXCLUDED via marker
#%HTCSS EXCLUDE
# Debug/testing code - don't include in job
print("Testing locally...")
model = load_model()

# Cell 4 (code) - Included automatically
if __name__ == "__main__":
    model = load_model()
    input_file = sys.argv[1]
    # ... job logic
```
Result: Cells 1, 2, and 4 concatenated into `_exec.py` (Cell 3 excluded)

**Example Workflow (Opt-In Mode)**:
```python
# Cell 1 (code) - NOT included (no marker)
import pandas as pd
df = pd.read_csv('data.csv')  # Local exploration

# Cell 2 (code) - INCLUDED via marker
#%HTCSS INCLUDE
import torch
import sys

# Cell 3 (code) - INCLUDED via marker
#%HTCSS INCLUDE
def load_model():
    return torch.load('model.pth')

# Cell 4 (code) - NOT included (no marker)
# More local testing
print(load_model())

# Cell 5 (code) - INCLUDED via marker
#%HTCSS INCLUDE
if __name__ == "__main__":
    model = load_model()
    # ... job logic
```
Result: Only cells 2, 3, and 5 concatenated into `_exec.py`

**Configuration**: Mode can be set via magic command argument or config:
```python
%%htcss_submit --include-mode=all  # Default: include all except excluded
%%htcss_submit --include-mode=explicit  # Only include cells with #%HTCSS INCLUDE
```

### User Interfaces

#### IPython Magic Command
```python
# In notebook:
%%htcss_submit
# Optional arguments: --dryrun, --cleanup
```

#### Python API
```python
from htcss import submit_notebook

# Submit current notebook
submit_notebook('notebook.ipynb', dryrun=False, cleanup=True)

# Or submit from within running notebook
submit_notebook(dryrun=True)  # Auto-detects current notebook
```

## Implementation Tasks

1. Create `parse_notebook.py` module with:
   - `parse_htcss_notebook(notebook_path)` function
   - Cell extraction logic based on tags/markers
   - Integration with existing `parse_htcss_string()`

2. Add notebook parsing to `parse.py`:
   - Add `--notebook` flag to CLI
   - Route to notebook parser

3. Create `magic.py` module:
   - Implement `%%htcss_submit` magic command
   - Handle IPython context and current notebook detection

4. Create `api.py` module:
   - Implement `submit_notebook()` function
   - Auto-detection of current notebook in IPython context

5. Update `pyproject.toml`:
   - Add `jupyter` and `ipython` dependencies
   - Add entry points for magic commands

6. Add tests and example notebook

## Resolved Design Decisions

✓ **Cell selection method**:
  - Default: Include all code cells, use `#%HTCSS EXCLUDE` to skip specific cells
  - Opt-in mode: Use `#%HTCSS INCLUDE` to explicitly mark cells for inclusion
  - Mode configurable via magic command argument `--include-mode`

## Acceptance Criteria

### Core Functionality
- [ ] Notebook parser can extract HTCSS TEMPLATE section from markdown cells
- [ ] Notebook parser can extract HTCSS TEMPLATE section from code cell comments
- [ ] Notebook parser can extract HTCSS TABLE section from markdown cells
- [ ] Notebook parser can extract HTCSS TABLE section from code cell comments
- [ ] Parser merges TEMPLATE/TABLE if found in multiple locations

### Cell Extraction
- [ ] Default mode: All code cells are included in `_exec.py` by default
- [ ] Cells with `#%HTCSS EXCLUDE` comment are skipped
- [ ] Opt-in mode (`--include-mode=explicit`): Only cells with `#%HTCSS INCLUDE` are included
- [ ] Exclusion takes precedence over inclusion in all modes
- [ ] Cells are concatenated in notebook order
- [ ] Generated `_exec.py` is syntactically valid Python

### User Interfaces
- [ ] `%%htcss_submit` magic command works in notebook cells
- [ ] Magic command supports `--dryrun` flag (shows submit description without submitting)
- [ ] Magic command supports `--cleanup` flag (removes temporary files)
- [ ] Magic command supports `--include-mode=all` and `--include-mode=explicit` flags
- [ ] `submit_notebook()` Python API function works programmatically
- [ ] API auto-detects current notebook when called without path argument
- [ ] CLI supports `python parse.py --notebook <file>.ipynb`

### Integration
- [ ] Notebook submission integrates with existing HTCondor submission flow
- [ ] Temporary files (`_table.csv`, `_exec.py`) are created correctly
- [ ] Submit description includes `executable = _exec.py` automatically
- [ ] All existing SUBMIT_REPLACEMENTS are applied to notebook submissions

### Testing & Documentation
- [ ] Example notebook demonstrates the workflow
- [ ] Tests cover both include modes (all vs explicit)
- [ ] Tests verify HTCSS parsing from both markdown and code comments
- [ ] Tests verify exclusion logic
- [ ] Documentation explains cell tagging approach

## Resolved Design Decisions

- ✅ **Error handling**: Use standard Python exceptions (can be caught with try/except). Simple and follows Python conventions.
- ✅ **Output capture**: Display formatted output in notebook cell AND return HTCondor result objects. Provides both immediate visual feedback and programmatic access.
- ✅ **Notebook state**: Code only - no variable serialization. Jobs start fresh with clean state. Simple and predictable.
- ✅ **Cell boundary markers**: Optional via `--debug-markers` flag. Adds comments like `# Cell 3` in `_exec.py` when enabled for debugging.

## Implementation Notes

### Notebook Structure
- Jupyter notebooks are JSON files with cells array
- Use `nbformat` library for parsing (standard Jupyter tool)
- Cell types: `markdown` and `code`
- Each cell has `source` field (string or list of strings)

### Markup Pattern
- The project uses `%HTCSS` as the markup pattern (consistent across `.htpy`, `.py`, and `.ipynb` files)
- Pattern defined in `parse.py`: `PATTERN = "%HTCSS"`
- Sections: TEMPLATE (required), TABLE (required), EXEC (optional)

### Existing Infrastructure to Leverage
- `parse_htcss_string(text: str) -> dict` - core parsing logic (reuse this!)
- `write_table(table)` - writes `_table.csv`
- `write_executable(executable)` - writes `_exec.py`
- `SUBMIT_REPLACEMENTS` - automatic attribute mapping (RequestCpus → request_cpus, etc.)
- Comprehensive test fixtures in `tests/conftest.py`

### Dependencies Needed
- `nbformat` - official Jupyter notebook format library
- `ipython` - for magic command support and notebook context detection
- Already have: `click` (CLI), `htcondor` (submission), `pytest` (testing)
