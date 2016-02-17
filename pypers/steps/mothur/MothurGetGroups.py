from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurGetGroups(Mothur):
    """
    The get.groups command selects sequences from a specific group or set of groups from the following file types: fasta, name, group, list, taxonomy.
    """

    spec = {
        'name'    : 'MothurGetGroups',
        'version' : '20151106',
        'descr'   : [
            'Selects sequences for a specific group or set of groups, currently we only use this to create a counts file for error estimating'
        ],
        'url' : 'www.mothur.org/wiki/Get.groups',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_fasta',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input fasta filename'
                    },
                    {
                        'name'     : 'input_counts',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input counts filename'
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
                'name' : 'groups',
                'type' : 'str',
                'descr': 'Group on which to select',
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
        if type(self.input_counts) != list:
            self.input_counts = [self.input_counts]

        for idx, input_fasta in enumerate(self.input_fasta):

            self.mk_links([input_fasta],self.output_dir)
            self.mk_links([self.input_counts[idx]],self.output_dir)

            input_fasta = os.path.join(self.output_dir,os.path.basename(input_fasta))
            input_counts = os.path.join(self.output_dir,os.path.basename(self.input_counts[idx]))

            groups = self.groups.replace("-","\-") # need to escape hiphens in groups name param

            extra_params={'fasta':input_fasta, 'groups':groups, 'count':input_counts}
            self.run_cmd('get.groups',extra_params)

            self.output_fasta =  re.sub('.fasta$','.pick.fasta',input_fasta)
            self.output_counts =  re.sub('.count_table$','.pick.count_table',input_counts)

