from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurSeqError(Mothur):

    spec = {
        'name'    : 'MothurSeqError',
        'version' : '20151109',
        'descr'   : [
            'The seq.error command reads a query alignment file and a reference alignment file to measure the error rates'
        ],
        'url' : 'http://www.mothur.org/wiki/Seq.error',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_fasta',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input fasta filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_fasta',
                        'type' : 'file',
                        'descr': 'output fasta filename'
                    },
                    {
                        'name' : 'output_counts',
                        'type' : 'file',
                        'descr': 'output counts filename'
                    }
                ],
            'params'  : [
              {
                'name' : 'aligned',
                'type' : 'str',
                'descr': 'define whether seq is aligned',
                'value' : 'F',
                'readonly': True
              },
              {
                'name' : 'reference',
                'type' : 'file',
                'descr': 'the trimmed sequences used in the mock community',
                'value' : '/pypers/develop/ref/mothur/mock_seqs.V4.ng.fasta',
                'readonly': True
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

        for input_fasta in self.input_fasta:

            self.mk_links([input_fasta],self.output_dir)

            input_fasta = os.path.join(self.output_dir,os.path.basename(input_fasta))

            extra_params={'fasta':input_fasta, 'aligned':self.aligned, 'reference':self.reference}
            
            self.run_cmd('seq.error',extra_params)

            self.output_fasta =  re.sub('.fasta$','.pick.fasta',input_fasta)
            self.output_counts =  re.sub('.count_table$','.pick.count_table',input_counts)

