from pypers.core.step import CmdLineStep

class PredictMetagenomes(CmdLineStep):
    spec = {
        "version": "2015.05.28",
        "descr": [
            "Produces the metagenome functional predictions for a given OTU table in biom format",
            "Use the default prediction type ko - KEGG KO abundances"
        ],
        "url" : "http://picrust.github.io/picrust/scripts/predict_metagenomes.html#predict-metagenomes",
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
                    "value" : "metagenome.biom",
                    "descr" : "output metagenome functional predictions .biom OTU table",
                }
            ]
        },
        "cmd": [
            "predict_metagenomes.py -i {{input_biom}} -o {{output_dir}}/{{output_biom}}"
        ]
    }
