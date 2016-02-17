from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurCountSeqs(Mothur):
    """
    The count.seqs / make.table command counts the sequences represented by the representative
    sequence in a name file. If a group file is given, it will also provide the group count breakdown.
    This will generate a summary file called <root>.count_table
    """

    spec = {
        'name'    : 'MothurCountSeqs',
        'version' : '20150507',
        'descr'   : [
            'Ccounts the sequences represented by the representative sequence in a name file'
        ],
        'url' : 'www.mothur.org/wiki/Count.seqs',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_names',
                        'type'     : 'file',
                        'iterable' : True,
                        'required' : False,
                        'descr'    : 'input names filename'
                    },
                    {
                        'name'     : 'input_groups',
                        'type'     : 'file',
                        'iterable' : True,
                        'required' : False,
                        'descr'    : 'input groups filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_counts',
                        'type' : 'file',
                        'value'    : '*.count_table',
                        'descr': 'output count table filename'
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

        if type(self.input_names) != list:
            self.input_names = [self.input_names]
        if type(self.input_groups) != list:
            self.input_groups = [self.input_groups]

        for idx, input_names in enumerate(self.input_names):

            self.mk_links([input_names],self.output_dir)

            input_names = os.path.join(self.output_dir,os.path.basename(input_names))

            extra_params={'name':input_names}

            if self.input_groups[idx]:
                input_groups = os.path.join(self.output_dir,os.path.basename(self.input_groups[idx]))
                self.mk_links([self.input_groups[idx]],self.output_dir)
                extra_params['group'] = input_groups

            self.run_cmd('count.seqs',extra_params)

