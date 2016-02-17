from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurUniqueSeqs(Mothur):
    """
    The unique.seqs command returns only the unique sequences found in a fasta-formatted sequence file and a file that indicates those sequences that are identical to the reference sequence
    """

    spec = {
        'name'    : 'MothurUniqueSeqs',
        'version' : '20150507',
        'descr'   : [
            'Creates fasta file containing only  unique sequences and names file of sequence names identical to the reference'
        ],
        'url' : 'www.mothur.org/wiki/Unique.seqs',
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
                        'name' : 'output_fasta',
                        'type' : 'file',
                        'value'    : '*.unique.fasta',
                        'descr': 'output uniqued fasta filename'
                    },
                    {
                        'name' : 'output_names',
                        'type' : 'file',
                        'descr': 'output uniqued names filename'
                    },
                    {
                        'name' : 'output_counts',
                        'type' : 'file',
                        'required' : False,
                        'descr': 'output counts filename'
                    }
                ],
        },
        'requirements' : {}
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

            self.run_cmd('unique.seqs',extra_params)

            # Names file created even if no input names provided, but will be named differently
            output_root = os.path.splitext(input_fasta)[0]
            if self.input_names[idx]:
                self.output_names = output_root + '.unique.names'
            else:
                self.output_names = output_root + '.names'

            if self.input_counts[idx]:
                self.output_counts = output_root + '.unique.count_table'
