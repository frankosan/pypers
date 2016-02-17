from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurPreCluster(Mothur):

    spec = {
        'name'    : 'MothurPreCluster',
        'version' : '20151028',
        'descr'   : [
            'Runs the mothur pre.cluster command to remove seqs that are likely due to sequencing errors'
        ],
        'url' : 'www.mothur.org/wiki/Pre.cluster',
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
                        'name'     : 'input_groups',
                        'type'     : 'file',
                        'iterable' : True,
                        'required' : False,
                        'descr'    : 'input groups filename'
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
                        'value'    : '*.precluster.fasta',
                        'descr': 'output fasta filename'
                    },
                    {
                        'name' : 'output_names',
                        'type' : 'file',
                        'required' : False,
                        'descr': 'output names filename'
                    },
                    {
                        'name' : 'output_groups',
                        'type' : 'file',
                        'required' : False,
                        'descr': 'output groups filename'
                    },
                    {
                        'name' : 'output_counts',
                        'type' : 'file',
                        'required' : False,
                        'descr': 'output counts filename'
                    }
                ],
            'params'  : [
              {
                'name'    : 'diffs',
                'descr'   : 'remove sequences that are within this number of mismatches',
                'type'    : 'int',
                'value' : 2
              },
              {
                'name'    : 'topdown',
                'descr'   : 'cluster from largest abundance to smallest',
                'type'    : 'str',
                'value' : 'T'
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
        if type(self.input_groups) != list:
            self.input_groups = [self.input_groups]
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

            if self.input_groups[idx]:
                input_groups = os.path.join(self.output_dir,os.path.basename(self.input_groups[idx]))
                self.mk_links([self.input_groups[idx]],self.output_dir)
                extra_params['group'] = input_groups

            if self.input_counts[idx]:
                input_counts = os.path.join(self.output_dir,os.path.basename(self.input_counts[idx]))
                self.mk_links([self.input_counts[idx]],self.output_dir)
                extra_params['count'] = input_counts

            self.run_cmd('pre.cluster',extra_params)

            output_root = os.path.splitext(input_fasta)[0]

            if self.input_names[idx]:
                self.output_good_names = output_root + '.precluster.names'
            if self.input_groups[idx]:
                self.output_good_groups = output_root + '.precluster.groups'
            if self.input_counts[idx]:
                self.output_good_counts = output_root + '.precluster.count_table'

