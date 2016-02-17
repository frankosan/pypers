from pypers.core.step import CmdLineStep

class PrintBiomTableSummary(CmdLineStep):
    spec = {
        "version": "2015.05.13",
        "descr": [
            "Prints a summary of a .biom OTU table"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_biom",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input .biom OTU table filename",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_summary",
                    "type"  : "file",
                    "value" : "biom_table_summary.txt",
                    "descr" : "output .biom OTU table summary",
                }
            ],
            "params": [
                {
                    "name"  : "suppress_md5",
                    "type"  : "str",
                    "value" : "--suppress_md5",
                    "descr" : "Suppress generation of MD5 checksum in the output"
                }
            ]
        },
        "requirements": { },
        "extra_env" : {
            "PYTHONPATH" : "/software/pypers/qiime/qiime-1.8.0/lib/python2.7/site-packages",
            "PATH": "/software/pypers/qiime/qiime-1.8.0/bin/"
        },
        "cmd": [
            "print_biom_table_summary.py  -i {{input_biom}} -o {{output_summary}} {{suppress_md5}}"
        ]
    }
