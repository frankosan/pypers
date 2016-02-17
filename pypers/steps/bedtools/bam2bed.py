from pypers.core.step import Step
import os

class Bam2Bed(Step):
    spec = {
        "version": "0.0.1",
        "descr": [
            "Call bedtools bam2bed utility"
        ],
        "url" : "http://bedtools.readthedocs.org/en/latest/content/tools/bamtobed.html",
        "args": 
        {
            "inputs": [
                {
                    "name"  : "input_bam",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "bam files to be converted",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_bed",
                    "type"  : "file",
                    "descr" : "the output bed file"
                }
            ],
            "params": [
                {
                    "name"  : "bedtools_exe",
                    "type"  : "str",
                    "descr" : "The path to the bedtools executable",
                    "value" : "/software/pypers/bedtools/bedtools-2.23.0/bin/bedtools",
                    "readonly" : True
                }
            ]
        }
    }

    
    def process(self):

        self.output_bed = os.path.join(self.output_dir, os.path.basename(self.input_bam).replace('.bam', '.bed'))
        cmd = '%s bamtobed -i %s  > %s' % ( self.bedtools_exe, self.input_bam, self.output_bed )

        self.submit_cmd(cmd)

        statinfo = os.stat(self.output_bed)
        if statinfo.st_size == 0:
            raise Exception('[bed %s is zero size]' % (self.output_bed))
