from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurClassifySeqs(Mothur):
    """
    Aligns sequences to a taxonomy
    """

    spec = {
        'name'    : 'MothurClassifySeqs',
        'version' : '20150512',
        'descr'   : [
            'Aligns sequences to a taxonomy'
        ],
        'url' : 'www.mothur.org/wiki/Classify.seqs',
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
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_summary',
                        'type' : 'file',
                        'descr': 'output summary filename'
                    },
                    {
                        'name' : 'output_taxonomy',
                        'type' : 'file',
                        'descr': 'output taxonomy filename'
                    }
                ],
            'params'  : [
              {
                'name'    : 'taxonomy',
                'descr'   : 'taxonomy outline to assign the sequences to',
                'type'    : 'file',
                'rdir'    : '/Public_data/microbiome/reference/',
                'value' : '/Public_data/microbiome/reference/trainset9_032012.pds.tax',
                'required': False
              },
              {
                'name'    : 'reference',
                'descr'   : 'reference sequence',
                'type'    : 'file',
                'rdir'    : '/Public_data/microbiome/reference',
                'value' : '/Public_data/microbiome/reference/trainset9_032012.pds.fasta',
                'required': False
              },
              {
                'name'    : 'search',
                'descr'   : 'nearest neighbour search method',
                'type'    : 'enum',
                'options' : [ 'kmer', 'blast', 'suffix', 'distance', 'align' ],
                'value' : 'kmer',
                'required': False
              },
              {
                'name'    : 'ksize',
                'descr'   : 'kmer search method parameter',
                'type'    : 'int',
                'value' : 8,
                'required': False
              },
              {
                'name'    : 'method',
                'descr'   : 'method for finding the taxonomy of a given query sequence',
                'type'    : 'enum',
                'options' : [ 'wang', 'knn', 'zap' ],
                'value' : 'wang',
                'required': False
              },
              {
                'name'    : 'match',
                'descr'   : 'blast search: reward for matching bases',
                'type'    : 'int',
                'value' : 1,
                'required': False
              },
              {
                'name'    : 'mismatch',
                'descr'   : 'blast search: penalty for mismatching bases',
                'type'    : 'int',
                'value' : -1,
                'required': False
              },
              {
                'name'    : 'gapopen',
                'descr'   : 'blast search: penalty for opening a gap',
                'type'    : 'int',
                'value' : -2,
                'required': False
              },
              {
                'name'    : 'gapextend',
                'descr'   : 'blast search: penalty for extending a gap',
                'type'    : 'int',
                'value' : -1,
                'required': False
              },
              {
                'name'    : 'cutoff',
                'descr'   : 'minimum bootstrap value for a taxonomic assignment',
                'type'    : 'int',
                'value' : 80,
                'required': False
              },
              {
                'name'    : 'probs',
                'descr'   : 'print bootstrap values together with taxonomic assignment',
                'type'    : 'boolean',
                'value' : True,
                'required': False
              },
              {
                'name'    : 'iters',
                'descr'   : 'iterations to do when calculating the bootstrap confidence score',
                'type'    : 'int',
                'value' : 100,
                'required': False
              },
              {
                'name'    : 'relabund',
                'descr'   : 'store relative abundances rather than raw abundances in the summary file',
                'type'    : 'boolean',
                'value' : False,
                'required': False
              },
              {
                'name'    : 'numwanted',
                'descr'   : 'number of nearest neighbours to look for',
                'type'    : 'int',
                'value' : 10,
                'required': False
              },
              {
                'name'    : 'save',
                'descr'   : '',
                'type'    : 'boolean',
                'value' : False,
                'required': False
              },
              {
                'name'    : 'shortcuts',
                'descr'   : '',
                'type'    : 'boolean',
                'value' : True,
                'required': False
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

        for idx, input_fasta in enumerate(self.input_fasta):

            self.mk_links([input_fasta],self.output_dir)
            self.mk_links([self.input_names[idx]],self.output_dir)
            self.mk_links([self.input_groups[idx]],self.output_dir)

            input_fasta = os.path.join(self.output_dir,os.path.basename(input_fasta))
            input_names = os.path.join(self.output_dir,os.path.basename(self.input_names[idx]))
            input_groups = os.path.join(self.output_dir,os.path.basename(self.input_groups[idx]))

            extra_params={'fasta':input_fasta,'name':input_names,'group':input_groups}
            self.run_cmd('classify.seqs',extra_params)

            output_root = re.sub('.fasta$','',input_fasta)
            self.output_summary = output_root + '.pds.wang.tax.summary'
            self.output_taxonomy = output_root + '.pds.wang.taxonomy'

