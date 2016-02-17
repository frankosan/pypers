from pypers.core.step import Step
import os
import re
from datetime import datetime


class BamAutoQc(Step):
    """
    Run AutoQc against a bam file, parsing outputs from Qplot and bamcheck
    """

    spec = {
        'version' : '0.0.1',
        'descr'   : [
            'Run AutoQc against a bam file, parsing outputs from Qplot and bamcheck'
        ],
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_qplots',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input qplot file names'
                    },
                    {
                        'name'     : 'input_bamchecks',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input bamchek file names'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_files',
                        'type' : 'file',
                        'descr': 'output stats file name',
                    }
                ],
            'params'  : [
                    {
                      'name'    : 'min_target_percent',
                      'type'    : 'int',
                      'value'   : 65,
                    },
                    {
                      'name'    : 'min_mapped_bases_pct',
                      'type'    : 'int',
                      'value'   : 90,
                    },
                    {
                      'name'    : 'max_error_rate',
                      'type'    : 'int',
                      'value'   : 0.02,
                    },
                    {
                      'name'    : 'max_reads_duplicated_pct',
                      'type'    : 'int',
                      'value'   : 8,
                    },
                    {
                      'name'    : 'min_reads_paired_pct',
                      'type'    : 'int',
                      'value'   : 80,
                    }
            ]
        },
        'requirements' : {}
    }

    def __init__(self):
        super(BamAutoQc,self).__init__()

    def process(self):
        """
        Run the step as configured.
        """

        bam_name = os.path.basename(self.input_bamchecks).split('.')[0]
        self.output_files = bam_name + '.autoqc.txt'
        print 'Running auto QC for %s' % bam_name

        ofile = open(self.output_files,'w')
        autoqc_result = 'PASS'

        # Percentage Mapped to Target from qplot output
        target_mapped_pct = None
        try:
            with open(self.input_qplots) as qfile:
                for read in qfile:
                    target_mapped = re.match('TargetMapping\(\%\) *(.*)', read)
                    if target_mapped:
                        target_mapped_pct = float(target_mapped.group(1))
        except IOError,e:
            print 'Problem with qplot stats file [%s]:\n%s' % (self.input_qplots,e)

        if target_mapped_pct >= self.min_target_percent:
            res = 'PASS'
        else:
            res = 'FAIL'
            autoqc_result = 'FAIL'
        ofile.write('%s min_target_percent : %s (%s)\n' % (res, target_mapped_pct, self.min_target_percent))

        # BamCheck statistics
        error_rate = None
        total_bases = None
        bases_mapped = None
        mapped_bases_pct = None
        total_sequences = None
        reads_duplicated = None
        reads_duplicated_pct = None
        reads_paired = None
        reads_paired_pct = None

        try:
            with open(self.input_bamchecks) as bcfile:
                for read in bcfile:
                    error_rate_ln = re.match('SN\terror rate:\t(.*)$', read)
                    if error_rate_ln:
                        error_rate = float(error_rate_ln.group(1))

                    total_bases_ln = re.match('SN\ttotal length:\t(.*)$', read)
                    if total_bases_ln:
                        total_bases = total_bases_ln.group(1)

                    bases_mapped_ln = re.match('SN\tbases mapped:\t(.*)$', read)
                    if bases_mapped_ln:
                        bases_mapped = bases_mapped_ln.group(1)

                    total_seq_ln = re.match('SN\traw total sequences:\t(.*)$', read)
                    if total_seq_ln:
                        total_sequences = total_seq_ln.group(1)

                    reads_dup_ln = re.match('SN\treads duplicated:\t(.*)$', read)
                    if reads_dup_ln:
                        reads_duplicated = reads_dup_ln.group(1)

                    reads_paired_ln = re.match('SN\treads paired:\t(.*)$', read)
                    if reads_paired_ln:
                        reads_paired = reads_paired_ln.group(1)
        except IOError,e:
            print 'Problem with bamcheck file [%s]:\n%s' % (self.input_bamchecks,e)

        if (total_bases and bases_mapped) is not None:
            mapped_bases_pct = 100.*float(bases_mapped)/float(total_bases)
        if (total_sequences and reads_duplicated) is not None:
            reads_duplicated_pct = 100 * float(reads_duplicated) / float(total_sequences)
            print 'reads_duplicated_pct =',reads_duplicated_pct
        if (total_sequences and reads_paired) is not None:
            reads_paired_pct = 100 * float(reads_paired) / float(total_sequences)

        if error_rate < self.max_error_rate:
            res = 'PASS'
        else:
            res = 'FAIL'
            autoqc_result = 'FAIL'
        if error_rate is not None:
           error_rate_disp = '%.4f' % error_rate
        else:
           error_rate_disp = 'None'
        ofile.write('%s max_error_rate %s (%s)\n' % (res,error_rate_disp,self.max_error_rate))

        if mapped_bases_pct >= self.min_mapped_bases_pct:
            res = 'PASS'
        else:
            res = 'FAIL'
            autoqc_result = 'FAIL'
        if mapped_bases_pct is not None:
           mapped_bases_pct_disp = '%.3f' % mapped_bases_pct
        else:
           mapped_bases_pct_disp = 'None'
        ofile.write('%s min_mapped_bases_pct %s (%s)\n' % (res,mapped_bases_pct_disp,self.min_mapped_bases_pct))

        if reads_duplicated_pct < self.max_reads_duplicated_pct:
            res = 'PASS'
        else:
            res = 'FAIL'
            autoqc_result = 'FAIL'
        if reads_duplicated_pct is not None:
           reads_duplicated_pct_disp = '%.3f' % reads_duplicated_pct
        else:
           reads_duplicated_pct_disp = 'None'
        ofile.write('%s max_reads_duplicated_pct %s (%s)\n' % (res,reads_duplicated_pct_disp,self.max_reads_duplicated_pct))

        if reads_paired_pct >= self.min_reads_paired_pct:
            res = 'PASS'
        else:
            res = 'FAIL'
            autoqc_result = 'FAIL'
        if reads_paired_pct is not None:
           reads_paired_pct_disp = '%.3f' % reads_paired_pct
        else:
           reads_paired_pct_disp = 'None'
        ofile.write('%s min_reads_paired_pct %s (%s)\n' % (res,reads_paired_pct_disp,self.min_reads_paired_pct))

        ofile.write('RESULT : %s\n' % (autoqc_result))

        # add stats to summary file (in future releases this should be a database?)
        i = datetime.now()
        now = i.strftime('%Y/%m/%d %H:%M:%S')
        flds = (autoqc_result, bam_name, now,
                str(target_mapped_pct), error_rate_disp, mapped_bases_pct_disp,
                reads_duplicated_pct_disp, reads_paired_pct_disp)
        ofile.write('\t'.join(flds) + "\n")
        ofile.close()
