import re
from pypers.core.step import CmdLineStep

class CalculateHsMetrics(CmdLineStep):
    spec = {
        "version": "1.119",
        "descr": [
            "Runs picard tool CalculateHsMetrics"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_bams",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input bam file",
                },
                {
                    "name"     : "input_intervals",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input intervals file",
                },
                {
                    "name"  : "reference",
                    "type"  : "ref_genome",
                    "tool"  : "gatk",
                    "descr" : "reference sequence file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_metrics",
                    "type"  : "file",
                    "value" : "{{input_bams}}.HsMetric.txt",
                    "descr" : "the hs metrics file name",
                },
                {
                    "name"  : "output_targets",
                    "type"  : "file",
                    "value" : "null",
                    "descr" : "An optional file to output per target coverage information to (requires reference file)"
                }
            ],
            "params": [
                {
                    "name"  : "jvm_args",
                    "value" : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr" : "java virtual machine arguments",
                    "readonly" : True
                },
                {
                    "name"  : "validation_stringency",
                    "type"  : "enum",
                    'options' : [ 'STRICT', 'LENIENT', 'SILENT'],
                    "value" : "LENIENT",
                    "descr" : "Validation stringency for all SAM files read by this program. Possible values: {STRICT, LENIENT, SILENT}"
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/CalculateHsMetrics.jar",
            " I={{input_bams}} TI={{input_intervals}} BI={{input_intervals}} R={{reference}}",
            " O={{output_metrics}} PER_TARGET_COVERAGE={{output_targets}}",
            " VALIDATION_STRINGENCY={{validation_stringency}}",
            " TMP_DIR=./tmp"
        ],
        "requirements": {
            "memory": "8"
        }

    }

    def preprocess(self):
        if self.reference:
            self.output_targets = self.input_bams+".PerTgtCov.txt"
