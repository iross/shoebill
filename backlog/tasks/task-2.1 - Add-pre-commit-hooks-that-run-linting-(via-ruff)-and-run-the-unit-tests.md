---
id: task-2.1
title: Add pre-commit hooks that run linting (via ruff) and run the unit tests
status: To Do
assignee: []
created_date: '2025-10-31 19:18'
labels: []
dependencies: [task-2]
parent_task_id: task-2
---

## Overview

Implement pre-commit hooks to automatically run code quality checks (linting via ruff) and unit tests before commits are allowed. This ensures code quality standards are maintained and prevents broken code from being committed.

## Goals

1. Configure pre-commit framework to run on every git commit
2. Add ruff for Python linting and formatting checks
3. Run pytest unit tests as part of pre-commit validation
4. Ensure hooks are fast enough to not disrupt development workflow
5. Provide clear feedback when hooks fail

## Technical Approach

### Pre-commit Framework

Use the [pre-commit](https://pre-commit.com/) framework, which provides:
- Standardized hook configuration (`.pre-commit-config.yaml`)
- Automatic environment management for each hook
- Easy installation and sharing across team members
- Large ecosystem of existing hooks

### Hook Configuration

Create `.pre-commit-config.yaml` in repository root:

```yaml
repos:
  # Ruff for linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0  # Use latest stable version
    hooks:
      # Run the linter
      - id: ruff
        args: [--fix]
      # Run the formatter
      - id: ruff-format

  # Run unit tests
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit]

  # Standard pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
```

### Ruff Configuration

Create `ruff.toml` or add to `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Performance Optimization

To keep hooks fast:
- **Ruff**: Already very fast (written in Rust)
- **Pytest**: Consider adding `--lf` (last-failed) or `--maxfail=1` for faster feedback
- **File filtering**: Only run tests related to changed files (advanced)

### Skip Hook Option

Allow developers to skip hooks when needed:
```bash
git commit --no-verify  # Skip all hooks
SKIP=pytest git commit  # Skip just pytest
```

## Implementation Tasks

1. **Install pre-commit framework**:
   - Add `pre-commit` to `pyproject.toml` dev dependencies
   - Document installation in README or CLAUDE.md

2. **Create `.pre-commit-config.yaml`**:
   - Add ruff hooks (linter and formatter)
   - Add local pytest hook
   - Add standard pre-commit hooks (trailing whitespace, etc.)

3. **Configure ruff**:
   - Add ruff configuration to `pyproject.toml`
   - Choose appropriate rule set for project
   - Add any project-specific ignores

4. **Setup instructions**:
   - Document how to install hooks: `pre-commit install`
   - Document how to run manually: `pre-commit run --all-files`
   - Document how to update hooks: `pre-commit autoupdate`

5. **Run initial formatting**:
   - Run `ruff format .` to format all existing code
   - Run `ruff check --fix .` to fix auto-fixable issues
   - Manually fix any remaining ruff violations
   - Commit formatted code

6. **Test hooks**:
   - Make a test commit to verify hooks run
   - Verify hooks catch violations
   - Verify hooks provide clear error messages

7. **Document workflow**:
   - Update CLAUDE.md with pre-commit information
   - Add development setup instructions
   - Document how to skip hooks when needed

## Acceptance Criteria

### Installation & Configuration
- [ ] `pre-commit` added to `pyproject.toml` as dev dependency
- [ ] `.pre-commit-config.yaml` created in repository root
- [ ] Ruff configuration added to `pyproject.toml`
- [ ] Hooks can be installed with `pre-commit install`

### Ruff Linting Hooks
- [ ] Ruff linter hook runs on commit
- [ ] Ruff formatter hook runs on commit
- [ ] Ruff auto-fixes issues when possible (e.g., import sorting)
- [ ] Ruff reports violations clearly with file and line numbers
- [ ] Configuration covers relevant Python style rules

### Pytest Hook
- [ ] Pytest runs automatically on commit
- [ ] Hook fails commit if tests fail
- [ ] Test output is visible when tests fail
- [ ] Hook is reasonably fast (< 10 seconds for current test suite)

### Standard Hooks
- [ ] Trailing whitespace is removed automatically
- [ ] Files end with newline
- [ ] YAML files are validated
- [ ] Large files are blocked from commit
- [ ] Merge conflict markers are detected

### Code Quality
- [ ] All existing code passes ruff checks
- [ ] All existing code is formatted with ruff
- [ ] No remaining `pdb.set_trace()` debug breakpoints in production code
- [ ] Tests pass before initial commit with hooks

### Documentation
- [ ] README or CLAUDE.md documents pre-commit setup
- [ ] Instructions explain how to install hooks
- [ ] Instructions explain how to run hooks manually
- [ ] Instructions explain how to skip hooks when needed
- [ ] Instructions explain how to update hook versions

### Developer Experience
- [ ] Hooks complete in reasonable time (< 15 seconds total)
- [ ] Error messages are clear and actionable
- [ ] Hooks can be bypassed with `--no-verify` for emergencies
- [ ] Individual hooks can be skipped with `SKIP=<hook-id>`

## Design Decisions

### Why Ruff?
- **Speed**: 10-100x faster than traditional linters (written in Rust)
- **All-in-one**: Combines linting + formatting (replaces black, flake8, isort, etc.)
- **Modern**: Built for modern Python with pyproject.toml support
- **Active development**: Well-maintained by Astral (same team as uv)

### Hook Ordering
1. **Fast checks first** (trailing whitespace, YAML validation)
2. **Formatting** (ruff-format) - modifies files
3. **Linting** (ruff) - reports issues
4. **Tests** (pytest) - slowest, runs last

### Pytest in Pre-commit
Running tests in pre-commit is somewhat controversial:
- **Pros**: Catches broken code immediately, enforces test discipline
- **Cons**: Can slow down commits, may discourage frequent commits
- **Compromise**: Tests should be fast (< 10s), can be skipped with `SKIP=pytest`

## Open Questions

- **Test performance**: Should we add pytest optimizations like `--lf` or `--maxfail=1` to make it faster?
- **CI vs pre-commit**: Should pre-commit run a subset of tests, with full suite in CI?
- **Auto-formatting**: Should ruff-format auto-fix files, or just report issues?
- **Ruff rules**: Which ruff rules should we enable/disable for this project?
