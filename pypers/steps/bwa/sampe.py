import os
import re
from pypers.core.step import Step

class SamPe(Step):
    spec = {
        'version': '0.6.1',
        'descr': [
            'Generate alignments in the SAM format given paired-end reads.',
            'Repetitive read pairs will be placed randomly.',
            'If sample id is provided, includes it in the @RG tag'
        ],
        'args':
        {
            'inputs': [
                {
                    'name' : 'input_fastq_files',
                    'type' : 'file',
                    'iterable' : True,
                    'descr' : 'pairs of fastq files to be aligned'
                },
                {
                    'name' : 'input_sai_files',
                    'type' : 'file',
                    'iterable' : True,
                    'descr' : 'pairs of fastq files to be aligned'
                },
                {
                    'name'  : 'ref_path',
                    'type'  : 'ref_genome',
                    'tool'  : 'bwa',
                    'descr' : 'path to the directory containing the reference genome'
                }
            ],
            'outputs': [
                {
                    'name'  : 'output_files',
                    'type'  : 'file',
                    'descr' : 'output sam file containing the alignment results',
                }
            ],
            'params': [
            ]
        },
        'requirements' : {
            'memory' : '30'
        }
    }

    def process(self):
        sample_id = self.meta['job'].get('sample_id')

        # Read group to be added to command call
        read_group_opt = ''
        if sample_id:
            read_group_opt = '-r "@RG\tID:{s}\tSM:{s}\tPL:ILLUMINA"'.format(s = sample_id)
            
        # Output file name from basename of fastq input file
        self.output_files = re.sub(r'_R\d_(\d{3})\.fastq\.gz',r'_\1.sam',os.path.basename(self.input_fastq_files[0]))

        executable = '/software/pypers/bwa/bwa-0.6.1/bwa sampe'

        cmd = '{exe} {readgr} {ref} {sai} {fastq} > {out}'.format(
                exe    = executable,
                readgr = read_group_opt,
                ref    = self.ref_path,
                sai    = ' '.join(self.input_sai_files),
                fastq  = ' '.join(self.input_fastq_files),
                out    = self.output_files
                )
        self.submit_cmd(cmd)
