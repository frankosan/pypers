import os
import sys
import re
from pypers.core.step import FunctionStep
from pypers.utils import utils as ut


class Find(FunctionStep):
    """
    Return list of files read from a fofn
    """
    spec = {
        "version": "1.0",
        "descr": [
            "Return list of files read from a input directory matching the input pattern"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_dirs",
                    "type"     : "dir",
                    "iterable" : True,
                    "descr"    : "the input directory",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "output file names",
                }
            ],
            "params" : [
                {
                    "name"     : "pattern",
                    "type"     : "str",
                    "descr"    : "the unix style search pattern or a regular expression",
                },
                {
                    "name"     : "regex_match",
                    "type"     : "boolean",
                    "value"    : False,
                    "descr"    : "if True regular expression pattern matching is used, otherwise unix style pattern matching",
                }
            ],
        }
    }

    def process(self):
        self.output_files = ut.find(self.input_dirs, self.pattern, self.regex_match)
