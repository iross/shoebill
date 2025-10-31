"""
Tests for parse_htcss_file() function.

This module tests file-based HTCSS parsing, including:
- Reading .htpy files correctly
- Proper integration with parse_htcss_string()
- File I/O error handling
"""

from pathlib import Path

import pytest

from parse import parse_htcss_file


class TestParseHTCSSFile:
    """Test parsing HTCSS from files."""

    def test_parse_htpy_file(self, sample_htpy_file):
        """Test parsing a .htpy file."""
        result = parse_htcss_file(str(sample_htpy_file))

        assert "TEMPLATE" in result
        assert "TABLE" in result
        assert "executable = /bin/echo" in result["TEMPLATE"]
        assert "ID, Text" in result["TABLE"]

    def test_parse_file_contains_queue_statement(self, sample_htpy_file):
        """Test that parsed file includes queue statement."""
        result = parse_htcss_file(str(sample_htpy_file))
        assert "queue from TABLE _table.csv" in result["TEMPLATE"]

    def test_parse_file_applies_replacements(self, tmp_path):
        """Test that file parsing applies SUBMIT_REPLACEMENTS."""
        htpy_file = tmp_path / "replacements.htpy"
        htpy_file.write_text("""%HTCSS TEMPLATE
RequestCpus = 2
RequestMemory = 4GB
%HTCSS TABLE
ID
1
""")
        result = parse_htcss_file(str(htpy_file))

        assert "request_cpus = 2" in result["TEMPLATE"]
        assert "request_memory = 4GB" in result["TEMPLATE"]

    def test_parse_file_with_exec_section(self, tmp_path):
        """Test parsing file with EXEC section."""
        htpy_file = tmp_path / "with_exec.htpy"
        htpy_file.write_text("""%HTCSS TEMPLATE
arguments = test
%HTCSS TABLE
ID
1
%HTCSS EXEC
print("Hello")
""")
        result = parse_htcss_file(str(htpy_file))

        assert "EXEC" in result
        assert 'print("Hello")' in result["EXEC"]

    def test_parse_file_with_container(self, tmp_path):
        """Test parsing file with container_image."""
        htpy_file = tmp_path / "container.htpy"
        htpy_file.write_text("""%HTCSS TEMPLATE
container_image = docker://ubuntu:22.04
executable = /bin/bash
%HTCSS TABLE
ID
1
""")
        result = parse_htcss_file(str(htpy_file))

        assert "universe = container" in result["TEMPLATE"]
        assert "container_image = docker://ubuntu:22.04" in result["TEMPLATE"]

    def test_parse_fixture_simple(self):
        """Test parsing the simple fixture file."""
        fixture_path = Path("tests/fixtures/simple.htpy")
        if fixture_path.exists():
            result = parse_htcss_file(str(fixture_path))
            assert "TEMPLATE" in result
            assert "TABLE" in result
            assert "executable = /bin/echo" in result["TEMPLATE"]

    def test_parse_fixture_with_exec(self):
        """Test parsing the with_exec fixture file."""
        fixture_path = Path("tests/fixtures/with_exec.htpy")
        if fixture_path.exists():
            result = parse_htcss_file(str(fixture_path))
            assert "TEMPLATE" in result
            assert "TABLE" in result
            assert "EXEC" in result
            assert "def process_file" in result["EXEC"]

    def test_parse_fixture_with_container(self):
        """Test parsing the with_container fixture file."""
        fixture_path = Path("tests/fixtures/with_container.htpy")
        if fixture_path.exists():
            result = parse_htcss_file(str(fixture_path))
            assert "universe = container" in result["TEMPLATE"]
            assert "transfer_input_files = script.sh" in result["TEMPLATE"]
            assert "transfer_output_files = result.txt" in result["TEMPLATE"]


class TestParseHTCSSFileErrors:
    """Test error handling in file parsing."""

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parse_htcss_file("/nonexistent/path/file.htpy")

    def test_parse_file_missing_template(self, tmp_path):
        """Test parsing file with missing TEMPLATE section."""
        htpy_file = tmp_path / "no_template.htpy"
        htpy_file.write_text("""%HTCSS TABLE
ID
1
""")
        with pytest.raises(Exception) as exc_info:
            parse_htcss_file(str(htpy_file))
        assert "Missing template or table" in str(exc_info.value)

    def test_parse_file_missing_table(self, tmp_path):
        """Test parsing file with missing TABLE section."""
        htpy_file = tmp_path / "no_table.htpy"
        htpy_file.write_text("""%HTCSS TEMPLATE
executable = /bin/true
""")
        with pytest.raises(Exception) as exc_info:
            parse_htcss_file(str(htpy_file))
        assert "Missing template or table" in str(exc_info.value)

    def test_parse_empty_file(self, tmp_path):
        """Test parsing an empty file."""
        htpy_file = tmp_path / "empty.htpy"
        htpy_file.write_text("")
        with pytest.raises(Exception):  # noqa: B017
            parse_htcss_file(str(htpy_file))

    def test_parse_file_with_only_comments(self, tmp_path):
        """Test parsing file with only comments/no HTCSS markers."""
        htpy_file = tmp_path / "comments_only.htpy"
        htpy_file.write_text("""# This is a comment
# Another comment
# No HTCSS markers here
""")
        with pytest.raises(Exception):  # noqa: B017
            parse_htcss_file(str(htpy_file))


class TestParseHTCSSFileIntegration:
    """Integration tests for file parsing."""

    def test_file_and_string_parsing_equivalent(self, tmp_path, simple_htcss_template):
        """Test that file parsing produces same result as string parsing."""
        from parse import parse_htcss_string

        # Write template to file
        htpy_file = tmp_path / "test.htpy"
        htpy_file.write_text(simple_htcss_template)

        # Parse both ways
        file_result = parse_htcss_file(str(htpy_file))
        string_result = parse_htcss_string(simple_htcss_template)

        # Results should be identical
        assert file_result.keys() == string_result.keys()
        assert file_result["TEMPLATE"] == string_result["TEMPLATE"]
        assert file_result["TABLE"] == string_result["TABLE"]

    def test_parse_file_with_utf8_characters(self, tmp_path):
        """Test parsing file with UTF-8 characters."""
        htpy_file = tmp_path / "utf8.htpy"
        htpy_file.write_text(
            """%HTCSS TEMPLATE
executable = /bin/echo
arguments = "Hello 世界 🌍"
%HTCSS TABLE
ID
1
""",
            encoding="utf-8",
        )

        result = parse_htcss_file(str(htpy_file))
        assert "Hello 世界 🌍" in result["TEMPLATE"]

    def test_parse_file_with_windows_line_endings(self, tmp_path):
        """Test parsing file with Windows line endings (CRLF)."""
        htpy_file = tmp_path / "crlf.htpy"
        content = "%HTCSS TEMPLATE\r\nexecutable = /bin/echo\r\n%HTCSS TABLE\r\nID\r\n1\r\n"
        htpy_file.write_bytes(content.encode("utf-8"))

        result = parse_htcss_file(str(htpy_file))
        assert "TEMPLATE" in result
        assert "TABLE" in result
