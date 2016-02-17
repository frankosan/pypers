from pypers.core.step import CmdLineStep
import re

class BamMerge(CmdLineStep):
    spec = {
        "version": "0.1.19",
        "descr": [
          "Uses samtools to merge two or more bams.",
          "Also runs indexing on the merged output"
        ],
        "args": 
        {
            "inputs": [
                {
                    "name"  : "input_files",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "a list of bam files to be merged",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "{{input_files}}.merged.bam",
                    "descr" : "the output merged file"
                }
            ]   
        },
        "cmd": [
            "/software/pypers/samtools/samtools-0.1.19/bin/samtools merge",
            "{{output_files}} -f {{input_files}}"
            " && /software/pypers/samtools/samtools-0.1.19/bin/samtools index {{output_files}}"
        ]
    }

    def process(self):
        if len(self.input_files) == 1:
            self.cmd = "cp %s %s" % (self.input_files[0], self.output_files)
        super(BamMerge,self).process()
    
