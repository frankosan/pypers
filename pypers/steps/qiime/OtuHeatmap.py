import re
import os
from pypers.steps.qiime import Qiime

class OtuHeatmap(Qiime):
    spec = {
        "version": "2015.05.13",
        "descr": [
            "Generate OTU heatmap images from BIOM tables"
        ],
        "url" : "http://qiime.org/scripts/make_otu_heatmap.html",
        "args": 
        {
            "inputs": [
                {
                    "name"     : "input_biom",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input .biom OTU table filename"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_html",
                    "type"  : "file",
                    "descr" : "output OTU table heatmap html"
                }
            ]
        }
    }

    def process(self):

        cmd = 'make_otu_heatmap_html.py -i %s -o %s' % (self.input_biom, self.output_dir)
        self.submit_cmd(cmd,extra_env=self.extra_env)

        # substitute Image and Icon paths in a way to be
        # visibile in ui (using /api/fs service)
        reg = re.compile(r'script.*text\/javascript.*src=\"(.*)\"')

        self.output_html =  os.path.join(self.output_dir, 'otu_table.html')
        transformed_html   = os.path.join(self.output_dir, 'otu_table.tmp.html')
        src_url_prefix  = '/api/fs/txt?path=%s' %  (self.output_dir)

        with open(self.output_html, 'r') as orig_file, open(transformed_html, "w") as trans_file:
            for line in orig_file:
                match = reg.search(line)
                if match:
                    matched = match.group(1)
                    line = line.replace(matched, os.path.join(src_url_prefix, matched))

                trans_file.write(line)

        os.rename(self.output_html, os.path.join(self.output_dir, '.otu_table.original.html'))
        os.rename(transformed_html, os.path.join(self.output_dir, 'otu_table.html'))

