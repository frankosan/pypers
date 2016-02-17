from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurRemoveSeqs(Mothur):
    """
    Removes sequences in a fasta file using an accnos file
    """

    spec = {
        'name'    : 'MothurRemoveSeqs',
        'version' : '20150511',
        'descr'   : [
            'Removes sequences in a fasta file using an accnos file'
        ],
        'url' : 'www.mothur.org/wiki/Remove.seqs',
        'args' : {
            'inputs'  : [
                    { 
                        'name'     : 'input_accnos',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input accnos filename'
                    },
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
                        'descr'    : 'input names filename'
                    },
                    { 
                        'name'     : 'input_groups',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input groups filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_fasta',
                        'type' : 'file',
                        'descr': 'output fasta filename'
                    },
                    {
                        'name' : 'output_names',
                        'type' : 'file',
                        'descr': 'output names filename'
                    },
                    {
                        'name' : 'output_groups',
                        'type' : 'file',
                        'descr': 'output groups filename'
                    }
                ],
            'params'  : [
              {
                'name'    : 'dups',
                'descr'   : 'remove all sequences in a line of the names file if any sequence in that line is in the .accnos file',
                'type'    : 'boolean',
                'value' : True
              }
            ]
        },
        'requirements' : {}
    }

    
    def process(self):
        """
        Create the necessary input file links and run mothur command
        """

        if type(self.input_accnos) != list:
            self.input_accnos = [self.input_accnos]
        if type(self.input_fasta) != list:
            self.input_fasta = [self.input_fasta]
        if type(self.input_names) != list:
            self.input_names = [self.input_names]
        if type(self.input_groups) != list:
            self.input_groups = [self.input_groups]

        for idx, input_accnos in enumerate(self.input_accnos):

            self.mk_links([input_accnos],self.output_dir)
            self.mk_links([self.input_fasta[idx]],self.output_dir)
            self.mk_links([self.input_names[idx]],self.output_dir)
            self.mk_links([self.input_groups[idx]],self.output_dir)

            input_accnos = os.path.join(self.output_dir,os.path.basename(input_accnos))
            input_fasta = os.path.join(self.output_dir,os.path.basename(self.input_fasta[idx]))
            input_names = os.path.join(self.output_dir,os.path.basename(self.input_names[idx]))
            input_groups = os.path.join(self.output_dir,os.path.basename(self.input_groups[idx]))

            extra_params={'accnos':input_accnos,'fasta':input_fasta,'name':input_names,'group':input_groups}
            self.run_cmd('remove.seqs',extra_params)

            self.output_fasta = re.sub('.fasta$','.pick.fasta',input_fasta)
            self.output_names = re.sub('.names$','.pick.names',input_names)
            self.output_groups = re.sub('.groups$','.pick.groups',input_groups)

