import re
from pypers.core.step import CmdLineStep

class MarkDuplicates(CmdLineStep):
    spec = {
        "version": "1.119",
        "descr": [
            "Runs picard tool to mark duplicates in a bam file.",
            "By default we assume a sorted input, and mark, not remove, the dups"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input sam/bam file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_bams",
                    "type"  : "file",
                    "value" : "{{input_files}}.markdup.bam",
                    "descr" : "the marked bam output file name",
                },
                {
                    "name"  : "output_metrics",
                    "type"  : "file",
                    "value" : "{{input_files}}.metrics.txt",
                    "descr" : "the duplication metrics file name",
                }
            ],
            "params": [
                {
                    "name"  : "create_index",
                    "type"  : "boolean",
                    "value" : "true",
                    "descr" : "Whether to create a BAM index when writing the coordinate-sorted BAM file"
                },
                {
                    "name"  : "remove_duplicates",
                    "type"  : "boolean",
                    "value" : "false",
                    "descr" : "If true do not write duplicates to the output file instead of writing them with appropriate flags set."
                },
                {
                    "name"  : "assume_sorted",
                    "type"  : "boolean",
                    "value" : "true",
                    "descr" : "If true, assume that the input file is coordinate sorted even if the header says otherwise"
                },
                {
                    "name"  : "validation_stringency",
                    "type"  : "enum",
                    'options' : [ 'STRICT', 'LENIENT', 'SILENT'],
                    "value" : "LENIENT",
                    "descr" : "Validation stringency for all SAM files read by this program. Possible values: {STRICT, LENIENT, SILENT}"
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
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/MarkDuplicates.jar",
            " I={{input_files}} O={{output_bams}} METRICS_FILE={{output_metrics}}",
            " CREATE_INDEX={{create_index}} REMOVE_DUPLICATES={{remove_duplicates}} ASSUME_SORTED={{assume_sorted}} VALIDATION_STRINGENCY={{validation_stringency}}",
            " TMP_DIR=./tmp"
        ],
        "requirements": {
            "memory": "8"
        }
    }

