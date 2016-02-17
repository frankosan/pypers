from pypers.core.step import Step
import os

class SPAdes(Step):
    spec = {
        "version": "2015.06.23",
        "descr": [
            "Run the SPAdes Genome Assembler for a single fastq file, or paired read fastq files",
            "The single fastq file may be interleaved",
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
                    "name"  : "spades_cmd",
                    "type"  : "str",
                    "descr" : "path to SPAdes executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/SPAdes-3.1.1-Linux/bin/spades.py",
                    "readonly": True
                },
                {
                    "name"  : "interleaved",
                    "type"  : "boolean",
                    "descr" : "Use a single input interleaved fasta, SPAdes option --12",
                    "value" : False
                },
                {
                    "name"  : "read_length",
                    "type"  : "str",
                    "descr" : "read length, valid values are 'short'(default),'medium','medium2','long','150','200','250'",
                    "value" : "short"
                },
                {
                    "name"  : "only_assembler",
                    "type"  : "boolean",
                    "descr" : "Assemble only",
                    "value" : True
                },
                {
                    "name"  : "recover_errors",
                    "type"  : "boolean",
                    "descr" : "No exception raised if error encountered",
                    "value" : True
                },
                {
                    "name"  : "process_threads_allowed",
                    "type"  : "int",
                    "descr" : "Number of threads to run",
                    "value" : 16
                }
            ]
        },
        "requirements": { 
            "cpus" : "16"
        }
    }

    def process(self):

        self.log.info('Runnning SPAdes on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        valid_read_length = ['short','medium','medium2','long','150','200','250']
        if self.read_length not in valid_read_length:
            raise Exception('[Invalid read_length option %s, must be in %s]' % (self.read_length,valid_read_length))

        if self.input_fq2 and self.interleaved:
            self.log.warn('Runnning with interleaved option, ignoring the fastq2 parameter')

        cmd_args = self.spades_cmd

        if self.interleaved:
            cmd_args += ' --12 %s' % self.input_fq1
        elif self.input_fq2:
            cmd_args += ' -1 %s -2 %s' % (self.input_fq1,self.input_fq2)
        else:
            cmd_args += ' -s %s' % self.input_fq1

        if self.only_assembler:
            cmd_args  += ' --only-assembler'

        # default read length 'short' does not set spades -k param
        if self.read_length == 'medium' or self.read_length == '150':
            cmd_args += ' -k 21,33,55,77'

        if self.read_length == 'medium2' or self.read_length == '200':
            cmd_args += ' -k 21,33,55,77,99'

        if self.read_length == 'long' or self.read_length == '250':
            cmd_args += ' -k 21,33,55,77,99,127'

        cmd_args += ' -o %s' % self.output_dir
        cmd_args += ' -t %i' % self.process_threads_allowed

        # Note, we do not automatically raise excecption if spades has non-zero RC
        self.submit_cmd(cmd_args,raise_exception=False)

        self.output_contigs = os.path.join(self.output_dir, 'contigs.fasta')

        if not os.path.exists(self.output_contigs):
            if self.recover_errors:
                self.log.warn('Continuing as recover_errors is set, contigs file null')
                open(self.output_contigs, 'a').close()
            else:
                raise Exception('[Failed to create %s]' % (self.output_contigs))

