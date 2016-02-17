from pypers.core.step import Step
import os

class A6(Step):
    spec = {
        "version": "2015.06.25",
        "descr": [
            """
            Runs the A6 or A5 assembly pipeline for a single interleaved illumina fastq file, or paired read fastq files
            A6 is describes as a Modified A5 microbial assembly pipeline for use when A5 crashes
            The assembly pipeline does some pre-assembly steps including SGA preprocess and tagdust, and assembles using IDBA-UD

            For the A5 pipline, set param "A6_cmd" to
            /software/pypers/KBaseExecutables/prod-Nov222013/runtime/a6/bin/a5
            rather than
            /software/pypers/KBaseExecutables/prod-Nov222013/runtime/a6/bin/a5_pipeline.pl

            A5/6 will likely not work well with Illumina reads shorter than around 80nt, or reads where the base qualities are
            low in all or most reads before 60nt. A5 assumes it is assembling homozygous haploid genomes

            As the idba assembler is prone to core dumps, by default we capture thrown errros and return a null contigs file

            NOTE : a5_pipeline.pl picks up the idba in prod-Nov222013/runtime/a6/bin, regardless of the "a6_bin" param
            """
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
                    "name"  : "A6_cmd",
                    "type"  : "str",
                    "descr" : "path to (modified) a6 pipeline perl script (default), or the old a5 executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/a6/bin/a5_pipeline.pl",
                    "readonly": True
                },
                {
                    "name"  : "interleaved",
                    "type"  : "boolean",
                    "descr" : "Use a single input interleaved fasta",
                    "value" : False
                },
                {
                    "name"  : "a6_bin",
                    "type"  : "str",
                    "descr" : "path to required executables, plus workround for RH7/8 problem and new location of standard unix cmds in /bin",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/a6/bin/:/bin",
                    "readonly": True
                },
                {
                    "name"  : "legacy_perl_lib",
                    "type"  : "str",
                    "descr" : "path to legacy perl lib containing getopts.pl, a workround for perl5",
                    "value" : "/scratch/rdjoycech/assembly/a5/lib/",
                    "readonly": True
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

        self.log.info('Runnning assembly pipeline on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        if self.input_fq2 and self.interleaved:
            self.log.warn('Runnning with interleaved option, ignoring the fastq2 parameter')

        cmd_args = '%s %s' % (self.A6_cmd,self.input_fq1)

        if not self.interleaved:
            if self.input_fq2:
                cmd_args += ' %s' % self.input_fq2

        ## Need to cd to self.output_dir first
        cmd = 'cd %s;%s .' % (self.output_dir,cmd_args) 

        self.output_contigs = os.path.join(self.output_dir, '..final.scaffolds.fasta')

        extra_env = {'PATH': self.a6_bin, 'PERL5LIB': self.legacy_perl_lib}

        try:
            self.submit_cmd(cmd, extra_env=extra_env)
        except Exception, e:
            if self.recover_errors:
                self.log.warn('Exception raised %s' % str(e))
                self.log.warn('Continuing as recover_errors is set, contigs file may be null')
                if not os.path.exists(self.output_contigs):
                    open(self.output_contigs, 'a').close()
            else:
                raise Exception(e)

