import os
import re
import json
import jinja2
from collections import OrderedDict
from pypers.core.step import Step
from pypers.utils import utils as ut

class ExomeMergeAutoQcReport(Step):
    """
    Create the auto_qc final report
    """

    spec = {
        "name": "BamAutoQcReport",
        "version": "0.1",
        "descr": [
            "Create an HTML report based on the auto_qc results"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"  : "autoqc_files",
                    "type"  : "file",
                    "descr" : "the auto_qc reports",
                },
                {
                    "name"  : "bam_files",
                    "type"  : "file",
                    "descr" : "the bam files",
                }
            ],
            "outputs": [
                {
                    "name"  : "autoqc_report",
                    "type"  : "file",
                    "value" : "autoqc_report.html",
                    "descr" : "the html reports",
                },
                {
                    "name"  : "report_all",
                    "type"  : "file",
                    "value" : "qc_report.csv",
                    "descr" : "the csv reports",
                },
                {
                    "name"  : "report_passed",
                    "type"  : "file",
                    "value" : "qc_passed.csv",
                    "descr" : "the csv reports",
                },
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "the list of output files",                
                }

            ]
        }
    }        


    def process(self):

        code_root = os.path.abspath(os.path.dirname(__file__))
        self.html_template = os.path.join(code_root, 'bamautoqcreport.html')

        html_rows = []
        passed = []
        failed = []
        for i, f in enumerate(self.autoqc_files):           
            with open(f) as fh:
                if fh.readlines()[-1].find('PASS') > -1:
                    passed.append(self.bam_files[i])
                    html_rows.append({
                        'file':os.path.basename(f),
                        'path':f,
                        'status': 'PASS'
                    })
                else:
                    failed.append(f)
                    html_rows.append({
                        'file':os.path.basename(f),
                        'path':f,
                        'status': 'FAILED'
                    })

        self.output_files = passed
        with open(self.report_all, "w") as fh_all, open(self.report_passed, "w") as fh_passed:
            for filename in passed:
                fh_all.write('PASSED  %s\n' % filename)
                fh_passed.write('PASSED  %s\n' % filename)
            for filename in failed:
                fh_all.write('FAILED  %s\n' % filename)
      


        ut.template_render(self.html_template,
                           self.autoqc_report,
                           header=["file", "status"],
                           rows=html_rows)

