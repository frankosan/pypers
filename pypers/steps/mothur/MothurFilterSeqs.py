from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurFilterSeqs(Mothur):
    """
    Removes columns from alignments based on a criteria defined by the user.
    This will generate a <root>.filter.fasta file (and a .filter file)
    """

    spec = {
        'name'    : 'MothurFilterSeqs',
        'version' : '20150508',
        'descr'   : [
            'Removes columns from alignments based on a criteria defined by the user'
        ],
        'url' : 'www.mothur.org/wiki/Filter.seqs',
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
                        'name' : 'output_filter_fasta',
                        'type' : 'file',
                        'descr': 'output filtered fasta filename'
                    }
                ],
            'params'  : [
              {
                'name'    : 'trump',
                'descr'   : 'remove a column if the trump character is found at that position in any sequence of the alignment',
                'type'    : 'str',
                'value' : '*'
              },
              {
                'name'    : 'soft',
                'descr'   : 'remove any column where the dominant base does not occur in at least a designated percentage of sequences',
                'type'    : 'int',
                'value' : 0
              },
              {
                'name'    : 'vertical',
                'descr'   : 'ignore any column that only contains gap characters',
                'type'    : 'boolean',
                'value' : True
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

            extra_params={'fasta':input_fasta}
            self.run_cmd('filter.seqs',extra_params)

            self.output_filter_fasta = re.sub('.align$','.filter.fasta',input_fasta)

