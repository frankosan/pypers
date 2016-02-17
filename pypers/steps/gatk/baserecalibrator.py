import re
from pypers.core.step import CmdLineStep

class BaseRecalibrator(CmdLineStep):
    spec = {
        "version": "2.3.9",
        "descr": [
            "Runs gatk's BaseRecalibrator as a first pass to the base quality score recalibration, ",
            "based on various user-specified covariates such as read group, reported quality score, ",
            "machine cycle, and nucleotide context."
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input bam file",
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
                    "value" : "{{input_files}}.recal.txt",
                    "descr" : "the recalibration table file name",
                }
            ],
            "params": [
                {
                    "name"     : "jvm_args",
                    "value"    : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr"    : "java virtual machine arguments",
                    "readonly" : True
                },
                {
                    "name"  : "known_sites",
                    "type"  : "str",
                    "descr" : "Input VCF file with known indels. Format: -knownSites <file1> [-knownSites <file2> ...]"
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/GATK/GenomeAnalysisTKLite-2.3-9-gdcdccbb/GenomeAnalysisTKLite.jar",
            " -I {{input_files}} -o {{output_files}}",
            " -T BaseRecalibrator -R {{reference}} {{known_sites}}",
            " --disable_indel_quals -nt 1 -nct {{cpus}}"
        ],
        "requirements": {
            "cpus" : '8',
            "memory": '8'
        }
    }
