"""
Tests for parse_htcss_string() function.

This module tests the core HTCSS string parsing logic, including:
- Valid templates with TEMPLATE and TABLE sections
- Templates with EXEC sections
- Error handling for missing required sections
- Edge cases: empty sections, missing END markers
- Template processing: replacements, container universe, queue statement
"""

import pytest
from parse import parse_htcss_string, SUBMIT_REPLACEMENTS


class TestParseHTCSSStringBasic:
    """Test basic parsing functionality."""

    def test_parse_valid_template_and_table(self, simple_htcss_template):
        """Test parsing valid HTCSS with TEMPLATE and TABLE sections."""
        result = parse_htcss_string(simple_htcss_template)

        assert "TEMPLATE" in result
        assert "TABLE" in result
        assert "executable = /bin/echo" in result["TEMPLATE"]
        assert "JobID, Message" in result["TABLE"]

        # Verify queue statement is appended
        assert "queue from TABLE _table.csv" in result["TEMPLATE"]

    def test_parse_template_table_and_exec(self, htcss_with_exec):
        """Test parsing HTCSS with TEMPLATE, TABLE, and EXEC sections."""
        result = parse_htcss_string(htcss_with_exec)

        assert "TEMPLATE" in result
        assert "TABLE" in result
        assert "EXEC" in result
        assert "import sys" in result["EXEC"]
        assert "def main():" in result["EXEC"]

    def test_parse_with_end_marker(self, htcss_with_end_marker):
        """Test that content after END marker is ignored."""
        result = parse_htcss_string(htcss_with_end_marker)

        assert "TEMPLATE" in result
        assert "TABLE" in result
        # Verify content after END is not in TEMPLATE or TABLE sections
        assert "This text should be ignored" not in result["TEMPLATE"]
        assert "This text should be ignored" not in result["TABLE"]
        # END marker should not create a section
        assert "END" not in result or "This text should be ignored" not in result.get("END", "")

    def test_parse_preserves_multiline_sections(self, simple_htcss_template):
        """Test that multiline sections are preserved correctly."""
        result = parse_htcss_string(simple_htcss_template)

        # Verify multiple lines in template
        lines = result["TEMPLATE"].split("\n")
        assert len([l for l in lines if l.strip()]) >= 5

        # Verify table has multiple rows
        table_lines = result["TABLE"].split("\n")
        assert len(table_lines) >= 3  # Header + at least 2 data rows


class TestParseHTCSSStringErrorHandling:
    """Test error handling for invalid inputs."""

    def test_missing_template_raises_exception(self, htcss_missing_template):
        """Test that missing TEMPLATE raises an exception."""
        with pytest.raises(Exception) as exc_info:
            parse_htcss_string(htcss_missing_template)
        assert "Missing template or table" in str(exc_info.value)

    def test_missing_table_raises_exception(self, htcss_missing_table):
        """Test that missing TABLE raises an exception."""
        with pytest.raises(Exception) as exc_info:
            parse_htcss_string(htcss_missing_table)
        assert "Missing template or table" in str(exc_info.value)

    def test_empty_sections_raises_exception(self, htcss_empty_sections):
        """Test that empty sections raise an exception."""
        with pytest.raises(Exception) as exc_info:
            parse_htcss_string(htcss_empty_sections)
        assert "Missing template or table" in str(exc_info.value)

    def test_no_htcss_markers(self):
        """Test parsing text without HTCSS markers."""
        text = "This is just plain text\nwith no HTCSS markers"
        with pytest.raises(Exception):
            parse_htcss_string(text)


class TestParseHTCSSStringReplacements:
    """Test SUBMIT_REPLACEMENTS are applied correctly."""

    def test_request_cpus_replacement(self):
        """Test RequestCpus is replaced with request_cpus."""
        htcss = """%HTCSS TEMPLATE
RequestCpus = 4
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)
        assert "request_cpus = 4" in result["TEMPLATE"]
        assert "RequestCpus" not in result["TEMPLATE"]

    def test_request_memory_replacement(self):
        """Test RequestMemory is replaced with request_memory."""
        htcss = """%HTCSS TEMPLATE
RequestMemory = 8GB
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)
        assert "request_memory = 8GB" in result["TEMPLATE"]
        assert "RequestMemory" not in result["TEMPLATE"]

    def test_request_disk_replacement(self):
        """Test RequestDisk is replaced with request_disk."""
        htcss = """%HTCSS TEMPLATE
RequestDisk = 10GB
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)
        assert "request_disk = 10GB" in result["TEMPLATE"]
        assert "RequestDisk" not in result["TEMPLATE"]

    def test_transfer_input_files_replacement(self):
        """Test TransferInputFiles is replaced with transfer_input_files."""
        htcss = """%HTCSS TEMPLATE
TransferInputFiles = file1.txt, file2.txt
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)
        assert "transfer_input_files = file1.txt, file2.txt" in result["TEMPLATE"]
        assert "TransferInputFiles" not in result["TEMPLATE"]

    def test_transfer_output_files_replacement(self):
        """Test TransferOutputFiles is replaced with transfer_output_files."""
        htcss = """%HTCSS TEMPLATE
TransferOutputFiles = output.txt
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)
        assert "transfer_output_files = output.txt" in result["TEMPLATE"]
        assert "TransferOutputFiles" not in result["TEMPLATE"]

    def test_multiple_replacements(self, htcss_with_exec):
        """Test multiple replacements in same template."""
        result = parse_htcss_string(htcss_with_exec)

        # Check all replacements were applied
        assert "request_cpus = 2" in result["TEMPLATE"]
        assert "request_memory = 2GB" in result["TEMPLATE"]
        assert "RequestCpus" not in result["TEMPLATE"]
        assert "RequestMemory" not in result["TEMPLATE"]

    def test_all_submit_replacements_defined(self):
        """Test all SUBMIT_REPLACEMENTS are applied."""
        # Build template with all replacement keys
        template_parts = ["%HTCSS TEMPLATE"]
        for key in SUBMIT_REPLACEMENTS.keys():
            template_parts.append(f"{key} = test_value")
        template_parts.append("%HTCSS TABLE\nID\n1")

        htcss = "\n".join(template_parts)
        result = parse_htcss_string(htcss)

        # Verify all old keys are replaced
        for old_key in SUBMIT_REPLACEMENTS.keys():
            assert old_key not in result["TEMPLATE"]

        # Verify all new keys are present
        for new_key in SUBMIT_REPLACEMENTS.values():
            assert f"{new_key} = test_value" in result["TEMPLATE"]


class TestParseHTCSSStringContainerHandling:
    """Test container_image handling and universe addition."""

    def test_container_image_adds_universe(self, htcss_with_container):
        """Test that container_image in template adds universe = container."""
        result = parse_htcss_string(htcss_with_container)

        assert "container_image = docker://python:3.12" in result["TEMPLATE"]
        assert "universe = container" in result["TEMPLATE"]

    def test_no_container_image_no_universe(self, simple_htcss_template):
        """Test that templates without container_image don't get universe added."""
        result = parse_htcss_string(simple_htcss_template)

        assert "container_image" not in result["TEMPLATE"]
        assert "universe = container" not in result["TEMPLATE"]

    def test_container_universe_added_once(self):
        """Test universe = container is only added once even if container_image appears multiple times."""
        htcss = """%HTCSS TEMPLATE
container_image = docker://ubuntu:22.04
# Using container_image again in comment
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)

        # Count occurrences of universe = container
        count = result["TEMPLATE"].count("universe = container")
        assert count == 1


class TestParseHTCSSStringQueueStatement:
    """Test queue statement is always appended."""

    def test_queue_statement_appended(self, simple_htcss_template):
        """Test that queue from TABLE statement is appended."""
        result = parse_htcss_string(simple_htcss_template)
        assert "queue from TABLE _table.csv" in result["TEMPLATE"]

    def test_queue_statement_at_end(self, htcss_with_exec):
        """Test queue statement appears at end of template."""
        result = parse_htcss_string(htcss_with_exec)
        assert result["TEMPLATE"].strip().endswith("queue from TABLE _table.csv")

    def test_queue_statement_with_container(self, htcss_with_container):
        """Test queue statement is appended even with container universe."""
        result = parse_htcss_string(htcss_with_container)
        assert "queue from TABLE _table.csv" in result["TEMPLATE"]
        # Verify universe comes before queue
        template_lines = result["TEMPLATE"].split("\n")
        universe_idx = next(i for i, l in enumerate(template_lines) if "universe = container" in l)
        queue_idx = next(i for i, l in enumerate(template_lines) if "queue from TABLE" in l)
        assert universe_idx < queue_idx


class TestParseHTCSSStringEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_multiple_blocks_same_type(self):
        """Test that multiple blocks of same type overwrites previous."""
        htcss = """%HTCSS TEMPLATE
first_executable = /bin/true
%HTCSS TEMPLATE
second_executable = /bin/false
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)

        # Second block should overwrite first
        assert "first_executable" not in result["TEMPLATE"]
        assert "second_executable = /bin/false" in result["TEMPLATE"]

    def test_whitespace_preserved_in_sections(self):
        """Test that whitespace within sections is preserved."""
        htcss = """%HTCSS TEMPLATE
executable = /bin/echo

arguments = test with spaces
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)
        assert "arguments = test with spaces" in result["TEMPLATE"]

    def test_special_characters_in_sections(self):
        """Test sections with special characters."""
        htcss = """%HTCSS TEMPLATE
arguments = $(VAR) "quoted string" 'single quotes'
%HTCSS TABLE
ID
1
"""
        result = parse_htcss_string(htcss)
        assert '"quoted string"' in result["TEMPLATE"]
        assert "'single quotes'" in result["TEMPLATE"]

    def test_section_name_case_sensitive(self):
        """Test that section names are case sensitive."""
        htcss = """%HTCSS template
executable = /bin/true
%HTCSS table
ID
1
"""
        # This should fail because lowercase template/table won't be recognized
        # The implementation is case-sensitive
        with pytest.raises(Exception) as exc_info:
            parse_htcss_string(htcss)
        assert "Missing template or table" in str(exc_info.value)
