import os
from pypers.steps.genome_annotation.kbase import KbaseStep

class FastaToGenome(KbaseStep):
    spec = {
        "name": "FastaToGenome",
        "version": "2015.08.12",
        "descr": [
            """
            Runs kbase fasta_to_genome perl script to convert a fasta contig file to a kbase genome encoded in a json file
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_fasta",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the name of the input fasta contig file in",
                },
                {
                    "name"  : "genus",
                    "type"  : "str",
                    'iterable' : True,
                    "descr" : "genus or scientific name for input contig file",
                    "value" : "Unspecified_Genome"
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
                    "name"  : "domain",
                    "type"  : "str",
                    "descr" : "organism domain, default Bacteria",
                    "value" : "Bacteria"
                },
                {
                    "name"  : "genetic_code",
                    "type"  : "int",
                    "descr" : "genetic code, normally 11 for prokaryotes",
                    "value" : 11
                }
            ],
        }
    }

    def process(self):

        fn_root = os.path.splitext(os.path.basename(self.input_fasta))[0]
        self.output_genome = "%s/%s.genome" % (self.output_dir,fn_root)

        # prevent wrapped quotes
        genus = self.genus.replace('"','')

        cmd = 'perl %s/fasta_to_genome.pl --input %s --output %s "%s" "%s" %s' % (self.perl_bin_path, self.input_fasta, self.output_genome, genus, self.domain, self.genetic_code)
        self.submit_cmd(cmd, extra_env=self.extra_env)
