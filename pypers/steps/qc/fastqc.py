import os
from pypers.core.step import CmdLineStep
from pypers.utils import utils


class FastQc(CmdLineStep):
    spec = {
        "name": "FastQc",
        "version": "0.10",
        "descr": [
            "Runs FasQc on the input files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input fastq files",
                }
            ],
            "outputs": [
                {
                    "name"  : "html_reports",
                    "type"  : "file",
                    "descr" : "the html reports",
                },
                {
                    "name"  : "summary_reports",
                    "type"  : "file",
                    "descr" : "the summary reports",
                },
                {
                    "name"  : "detailed_reports",
                    "type"  : "file",
                    "descr" : "the detailed reports",
                }
            ]
        },
        "cmd": [
            "/software/pypers/FastQC/FastQC-0.10.0/bin/fastqc ",
            "-o {{output_dir}} --nogroup -t 1 -f fastq {{input_files}}",
        ]
    }

    def process(self):
        super(FastQc,self).process()
        self.summary_reports = utils.find_one(self.output_dir, "*/summary.txt")
        self.detailed_reports = utils.find_one(self.output_dir, "*/fastqc_data.txt")
        raw_html_reports = utils.find_one(self.output_dir, "*/fastqc_report.html")
        self.html_reports = utils.format_html(raw_html_reports)

