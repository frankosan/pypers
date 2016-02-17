import os
from pypers.core.step import CmdLineStep

class ReorderSam(CmdLineStep):
    spec = {
        "version": "0.0.1",
        "descr": [
            "Runs ReorderSam to reorder chromosomes into GATK order"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_bam",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input bam file",
                },
                {
                    "name"  : "reference",
                    "type"  : "ref_genome",
                    "tool"  : "reordersam",
                    "descr" : "Reference whole genome fasta"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_bam",
                    "type"  : "file",
                    "value" : "dummy",
                    "descr" : "the reordered output bam",
                }
            ],
            "params": [
                {
                    "name"     : "jvm_args",
                    "value"    : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr"    : "java virtual machine arguments",
                    "readonly" : True
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/ReorderSam.jar",
            " I={{input_bam}} O={{output_bam}} CREATE_INDEX=True R={{reference}}"
        ],
        "requirements": {
            "memory": '8'
        }
    }

    def preprocess(self):
        """
        Set output bam name
        """
        file_name = os.path.basename(self.input_bam)
        self.output_bam = file_name.replace('.bam','.reord.bam')
        super(ReorderSam, self).preprocess()

