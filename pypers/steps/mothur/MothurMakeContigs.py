from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurMakeContigs(Mothur):

    spec = {
        'name'    : 'MothurMakeContigs',
        'version' : '20151106',
        'descr'   : [
            'Runs make.contigs with the file option to output a single fasta file from a list of paired fastq files'
        ],
        'url' : 'http://www.mothur.org/wiki/Make.contigs',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_list',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input filename for list of paired fastq files'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_fasta',
                        'type' : 'file',
                        'descr': 'output fasta filename'
                    },
                    {
                        'name' : 'output_groups',
                        'type' : 'file',
                        'descr': 'output groups filename'
                    }
                ],
            'params'  : [
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

        if type(self.input_list) != list:
            self.input_list = [self.input_list]

        for input_list in self.input_list:

            self.mk_links([input_list],self.output_dir)

            input_list = os.path.join(self.output_dir,os.path.basename(input_list))

            extra_params={'file':input_list}
            self.run_cmd('make.contigs',extra_params)

            output_root = os.path.splitext(os.path.basename(input_list))[0]
            self.output_fasta = os.path.join(self.output_dir,'%s.trim.contigs.fasta' % output_root)
            self.output_groups = os.path.join(self.output_dir,'%s.contigs.groups' % output_root) 

