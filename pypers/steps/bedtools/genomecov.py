from pypers.core.step import Step
import os

class GenomeCov(Step):
    spec = {
        "version": "0.0.1",
        "descr": [
            "Call bedtools genomecov utility to compute BEDGRAPH (-bg) summary of feature coverage for a bam"
        ],
        "url" : "http://bedtools.readthedocs.org/en/latest/content/tools/genomecov.html",
        "args": 
        {
            "inputs": [
                {
                    "name"  : "input_bam",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "input bam files",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_bg",
                    "type"  : "file",
                    "descr" : "the output bg file"
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

        self.output_bg = os.path.join(self.output_dir, os.path.basename(self.input_bam).replace('.bam', '.bg'))
        cmd = '%s genomecov -ibam %s -bg > %s' % ( self.bedtools_exe, self.input_bam, self.output_bg )

        self.submit_cmd(cmd)

        statinfo = os.stat(self.output_bg)
        if statinfo.st_size == 0:
            raise Exception('[bg %s is zero size]' % (self.output_bg))
