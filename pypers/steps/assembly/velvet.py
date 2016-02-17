from pypers.core.step import Step
import os

class Velvet(Step):
    spec = {
        "version": "2015.06.23",
        "descr": [
            "Run the Velvet de-bruijn graph based assembler for a single fastq file, or paired read fastq files",
            "The single fastq file may be interleaved or single-read",
            "We assume no seperate insertsize library (read types short2 or shortPaired2)"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_fq1",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the input fastq (single or read pair 1) file",
                },
                {
                    "name"     : "input_fq2",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the optional input fastq read pair 2 file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_contigs",
                    "type"  : "file",
                    "descr" : "The output assembled contigs fasta file"
                }
            ],
            "params": [
                {
                    "name"  : "velveth_cmd",
                    "type"  : "str",
                    "descr" : "path to velveth executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin/velveth",
                    "readonly": True
                },
                {
                    "name"  : "velvetg_cmd",
                    "type"  : "str",
                    "descr" : "path to velvetg executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin/velvetg",
                    "readonly": True
                },
                {
                    "name"  : "interleaved",
                    "type"  : "boolean",
                    "descr" : "Use a single input interleaved fasta",
                    "value" : False
                },
                {
                    "name"  : "hash_length",
                    "type"  : "int",
                    "descr" : "kmer length for hash table",
                    "value" : 29
                },
                {
                    "name"  : "recover_errors",
                    "type"  : "boolean",
                    "descr" : "No exception raised if error encountered",
                    "value" : True
                }
            ]
        },
        "requirements": { },
    }

    def process(self):

        self.log.info('Runnning velvet on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        # Run velveth to create Sequences and Roadmaps, which are necessary to velvetg
        if self.input_fq2 and self.interleaved:
            self.log.warn('Runnning with interleaved option, ignoring the fastq2 parameter')

        #-fmtAuto will detecte fastq fastq and compression
        # [the kbase prog would not work with comressed files]
        cmd_args = '%s %s %s -fmtAuto' % (self.velveth_cmd,self.output_dir,self.hash_length)

        if self.interleaved:
            cmd_args += ' -shortPaired -interleaved %s' % self.input_fq1
        else:
            if self.input_fq2:
                cmd_args += ' -shortPaired -separate %s %s' % (self.input_fq1,self.input_fq2)
            else:
                cmd_args += ' -short %s' % self.input_fq1

        self.submit_cmd(cmd_args)

        if not (os.path.exists(os.path.join(self.output_dir, 'Sequences')) and os.path.exists(os.path.join(self.output_dir, 'Roadmaps'))):
            raise Exception('[Failed to create Sequences and/or Roadmaps in %s]' % (self.output_dir))

        # velvetg - de Bruijn graph construction, error removal and repeat resolution
        self.log.info('Runnning velvetg')
        cmd_args = '%s %s -exp_cov auto' % (self.velvetg_cmd,self.output_dir) # infer expected coverage of unique regions
        self.submit_cmd(cmd_args)

        self.output_contigs = os.path.join(self.output_dir, 'contigs.fa')

        if not os.path.exists(self.output_contigs):
            if self.recover_errors:
                self.log.warn('Continuing as recover_errors is set, contigs file null')
                open(self.output_contigs, 'a').close()
            else:
                raise Exception('[Failed to create %s]' % (self.output_contigs))

