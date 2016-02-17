import re
from pypers.core.step import CmdLineStep

class CollectMetrics(CmdLineStep):
    spec = {
        "version": "1.119",
        "descr": [
            "Reads a SAM or BAM file and writes a file containing metrics",
            " about the statistical distribution of insert size (excluding duplicates),"
            " and generates a Histogram plot."
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
                    "name"  : "output_stats",
                    "type"  : "file",
                    "value" : "{{input_files}}.CollectorInsertSizeMetrics.txt",
                    "descr" : "output text file containing the statistics",
                },
                {
                    "name"  : "output_hists",
                    "type"  : "file",
                    "value" : "{{input_files}}.CollectorInsertSizeMetrics.pdf",
                    "descr" : "output pdf file containing the insert size Histogram chart",
                }
            ],
            "params": [
                {
                    "name"  : "validation_stringency",
                    "type"  : "enum",
                    'options' : [ 'STRICT', 'LENIENT', 'SILENT'],
                    "value" : "LENIENT",
                    "descr" : "Validation stringency for all SAM files read by this program. Possible values: {STRICT, LENIENT, SILENT}"
                },
                {
                    "name"  : "reference",
                    "type"  : "str",
                    "descr" : "reference sequence file",
                    "value" : "null"
                },
                {
                    "name"  : "jvm_args",
                    "value" : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr" : "java virtual machine arguments",
                    "readonly" : True
                }
            ]
        },
        "requirements": { 
            "memory" : "8"
        },
        "extra_env" : {
            "PATH" : "/software/pypers/R/R-3.0.0/bin",
            "LD_LIBRARY_PATH": "/software/pypers/gcc/gcc-4.7.1/lib64:/software/pypers/intel/l_ics-2013.0.028/composer_xe_2013.1.117/compiler/lib/intel64"
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/CollectInsertSizeMetrics.jar",
            " I={{input_files}} R={{reference}} O={{output_stats}} H={{output_hists}}",
            " VALIDATION_STRINGENCY={{validation_stringency}}"
        ]
    }
