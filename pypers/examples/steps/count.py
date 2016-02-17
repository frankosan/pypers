from pypers.core.step import CmdLineStep


class Count(CmdLineStep):
    spec = {
        "version": "1.0",
        "descr": [
            "Counts occurence of string in file"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "descr"    : "input file name",
                    "iterable" : True
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "files containing number of counts",
                    "value" : "counts.txt"
                }
            ],
            "params" : [
                {
                    "name"      : "string",
                    "type"      : "str",
                    "descr"     : "string to search for"
                }
            ]
        },
        "cmd": [
            "grep -o {{string}} {{input_files}} | wc -w > {{output_files}}"
        ]
    }
