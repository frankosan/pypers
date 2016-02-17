import os
import re
import jinja2
from collections import OrderedDict
from pypers.core.step import Step
from pypers.utils import utils

class FastqScreenReport(Step):
    spec = {
        "version": "0.1",
        "descr": [
            "Create a report of from a list of fastqscreen files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "txt_files",
                    "type"     : "file",
                    "descr"    : "fastqscreen reports",
                },
                {
                    "name"     : "png_files",
                    "type"     : "file",
                    "descr"    : "fastqscreen png files",
                },
            ],
            "outputs": [
                {
                    "name"  : "html_report",
                    "type"  : "file",
                    "descr" : "a html report",
                },
                {
                    "name"  : "csv_report",
                    "type"  : "file",
                    "descr" : "a csv report",
                }
            ]
        }
    }
    def process(self):
            self.output_files = {}
            self.html_report = os.path.join(self.output_dir, 'html_report.html')
            self.csv_report = os.path.join(self.output_dir, 'csv_report.csv')
            with open(self.csv_report, 'w+') as csv_out:
                png_dict = {}

                # sorting alpha-numerically
                convert_f = lambda x: int(x) if x.isdigit() else x.lower()
                alphanum_f = lambda key: [ convert_f(c) for c in re.split('([0-9]+)', key) ]

                for png in self.png_files:
                    png_name = os.path.basename(png)
                    png_dict[png_name] = png

                csv_out.write('FastQ Screen\n\n')
                for txt_file in sorted(self.txt_files,
                                key=lambda x: alphanum_f(os.path.basename(x))):
                    data_id = re.sub(r'_(R1_\d{3})_screen\.txt', r'_\1', os.path.basename(txt_file))
                    csv_out.write('%s\n' % data_id)
                    with open(txt_file, 'r') as infile:
                        for line in infile:
                            csv_out.write(line.replace('\t', ','))
                    csv_out.write('\n\n')

                #############
                # HTML Report
                #############
                with open(self.html_report, "w")  as html_out:
                    code_root = os.path.abspath(os.path.dirname(__file__))
                    env = jinja2.Environment(loader=jinja2.FileSystemLoader(code_root))
                    t = env.get_template('fastqscreenreport.html')

                    html_out.write(t.render(pngs=OrderedDict(sorted(png_dict.items(), key=lambda x: alphanum_f(x[0])))))
