import os
import re

from pypers.core.step import CmdLineStep

class RnaStar(CmdLineStep):
    spec = {
        "version":"V2_3e",
        "descr": [
            "Runs the STAR RNA-seq aligner"
        ],
        "url": "http://github.com/alexdobin/STAR",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "a list of fastq files",
                },
                {
                    "name"      : "ref_genome_dir",
                    "type"      : "ref_genome",
                    "tool"      : "STAR",
                    "descr"     : "reference genome directory",
                }
            ],
            "outputs": [
                {
                    "name"      : "output_sams",
                    "type"      : "file",
                    "descr"     : "the sam output file",
                    "value"     : "dummy"
                },
                {
                    "name"      : "output_stats",
                    "type"      : "file",
                    "descr"     : "the log file containing stats",
                    "value"     : "dummy"
                }
            ], 
            "params": [
            ]
        },
        "cmd": [
            "/software/pypers/rna-star/STAR_2.3.0e/bin/STAR",
            "--genomeDir {{ref_genome_dir}}",
            "--genomeLoad NoSharedMemory",
            "--readFilesIn {{input_files}}",
            "--runThreadN {{cpus}}",
            "--outReadsUnmapped Fastx",
            "&& mv Aligned.out.sam {{output_sams}}",
            "&& mv Log.final.out {{output_stats}}"
        ],
        "requirements": {
            "memory" : "25",
            "cpus"   : "6"
        }
    }

    def preprocess(self):
        """
        Set output name depending on whether the input consists of one or two files
        """
        file_name = os.path.basename(self.input_files[0]).split('.')[0] + '.sam'
        self.output_sams  = re.sub(r'(_L\d{3}_)R1_(\d{3})', r'\1\2', file_name)
        self.output_stats = re.sub(r'sam$', r'log.final.out', self.output_sams)
        super(RnaStar, self).preprocess()
