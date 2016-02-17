from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json

class MothurSffinfo(Mothur):
    """
    The mothur sffinfo command extracts sequence reads from a .sff file and
    generate a .fasta, a .flow and a .qual file.
    """

    spec = {
        'name'    : 'MothurSffinfo',
        'version' : '20150502',
        'descr'   : [
            'Runs mothur sffinfo to generate .fasta, a .flow and a .qual files from a .sff file'
        ],
        'url' : 'www.mothur.org/wiki/Sffinfo',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_sff',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input sff filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_fasta',
                        'type' : 'file',
                        'descr': 'output fasta filename'
                    },
                    {
                        'name' : 'output_flow',
                        'type' : 'file',
                        'descr': 'output flow filename'
                    },
                    {
                        'name' : 'output_qual',
                        'type' : 'file',
                        'descr': 'output qual filename'
                    }

                ],
            'params'  : [
                    {
                        'name' : 'trim',
                        'type' : 'boolean',
                        'descr': 'Trim sequences and quality scores to the clipQualLeft and clipQualRight values',
                        'value': 'true'
                    },
                    {
                        'name' : 'bdiffs',
                        'type' : 'int',
                        'descr': 'maximum number of differences to the barcode sequence',
                        'value': 0
                    },
                    {
                        'name' : 'pdiffs',
                        'type' : 'int',
                        'descr': 'maximum number of differences to the primer sequence',
                        'value': 0
                    },
                    {
                        'name' : 'ldiffs',
                        'type' : 'int',
                        'descr': 'maximum number of differences to the linker sequence',
                        'value': 0
                    },
                    {
                        'name' : 'sdiffs',
                        'type' : 'int',
                        'descr': 'maximum number of differences to the spacer sequence',
                        'value': 0
                    },
                    {
                        'name' : 'tdiffs',
                        'type' : 'int',
                        'descr': 'maximum total number of differences to the barcode, primer, linker and spacer sequences',
                        'value': 0
                    },
                ]
        },
        'requirements' : {}
    }

    def process(self):
        """
        Create the necessary input file links and run mothur command
        """

        if type(self.input_sff) != list:
            self.input_sff = [self.input_sff]

        for ifile in self.input_sff:

            self.mk_links([ifile],self.output_dir)
            input_sff = os.path.join(self.output_dir,os.path.basename(ifile))

            extra_params={'sff':input_sff,'qfile':'true','flow':'true'}
            self.run_cmd('sffinfo',extra_params)

            output_root = os.path.splitext(input_sff)[0]
            self.output_fasta = output_root + '.fasta'
            self.output_qual = output_root + '.qual'
            self.output_flow = output_root + '.flow'

