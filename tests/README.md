# Tests for HTCondor Shoebill Parser

This directory contains comprehensive unit tests for the HTCondor single-file submission tool.

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_parse_htcss_string.py

# Run specific test
pytest tests/test_parse_htcss_string.py::TestParseShoebillStringBasic::test_parse_valid_template_and_table

# Run with coverage report
pytest --cov=parse --cov-report=html
```

### Setup

Tests require pytest and pytest-mock:

```bash
uv pip install -e ".[dev]"
```

## Test Structure

### Test Files

- **`conftest.py`** - Shared fixtures and test configuration
  - Sample Shoebill strings with various configurations
  - Temporary file fixtures for testing file I/O
  - Mock HTCondor objects for submission testing

- **`test_parse_htcss_string.py`** - Tests for `parse_htcss_string()` function
  - Basic parsing of TEMPLATE and TABLE sections
  - EXEC section handling
  - Error handling for missing sections
  - SUBMIT_REPLACEMENTS (RequestCpus → request_cpus, etc.)
  - Container image handling (adds universe = container)
  - Queue statement appending
  - Edge cases (empty sections, multiple blocks, special characters)

- **`test_parse_htcss_file.py`** - Tests for `parse_htcss_file()` function
  - Reading .htpy files
  - Integration with parse_htcss_string()
  - File I/O error handling
  - UTF-8 and Windows line ending support

- **`test_read_comments.py`** - Tests for `read_comments()` function
  - Extracting comments from Python files using tokenize
  - Various comment styles
  - Integration with Shoebill parsing
  - Edge cases and error handling

- **`test_submission_flow.py`** - Tests for submission workflow
  - `write_table()` and `write_executable()` functions
  - CLI main() function with various flags (--dryrun, --cleanup, --executable)
  - HTCondor submission with mocked Schedd
  - Error handling for missing files and unavailable scheduler

### Test Fixtures

The `tests/fixtures/` directory contains sample files for testing:

- **`simple.htpy`** - Basic Shoebill file with TEMPLATE and TABLE
- **`with_exec.htpy`** - Shoebill file with EXEC section
- **`with_container.htpy`** - Shoebill file using container_image
- **`sample_script.py`** - Python file with Shoebill in comments

## Test Coverage

The test suite covers:

- ✅ Core parsing logic (`parse_htcss_string`)
- ✅ File parsing (`parse_htcss_file`)
- ✅ Comment extraction from Python files (`read_comments`)
- ✅ SUBMIT_REPLACEMENTS application
- ✅ Container universe addition
- ✅ Queue statement generation
- ✅ File operations (`write_table`, `write_executable`)
- ✅ CLI functionality with all flags
- ✅ Error handling for missing sections and files
- ✅ Edge cases (empty sections, special characters, various encodings)

### Known Limitations

Some tests are marked as `xfail` (expected to fail) due to known limitations:

- **Comment extraction**: The current `read_comments()` implementation uses `line.startswith("#")` which may not capture indented comments in Python files. This is a known limitation of the tokenize-based approach.

## Continuous Integration

Tests should be run before commits to ensure code quality:

```bash
# Run tests before committing
pytest -v

# Check coverage
pytest --cov=parse --cov-report=term-missing
```

## Adding New Tests

When adding new functionality:

1. Add appropriate fixtures to `conftest.py` if needed
2. Create tests in the relevant test file
3. Use descriptive test names and docstrings
4. Test both success and failure cases
5. Use mocking for external dependencies (HTCondor, file I/O where appropriate)

## Test Philosophy

- Tests should be **independent** - no test should depend on another
- Tests should be **isolated** - use temporary directories and mocking
- Tests should be **comprehensive** - cover success, failure, and edge cases
- Tests should be **maintainable** - clear names, docstrings, and structure
