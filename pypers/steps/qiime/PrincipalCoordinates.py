from pypers.core.step import CmdLineStep

class PrincipalCoordinates(CmdLineStep):
    spec = {
        "version": "2015.05.18",
        "descr": [
            "Performs Principal Coordinate Analysis (PCoA) to compare groups of samples",
            "based on phylogenetic or count-based distance metrics"
        ],
        "url" : "http://qiime.org/scripts/principal_coordinates.html",
        "args": 
        {
            "inputs": [
                {
                    "name"     : "input_matrix",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input distance matrix file from beta_diversity.py"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_pca",
                    "type"  : "file",
                    "value" : "otu.pca.txt",
                    "descr" : "output PCoA analysis filename",
                }
            ]
        },
        "requirements": { },
        "extra_env" : {
            "PYTHONPATH" : "/software/pypers/qiime/qiime-1.8.0/lib/python2.7/site-packages",
            "PATH": "/software/pypers/qiime/qiime-1.8.0/bin/"
        },
        "cmd": [
            "principal_coordinates.py -i {{input_matrix}} -o {{output_pca}}"
        ]
    }
