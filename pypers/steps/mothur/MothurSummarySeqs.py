from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re
import glob

class MothurSummarySeqs(Mothur):
    """
    Summarizes the quality of sequences in an unaligned or aligned fasta-formatted sequence file.
    """

    spec = {
        'name'    : 'MothurSummarySeqs',
        'version' : '20150512',
        'descr'   : [
            'Summarizes the quality of sequences in an unaligned or aligned fasta-formatted sequence file'
        ],
        'url' : 'www.mothur.org/wiki/Summary.seqs',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_fasta',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input fasta filename'
                    },
                    {
                        'name'     : 'input_names',
                        'type'     : 'file',
                        'iterable' : True,
                        'required' : False,
                        'descr'    : 'input names filename'
                    },
                    {
                        'name'     : 'input_counts',
                        'type'     : 'file',
                        'iterable' : True,
                        'required' : False,
                        'descr'    : 'input counts filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_summary',
                        'type' : 'file',
                        'value'    : '*.summary',
                        'descr': 'output summary filename'
                    },
                    {
                        'name' : 'output_log',
                        'type' : 'file',
                        'value'    : '*.log.txt',
                        'descr': 'output summary logfile with tile summary table'
                    }
                ]
        },
        'requirements' : {
            'cpus' : '8'
        }
    }


    def process(self):
        """
        Create the necessary input file links and run mothur command
        """

        if type(self.input_fasta) != list:
            self.input_fasta = [self.input_fasta]
        if type(self.input_names) != list:
            self.input_names = [self.input_names]
        if type(self.input_counts) != list:
            self.input_counts = [self.input_counts]

        for idx, input_fasta in enumerate(self.input_fasta):

            self.mk_links([input_fasta],self.output_dir)

            input_fasta = os.path.join(self.output_dir,os.path.basename(input_fasta))

            extra_params={'fasta':input_fasta}

            if self.input_names[idx]:
                input_names = os.path.join(self.output_dir,os.path.basename(self.input_names[idx]))
                self.mk_links([self.input_names[idx]],self.output_dir)
                extra_params['name'] = input_names

            if self.input_counts[idx]:
                input_counts = os.path.join(self.output_dir,os.path.basename(self.input_counts[idx]))
                self.mk_links([self.input_counts[idx]],self.output_dir)
                extra_params['count'] = input_counts

            self.run_cmd('summary.seqs',extra_params)

