#!/usr/bin/env python
import os
import tokenize
import click
import htcondor as htcondor

PATTERN = "%HTCSS"
ENDPATTERN = "%HTCSS END"
SUBMIT_REPLACEMENTS = {
    "RequestDisk" : "request_disk",
    "RequestMemory" : "request_memory",
    "RequestCpus" : "request_cpus",
    "TransferInputFiles" : "transfer_input_files",
    "TransferOutputFiles" : "transfer_output_files"
}




def read_comments(fileObj: bytes):
    comments = ''
    for toktype, tok, start, end, line in tokenize.tokenize(fileObj.readline):
        # we can also use token.tok_name[toktype] instead of 'COMMENT'
        # from the token module
        if toktype == tokenize.COMMENT and line.startswith("#"):
            if line[0] == "#": # TODO: make this less bad.
                line = line[1:]
            comments+=line
    return comments


def parse_htcss_string(text: str) -> dict:
    text = [i+"\n" for i in text.split("\n")]
    result = {}
    in_block = False
    current_block_name = None
    block_contents = []
    for line in text:
        if line.startswith(PATTERN):
            if in_block:
                result[current_block_name] = "".join(block_contents).strip()
                block_contents = []
            current_block_name = line.split()[1]
            in_block = True
        elif in_block:
            block_contents.append(line)
        elif line.startswith(ENDPATTERN):
            in_block = False
            break
    if in_block:
        result[current_block_name] = "".join(block_contents).strip()
    print(result)
    import pdb; pdb.set_trace()
    if not result["TEMPLATE"] or not result["TABLE"]:
        raise Exception("Missing template or table in submission file")
    if "container_image" in result["TEMPLATE"]:
        result["TEMPLATE"] += "universe = container\n"
    result["TEMPLATE"] += "\nqueue from TABLE _table.csv\n"

    # Replace placeholders with submit language equivalent, to please Miron's interface request..
    for k, v in SUBMIT_REPLACEMENTS.items():
        result["TEMPLATE"] = result["TEMPLATE"].replace(k, v)
    # TODO: Check for validity of submit template and/or input tables.
    return result

def parse_htcss_file(file):
    """Parse a txt file, looking for lines that start with %HTCSS and extract
    the next word in that line. All of the text until the next line that starts
    with %HTCSS should be captures
    """
    with open(file) as f:
        lines = f.read()
    return parse_htcss_string(lines)

def write_table(table):
    with open("_table.csv", "w") as f:
        f.write(table)
    return 0

def write_executable(executable):
    with open("_exec.py", "w") as f:
        f.write(executable)
    return 0


@click.command()
@click.option("--executable", help="Treat the input file as an executable and extract from comments", is_flag=True, default=False)
@click.option("--cleanup", help="Cleanup after running", is_flag=True, default=False)
@click.option("--dryrun", help="Don't submit.", is_flag=True, default=False)
@click.argument('file', type=click.Path(exists=True))
def main(file, executable, cleanup, dryrun):
    if executable:
        with open(file, "rb") as file:
            res = parse_htcss_string(read_comments(file))
    else:
        res = parse_htcss_file(file)
    write_table(res["TABLE"])
    if "EXEC" in res:
        write_executable(res["EXEC"])
        res["TEMPLATE"] += "executable = _exec.py\n"

    schedd = htcondor.Schedd()
    try:
        if dryrun:
            print(htcondor.Submit(res["TEMPLATE"]))
            # print(htcondor.Submit(res["TEMPLATE"]).getQArgs())
        else:
            submit_result = schedd.submit(htcondor.Submit(res["TEMPLATE"]))
            print(submit_result)
    except TypeError:
        import pdb; pdb.set_trace()
    if cleanup:
        os.remove("_table.csv")

if __name__ == "__main__":
    main()
