from pypers.core.step import Step
import os
import json

class Qplot(Step):
    """
    Run the qplot program to calculate summary statistics for illumina sequenced bams
    """

    spec = {
        'version' : '20120602',
        'descr'   : [
            'Run the qplot program to calculate summary statistics for illumina sequenced bams.'
        ],
        'url' : '//genome.sph.umich.edu/wiki/QPLOT',
        'args' : {
            'inputs'  : [
                    {
                        'name'     : 'input_files',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input bam file names'
                    },
                    {
                        'name' : 'reference',
                        'type' : 'ref_genome',
                        'tool' : 'gatk',
                        'descr': 'Reference sequence file',
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_stats',
                        'type' : 'file',
                        'descr': 'output text file name'
                    },
                    {
                        'name' : 'output_pdf',
                        'type' : 'file',
                        'descr': 'output pdf file name'
                    },
                    {
                        'name' : 'output_R',
                        'type' : 'file',
                        'descr': 'output R file name'
                    }

                ],
            'params'  : [
                    {
                        'name' : 'doR',
                        'type' : 'boolean',
                        'value': True,
                        'descr': 'also produce an R plot'
                    },
                    {
                        'name' : 'doPDF',
                        'type' : 'boolean',
                        'value': True,
                        'descr': 'also produce a PDF file'
                    },
                    {
                        'name' : 'baits_file',
                        'type' : 'str',
                        'value': '',
                        'descr': 'agilent baits file. It is a file containing regions to plot (format: chr start end label)'
                    },
                    {
                        'name' : 'gc_content',
                        'type' : 'str',
                        'value' : '',
                        'descr': 'File describing the GC content'
                    },
                    {
                        'name' : 'dbsnp',
                        'type' : 'str',
                        'value' : '',
                        'descr': 'SNP position db file'
                    },
                    {
                        'name' : 'winsize',
                        'type' : 'int',
                        'descr': 'window size',
                        'value': 100
                    },
                    {
                        'name' : 'min_map_q',
                        'type' : 'int',
                        'descr': '',
                        'value': 0
                    }
                ]
        },
        'requirements' : {}
    }

    def __init__(self):
        super(Qplot,self).__init__()

    def process(self):
        """
        Run the step as configured.
        """
        bam_name = os.path.basename(self.input_files).split('.')[0]
        self.output_stats = bam_name + '.qplotQC.stats'


        cmd = [ '/software/pypers/qplot/qplot-20120602/bin/qplot',
                '--reference', str(self.reference),
                '--gccontent', self.gc_content,
                '--dbsnp', str(self.dbsnp),
                '--stats', self.output_stats,
                '--winsize', str(self.winsize),
                '--minMapQuality', str(self.min_map_q)]

        if self.baits_file:
            cmd += ['--regions', self.baits_file]

        if self.doPDF:
            self.output_pdf = bam_name + '.qplotQC.pdf'
            cmd += ['--plot', self.output_pdf]

        if self.doR:
            self.output_R = bam_name + '.qplotQC.R'
            cmd += ['--Rcode', self.output_R]

        cmd += [self.input_files]
        print '[Qplot] command:',cmd

        extra_env = {'PATH': '/software/pypers/R/R-3.0.0-gcc/bin',
                     'LD_LIBRARY_PATH': '/software/pypers/gcc/gcc-4.7.1/lib64' }
        self.submit_cmd(' '.join(cmd),extra_env=extra_env)
