import os
import re

from pypers.core.step import CmdLineStep

class AlignMem(CmdLineStep):
    spec = {
        "version": "0.7.6a",
        "descr": [
            "Aligns 70bp-1Mbp query sequences with the BWA-MEM algorithm."
        ],
        "args":
        {
            "inputs": [
                {
                    "name" : "input_fastq",
                    "type" : "file",
                    "iterable" : True,
                    "descr" : "list of fastq files (paired by read, if appropriate)"
                },
                {
                    "name"  : "ref_path",
                    "type"  : "ref_genome",
                    "tool"  : "bwa",
                    "descr" : "path to the directory containing the reference genome"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "output sam files",
                    "value" : "dummy"
                }
            ],
            "params": [ ]
        },
        "cmd" : [
            "/software/pypers/bwa/bwa-0.7.6a/bwa mem -v 1 -t {{cpus}}",
            " {{ref_path}} {{input_fastq}} > {{output_files}}"
        ],
        "requirements": {
            "cpus"   : "6"
        }
    }

    def preprocess(self):
        """
        Set output name depending on whether the input consists of one or two files
        """
        file_name = os.path.basename(self.input_fastq[0]).split('.')[0] + '.sam'
        self.output_files = re.sub(r'(_L\d{3}_)R1_(\d{3})', r'\1\2', file_name)
        super(AlignMem, self).preprocess()

