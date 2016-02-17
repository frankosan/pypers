from pypers.core.step import CmdLineStep

class MakeEmporer(CmdLineStep):
    spec = {
        "version": "2015.05.18",
        "descr": [
            "Create three dimensional PCoA plots"
        ],
        "url" : "http://biocore.github.io/emperor/build/html/scripts/make_emperor.html",
        "args": 
        {
            "inputs": [
                {
                    "name"     : "input_pca",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input PCoA analysis coords filename"
                },
                {
                    "name"     : "input_map",
                    "type"     : "file",
                    "descr"    : "Path to a metadata mapping file"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_html",
                    "type"  : "file",
                    "value" : "index.html",
                    "descr" : "output html index filename",
                }
            ]
        },
        "requirements": { },
        "extra_env" : {
            "PYTHONPATH" : "/software/pypers/qiime/qiime-1.8.0/lib/python2.7/site-packages",
            "PATH": "/software/pypers/qiime/qiime-1.8.0/bin/:/bin"
        },
        "cmd": [
            "make_emperor.py -i {{input_pca}} -m {{input_map}} -o {{output_dir}}"
        ]
    }
