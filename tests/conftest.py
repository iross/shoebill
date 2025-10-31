"""
Shared fixtures for HTCondor HTCSS parser tests.

This module provides common test fixtures including:
- Sample HTCSS strings with various configurations
- Sample file content for testing file parsing
- Mock HTCondor objects for submission testing
"""

import sys
from unittest.mock import MagicMock

import pytest

# Mock htcondor module since it's not available in test environment
sys.modules["htcondor"] = MagicMock()


@pytest.fixture
def simple_htcss_template():
    """Basic HTCSS template with TEMPLATE and TABLE sections."""
    return """%HTCSS TEMPLATE
executable = /bin/echo
arguments = $(Message)
output = test_$(JobID).out
error = test_$(JobID).err
log = test.log
request_cpus = 1
request_memory = 1GB
%HTCSS TABLE
JobID, Message
1, Hello
2, World
3, Test
"""


@pytest.fixture
def htcss_with_exec():
    """HTCSS template with TEMPLATE, TABLE, and EXEC sections."""
    return """%HTCSS TEMPLATE
arguments = $(Input) $(Output)
output = job_$(JobID).out
error = job_$(JobID).err
log = job.log
RequestCpus = 2
RequestMemory = 2GB
%HTCSS TABLE
JobID, Input, Output
1, input1.txt, output1.txt
2, input2.txt, output2.txt
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
"""


@pytest.fixture
def htcss_with_container():
    """HTCSS template with container_image specification."""
    return """%HTCSS TEMPLATE
container_image = docker://python:3.12
arguments = $(Script)
output = container_$(JobID).out
error = container_$(JobID).err
log = container.log
TransferInputFiles = input.txt
TransferOutputFiles = output.txt
%HTCSS TABLE
JobID, Script
1, script1.py
2, script2.py
"""


@pytest.fixture
def htcss_with_end_marker():
    """HTCSS template with explicit END marker."""
    return """%HTCSS TEMPLATE
executable = /bin/date
output = date.out
error = date.err
log = date.log
%HTCSS TABLE
JobID
1
2
%HTCSS END
This text should be ignored after the END marker.
"""


@pytest.fixture
def htcss_missing_template():
    """HTCSS with TABLE but no TEMPLATE (should raise error)."""
    return """%HTCSS TABLE
JobID, Value
1, A
2, B
"""


@pytest.fixture
def htcss_missing_table():
    """HTCSS with TEMPLATE but no TABLE (should raise error)."""
    return """%HTCSS TEMPLATE
executable = /bin/true
output = test.out
"""


@pytest.fixture
def htcss_empty_sections():
    """HTCSS with empty sections."""
    return """%HTCSS TEMPLATE

%HTCSS TABLE

"""


@pytest.fixture
def python_file_with_htcss_comments():
    """Python file with HTCSS markup in comments."""
    return """#!/usr/bin/env python
# %HTCSS TEMPLATE
# executable = /bin/python
# arguments = script.py $(Input)
# output = py_$(JobID).out
# error = py_$(JobID).err
# log = py.log
# %HTCSS TABLE
# JobID, Input
# 1, data1.txt
# 2, data2.txt

def main():
    print("This is a Python script")

if __name__ == "__main__":
    main()
"""


@pytest.fixture
def sample_htpy_file(tmp_path):
    """Create a temporary .htpy file for testing file parsing."""
    htpy_file = tmp_path / "test_job.htpy"
    htpy_file.write_text("""%HTCSS TEMPLATE
executable = /bin/echo
arguments = $(Text)
output = echo_$(ID).out
error = echo_$(ID).err
log = echo.log
%HTCSS TABLE
ID, Text
1, First
2, Second
""")
    return htpy_file


@pytest.fixture
def sample_py_file(tmp_path):
    """Create a temporary .py file with HTCSS in comments."""
    py_file = tmp_path / "test_script.py"
    py_file.write_text("""#!/usr/bin/env python
# %HTCSS TEMPLATE
# executable = python_script.py
# arguments = $(Value)
# output = result_$(N).out
# %HTCSS TABLE
# N, Value
# 1, Alpha
# 2, Beta

def process(value):
    return value.lower()

if __name__ == "__main__":
    import sys
    print(process(sys.argv[1]))
""")
    return py_file


@pytest.fixture
def mock_schedd(mocker):
    """Mock HTCondor Schedd object for submission testing."""
    mock = mocker.MagicMock()
    mock.submit.return_value = mocker.MagicMock(cluster=lambda: 12345)
    return mock


@pytest.fixture
def mock_submit_result(mocker):
    """Mock HTCondor submit result."""
    result = mocker.MagicMock()
    result.cluster.return_value = 12345
    result.__str__ = lambda self: "Submitted job cluster 12345"
    return result
