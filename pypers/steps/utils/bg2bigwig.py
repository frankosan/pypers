from pypers.core.step import Step
import os

class BedgraphToBigwig(Step):
    spec = {
        "version": "0.0.1",
        "descr": [
            "Calls the UCSC bedgraph to bigwig file converter"
        ],
        "url" : "https://www.encodeproject.org/software/bedgraphtobigwig/",
        "args": 
        {
            "inputs": [
                {
                    "name"  : "input_bg",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "input bedgraph files",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_bw",
                    "type"  : "file",
                    "descr" : "the output bigwig file"
                }
            ],
            "params": [
                {
                    "name"  : "bg2bw_exe",
                    "type"  : "str",
                    "descr" : "The path to the bedGraphToBigWig executable",
                    "value" : "/software/pypers/ucsc/bin/bedGraphToBigWig",
                    "readonly" : True
                },
                {
                    "name"  : "chrom_sizes",
                    "type"  : "str",
                    "descr" : "The path to chrom.sizes file (two column: <chromosome name> <size in bases>)",
                    "value" : "/pypers/develop/ref/genome/hs/hg19.chrom.sizes",
                    "readonly" : True
                }
            ]
        }
    }

    
    def process(self):

        self.output_bw = os.path.join(self.output_dir, os.path.basename(self.input_bg).replace('.bg', '.bw'))
        cmd = '%s %s %s %s' % ( self.bg2bw_exe, self.input_bg, self.chrom_sizes, self.output_bw)

        self.submit_cmd(cmd)

        statinfo = os.stat(self.output_bw)
        if statinfo.st_size == 0:
            raise Exception('[bg %s is zero size]' % (self.output_bw))
