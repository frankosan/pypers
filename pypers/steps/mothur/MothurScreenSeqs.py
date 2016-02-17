from pypers.core.step import Step
from pypers.steps.mothur import Mothur
import os
import json
import re

class MothurScreenSeqs(Mothur):
    """
    The screen.seqs command enables you to keep sequences that fulfill certain
    user defined criteria. Furthermore, it enables you to cull those sequences
    not meeting the criteria from a names, group, contigsreport, alignreport and
    summary file.
    """

    spec = {
        'name'    : 'MothurScreenSeqs',
        'version' : '20150508',
        'descr'   : [
            'Removes sequences that do not fulfill user defined criteria'
        ],
        'url' : 'www.mothur.org/wiki/Screen.seqs',
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
                    },
                    {
                        'name'     : 'input_summary',
                        'type'     : 'file',
                        'iterable' : True,
                        'required' : False,
                        'descr'    : 'input summary filename'
                    },
                    {
                        'name'     : 'input_summary_log',
                        'type'     : 'file',
                        'iterable' : True,
                        'required' : False,
                        'value'    : '',
                        'descr'    : 'input summary log filename from which to derive Start end End params'
                    },
                ],
            'outputs' : [
                    {
                        'name' : 'output_good_fasta',
                        'type' : 'file',
                        'descr': 'output good fasta filename'
                    },
                    {
                        'name' : 'output_good_names',
                        'type' : 'file',
                        'required' : False,
                        'descr': 'output good names filename'
                    },
                    {
                        'name' : 'output_good_groups',
                        'type' : 'file',
                        'required' : False,
                        'descr': 'output good groups file filename'
                    },
                    {
                        'name' : 'output_good_counts',
                        'type' : 'file',
                        'required' : False,
                        'descr': 'output good count table filename'
                    },
                    {
                        'name' : 'output_bad_accnos',
                        'type' : 'file',
                        'value'    : '*.bad.accnos',
                        'descr': 'output rejected accnos filename'
                    }
                ],
            'params'  : [
              {
                'name'    : 'start',
                'descr'   : 'remove sequences that start after this position',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'end',
                'descr'   : 'remove sequences that end before this position',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'minlength',
                'descr'   : 'minimum sequence length',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'maxlength',
                'descr'   : 'maximum sequence length',
                'type'    : 'int',
                'value' : -1,
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
                'name'    : 'maxn',
                'descr'   : 'maximum number of Ns allowed in a sequence',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'optimize',
                'descr'   : 'select criterion to use to select sequences',
                'type'    : 'enum',
                'options' : [ 'none', 'start', 'end', 'maxambig', 'maxhomop', 'minlength', 'maxlength' ],
                'value' : 'start',
              },
             {
                'name'    : 'criteria',
                'descr'   : 'set threshold for optimize criterion',
                'type'    : 'int',
                'value' : 95,
              },
              {
                'name'    : 'minoverlap',
                'descr'   : 'minimum overlap length',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'ostart',
                'descr'   : 'position the overlap must start by',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'oend',
                'descr'   : 'position the overlap must end after',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'mismatches',
                'descr'   : 'set maximum mismatches',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'minscore',
                'descr'   : 'minimum search score during alignment',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'maxinsert',
                'descr'   : 'maximum number of insertions during alignment',
                'type'    : 'int',
                'value' : -1,
              },
              {
                'name'    : 'minsim',
                'descr'   : 'minimum similarity to template sequences during alignment',
                'type'    : 'int',
                'value' : -1,
              }
            ]
        },
        'requirements' : {
            'cpus': '8'
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
        if type(self.input_summary) != list:
            self.input_summary = [self.input_summary]

       # If a summary.seqs output log is passed, use this to derive start and end params
        lower_tile = '25%'
        upper_tile = '75%'

        if self.input_summary_log:
            summ_start=0
            summ_end=0
            fh = open(self.input_summary_log,'r')
            for line in fh:
                flds=line.split()
                if line.startswith('%s-tile:' % lower_tile):
                    summ_start=flds[1]
                if line.startswith('%s-tile:' % upper_tile):
                    summ_end=flds[2]
            if summ_start > 0 and summ_end > 0:
                self.start = summ_start
                self.end = summ_end
                self.log.info('Derived start and end params %s,%s from the %s and %s tile values in summary_log' % (summ_start,summ_end,lower_tile,upper_tile))
            else:
                self.log.warn('Failed to find %s and %s tile values in %s' % (lower_tile,upper_tile,self.input_summary_log))

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

            if self.input_summary[idx]:
                input_summary = os.path.join(self.output_dir,os.path.basename(self.input_summary[idx]))
                self.mk_links([self.input_summary[idx]],self.output_dir)
                extra_params['summary'] = input_summary

            self.run_cmd('screen.seqs',extra_params)

            output_root = os.path.splitext(input_fasta)[0]
            fa_fn = os.path.splitext(os.path.basename(input_fasta))[1] # eg .fasta, .align
            self.output_good_fasta = output_root + '.good' + fa_fn

            if self.input_groups[idx]:
                self.output_good_groups = output_root + '.good.groups'
            if self.input_names[idx]:
                self.output_good_names = output_root + '.good.names'

            if self.input_counts[idx]:
                output_root = os.path.splitext(input_counts)[0]
                self.output_good_counts = output_root + '.good.count_table'
