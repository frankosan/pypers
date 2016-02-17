import os
import re
from pypers.core.step import FunctionStep
from pypers.utils.fofn import Fofn


class MkFofn(FunctionStep):
    """
    Creates a fofn from an Illumina sample sheet and an input directory
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns list of files read from a fofn"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_dirs",
                    "type"     : "dir",
                    "descr"    : "the input directories containing the fastq files",
                },
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "descr"    : "the corresponding sample sheets (by default look into input directories)",
                    "value"    : ""
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "the fofn file created by the step",
                    "value" : "fofn.csv"
                }
            ],
            "params" : [
                {
                    "name"  : "ss_name",
                    "type"  : "str",
                    "descr" : "the default name of the sample sheet",
                    "value" : "SampleSheet.csv"
                }
            ]
        }
    }

    def process(self):
        fofns = []
        if not hasattr(self.input_dirs, '__iter__'):
            self.input_dirs = [self.input_dirs]
        for i, idir in enumerate(self.input_dirs):
            sample_sheet = ''
            if self.input_files:
                sample_sheet = self.input_files[i]
            else:
                sample_sheet = os.path.join(idir, self.ss_name)           
            ifofn = 'fofn_%03d.csv' % i
            fofns.append(Fofn.create(
                                sample_sheet,
                                idir,
                                self.output_dir,
                                ifofn)
                        )
        mfofn = os.path.join(self.output_dir, self.output_files)
        with open(mfofn, 'w') as ofh:
            for fofn in fofns:
                with open(fofn) as ifh:
                    ofh.write( ''.join(ifh.readlines()) )
                os.remove(fofn)
        self.output_files = [mfofn]
