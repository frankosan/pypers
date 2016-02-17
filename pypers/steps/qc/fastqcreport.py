import os
import re
import jinja2
from collections import OrderedDict
from pypers.core.step import Step
from pypers.utils import utils

class FastQCReport(Step):
    """
    Create the fastqc final report
    """

    spec = {
        "name": "FastQCFinalReport",
        "version": "0.1",
        "descr": [
            "Create a FastQc report"
        ],
        "args":
        {
            "inputs": [
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
            ],
            "outputs": [
                {
                    "name"  : "final_report",
                    "type"  : "file",
                    "value" : "final_report.txt",
                    "descr" : "the output final reports",
                },
                {
                    "name"  : "failed_report",
                    "type"  : "file",
                    "value" : "failed_report.txt",
                    "descr" : "the failed reports",
                },
                {
                    "name"  : "html_report",
                    "type"  : "file",
                    "value" : "html_report.html",
                    "descr" : "the html reports",
                },
                {
                    "name"  : "csv_report",
                    "type"  : "file",
                    "value" : "csv_report.csv",
                    "descr" : "the csv reports",
                }
            ]
        }
    }


    def process(self):
        """
        Create a fastqc final report and a report containing only the failed
        """

        with open(self.final_report, "w")  as final_report_file, \
             open(self.failed_report, "w") as failed_report_file:
            summary_list = {}
            # >>Basic Statistics    pass
            # #MeasureValue
            # Filename      22_GGACTCCT-CCTAGAGT_L008_R2_001.fastq.gz
            # File type     Conventional base calls
            # Encoding      Sanger / Illumina 1.9
            # Total Sequences   2031309
            # Filtered Sequences    20313090
            # Sequence length       125
            # %GC           45
            # >>END_MODULE

            for i, filename in enumerate(self.detailed_reports):
                sample_id = ''
                with open(filename, "r") as fh:
                    for line in fh:
                        if line.startswith('Filename'):
                            sample_id = line.split('\t')[1]
                            sample_id = sample_id.replace('.gz', '')
                            sample_id = sample_id.replace('.fastq', '')
                            break

                    for line in fh:
                        if line.startswith('>>END_MODULE'):
                            break
                        cells = line.split('\t')
                        if not summary_list.has_key(sample_id):
                            summary_list[sample_id] = {'FastQ File': sample_id}
                        summary_list[sample_id]['report'] = self.html_reports[i]
                        summary_list[sample_id][cells[0]] = cells[1]

            for filename in self.summary_reports:
                with open(filename, "r") as su:
                    for line in su:
                        line = line.strip()
                        cells = line.split('\t')
                        sample_id = cells[2].replace('.gz', '').replace('.fastq', '')
                        if not summary_list.has_key(sample_id):
                            summary_list[sample_id] = {'FastQ File': sample_id}
                        summary_list[sample_id][cells[1]] = cells[0]

                    su.seek(0)
                    line = su.readline().replace("\n", "") + "     " + su.readline()
                    final_report_file.write(line)
                    #if there is a failed then append the line in the failed report
                    if line.find("FAIL") >= 0:
                        failed_report_file.write(line)

            csv_header = [
                'FastQ File',
                'Total Sequences',
                'Filtered Sequences',
                'Sequence length',
                '%GC',
                'Basic Statistics',
                'Per base sequence quality',
                'Per sequence quality scores',
                'Per base sequence content',
                'Per base GC content',
                'Per sequence GC content',
                'Per base N content',
                'Sequence Length Distribution',
                'Sequence Duplication Levels',
                'Overrepresented sequences',
                'Kmer Content'
            ]

        # sorting alpha-numerically
        convert_f = lambda x: int(x) if x.isdigit() else x.lower()
        alphanum_f = lambda key: [ convert_f(c) for c in re.split('([0-9]+)', key) ]

        ############
        # CSV Report
        ############
        with open(self.csv_report, "w")  as csv_fh:

            csv_fh.write(','.join(csv_header))
            csv_fh.write('\n')

            for sample_id in sorted(summary_list.keys(),
                                    key=alphanum_f):
                sample_results = summary_list[sample_id]

                vals = []

                for col in csv_header:
                    vals.append(sample_results[col])

                csv_fh.write(','.join(vals))
                csv_fh.write('\n')


        #############
        # HTML Report
        #############
        with open(self.html_report, "w")  as html_fh:
            code_root = os.path.abspath(os.path.dirname(__file__))
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(code_root))
            t = env.get_template('fastqcreport.html')
            html_fh.write(t.render(keys=csv_header,
                                   table=OrderedDict(sorted(summary_list.items(),
                                   key=lambda x: alphanum_f(x[0])))))
