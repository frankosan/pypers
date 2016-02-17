import os
from pypers.steps.genome_annotation.kbase import KbaseStep

class Rast_call_rRNAs(KbaseStep):
    spec = {
        "name": "Rast_call_rRNAs",
        "version": "2015.07.30",
        "descr": [
            """
            DEPRECATED use kbase_annotation.py
            Runs kbase call_features_rRNA_SEED workflow, rast_call_rRNAs.pl, to find ribosomal RNAs in the input genome
            http://www.theseed.org
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_genome",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the name of the input genome file in Genbank JSON format",
                }
            ],
            "outputs": [
                {
                    "name"     : "output_genome",
                    "type"     : "file",
                    "descr"    : "the name of the output genome file",
                }
            ],
            "params": [
                {
                    "name"  : "rna_class",
                    "type"  : "enum",
                    "options": ['', '--5S', '--LSU', '--SSU'],
                    "descr" : "optional rRNA gene classs to find, --5S (5S), --LSU (large subunit), or --SSU (small subunit): default is null: all rRNA classes",
                    "value" : ""
                }
            ],
        }
    }

    def process(self):

        output_genome = os.path.basename(self.input_genome.replace('genome','rRNAs.genome'))
        self.output_genome = "%s/%s" % (self.output_dir,output_genome)

        cmd = "perl %s/rast_call_rRNAs.pl --input %s --output %s %s" % (self.perl_bin_path, self.input_genome, self.output_genome, self.rna_class)
        self.submit_cmd(cmd, extra_env=self.extra_env)
