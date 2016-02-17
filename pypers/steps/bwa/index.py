from pypers.core.step import CmdLineStep

class Index(CmdLineStep):
    spec = {
        "version": "0.7.6a",
        "descr": [
            "Indexes database sequences in the FASTA format using the bwa software"
        ],
        "args":
        {
            "inputs": [
                {
                    "name" : "input_files",
                    "type" : "file",
                    "iterable" : True,
                    "descr" : "list of fasta files to be indexed"
                }
            ],
            "outputs": [
                {
                    "name" : "output_files",
                    "type" : "file",
                    "value" : "{{input_files}}.fa",
                    "descr" : "path to the copied fasta file after indexing"
                }
            ]
        },
        "cmd" : [
            "cp {{input_files}} {{output_files}}",
            "&& /software/pypers/bwa/bwa-0.7.6a/bwa index {{output_files}}"
        ]
    }

