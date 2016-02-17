import os
from pypers.core.step import CmdLineStep
from pypers.utils import utils


class Split(CmdLineStep):
    spec = {
        "name": "split",
        "version": "1.0",
        "descr": [
            "Splits an input file in several chuncks"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_file",
                    "type"     : "file",
                    "descr"    : "input file name",
                },
                {
                    "name"     : "nchunks",
                    "type"     : "int",
                    "descr"    : "number of chunks in which the input file get splitted",
                },
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
                    "name"      : "prefix",
                    "value"     : "chunk_",
                    "descr"     : "string prefix on the output files",
                    "readonly"  : True,
                },
                {
                    "name"      : "extension",
                    "value"     : ".bed",
                    "descr"     : "extension added to the splitted files",
                    "readonly"  : True,
                }


            ]
        },
        "cmd": [
            "/usr/bin/split -l {{line_chunks}} --suffix-length=4 -d {{input_file}} {{full_prefix}}",
        ]
    }


    def process(self):

        with open(self.input_file) as fh:
            lines = len(fh.readlines())

        self.line_chunks = int(lines /  self.nchunks)
        self.full_prefix = os.path.join(self.output_dir, self.prefix)

        self.submit_cmd(self.render())
        self.output_files = []
        for filename in os.listdir(self.output_dir):
            if filename.startswith(self.prefix):
                original_path = os.path.join(self.output_dir, filename)
                new_path = original_path + self.extension
                os.rename(original_path, new_path)
                self.output_files.append(new_path)

        self.meta['job']['input_file'] = []
        for output_file in self.output_files:
            self.meta['job']['input_file'].append(self.input_file)

