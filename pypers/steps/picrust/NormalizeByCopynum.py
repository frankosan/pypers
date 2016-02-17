from pypers.core.step import CmdLineStep

class NormalizeByCopynum(CmdLineStep):
    spec = {
        "version": "2015.05.28",
        "descr": [
            "Normalises an OTU table in biom format by Greengenes marker gene copy number"
        ],
        "url" : "http://picrust.github.io/picrust/scripts/normalize_by_copy_number.html",
        "args": 
        {
            "inputs": [
                {
                    "name"     : "input_biom",
                    "type"     : "file",
                    "descr"    : "the input .biom OTU table",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_biom",
                    "type"  : "file",
                    "value" : "cpnorm.biom",
                    "descr" : "output normalised .biom OTU table",
                }
            ],
        },
        "cmd": [
            "normalize_by_copy_number.py -i {{input_biom}} -o {{output_dir}}/{{output_biom}}"
        ]
    }
