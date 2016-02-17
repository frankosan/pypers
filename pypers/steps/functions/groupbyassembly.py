import os
import re
from pypers.core.step import FunctionStep

class GroupByAssembly(FunctionStep):
    spec = {
        "version": "0.1",
        "descr": [
            "Returns list of lists with each sublist containing files from the same assembly input"
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

        if len(self.input_files) == 1:
            self.output_files = self.input_files
            return 0

        assemblers_list = {}
        commonprefix = os.path.commonprefix(self.input_files)

        for file in self.input_files:
            assembly_no = file.replace(commonprefix,'').split('/')[1]

            if assembly_no in assemblers_list:
                assemblers_list[assembly_no].append(file)
            else:
                assemblers_list[assembly_no] = [file]
            
        self.meta['job']['assembly_no'] = []
        self.output_files = []
        for k in assemblers_list:
            self.output_files.append(assemblers_list[k])
            self.meta['job']['assembly_no'].append(k)
