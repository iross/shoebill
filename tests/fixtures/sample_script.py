#!/usr/bin/env python
# %HTCSS TEMPLATE
# executable = /usr/bin/python3
# arguments = $(ScriptName) $(Input)
# output = py_$(JobID).out
# error = py_$(JobID).err
# log = python_jobs.log
# RequestCpus = 1
# RequestMemory = 2GB
# %HTCSS TABLE
# JobID, ScriptName, Input
# 1, process.py, data1.txt
# 2, process.py, data2.txt

def main():
    """Sample Python script with HTCSS markup in comments."""
    print("This script demonstrates HTCSS in Python comments")

if __name__ == "__main__":
    main()
