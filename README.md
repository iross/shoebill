# HTCondor Single-File Submit Tool

A specialized HTCondor job submission tool that implements a custom markup format (HTCSS) for embedding HTCondor submit descriptions and job tables within single files.

## Features

- **HTCSS Markup Format**: Embed HTCondor submit descriptions directly in `.htpy` files or Python comments
- **Job Tables**: Define multiple jobs with parameters in CSV format
- **Executable Embedding**: Include Python code directly in submission files
- **Automatic Processing**: Converts convenience attributes, adds container universe, generates queue statements
- **Type Safety**: Comprehensive test suite with 83 passing tests
- **Code Quality**: Enforced through pre-commit hooks with ruff and pytest

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd single_file_submit

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package with dev dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks (for contributors)
pre-commit install
```

### Basic Usage

```bash
# Submit a .htpy file with HTCSS markup
python parse.py job.htpy

# Submit a Python file with HTCSS in comments
python parse.py --executable script.py

# Dry run (show submit description without submitting)
python parse.py --dryrun job.htpy

# Cleanup temporary files after submission
python parse.py --cleanup job.htpy
```

## HTCSS Markup Format

HTCSS uses special markers to delimit sections in files:

### Required Sections

- **`%HTCSS TEMPLATE`** - HTCondor submit description
- **`%HTCSS TABLE`** - CSV-formatted job parameters

### Optional Sections

- **`%HTCSS EXEC`** - Python executable code (written to `_exec.py`)
- **`%HTCSS END`** - Explicit end marker (optional)

### Example: Simple Job Submission

Create a file `hello.htpy`:

```
%HTCSS TEMPLATE
executable = /bin/echo
arguments = $(Message)
output = hello_$(JobID).out
error = hello_$(JobID).err
log = hello.log
request_cpus = 1
request_memory = 1GB

%HTCSS TABLE
JobID, Message
1, "Hello from job 1"
2, "Hello from job 2"
3, "Hello from job 3"
```

Submit it:

```bash
python parse.py hello.htpy
```

### Example: With Executable Code

Create a file `process.htpy`:

```
%HTCSS TEMPLATE
arguments = $(Input) $(Output)
output = process_$(JobID).out
error = process_$(JobID).err
log = process.log
RequestCpus = 2
RequestMemory = 2GB

%HTCSS TABLE
JobID, Input, Output
1, data1.txt, result1.txt
2, data2.txt, result2.txt

%HTCSS EXEC
import sys

def main():
    input_file, output_file = sys.argv[1:3]
    with open(input_file) as f:
        content = f.read()
    with open(output_file, 'w') as f:
        f.write(content.upper())

if __name__ == "__main__":
    main()
```

### Example: Container Job

```
%HTCSS TEMPLATE
container_image = docker://python:3.12
arguments = script.py $(Data)
output = container_$(JobID).out
error = container_$(JobID).err
log = container.log
TransferInputFiles = script.py, data.txt
TransferOutputFiles = result.txt

%HTCSS TABLE
JobID, Data
1, data1.txt
2, data2.txt
```

The parser automatically:
- Adds `universe = container` when `container_image` is present
- Converts `RequestCpus` → `request_cpus` (and similar conveniences)
- Appends `queue from TABLE _table.csv`

## Running Tests

### Quick Test Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_parse_htcss_string.py

# Run specific test
pytest tests/test_parse_htcss_string.py::TestParseHTCSSStringBasic::test_parse_valid_template_and_table

# Run with coverage
pytest --cov=parse --cov-report=html
```

### Test Structure

The project has comprehensive test coverage (83 passing tests):

- **`tests/test_parse_htcss_string.py`** (41 tests) - Core HTCSS parsing logic
  - Valid/invalid templates
  - SUBMIT_REPLACEMENTS
  - Container handling
  - Edge cases

- **`tests/test_parse_htcss_file.py`** (16 tests) - File-based parsing
  - Reading `.htpy` files
  - Error handling
  - UTF-8 and Windows line endings

- **`tests/test_read_comments.py`** (19 tests) - Comment extraction
  - Python file tokenization
  - Various comment styles
  - Integration with HTCSS parsing

- **`tests/test_submission_flow.py`** (24 tests) - CLI and submission
  - File operations (`write_table`, `write_executable`)
  - CLI flags (`--dryrun`, `--cleanup`, `--executable`)
  - Mocked HTCondor submission

### Test Fixtures

Test fixtures are available in:
- `tests/conftest.py` - Shared fixtures with documentation
- `tests/fixtures/` - Sample `.htpy` and `.py` files

### Running Tests During Development

Tests run automatically before each commit via pre-commit hooks. To run manually:

```bash
# Run tests manually
pytest -v

# Skip tests for WIP commits (use sparingly!)
SKIP=pytest git commit -m "WIP: feature in progress"
```

For detailed testing documentation, see [`tests/README.md`](tests/README.md).

## Development

### Project Setup

```bash
# Install with dev dependencies (includes pytest, ruff, pre-commit)
uv pip install -e ".[dev]"

# Install pre-commit hooks (REQUIRED for contributors)
pre-commit install
```

### Code Quality

This project uses automated code quality checks:

```bash
# Run all pre-commit hooks manually
pre-commit run --all-files

# Run specific checks
ruff check .           # Linting
ruff format .          # Formatting
pytest                 # Tests
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

- **Ruff**: Fast Python linter and formatter
- **Pytest**: All unit tests must pass
- **Standard checks**: Whitespace, line endings, YAML validation

See [`PRE_COMMIT_SETUP.md`](PRE_COMMIT_SETUP.md) for detailed documentation.

### Development Workflow

1. **Make changes** to code
2. **Run tests**: `pytest -v`
3. **Commit**: `git commit -m "Your message"`
   - Pre-commit hooks run automatically
   - If hooks fail, fix issues and commit again
4. **Push**: `git push`

## Architecture

### Core Components

- **`parse.py`** - Main parsing and submission logic
  - `parse_htcss_string()` - Core HTCSS parser
  - `parse_htcss_file()` - File-based parsing
  - `read_comments()` - Extract HTCSS from Python comments
  - `main()` - CLI entry point

### HTCSS Processing

1. Parse input file to extract TEMPLATE, TABLE, and optional EXEC sections
2. Write TABLE to temporary `_table.csv` file
3. Write EXEC (if present) to `_exec.py` and add `executable = _exec.py` to template
4. Apply SUBMIT_REPLACEMENTS and add container universe if needed
5. Create `htcondor.Submit` object from processed template
6. Submit to HTCondor scheduler
7. Optionally cleanup temporary files

### Submit Template Processing

The parser automatically:
- Adds `universe = container` if `container_image` is specified
- Appends `queue from TABLE _table.csv`
- Replaces convenience attributes:
  - `RequestDisk` → `request_disk`
  - `RequestMemory` → `request_memory`
  - `RequestCpus` → `request_cpus`
  - `TransferInputFiles` → `transfer_input_files`
  - `TransferOutputFiles` → `transfer_output_files`

## Configuration

### Ruff Configuration

Configured in `pyproject.toml`:
- Line length: 100 characters
- Target: Python 3.12+
- Rules: pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, bugbear, comprehensions

### Pytest Configuration

Configured in `pyproject.toml`:
- Test paths: `tests/`
- Python path: `.` (project root)

## Requirements

- Python 3.12+
- HTCondor Python bindings (for actual job submission)
- click (CLI framework)
- pytest and pytest-mock (for testing)
- ruff (for linting/formatting)
- pre-commit (for git hooks)

## Example Files

- **`is_cat.htpy`** - Container-based cat detection job using PyTorch
- **`is_cat.py`** - Python executable with HTCSS embedded in comments
- **`Table Submit.ipynb`** - Jupyter notebook demonstrating parsing workflow

## Temporary Files

The tool creates temporary files in the current working directory:
- `_table.csv` - Job parameter table
- `_exec.py` - Executable code (if EXEC section present)

Use `--cleanup` flag to automatically remove `_table.csv` after submission.

## Documentation

- **`CLAUDE.md`** - Development guidelines and project overview
- **`tests/README.md`** - Comprehensive testing documentation
- **`PRE_COMMIT_SETUP.md`** - Pre-commit hooks guide

## Contributing

1. Fork the repository
2. Install dev dependencies: `uv pip install -e ".[dev]"`
3. Install pre-commit hooks: `pre-commit install`
4. Create a feature branch
5. Make your changes (tests run automatically on commit)
6. Submit a pull request

### Code Quality Standards

All contributions must:
- Pass all existing tests (83 tests)
- Pass ruff linting and formatting
- Include tests for new functionality
- Follow PEP8 naming conventions
- Have meaningful commit messages

## License

[Add license information]

## Support

For issues or questions:
- Check `CLAUDE.md` for development guidelines
- See `tests/README.md` for testing help
- See `PRE_COMMIT_SETUP.md` for git hook issues
