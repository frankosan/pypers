from pypers.core.step import Step
from pypers.utils.utils import which
import os

class Biom2Tsv(Step):
    spec = {
        "version": "2015.05.28",
        "descr": [
            "Calls the biom convert function to convert files in .biom format into 'classic format' tsv",
            "Optinally remove the first line '# Constructed from biom file' for subsequent processing using HUMAnN"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the input .biom OTU table",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "The output converted biom file in tsv format"
                }
            ],
            "params": [
                {
                    "name"  : "remove_hdr",
                    "type"  : "boolean",
                    "descr" : "Remove the first line, biom file header, default True",
                    "value" : True
                },
            ]
        },
        "requirements": { },
    }

    def process(self):


        if type(self.input_files) != list:
            self.input_files = [self.input_files]

        self.output_files = []
        for input_biom in self.input_files:
            fileName, fileExt = os.path.splitext(os.path.basename(input_biom))
            output_tsv = '%s.tsv' % fileName

            if os.path.isfile(output_tsv):
                os.remove(output_tsv)
            self.log.info('Converting %s into %s', input_biom, output_tsv)

            # For now only allow tsv conversion using option '-b'
            cmd = '%s convert -i %s -o %s -b' % (which('biom'), input_biom, output_tsv)

            self.submit_cmd(cmd)

            if self.remove_hdr:
                ip_fn = open(output_tsv,'r')
                op_fn = open('%s.tmp' % output_tsv,'w')
                next(ip_fn)
                for line in ip_fn:
                   op_fn.write(line)
                ip_fn.close()
                op_fn.close()
                os.rename('%s.tmp' % output_tsv, output_tsv)

            self.output_files.append(output_tsv)

