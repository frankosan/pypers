from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurTrimSeqs(Mothur):
    """
    The trim.seqs command will enable you to trim off primer sequences and barcodes,
    use the barcode information to generate a group file and split a fasta file into
    sub-files, screen sequences based on the qual file that comes from 454 sequencers,
    cull sequences based on sequence length and the presence of ambiguous bases and get
    the reverse complement of your sequences.
    """

    spec = {
        'name'    : 'MothurTrimSeqs',
        'version' : '20150507',
        'descr'   : [
            'Provides the preprocessing features needed to screen and sort pyrosequences'
        ],
        'url' : 'www.mothur.org/wiki/Trim.seqs',
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
                        'name'     : 'input_oligos',
                        'type'     : 'file',
                        'iterable' : False,
                        'descr'    : 'input oligos filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_trim_fasta',
                        'type' : 'file',
                        'descr': 'output trimmed fasta filename'
                    },
                    {
                        'name' : 'output_trim_names',
                        'type' : 'file',
                        'descr': 'output trimmed names filename'
                    },
                    {
                        'name' : 'output_scrap_fasta',
                        'type' : 'file',
                        'descr': 'output scrapped fasta filename'
                    },
                    {
                        'name' : 'output_scrap_names',
                        'type' : 'file',
                        'descr': 'output scrapped names filename'
                    },
                    {
                        'name' : 'output_groups',
                        'type' : 'file',
                        'descr': 'output groups file filename'
                    }

                ],
            'params'  : [
              {
                'name'    : 'flip',
                'descr'   : 'calculate the reverse complement of the sequence',
                'type'    : 'boolean',
                'value' : True,
              },
              {
                'name'    : 'checkorient',
                'descr'   : 'search the reverse compliment if barcodes and primers not found',
                'type'    : 'boolean',
                'value' : False,
              },
              {
                'name'    : 'maxambig',
                'descr'   : 'number of ambiguous base calls to allow for',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'maxhomop',
                'descr'   : 'maximum screened homopolymer length',
                'type'    : 'int',
                'value' : 8,
              },
              {
                'name'    : 'minlength',
                'descr'   : 'minimum sequence length',
                'type'    : 'int',
                'value' : 200,
              },
              {
                'name'    : 'maxlength',
                'descr'   : 'maximum sequence length',
                'type'    : 'int',
                'value' : 600,
              },
              {
                'name'    : 'pdiffs',
                'descr'   : 'maximum number of differences to the primer sequence',
                'type'    : 'int',
                'value' : 2,
              },
              {
                'name'    : 'bdiffs',
                'descr'   : 'maximum number of differences to the barcode sequence',
                'type'    : 'int',
                'value' : 1,
              },
              {
                'name'    : 'ldiffs',
                'descr'   : 'maximum number of differences to the linker sequence',
                'type'    : 'int',
                'value' : 0,
              },
              {
                'name'    : 'sdiffs',
                'descr'   : 'maximum number of differences to the spacer sequence',
                'type'    : 'int',
                'value' : 0,
              },
              {
                'name'    : 'tdiffs',
                'descr'   : 'maximum total number of differences to the barcode, primer, linker and spacer',
                'type'    : 'int',
                'value' : 0,
              },
              {
                'name'    : 'allfiles',
                'descr'   : 'create separate group and fasta file for each grouping',
                'type'    : 'boolean',
                'value' : False,
              },
              {
                'name'    : 'keepforward',
                'descr'   : 'keep the primer',
                'type'    : 'boolean',
                'value' : False,
              },
              {
                'name'    : 'logtransform',
                'descr'   : 'calculate averages using a logtransform',
                'type'    : 'boolean',
                'value' : False,
              },
              {
                'name'    : 'qtrim',
                'descr'   : 'if false, put trimmed sequence in scrap file instead of trim file',
                'type'    : 'boolean',
                'value' : False,
              },
              {
                'name'    : 'qthreshold',
                'descr'   : 'terminate sequence if any of its base calls has a quality score below this value',
                'type'    : 'int',
                'value' : 0,
              },
              {
                'name'    : 'qaverage',
                'descr'   : 'remove sequences that have an average quality score below this value',
                'type'    : 'int',
                'value' : 0,
              },
              {
                'name'    : 'rollaverage',
                'descr'   : 'minimum rolling average quality score allowed over a window',
                'type'    : 'int',
                'value' : 0,
              },
              {
                'name'    : 'qwindowaverage',
                'descr'   : 'minimum average quality score allowed over a window',
                'type'    : 'int',
                'value' : 0,
              },
              {
                'name'    : 'qstepsize',
                'descr'   : 'number of bases to move the window over',
                'type'    : 'int',
                'value' : 1,
              },
              {
                'name'    : 'qwindowsize',
                'descr'   : 'set a number of bases in a window',
                'type'    : 'int',
                'value' : 50,
              },
              {
                'name'    : 'keepfirst',
                'descr'   : 'number of head bases to trim before checking sequence',
                'type'    : 'int',
                'value' : 0,
              },
              {
                'name'    : 'removelast',
                'descr'   : 'number of tail bases to trim before checking sequence',
                'type'    : 'int',
                'value' : 0,
              }
            ]
        },
        'requirements' : {
            "cpus" : "8"
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

        self.mk_links([self.input_oligos],self.output_dir)

        for idx, input_fasta in enumerate(self.input_fasta):

            self.mk_links([input_fasta],self.output_dir)
            self.mk_links([self.input_names[idx]],self.output_dir)

            input_fasta = os.path.join(self.output_dir,os.path.basename(input_fasta))
            input_names = os.path.join(self.output_dir,os.path.basename(self.input_names[idx]))
            input_oligos = os.path.join(self.output_dir,os.path.basename(self.input_oligos))

            extra_params={'fasta':input_fasta, 'name':input_names, 'oligos':input_oligos}
            self.run_cmd('trim.seqs',extra_params)

            output_root = re.sub('.fasta$','',input_fasta)
            self.output_trim_fasta = output_root + '.trim.fasta'
            self.output_trim_names = output_root + '.trim.names'
            self.output_scrap_fasta = output_root + '.scrap.fasta'
            self.output_scrap_names = output_root + '.scrap.names'
            self.output_groups = output_root + '.groups'

