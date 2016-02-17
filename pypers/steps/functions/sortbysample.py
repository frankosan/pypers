import os
import re
from collections import defaultdict
from pypers.core.step import FunctionStep

class SortBySample(FunctionStep):
    spec = {
        "version": "0.1",
        "descr": [
            "Extract the sample ID from the input file name and set it to the metadata"
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
                    "value"    : "^(.*)_([ATCG-]*?)_(L\\d{3}?)_(R\\d{1}?)_(\\d{3})",
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
        group_list = defaultdict(list)
        self.output_files = []
        if not self.meta['job'].get('sample_id', ''):
            # <sample name>_<barcode sequence>_L<lane(0-padded to 3 digits)>_R<read number>_<set number(0-padded to 3 digits>.fastq.gz
            self.meta['job']['sample_id'] = []
            for input_file in self.input_files:
                m = re.search(self.regex_sample_id, os.path.basename(input_file))
                if m:
                    group_list[m.group(1)].append(input_file)

        self.meta['job']['sample_id'] = []
        for k in sorted(group_list):
            for f in group_list[k]:
                self.output_files.append(f)
                self.meta['job']['sample_id'].append(k)


