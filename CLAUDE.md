# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Shoebill** is a specialized HTCondor job submission tool that implements a custom markup format (Shoebill markup) for embedding HTCondor submit descriptions and job tables within single files. The tool parses these annotated files and submits jobs to HTCondor using the Python bindings. It includes a core parsing system (`parse.py`) that currently handles two input modes:

1. **Direct Shoebill files** (`.htpy`): Plain text files with markup
2. **Executable files with embedded Shoebill**: Python files where markup is embedded in comments (using `tokenize` module to extract)

In time, this should grow to a full library, which would also allow for "self-submitting notebooks" which can read cells and embedded comments and similar submit a job.
## Architecture

### Core Parsing System (parse.py)

The parser handles two input modes:

1. **Direct Shoebill files** (`.htpy`): Plain text files with Shoebill markup
2. **Executable files with embedded Shoebill**: Python files where Shoebill markup is embedded in comments (using `tokenize` module to extract)

### Shoebill Markup Format

Files use special markers to delimit sections:
- `%Shoebill <SECTION_NAME>` - Starts a section
- `%Shoebill END` - Ends parsing (optional)

**Required sections:**
- `TEMPLATE` - HTCondor submit description
- `TABLE` - CSV-formatted job parameters

**Optional sections:**
- `EXEC` - Python executable code to be written to `_exec.py`

### Submit Template Processing

The parser automatically:
1. Adds `universe = container` if `container_image` is specified in TEMPLATE
2. Appends `queue from TABLE _table.csv` to submit template
3. Replaces convenience attributes with HTCondor submit language:
   - `RequestDisk` → `request_disk`
   - `RequestMemory` → `request_memory`
   - `RequestCpus` → `request_cpus`
   - `TransferInputFiles` → `transfer_input_files`
   - `TransferOutputFiles` → `transfer_output_files`

### Job Submission Flow

1. Parse input file to extract TEMPLATE, TABLE, and optional EXEC sections
2. Write TABLE to temporary `_table.csv` file
3. Write EXEC (if present) to `_exec.py` and add `executable = _exec.py` to template
4. Create `htcondor.Submit` object from processed template
5. Submit to HTCondor scheduler
6. Optionally cleanup temporary files

## Development Commands

### Running the Tool

```bash
# Submit a .htpy file with Shoebill markup
python parse.py <file>.htpy

# Submit a Python file with Shoebill in comments
python parse.py --executable <file>.py

# Dry run (show submit description without submitting)
python parse.py --dryrun <file>

# Cleanup temporary files after submission
python parse.py --cleanup <file>
```

### Project Setup
Use uv for all package management.

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install for development (without HTCondor - useful on macOS)
uv pip install -e ".[dev]"

# Install with HTCondor support (Linux only)
uv pip install -e ".[dev,condor]"

# Or install everything for production use
uv pip install -e ".[all]"

# Install pre-commit hooks (REQUIRED for development)
pre-commit install
```

**Note**: HTCondor is only available on Linux. On macOS/Windows, you can still develop and test the parsing/markup functionality without HTCondor installed. Tests requiring actual HTCondor submission will be automatically skipped on unsupported platforms.

### Testing

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_parse_htcss_string.py
```

See `tests/README.md` for comprehensive testing documentation.

### Code Quality & Pre-commit Hooks

This project uses pre-commit hooks to automatically ensure code quality before commits:

- **Ruff**: Fast Python linter and formatter (replaces black, flake8, isort)
- **Pytest**: All unit tests must pass before commit
- **Standard checks**: Trailing whitespace, file endings, YAML validation, etc.

```bash
# Run pre-commit hooks manually on all files
pre-commit run --all-files

# Run pre-commit on staged files only
pre-commit run

# Update hook versions to latest
pre-commit autoupdate

# Skip hooks for emergency commits (use sparingly!)
git commit --no-verify

# Skip specific hook
SKIP=pytest git commit
```

**Note**: Pre-commit hooks are automatically run before each commit. If hooks fail, the commit will be blocked until issues are fixed.

### Git Commit Authorship

When creating git commits:

- **NEVER** modify git config or change the author/committer settings
- All commits MUST be authored by the user (using their configured git identity)
- Claude MAY be listed as co-author in commit messages using:
  ```
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```
- The user is the primary author of all work; Claude assists with implementation

## Key Implementation Details

- The parser uses `parse_htcss_string()` as the core parsing function, making it testable independently of file I/O
- Temporary files (`_table.csv`, `_exec.py`) are created in the current working directory
- The tool requires a running HTCondor scheduler to submit jobs (will fail with "Unable to locate local daemon" if HTCondor is not running)
- Code quality is enforced through pre-commit hooks (ruff linting/formatting + pytest)

## Example Files

- `is_cat.htpy` - Example Shoebill file with container-based cat detection job using PyTorch
- `is_cat.py` - Example Python executable with Shoebill embedded in comments (currently incomplete/commented out)
- `Table Submit.ipynb` - Jupyter notebook demonstrating the parsing and submission workflow

<!-- BACKLOG.MD MCP GUIDELINES START -->

<CRITICAL_INSTRUCTION>

## BACKLOG WORKFLOW INSTRUCTIONS

This project uses Backlog.md MCP for all task and project management activities.

**CRITICAL GUIDANCE**

- If your client supports MCP resources, read `backlog://workflow/overview` to understand when and how to use Backlog for this project.
- If your client only supports tools or the above request fails, call `backlog.get_workflow_overview()` tool to load the tool-oriented overview (it lists the matching guide tools).

- **First time working here?** Read the overview resource IMMEDIATELY to learn the workflow
- **Already familiar?** You should have the overview cached ("## Backlog.md Overview (MCP)")
- **When to read it**: BEFORE creating tasks, or when you're unsure whether to track work

These guides cover:
- Decision framework for when to create tasks
- Search-first workflow to avoid duplicates
- Links to detailed guides for task creation, execution, and completion
- MCP tools reference

You MUST read the overview resource to understand the complete workflow. The information is NOT summarized here.

</CRITICAL_INSTRUCTION>

<!-- BACKLOG.MD MCP GUIDELINES END -->
