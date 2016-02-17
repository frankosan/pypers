from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurRemoveLineage(Mothur):
    """
    Reads a taxonomy file and sequence data and generates sequence files not containing that taxonomy
    """

    spec = {
        'name'    : 'MothurRemoveLineage',
        'version' : '20150512',
        'descr'   : [
            'Reads a taxonomy file and sequence data and generates sequence files not containing that taxonomy'
        ],
        'url' : 'www.mothur.org/wiki/Remove.lineage',
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
                        'descr'    : 'input names filename'
                    },
                    {
                        'name'     : 'input_groups',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input groups filename'
                    },
                    {
                        'name'     : 'input_taxonomy',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input taxonomy filename'
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
                    },
                    {
                        'name' : 'output_taxonomy',
                        'type' : 'file',
                        'descr': 'output taxonomy filename'
                    }
                ],
            'params'  : [
              {
                'name'    : 'label',
                'descr'   : 'specific label to analyze in the input',
                'type'    : 'str',
                'value' : ''
              },
              {
                'name'    : 'dups',
                'descr'   : 'remove all sequences in a names file line that contains any sequence in the taxon',
                'type'    : 'boolean',
                'value' : True
              },
              {
                'name'    : 'taxon',
                'descr'   : 'the name of the taxon to look for',
                'type'    : 'str',
                'value' : 'Mitochondria-Chloroplast-Archaea-Eukaryota-unknown'
              }
            ]
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
        if type(self.input_groups) != list:
            self.input_groups = [self.input_groups]
        if type(self.input_taxonomy) != list:
            self.input_taxonomy = [self.input_taxonomy]

        for idx, input_fasta in enumerate(self.input_fasta):

            self.mk_links([input_fasta],self.output_dir)
            self.mk_links([self.input_names[idx]],self.output_dir)
            self.mk_links([self.input_groups[idx]],self.output_dir)
            self.mk_links([self.input_taxonomy[idx]],self.output_dir)

            input_fasta = os.path.join(self.output_dir,os.path.basename(input_fasta))
            input_names = os.path.join(self.output_dir,os.path.basename(self.input_names[idx]))
            input_groups = os.path.join(self.output_dir,os.path.basename(self.input_groups[idx]))
            input_taxonomy = os.path.join(self.output_dir,os.path.basename(self.input_taxonomy[idx]))

            extra_params={'taxonomy':input_taxonomy,'fasta':input_fasta,'name':input_names,'group':input_groups}
            self.run_cmd('remove.lineage',extra_params)

            self.output_fasta = re.sub('.fasta$','.pick.fasta',input_fasta)
            self.output_names = re.sub('.names$','.pick.names',input_names)
            self.output_groups = re.sub('.groups$','.pick.groups',input_groups)
            self.output_taxonomy= re.sub('.taxonomy$','.taxonomy',input_taxonomy)

