import os
from pypers.steps.qiime import Qiime

class PickClosedReferenceOtus(Qiime):
    spec = {
        "version": "20150512",
        "descr": [
            "Picks OTUs using a closed reference and constructs an OTU table.",
            "If a taxonomy map file is provided, Taxonomy is assigned."
        ],
        "url" : "http://qiime.org/scripts/pick_closed_reference_otus.html",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_fasta",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input fasta sequences file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_biom",
                    "type"  : "file",
                    "value" : "otu_table.biom",
                    "descr" : "the biom format picked OTU table",
                }
            ],
            "params": [
                {
                    "name"  : "ref_otu_fasta",
                    "type"  : "file",
                    "descr" : "Reference OTUs filename"
                },
                {
                    "name"  : "ref_otu_tax",
                    "type"  : "file",
                    "descr" : "Reference OTUs taxonomy filename"
                },
                {
                    "name"  : "threads",
                    "type"  : "int",
                    "descr" : "Number of process threads to run",
                    "value" : 1,
                    "readonly": True
                }
            ]
        },
        "requirements": { }
    }

    def process(self):
        """
        Run the step as configured.
        """

        if type(self.input_fasta) != list:
            self.input_fasta = [self.input_fasta]

        output_otu_dir = '%s/otus' % (self.output_dir)

        for input_fasta in self.input_fasta:

            cmd = 'pick_closed_reference_otus.py -i %s -r %s -t %s -o %s -f' % (input_fasta, self.ref_otu_fasta, self.ref_otu_tax, output_otu_dir)

            if self.threads > 1:
                cmd += ' -O %s -a' % self.threads

            self.submit_cmd(cmd,extra_env=self.extra_env)

            # Step generates a lot of files in the output subdir, we need to symlink the output biom
            self.output_biom = '%s/otu_table.biom' % output_otu_dir

            link = os.path.join(self.output_dir, 'otu_table.biom')
            if not os.path.exists(link):
                os.symlink(self.output_biom, link)

