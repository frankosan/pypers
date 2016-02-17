from pypers.core.step import CmdLineStep

class SingleRarefaction(CmdLineStep):
    spec = {
        "version": "2015.05.13",
        "descr": [
            "Rarefies (subsamples) an OTU table prior to rarefaction analyses",
            "Input param depth is the number of sequences to subsample per sample"
        ],
        "url" : "http://qiime.org/scripts/single_rarefaction.html",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_biom",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input .biom OTU table filename",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_biom",
                    "type"  : "file",
                    "value" : "otu_table.rare.biom",
                    "descr" : "output rarified .biom OTU table",
                }
            ],
            "params": [
                {
                    "name"  : "depth",
                    "type"  : "int",
                    "value" : 50000,
                    "descr" : "number of sequences to subsample per sample"
                }
            ]
        },
        "requirements": { },
        "extra_env" : {
            "PYTHONPATH" : "/software/pypers/qiime/qiime-1.8.0/lib/python2.7/site-packages",
            "PATH": "/software/pypers/qiime/qiime-1.8.0/bin/"
        },
        "cmd": [
            "single_rarefaction.py  -i {{input_biom}} -o {{output_biom}} -d {{depth}}"
        ]
    }
