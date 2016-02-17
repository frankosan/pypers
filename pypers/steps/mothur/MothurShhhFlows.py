from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurShhhFlows(Mothur):
    """
    Run mothur shhh.flows  to correct flowgrams, usingb the trim.flows flow.files as input
    Generates the following
      * .shhh.fasta - idealized fasta sequence data containing the de-noised sequences
      * .shhh.names - a names file that maps each read to an idealized fasta sequence
      * .shhh.qual - quality scores on a 100 point scale and should not be confused with the more conventional phred scores.
      * .shhh.groups - a group file indicating the group that each sequence in the names file comes from
      * .shhh.counts - a summary of the original translated sequences sorted with their idealized sequence counterpart

      Plus concatenated .shhh.fasta and .shhh.names files that can be used as input to trim.seqs. We only use the last two files.

    """

    spec = {
        'name'    : 'MothurShhhFlows',
        'version' : '20150507',
        'descr'   : [
            'Runs mothur shhh.flows to correct flowgrams using the PyroNoise algorithm'
        ],
        'url' : 'www.mothur.org/wiki/Shhh.flows',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'flow_file',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input flow.files file from trim.flows step'
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
                    }
                ],
            'params'  : [
                  {
                    'name'    : 'lookup',
                    'descr'   : 'lookup file required to run shhh.flows',
                    'type'    : 'file',
                    'value' : '/Public_data/microbiome/reference/LookUp_Titanium.pat'
                  },
                  {
                    'name'    : 'maxiter',
                    'descr'   : 'maximum iterations to run',
                    'type'    : 'int',
                    'value' : 1000,
                  },
                  {
                    'name'    : 'mindelta',
                    'descr'   : 'how much change in the flowgram correction is allowed before declaring job done',
                    'type'    : 'str',
                    'value' : '0.000001', # Keep as text to prevent conversion to exponential notation
                  },
                  {
                    'name'    : 'cutoff',
                    'descr'   : 'initial clustering step to seed the expectation-maximizaton step',
                    'type'    : 'int',
                    'value' : 0.01,
                  },
                  {
                    'name'    : 'sigma',
                    'descr'   : 'dispersion of the data in the expectation-maximization step',
                    'type'    : 'int',
                    'value' : 60.0,
                  },
                  {
                    'name'    : 'order',
                    'descr'   : 'select the flow order',
                    'type'    : 'enum',
                    'value' : 'A',
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

        if type(self.flow_file) != list:
            self.flow_file = [self.flow_file]

        for ifile in self.flow_file:

            self.mk_links([ifile],self.output_dir)
            in_flow_file = os.path.join(self.output_dir,os.path.basename(ifile))

            extra_params={'file':in_flow_file}
            self.run_cmd('shhh.flows',extra_params)

            output_root = re.sub('.flow.files$','',in_flow_file)
            self.output_fasta = output_root + '.shhh.fasta'
            self.output_names = output_root + '.shhh.names'

