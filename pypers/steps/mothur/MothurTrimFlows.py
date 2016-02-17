from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json

class MothurTrimFlows(Mothur):
    """
    The trim.flows command will allow you to partition your flowgram data by sample based
    on the barcode, trim the flows to a specified length range, and cull
    sequences that are too short or have too many mismatches to barcodes and primers.
    """

    spec = {
        'name'    : 'MothurTrimFlows',
        'version' : '20150504',
        'descr'   : [
            'Trim the flows to a specified length range, remove sequences that are too short or have too many barcode mismatches'
        ],
        'url' : 'www.mothur.org/wiki/Trim.flows',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_flow',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input flow filename'
                    },
                    {
                        'name'     : 'input_oligos',
                        'type'     : 'file',
                        'iterable' : False,
                        'descr'    : 'input oligos filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_trim',
                        'type' : 'file',
                        'descr': 'output trimmed flows filename'
                    },
                    {
                        'name' : 'output_scrap',
                        'type' : 'file',
                        'descr': 'output scrapped flows filename'
                    },
                    {
                        'name' : 'output_list',
                        'type' : 'file',
                        'descr': 'output flow files list filename'
                    }

                ],
            'params'  : [
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
                        'value': 2
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
                    {
                        'name' : 'minflows',
                        'type' : 'int',
                        'descr': 'minimum number of flows that each sequence must contain',
                        'value': 450
                    },
                    {
                        'name' : 'maxflows',
                        'type' : 'int',
                        'descr': 'maximum number of flows that each sequence can contain',
                        'value': 450
                    },
                    {
                        'name' : 'signal',
                        'type' : 'int',
                        'descr': 'signal intensity cutoff',
                        'value': 0.5
                    },
                    {
                        'name' : 'noise',
                        'type' : 'int',
                        'descr': 'noise intensity cutoff',
                        'value': 0.7
                    },
                    {
                        'name' : 'maxhomop',
                        'type' : 'int',
                        'descr': 'maximum homopolymer length',
                        'value': 9
                    },
                    {
                        'name' : 'order',
                        'type' : 'str',
                        'descr': 'flow order, Default=A meaning flow order of TACG',
                        'value': 'A'
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

        if type(self.input_flow) != list:
            self.input_flow = [self.input_flow]

        self.mk_links([self.input_oligos],self.output_dir)

        for ifile in self.input_flow:

            self.mk_links([ifile],self.output_dir)
            input_flow = os.path.join(self.output_dir,os.path.basename(ifile))
            input_oligos = os.path.join(self.output_dir,os.path.basename(self.input_oligos))

            extra_params={'flow':input_flow, 'oligos':input_oligos}
            self.run_cmd('trim.flows',extra_params)

            output_root = os.path.splitext(input_flow)[0]
            self.output_trim = output_root + '.trim.flow'
            self.output_scrap = output_root + '.scrap.flow'
            self.output_list = output_root + '.flow.files'

