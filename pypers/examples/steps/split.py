from pypers.core.step import CmdLineStep

class Split(CmdLineStep):
    spec = {
        "version": "1.0",
        "local" : True,
        "descr": [
            "Splits an input file in several chuncks"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"      : "input_file",
                    "type"      : "file",
                    "descr"     : "input file name"
                },
                {
                    "name"      : "nchunks",
                    "type"      : "int",
                    "value"     : 100,
                    "descr"     : "number of chunks in which the input file get splitted"
                },
            ],
            "outputs": [
                {
                    "name"      : "output_files",
                    "type"      : "file",
                    "value"     : "*.fa",
                    "descr"     : "output file names"
                }
            ],
            "params" : [
                {
                    "name"      : "prefix",
                    "type"      : "str",
                    "value"     : "chunk_",
                    "descr"     : "string prefix on the output files",
                    "readonly"  : True
                },
                {
                    "name"      : "suffix",
                    "type"      : "str",
                    "value"     : ".fa",
                    "descr"     : "suffix added to the splitted files",
                    "readonly"  : True
                }
            ]
        },
        "cmd": [
            "split -n {{nchunks}} --suffix-length=4 -d --additional-suffix {{suffix}} {{input_file}} {{output_dir}}/{{prefix}}"
        ]
    }

