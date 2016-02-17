from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurChimeraUchime(Mothur):
    """
    Reads a fasta file and reference file and outputs potentially chimeric sequences
    """

    spec = {
        'name'    : 'MothurChimeraUchime',
        'version' : '20150511',
        'descr'   : [
            'Reads a fasta file and reference file and outputs potentially chimeric sequences'
        ],
        'url' : 'www.mothur.org/wiki/Chimera.uchime',
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
                        'name' : 'output_chimeras_fasta',
                        'type' : 'file',
                        'descr': 'output chimeras fasta filename'
                    },
                    {
                        'name' : 'output_accnos',
                        'type' : 'file',
                        'descr': 'output chimera accnos'
                    }
                ],
            'params'  : [
              {
                'name'    : 'abskew',
                'descr'   : 'minimum abundance skew',
                'type'    : 'float',
                'value' : 1.9,
                'required': False
              },
              {
                'name'    : 'chimealns',
                'descr'   : 'create file containing multiple alignments of query sequences to parents in human readable format',
                'type'    : 'boolean',
                'value' : False,
                'required': False
              },
              {
                'name'    : 'minh',
                'descr'   : 'mininum score to report chimera',
                'type'    : 'float',
                'value' : 0.3,
                'required': False
              },
              {
                'name'    : 'mindiv',
                'descr'   : 'minimum divergence ratio',
                'type'    : 'float',
                'value' : 0.5,
                'required': False
              },
              {
                'name'    : 'xn',
                'descr'   : 'weight of a no vote',
                'type'    : 'float',
                'value' : 8.0,
                'required': False
              },
              {
                'name'    : 'dn',
                'descr'   : 'pseudo-count prior on number of no votes',
                'type'    : 'float',
                'value' : 1.4,
                'required': False
              },
              {
                'name'    : 'xa',
                'descr'   : 'weight of an abstain vote',
                'type'    : 'float',
                'value' : 1.0,
                'required': False
              },
              {
                'name'    : 'chunks',
                'descr'   : 'number of chunks to extract from the query sequence when searching for parents',
                'type'    : 'int',
                'value' : 4,
                'required': False
              },
              {
                'name'    : 'minchunk',
                'descr'   : 'minimum length of a chunk',
                'type'    : 'int',
                'value' : 64,
                'required': False
              },
             {
                'name'    : 'minchunk',
                'descr'   : 'minimum length of a chunk',
                'type'    : 'int',
                'value' : 64,
                'required': False
              },
              {
                'name'    : 'idsmoothwindow',
                'descr'   : 'length of id smoothing window',
                'type'    : 'int',
                'value' : 32,
                'required': False
              },
              {
                'name'    : 'dereplicate',
                'descr'   : 'if False: if one group finds the sequence to be chimeric, then all groups find it to be chimeric',
                'type'    : 'boolean',
                'value' : False,
                'required': False
              },
              {
                'name'    : 'maxp',
                'descr'   : 'maximum number of candidate parents to consider',
                'type'    : 'int',
                'value' : 2,
                'required': False
              },
              {
                'name'    : 'skipgaps',
                'descr'   : 'do not count columns containing gaps as diffs',
                'type'    : 'boolean',
                'value' : True,
                'required': False
              },
              {
                'name'    : 'skipgaps2',
                'descr'   : 'do not count columns immediatly adjacent to gap columns as diffs',
                'type'    : 'boolean',
                'value' : True,
                'required': False
              },
              {
                'name'    : 'minlen',
                'descr'   : 'minimum unaligned sequence length',
                'type'    : 'int',
                'value' : 10,
                'required': False
              },
             {
                'name'    : 'maxlen',
                'descr'   : 'maximum unaligned sequence length',
                'type'    : 'int',
                'value' : 10000,
                'required': False
              },
              {
                'name'    : 'ucl',
                'descr'   : 'use local-X alignments',
                'type'    : 'boolean',
                'value' : False,
                'required': False
              },
              {
                'name'    : 'queryfract',
                'descr'   : 'minimum fraction of the query sequence that must be covered by a local-X alignment',
                'type'    : 'float',
                'value' : 0.5,
                'required': False
              },
              {
                'name' : 'processors',
                'descr': 'number of processors to request',
                'type' : 'int',
                'value': 8,
                'readonly' : True
              }
            ]
        },
        'requirements' : {
            'cpus' : '8',
            'memory' : '40'
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

            self.run_cmd('chimera.uchime',extra_params)

            output_root = re.sub('.fasta$','',input_fasta)
            self.output_chimeras_fasta = output_root + '.uchime.chimeras'
            self.output_accnos = output_root + '.uchime.accnos'

