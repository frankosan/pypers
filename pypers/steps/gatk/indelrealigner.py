import re
from pypers.core.step import CmdLineStep

class IndelRealigner(CmdLineStep):
    spec = {
        "version": "2.3.9",
        "descr": [
            "Runs gatk IndelRealigner to perform local realignment of reads", 
            "based on misalignments due to the presence of indels"
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
                    "descr"    : "the input target intervals file from RealignerTargetCreator"
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
                    "value" : "{{input_bams}}.realn.bam",
                    "descr" : "the realigned output file name",
                }
            ],
            "params": [
                {
                    "name"  : "jvm_args",
                    "value" : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr" : "java virtual machine arguments",
                    "readonly" : True
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/GATK/GenomeAnalysisTKLite-2.3-9-gdcdccbb/GenomeAnalysisTKLite.jar",
            " -I {{input_bams}} -targetIntervals {{input_intervals}} -o {{output_files}}",
            " -T IndelRealigner -R {{reference}}",
            " --consensusDeterminationModel KNOWNS_ONLY -LOD 0.4"
        ],
        "requirements": {
            "memory": "8"
        }
    }
