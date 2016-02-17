from pypers.core.step import CmdLineStep

class ParallelBetaDiversity(CmdLineStep):
    spec = {
        "version": "2015.05.13",
        "descr": [
            "Calculates the beta diversity on an OTU table"
        ],
        "url" : "http://qiime.org/scripts/parallel_beta_diversity.html",
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
                    "name"  : "output_biom_unweighted",
                    "type"  : "file",
                    "value" : "unweighted_unifrac_otu_table.rare.txt",
                    "descr" : "output unweighted otu table",
                },
                {
                    "name"  : "output_biom_weighted",
                    "type"  : "file",
                    "value" : "weighted_unifrac_otu_table.rare.txt",
                    "descr" : "output weighted otu table",
                }
            ],
            "params": [
                {
                    "name"  : "metric",
                    "type"  : "str",
                    "descr" : "Beta-diversity metric(s) to use. A comma-separated list should be provided when multiple metrics are specified",
                    "value" : "unweighted_unifrac,weighted_unifrac"
                },
                {
                    "name"    : "tree",
                    "descr"   : "path to newick tree file, required for phylogenetic metrics",
                    "type"    : "file",
                    "value"   : "/Public_data/microbiome/16s/greengenes/gg_13_8_otus/trees/99_otus.tree"
                }
            ]
        },
        "requirements": {
            'cpus' : 6
        },
        "extra_env" : {
            "PYTHONPATH" : "/software/pypers/qiime/qiime-1.8.0/lib/python2.7/site-packages",
            # NB need to include /bin in path because this is used to get the bash shell exe location which is used in shell scripts run as child processes
            "PATH": "/software/pypers/qiime/qiime-1.8.0/bin/:/bin"
        },
        "cmd": [
            "parallel_beta_diversity.py -T  -t {{tree}} -i {{input_biom}} -o {{output_dir}} -m {{metric}} --jobs_to_start {{cpus}}"
        ]
    }
