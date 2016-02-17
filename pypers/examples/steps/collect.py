from pypers.core.step import CmdLineStep


class Collect(CmdLineStep):
    spec = {
        "version": "1.0",
        "descr": [
            "Collect and summarize counts"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "descr"    : "input file name"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "files containing number of counts",
                    "value" : "total_counts.txt"
                }
            ],
            "params" : [ ]
        },
        "cmd": [
            "/usr/bin/awk '{s+=$1} END {print s}' {{input_files}} > {{output_files}}"
        ]
    }
