import os
import re
from collections import defaultdict
from pypers.core.step import FunctionStep

class GroupBySample(FunctionStep):
    spec = {
        "version": "0.1",
        "descr": [
            "Return list of files grouped by sample"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "descr"    : "the input files",
                },
            ],
            "params": [
                {
                    "name"     : "regex_sample_id",
                    "value"    : "^(.*)_.*?_.*?_.*?",
                    "type"     : "str",
                    "descr"    : "reqular expression used to get the sample id in the first group",                
                    "readonly" : True
                }

            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "output file names",
                }
            ]
        }
    }

    def process(self):

        #if metadata are not passed then I metadata are created from the file names
        if not self.meta['job'].get('sample_id', ''):
            # <sample name>_<barcode sequence>_L<lane(0-padded to 3 digits)>_R<read number>_<set number(0-padded to 3 digits>.fastq.gz
            self.meta['job']['sample_id'] = []
            for input_file in self.input_files:
                m = re.search(self.regex_sample_id, os.path.basename(input_file))
                if m:
                    self.meta['job']['sample_id'].append(m.group(1))

        group_list = {}
        for index in xrange(0,len(self.input_files)):
            sample_id = self.meta['job']['sample_id'][index]
            if sample_id in group_list:
                group_list[sample_id].append(self.input_files[index])
            else:
                group_list[sample_id] = [self.input_files[index]]


        self.meta['job']['sample_id'] = []
        self.output_files = []
        for k in sorted(group_list):
            self.output_files.append(group_list[k])
            self.meta['job']['sample_id'].append(k)


