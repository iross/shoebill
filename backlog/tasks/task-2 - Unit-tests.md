---
id: task-2
title: Unit tests
status: Done
assignee: []
created_date: '2025-10-31 19:08'
updated_date: '2025-10-31 19:33'
labels: []
dependencies: []
---

## Overview

Add comprehensive unit tests for the HTCSS parser and submission system. Currently the codebase has no automated tests, which makes it difficult to refactor safely or verify correctness of the parsing logic and HTCondor integration.

## Goals

1. Establish pytest-based testing infrastructure
2. Test HTCSS parsing logic for all supported file formats
3. Test HTCondor submit description generation
4. Mock HTCondor scheduler interactions to enable testing without a running daemon
5. Achieve sufficient test coverage to enable confident refactoring

## Scope

### In Scope
- Unit tests for `parse_htcss_string()` function with various inputs
- Unit tests for `parse_htcss_file()` with `.htpy` files
- Unit tests for comment extraction from Python files
- Tests for SUBMIT_REPLACEMENTS attribute mapping
- Tests for automatic `universe = container` insertion
- Tests for `queue from TABLE` appending
- Mock-based tests for HTCondor submission flow
- Edge cases and error handling

### Out of Scope
- Integration tests requiring actual HTCondor daemon
- End-to-end tests with real job submission
- Performance/load testing
- Notebook testing (covered in task-1)

## Technical Approach

### Test Framework
- Use **pytest** as the test runner
- Use **pytest-mock** for mocking HTCondor interactions
- Organize tests in `tests/` directory mirroring source structure

### Test Structure
```
tests/
├── __init__.py
├── test_parse.py          # Core parsing tests
├── test_htcss_string.py   # String parsing tests
├── test_htcss_file.py     # File parsing tests
├── test_executable.py     # Python comment extraction tests
├── test_submission.py     # HTCondor submission tests (mocked)
├── fixtures/              # Test data files
│   ├── valid.htpy
│   ├── valid_with_exec.htpy
│   ├── invalid_no_template.htpy
│   ├── invalid_no_table.htpy
│   └── example.py
└── conftest.py            # Shared fixtures
```

### Key Test Categories

#### 1. String Parsing Tests
Test `parse_htcss_string()` with various inputs:
- Valid HTCSS with TEMPLATE and TABLE
- HTCSS with TEMPLATE, TABLE, and EXEC
- Missing TEMPLATE (should raise exception)
- Missing TABLE (should raise exception)
- Multiple blocks with same name (last one wins or merge?)
- Empty sections
- Sections without END marker

#### 2. Attribute Replacement Tests
Verify SUBMIT_REPLACEMENTS are applied:
- `RequestDisk` → `request_disk`
- `RequestMemory` → `request_memory`
- `RequestCpus` → `request_cpus`
- `TransferInputFiles` → `transfer_input_files`
- `TransferOutputFiles` → `transfer_output_files`

#### 3. Template Augmentation Tests
- `container_image` present → adds `universe = container`
- EXEC section present → adds `executable = _exec.py`
- Always adds `queue from TABLE _table.csv`

#### 4. Comment Extraction Tests
Test `read_comments()` function:
- Extract comments from valid Python file
- Handle files with no comments
- Handle mixed comment styles
- Tokenization error handling

#### 5. Mocked Submission Tests
Mock `htcondor.Schedd()` and test:
- Successful submission flow
- Dry run mode (no actual submission)
- Cleanup flag (temporary files removed)
- Error handling when scheduler unavailable

### Test Utilities
Create helper functions in `conftest.py`:
```python
@pytest.fixture
def sample_htcss():
    """Returns a valid HTCSS string"""

@pytest.fixture
def temp_htpy_file(tmp_path):
    """Creates a temporary .htpy file"""

@pytest.fixture
def mock_schedd(mocker):
    """Mocks htcondor.Schedd for submission tests"""
```

## Implementation Tasks

1. **Setup test infrastructure**:
   - Add pytest and pytest-mock to `pyproject.toml`
   - Create `tests/` directory structure
   - Configure pytest in `pyproject.toml` or `pytest.ini`

2. **Create test fixtures**:
   - Write sample `.htpy` files in `tests/fixtures/`
   - Write sample Python files with HTCSS in comments
   - Create `conftest.py` with shared fixtures

3. **Write parsing tests** (`test_parse.py`):
   - Test `parse_htcss_string()` happy path
   - Test missing sections (error cases)
   - Test edge cases (empty sections, no END marker)

4. **Write transformation tests**:
   - Test SUBMIT_REPLACEMENTS application
   - Test container universe insertion
   - Test executable addition
   - Test queue statement appending

5. **Write comment extraction tests** (`test_executable.py`):
   - Test `read_comments()` function
   - Test tokenization edge cases

6. **Write submission tests** (`test_submission.py`):
   - Mock HTCondor scheduler
   - Test submission flow
   - Test dry run mode
   - Test cleanup behavior

7. **Add CI configuration** (optional):
   - Create GitHub Actions workflow
   - Run tests on push/PR

## Acceptance Criteria
<!-- AC:BEGIN -->
### Infrastructure
- [x] #1 pytest and pytest-mock added to `pyproject.toml`
- [x] #2 `tests/` directory created with proper structure
- [x] #3 `conftest.py` contains shared fixtures for test data
- [x] #4 Tests can be run with `pytest` command
- [x] #5 Test fixtures directory contains sample `.htpy` and `.py` files

### Parsing Tests
- [x] #6 Test `parse_htcss_string()` with valid TEMPLATE and TABLE
- [x] #7 Test `parse_htcss_string()` with TEMPLATE, TABLE, and EXEC
- [x] #8 Test missing TEMPLATE raises exception
- [x] #9 Test missing TABLE raises exception
- [x] #10 Test `parse_htcss_file()` reads and parses `.htpy` files correctly
- [x] #11 Test edge cases: empty sections, missing END marker, multiple blocks

### Transformation Tests
- [x] #12 Test all SUBMIT_REPLACEMENTS are applied correctly
- [x] #13 Test `container_image` in template adds `universe = container`
- [x] #14 Test EXEC section triggers `executable = _exec.py` addition
- [x] #15 Test `queue from TABLE _table.csv` is always appended

### Comment Extraction Tests
- [x] #16 Test `read_comments()` extracts comments from Python file
- [x] #17 Test `--executable` flag triggers comment extraction mode
- [x] #18 Test tokenization handles various comment styles
- [x] #19 Test error handling for malformed Python files

### Submission Tests (Mocked)
- [x] #20 Test successful submission flow with mocked `htcondor.Schedd`
- [x] #21 Test `write_table()` creates `_table.csv` correctly
- [x] #22 Test `write_executable()` creates `_exec.py` correctly
- [x] #23 Test `--dryrun` flag prevents actual submission
- [x] #24 Test `--cleanup` flag removes temporary files
- [x] #25 Test error handling when scheduler is unavailable

### Code Quality
- [x] #26 All tests pass with `pytest`
- [x] #27 Tests have meaningful assertions and error messages
- [x] #28 Test coverage for critical parsing logic > 80%
- [x] #29 No debug breakpoints (`pdb.set_trace()`) remain in production code

### Documentation
- [x] #30 README or docs explain how to run tests
- [x] #31 Test files include docstrings explaining what they test
- [x] #32 Fixtures are documented in `conftest.py`

## Open Questions

- **Test coverage threshold**: What minimum coverage percentage should we target?
- **Debug breakpoints**: Lines 53 and 111 in `parse.py` have `pdb.set_trace()` - remove these as part of this task?
- **HTCondor version**: Should we test against multiple HTCondor Python binding versions?
- **Test data**: Should fixture files be minimal or representative of real-world usage?
<!-- AC:END -->
