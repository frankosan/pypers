from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurPcrSeqs(Mothur):

    spec = {
        'name'    : 'MothurPcrSeqs',
        'version' : '20151017',
        'descr'   : [
            'The pcr.seqs will trim sequences based on a variety of user-defined options.Currently we only trim based upon start and stop positions'
        ],
        'url' : 'www.mothur.org/wiki/Pcr.seqs',
        'args' : {
            'inputs'  : [
                ],
            'outputs' : [
                    {
                        'name' : 'output_fasta',
                        'type' : 'file',
                        'descr': 'output uniqued fasta filename'
                    }
                ],
            'params'  : [
              { 
                'name'     : 'fasta',
                'type'     : 'file',
                'descr'    : 'input fasta filename',
                'value': '/Public_data/microbiome/reference/silva.bacteria/silva.bacteria.fasta'
              },
              {
                'name' : 'start',
                'type' : 'int',
                'descr': 'trim up to this start position',
                'value': 6426
              },
              {
                'name' : 'end',
                'type' : 'int',
                'descr': 'trim from this end position',
                'value': 27654
              },
              {
                'name' : 'keepdots',
                'descr': 'keep the leading and trailing dots, default=false',
                'type' : 'boolean',
                'value': False
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
        self.mk_links([self.fasta],self.output_dir)

        self.fasta=os.path.join(self.output_dir,os.path.basename(self.fasta))
        self.run_cmd('pcr.seqs',{})

        self.output_fasta = re.sub('.fasta$','.pcr.fasta',self.fasta)

        if not os.path.exists(self.output_fasta):
            raise Exception('failed to create %s' % self.output_fasta)

