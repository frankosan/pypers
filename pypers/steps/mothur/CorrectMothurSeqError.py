import os
import re
from pypers.core.step import FunctionStep
from itertools import izip


class CorrectMothurSeqError(FunctionStep):
    spec = {
        "version": "0.1",
        "descr": [
            """
            Implement in python the Miseq SOP Error rate correction R 'jujitsu' (ie kludge) to adjust for count table
            http://www.mothur.org/wiki/MiSeq_SOP#Assessing_error_rates
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "error_summary",
                    "type"  : "file",
                    "descr"    : "the error summary file output from seq.error",
                },
                {
                    "name"     : "count_table",
                    "type"  : "file",
                    "descr"    : "the input counts table",
                },
            ],
            "outputs": [
                {
                    "name"  : "err_rate",
                    "type"  : "float",
                    "descr" : "output adjusted error rate",
                }
            ]
        }
    }

    def process(self):

        tot_mismatches = 0
        tot_bases = 0

        es_fh = open(self.error_summary,'r')
        ct_fh = open(self.count_table,'r')

        for es_line, ct_line in izip(es_fh, ct_fh):

            if es_line.startswith('query'):
                continue

            es_flds = es_line.split()
            ct_flds = ct_line.split()

            if es_flds[0] != ct_flds[0]:
                raise Exception('error.summary, count_table readname mismatch, %s, %s' % (es_flds[0],ct_flds[0]))

            if int(es_flds[40]) == 1: # non chimeric
                group_count = int(ct_flds[2])
                tot_mismatches += int(es_flds[37]) * group_count
                tot_bases += int(es_flds[38]) * group_count

        es_fh.close()
        ct_fh.close()

        self.err_rate =  float(tot_mismatches) / tot_bases

        self.log.info('Recalculated error rate: %.6f' % self.err_rate)

