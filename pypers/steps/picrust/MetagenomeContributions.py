from pypers.core.step import CmdLineStep

class MetagenomeContributions(CmdLineStep):
    spec = {
        "version": "2015.05.28",
        "descr": [
            "Partitions metagenome functional contributions according to function, OTU, and sample, for a given .biom OTU table",
            "Output is a tab-delimited file of OTU contributions for each function",
        ],
        "url" : "http://picrust.github.io/picrust/scripts/metagenome_contributions.html",
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
                    "name"  : "contrib_txt",
                    "type"  : "file",
                    "value" : "contrib.txt",
                    "descr" : "The output text file for the metagenome contributions"
                }
            ],
            "params": [
                {
                    "name"    : "type_of_prediction",
                    "type"    : "enum",
                    "options" : ['ko', 'cog', 'rfam'],
                    "descr"   : "Type of functional predictions. Valid choices are: ko, cog, rfam [default: ko]",
                    "value"   : "ko"
                }
            ]
        },
        "cmd": [
            "metagenome_contributions.py -i {{input_biom}} -o {{output_dir}}/{{contrib_txt}} -t {{type_of_prediction}}"
        ]
    }
