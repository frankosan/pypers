import re
from pypers.core.step import CmdLineStep

class FixMate(CmdLineStep):
    spec = {
        "version": "1.119",
        "descr": [
            "Runs picard tool to Fix mate pair information in a bam file"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input bam file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "{{input_files}}.paired.bam",
                    "descr" : "the fixed bam output file name",
                }
            ],
            "params": [
                {
                    "name"  : "sort_order",
                    'type' : 'enum',
                    'options' : ['unsorted','queryname','coordinate'],
                    'value' : 'coordinate',
                    "descr" : "Sort order of output file. Possible values: {unsorted, queryname, coordinate}"
                },
                {
                    "name"  : "validation_stringency",
                    "type"  : "enum",
                    'options' : [ 'STRICT', 'LENIENT', 'SILENT'],
                    "value" : "LENIENT",
                    "descr" : "Validation stringency for all SAM files read by this program. Possible values: {STRICT, LENIENT, SILENT}"
                },
                {
                    "name"  : "create_index",
                    "type"  : "boolean",
                    "value" : "True",
                    "descr" : "Whether to create a BAM index when writing the coordinate-sorted BAM file"
                },
                {
                    "name"  : "jvm_args",
                    "value" : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr" : "java virtual machine arguments",
                    "readonly" : True
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/FixMateInformation.jar",
            " I={{input_files}} O={{output_files}}",
            " SO={{sort_order}} VALIDATION_STRINGENCY={{validation_stringency}} CREATE_INDEX={{create_index}}"
        ],
        "requirements": {
           "memory" : "8"
        }
    }
