import re
from pypers.core.step import CmdLineStep

class ApplyBaseRecalib(CmdLineStep):
    spec = {
        "version": "2.3.9",
        "descr": [
            "Runs gatk PrintReads with the BQSR param to apply previously generated read recalibrations to a bam"
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
                    "name"     : "input_recalibs",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input recalibration table file",
                },
                {
                    "name"  : "reference",
                    "type"  : "ref_genome",
                    "tool"  : "gatk",
                    "descr" : "Reference sequence file"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "{{input_bams}}.recal.bam",
                    "descr" : "the recalibrated bam file name",
                }
            ],
            "params": [
            ]
        },
        "cmd": [
            "/usr/bin/java -Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}} -jar /software/pypers/GATK/GenomeAnalysisTKLite-2.3-9-gdcdccbb/GenomeAnalysisTKLite.jar",
            " -I {{input_bams}} -BQSR {{input_recalibs}} -o {{output_files}}",
            " -T PrintReads -R {{reference}}"
        ],
        "requirements": {
                "memory": '8'
        }
    }
