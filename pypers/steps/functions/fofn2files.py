import os
import re
from pypers.core.step import FunctionStep
from pypers.utils.fofn import Fofn


class Fofn2Files(FunctionStep):
    spec = {
        "version": "0.1",
        "descr": [
            "Returns list of files read from a fofn"
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
        ret_list = []
        sample_ids = []

        if type(self.input_files) != list:
            self.input_files = [self.input_files]

        for filename in self.input_files:
            for row in Fofn.get_rows(filename):
                ret_list.append(row[0])
                ret_list.append(row[1])
                sample_ids.extend(2*[row[2]])

        self.output_files = ret_list
        self.meta['job']['sample_id'] = sample_ids
