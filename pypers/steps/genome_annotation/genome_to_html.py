import os
from pypers.steps.genome_annotation.kbase import KbaseStep

class GenomeToHtml(KbaseStep):
    spec = {
        "name": "GenomeToHtml",
        "version": "2015.08.12",
        "descr": [
            """
            Creates a html summary report from an annotated kbase genome file
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_genome",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the name of the input genome file",
                }
            ],
            "outputs": [
                {
                    "name"     : "output_html",
                    "type"     : "file",
                    "descr"    : "the name of the output html file",
                }
            ]
        }
    }

    def process(self):

        self.output_html = "%s/index.html" % (self.output_dir)

        cmd = "perl %s/genomeTO_to_html.pl < %s > %s" % (self.perl_bin_path, self.input_genome, self.output_html)
        self.submit_cmd(cmd, extra_env=self.extra_env)
