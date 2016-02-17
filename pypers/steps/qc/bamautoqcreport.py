import os
import re
import json
import jinja2
from collections import OrderedDict
from pypers.core.step import Step
from pypers.utils import utils

class BamAutoQcReport(Step):
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
                    "name"  : "input_files",
                    "type"  : "file",
                    "descr" : "the auto_qc reports",
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
        Create a autoqc final report containing only the failed
        """

        if type(self.input_files) != list:
            self.input_files = [self.input_files]

        # Gather the information
        qc_info_list = []
        qc_keys = ['file']
        pattern = re.compile('^\s*(PASS|FAIL)\s+(\S+)[\s:]+([\d\.None]+)\s+\([\d\.]+\)')
        for fqc in self.input_files:
            qc_info = { 
                'file' : os.path.basename(fqc).split('.')[0],
                'path' : fqc 
            }
            
            with open(fqc) as fh:
                lines = fh.readlines()
                for line in lines:
                    m = re.match(pattern, line)
                    if m:
                        key = m.group(2)
                        qc_info[key] = m.group(1)
                        if not key in qc_keys:
                            qc_keys.append(key)
                    else:
                        m = re.match('RESULT\s?:\s?(.*)', line)
                        if m:
                            qc_info['result'] = m.group(1)
            qc_info_list.append(qc_info)


        with open(self.csv_report, "w")  as csv_fh:
            csv_fh.write(','.join(qc_keys))
            csv_fh.write('\n')
            for entry in qc_info_list:
                for key in qc_keys:
                    if key == 'file':
                        csv_fh.write(entry['path'])
                    else:
                        csv_fh.write(entry[key])
                    csv_fh.write(',')
                csv_fh.write('\n')


        #############
        # HTML Report
        #############
        with open(self.html_report, "w")  as html_fh:
            code_root = os.path.abspath(os.path.dirname(__file__))
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(code_root))
            t = env.get_template('bamautoqcreport.html')
            html_fh.write(t.render(keys=qc_keys, table=qc_info_list))


