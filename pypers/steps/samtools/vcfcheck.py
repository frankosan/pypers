import os
from pypers.core.step import CmdLineStep


class VcfCheck(CmdLineStep):
    spec = {
        "descr": [
            "Runs VcfCheck on the input files"
        ],
        "name": "VcfCheck",
        "version": "1.1",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_file",
                    "type"     : "file",
                    "descr"    : "the input vcf file",
                }
            ],
            "outputs": [
                {
                    "name"      : "output_file",
                    "type"      : "file",
                    "value"     : "{{input_file}}.vcfcheck",
                    "descr"     : "the stats reports"
                }
            ]
        },
        "cmd": [
            "/software/pypers/samtools/samtools-1.1/bin/bcftools stats {{input_file}} > {{output_file}}"
        ]
    }

