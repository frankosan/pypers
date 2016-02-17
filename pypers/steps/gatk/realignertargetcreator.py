import re
from pypers.core.step import CmdLineStep

class RealignerTargetCreator(CmdLineStep):
    spec = {
        "version": "2.3.9",
        "descr": [
            "Runs gatk RealignerTargetCreator to create the Realigner target intervals file"
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
                    "value" : "{{input_files}}.intervals",
                    "descr" : "the intervals output file name",
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
                    "name"  : "known_sites",
                    "type"  : "str",
                    "value" : "",
                    "descr" : "Input VCF file with known indels. Format: -known <file1> [-known <file2> ...]"
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/GATK/GenomeAnalysisTKLite-2.3-9-gdcdccbb/GenomeAnalysisTKLite.jar",
            " -I {{input_files}} -o {{output_files}}",
            " -T RealignerTargetCreator -R {{reference}} {{known_sites}}",
            " -nt 4"
        ],
        "requirements": {
            "cpus" : "1",
            "memory": "8"
        }
    }
