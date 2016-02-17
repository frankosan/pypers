from pypers.core.step import CmdLineStep
import re

class BamIndex(CmdLineStep):
    spec = {
        "version": "0.1.19",
        "descr": [
            "Uses samtools to create an index"
        ],
        "args": 
        {
            "inputs": [
                {
                    "name"  : "input_files",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "a list of bam files to be indexed",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "{{input_files}}.bai",
                    "descr" : "the indexed output files"
                }
            ]
        },
        "cmd": [
            "/software/pypers/samtools/samtools-0.1.19/bin/samtools index {{input_files}}",
            "&& ln -s {{input_files}}.bai {{output_files}}"
        ]
    }

    