from pypers.core.step import CmdLineStep

class FilterSamplesFromOTUTable(CmdLineStep):
    spec = {
        "version": "2015.05.13",
        "descr": [
            "Filters samples from an OTU table",
            "Currently we implement only filter on --min_count, ie minimum total observations"
        ],
        "url" : "http://qiime.org/scripts/filter_samples_from_otu_table.html",
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
                    "value" : "otu_table.filt.biom",
                    "descr" : "output filtered .biom OTU table",
                }
            ],
            "params": [
                {
                    "name"  : "min_count",
                    "type"  : "int",
                    "value" : 50000,
                    "descr" : " minimum total observations in a sample for it to be retained"
                }
            ]
        },
        "requirements": { },
        "extra_env" : {
            "PYTHONPATH" : "/software/pypers/qiime/qiime-1.8.0/lib/python2.7/site-packages",
            "PATH": "/software/pypers/qiime/qiime-1.8.0/bin/"
        },
        "cmd": [
            "filter_samples_from_otu_table.py  -i {{input_biom}} -o {{output_biom}} -n {{min_count}}"
        ]
    }
