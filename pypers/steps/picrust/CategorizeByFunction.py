from pypers.core.step import CmdLineStep

class CategorizeByFunction(CmdLineStep):
    spec = {
        "version": "2015.05.28",
        "descr": [
            "Collapses the predicted metagenome in an  OTU table in biom format to a specific level",
            "By default to level 3 using KEGG Pathway metadta"
        ],
        "url" : "http://picrust.github.io/picrust/scripts/categorize_by_function.html",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_biom",
                    "type"     : "file",
                    "descr"    : "the input metagenome .biom OTU table",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_biom",
                    "type"  : "file",
                    "value" : "collapse.biom",
                    "descr" : "output collapsed metagenome .biom OTU table",
                }
            ],
            "params": [
                {
                    "name"  : "metadata_category",
                    "type"  : "str",
                    "descr" : "Metadata category that describes the hierarchy",
                    "value" : "KEGG_Pathways"
                },
                {
                    "name"  : "level",
                    "type"  : "int",
                    "descr" : "Level in the hierarchy to collapse to",
                    "value" : 3
                }
            ]
        },
        "requirements": { },
        "extra_env" : { },
        "cmd": [
            "categorize_by_function.py -i {{input_biom}} -o {{output_dir}}/{{output_biom}} -c {{metadata_category}} -l {{level}}"
        ]
    }
