import os
import re

from pypers.steps.qiime import Qiime

class MakeRarefactionPlots(Qiime):
    spec = {
        "version": "2015.05.20",
        "descr": [
            """
            Generate Rarefaction Plots for batched alpha diversity files
            http://qiime.org/scripts/make_rarefaction_plots.html
            """
        ],
        "url" : "http://qiime.org/scripts/collate_alpha.html",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_dir",
                    "type"     : "dir",
                    "iterable" : True
                },
                {
                    "name"     : "input_map",
                    "type"     : "dir",
                    "iterable" : True,
                    "descr"    : "the input mapping file"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_html",
                    "type"  : "file"
                }
            ],
            "params": [
            ]
        },
        "requirements": {
        },
    }

    def process(self):

        cmd = 'make_rarefaction_plots.py -i %s -o %s -m %s' % (self.input_dir, self.output_dir, self.input_map)
        self.submit_cmd(cmd,extra_env=self.extra_env)

        # make a downloadable zip
        cmd = 'cd %s && /usr/bin/zip -r %s %s %s' % (
                self.output_dir,
                'rarefaction_plots.zip',
                os.path.join('average_plots', '*'),
                'rarefaction_plots.html')
        self.submit_cmd(cmd)

        # substitute Image and Icon paths in a way to be
        # visibile in ui (using /api/fs service)
        reg1 = re.compile(r'img.document\.createElement.(\'img\')')
        reg2 = re.compile(r'img\.setAttribute..src.*(\.\/average_plots)')

        input_html_file = os.path.join(self.output_dir, 'rarefaction_plots.html')
        out_html_file = '%s/%s.html' % (self.output_dir, 'rarefaction_plots.tmp')
        img_url_prefix = '/api/fs/png?embed=true&path=%s' %  os.path.join(self.output_dir, 'average_plots')
        with open(input_html_file, "r") as input_file, open(out_html_file, "w") as output_file:
            for line in input_file:
                match = reg1.search(line)
                if match:
                    matched = match.group(1)
                    line = line.replace(matched, "'iframe'")
                    line = line + '''
                        img.setAttribute("frameborder","0")
                        img.setAttribute("height","550px")
                    '''

                match = reg2.search(line)
                if match:
                    matched = match.group(1)
                    line = line.replace(matched, img_url_prefix)

                output_file.write(line)

        os.rename(input_html_file, os.path.join(self.output_dir, '.rarefaction_plots.original.html'))
        os.rename(out_html_file, os.path.join(self.output_dir, 'rarefaction_plots.html'))

