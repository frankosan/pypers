from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurAlignSeqs(Mothur):
    """
   The align.seqs command aligns a user-supplied fasta-formatted candidate
   sequence file to a user-supplied fasta-formatted template alignment.
    """

    spec = {
        'name'    : 'MothurAlignSeqs',
        'version' : '20150508',
        'descr'   : [
            'Aligns a user-supplied fasta-formatted candidate sequence file to a user-supplied fasta-formatted template alignment'
        ],
        'url' : 'www.mothur.org/wiki/Align.seqs',
        'args' : {
            'inputs'  : [
                    {
                       'name'     : 'input_fasta',
                       'type'     : 'file',
                       'iterable' : True,
                       'descr'    : 'input fasta filename'
                    },
                    {
                       'name'  : 'reference',
                       'descr' : 'reference sequence file',
                       'type'  : 'file',
                       'value' : '/Public_data/microbiome/reference/silva.bacteria/silva.bacteria.fasta'
                     }
                ],
            'outputs' : [
                    {
                        'name' : 'output_align',
                        'type' : 'file',
                        'descr': 'output aligned fasta filename'
                    },
                    {
                        'name' : 'output_align_report',
                        'type' : 'file',
                        'descr': 'output alignment report filename'
                    }
                ],
            'params'  : [
              {
                'name'    : 'search',
                'descr'   : 'choose method of finding the template sequence',
                'type'    : 'enum',
                'options' : [ 'kmer', 'blast', 'suffix' ],
                'value' : 'kmer',
              },
              {
                'name'    : 'ksize',
                'descr'   : 'size of the kmers used in the kmer search',
                'type'    : 'int',
                'value' : 8,
              },
              {
                'name'    : 'align',
                'descr'   : 'choose alignment method',
                'type'    : 'enum',
                'options' : [ 'needleman', 'gotoh', 'blast', 'noalign' ],
                'value' : 'needleman',
              },
              {
                'name'    : 'match',
                'descr'   : 'reward for a match',
                'type'    : 'int',
                'value' : 1,
              },
              {
                'name'    : 'mismatch',
                'descr'   : 'penalty for a mismatch',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'gapopen',
                'descr'   : 'penalty for opening a gap',
                'type'    : 'int',
                'value' : -5,
              },
              {
                'name'    : 'gapextend',
                'descr'   : 'penalty for extending a gap',
                'type'    : 'int',
                'value' : -2,
              },
              {
                'name'    : 'flip',
                'descr'   : 'try the reverse complement of a sequence if the sequence is deemed bad',
                'type'    : 'boolean',
                'value' : True,
              },
              {
                'name'    : 'threshold',
                'descr'   : 'cutoff at which an alignment is deemed bad',
                'type'    : 'int',
                'value' : 0.5,
              },
              {
                'name'    : 'save',
                'descr'   : 'save reference sequences in memory',
                'type'    : 'boolean',
                'value' : False,
              }
            ]
        },
        'requirements' : {
            'cpus' : "8"
        }
    }


    def process(self):
        """
        Create the necessary input file links and run mothur command
        """

        if type(self.input_fasta) != list:
            self.input_fasta = [self.input_fasta]
        if type(self.reference) != list:
            self.reference = [self.reference]

        for idx, input_fasta in enumerate(self.input_fasta):

            self.mk_links([input_fasta],self.output_dir)

            input_fasta = os.path.join(self.output_dir,os.path.basename(input_fasta))

            extra_params={'fasta':input_fasta, 'reference' : self.reference[idx]}
            self.run_cmd('align.seqs',extra_params)

            output_root = re.sub('.fasta$','',input_fasta)
            self.output_align = output_root + '.align'
            self.output_align_report = output_root + '.align.report'

            if not os.path.exists(self.output_align):
                raise Exception('failed to create %s' % self.output_align)
