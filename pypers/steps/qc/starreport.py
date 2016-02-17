import os
import re
import jinja2
import copy
from collections import OrderedDict
from pypers.core.step import Step
from pypers.utils import utils as ut

class StarReport(Step):
    spec = {
        "name": "StarReport",
        "version": "0.1",
        "descr": [
            "Create a report based on the STAR statistics"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"  : "stats_files",
                    "type"  : "file",
                    "descr" : "the rna STAR stats log files",
                }
            ],
            "outputs": [
                {
                    "name"  : "html_report",
                    "type"  : "file",
                    "value" : "report.html",
                    "descr" : "the html reports",
                },
                {
                    "name"  : "csv_report",
                    "type"  : "file",
                    "value" : "report.csv",
                    "descr" : "the csv reports",
                }
            ]
        }
    }


    def process(self):
        """
        Create a fastqc final report and a report containing only the failed
        """

        # N.B. This header defines the order and the info extracted from STAR stats, but %s will get overwritten
        header = [  
                    "Sample", "Directory ID", "Name", 
                    "Number of input reads", "Average input read length",
                    "Uniquely mapped reads number", "Average mapped length",
                    "Number of splices: Total", "Number of splices: Annotated (sjdb)",
                    "Number of reads mapped to multiple loci", "% of reads mapped to multiple loci",
                    "Number of reads mapped to too many loci", "% of reads mapped to too many loci",
                    "% of reads unmapped: too many mismatches", "% of reads unmapped: too short",
                    "% of reads unmapped: other" 
                 ]

        sample_ids = self.meta['job'].get('sample_id')
        csv_list = {}
        html_list = {}
        for i, filename in enumerate(self.stats_files):
            name = os.path.basename(filename).split('.')[0]
            sample_id = sample_ids[i] if sample_ids else ''
            csv_list[name] = { 'Sample': sample_id, 'Directory ID': str(i), 'Name': name }
            html_list[name] = copy.deepcopy(csv_list[name])
            with open(filename, "r") as fh:
                for line in fh:
                    cells = line.split('|')
                    if len(cells)==2:
                        key = cells[0].rstrip().lstrip()
                        value = cells[1].lstrip().rstrip('\n')
                        if key in header:
                            if key.find('%')>-1:
                                key = key.replace(r'%', r'Fraction')
                                value = str(float(value.replace('%',''))/100.)
                            csv_list[name][key] = value
                            html_list[name][key] = ut.pretty_number(value)


        # Add custom columns
        header.insert(header.index("Uniquely mapped reads number")+1,"Fraction of uniquely mapped reads")
        for name in csv_list:
            ratio = 0
            if csv_list[name]["Uniquely mapped reads number"]>0:
                ratio = float(csv_list[name]["Uniquely mapped reads number"])/float(csv_list[name]["Number of input reads"])
            ratio = '%.4f' % ratio
            csv_list[name]["Fraction of uniquely mapped reads"] = ratio
            html_list[name]["Fraction of uniquely mapped reads"] = ut.pretty_number(ratio)


        # sorting alpha-numerically
        convert_f = lambda x: int(x) if x.isdigit() else x.lower()
        alphanum_f = lambda key: [ convert_f(c) for c in re.split('([0-9]+)', key) ]

        ############
        # CSV Report
        ############
        keys = [k.replace('%', 'Fraction') for k in header]
        with open(self.csv_report, "w")  as csv_fh:
            csv_fh.write('"')
            csv_fh.write('","'.join(keys))
            csv_fh.write('"')
            csv_fh.write('\n')
            for name in sorted(csv_list.keys(), key=alphanum_f):
                vals = []
                for key in keys:
                    vals.append(csv_list[name][key])
                csv_fh.write(','.join(vals))
                csv_fh.write('\n')

        
        #############
        # HTML Report
        #############
        with open(self.html_report, "w")  as html_fh:
            code_root = os.path.abspath(os.path.dirname(__file__))
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(code_root))
            t = env.get_template('starreport.html')
            html_fh.write(t.render(keys=keys,
                                   table=OrderedDict(sorted(html_list.items(),
                                                            key=lambda x: alphanum_f(x[0])))))
