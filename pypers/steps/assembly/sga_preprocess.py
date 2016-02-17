from pypers.core.step import Step
import os
import sys
import re
import gzip

class SGAPreprocess(Step):
    spec = {
        "version": "2015.06.24",
        "descr": [
            "Run SGA assembler preprocess to perform quality filtering/trimming on fastq files",
            "Assume paired end reads, either interleaved or paired files, and split the output by read pair"
        ],
        "url" : "http://www.vcru.wisc.edu/simonlab/bioinformatics/programs/sga/preprocess.txt",
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
                    "name"     : "output_fq1",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the output fastq (single or read pair 1) file",
                },
                {
                    "name"     : "output_fq2",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the optional output fastq read pair 2 file",
                }
            ],
            "params": [
                {
                    "name"  : "sga_exe",
                    "type"  : "str",
                    "descr" : "path to SGA executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/a5/bin/sga",
                    "readonly": True
                },
                {
                    "name"  : "gzip_exe",
                    "type"  : "str",
                    "descr" : "path to gzip executable",
                    "value" : "/bin/gzip",
                    "readonly": True
                },
                {
                    "name"  : "quality_trim",
                    "type"  : "int",
                    "descr" : "quality trimming (-q) value",
                    "value" : 10
                },
                {
                    "name"  : "quality_filter",
                    "type"  : "int",
                    "descr" : "quality filter (-f) value",
                    "value" : 20
                },
                {
                    "name"  : "min_length",
                    "type"  : "int",
                    "descr" : "minimum sequence length (-m)",
                    "value" : 29
                },
                {
                    "name"  : "permute_ambiguous",
                    "type"  : "boolean",
                    "descr" : "Randomly change ambiguous base calls to one of possible bases",
                    "value" : True
                },
                {
                    "name"  : "phred64",
                    "type"  : "boolean",
                    "descr" : "reads are phred64 scaled",
                    "value" : False
                },
                {
                    "name"  : "recover_errors",
                    "type"  : "boolean",
                    "descr" : "No exception raised if error encountered",
                    "value" : True
                },
                {
                    "name"  : "run_singly",
                    "type"  : "boolean",
                    "descr" : "Run paired reads singly with pe-mode 0",
                    "value" : True
                }
            ]
        },
        "requirements": { },
    }

    def run_mode_0(self, fq, fn):
        # Run singly with pe-mode 0

        cmd = '%s preprocess -q %i -f %i -m %i' % (self.sga_exe, self.quality_trim, self.quality_filter, self.min_length)

        if self.permute_ambiguous:
            cmd += ' --permute-ambiguous'
        if self.phred64:
            cmd += ' --phred64'

        cmd += ' --pe-mode 0 %s' % (fq)

        # SGA autodetects gzipped files and outputs uncompressed, we prefer to gzip
        fq_out = '%s/sga_pp.00%s.fq.gz' % (self.output_dir,fn)
        cmd += ' | %s > %s' % (self.gzip_exe,fq_out)
        self.submit_cmd(cmd)

        if os.path.isfile(fq_out) is False:
            if self.recover_errors:
                self.log.warn('[Failed to create %s, returning original fq file as recover_errors set to True]' % (fq_out))
                fq_out = fq
            else:
                raise Exception('[Failed to create %s]' % (fq_out))

        return (fq_out)


    def process(self):

        self.log.info('Runnning SGAPreprocess on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        if not os.path.exists(self.input_fq1):
            raise Exception('[Cannot find file %s]' % self.input_fq1)

        fq_re_match = re.match('^(.*).(fastq|fq)($|.gz$)',self.input_fq1)
        if not fq_re_match:
            raise Exception('[Failed to parse fastq filename, we expect a filename ending in ".fastq|fq[.gz]" ]')

        if self.run_singly:
            self.output_fq1 = self.run_mode_0(self.input_fq1,1)
            self.output_fq2 = self.run_mode_0(self.input_fq2,2)
            return

        cmd = '%s preprocess -q %i -f %i -m %i' % (self.sga_exe, self.quality_trim, self.quality_filter, self.min_length)

        if self.permute_ambiguous:
            cmd += ' --permute-ambiguous'
        if self.phred64:
            cmd += ' --phred64'

        if self.input_fq2:
            if not os.path.exists(self.input_fq2):
                raise Exception('[Cannot find file %s]' % self.input_fq2)
            cmd += ' --pe-mode 1 %s %s' % (self.input_fq1, self.input_fq2)
        else:
            self.log.warn('Assuming single fastq has interleaved read pairs')
            cmd += ' --pe-mode 2 %s' % (self.input_fq1)

        # SGA autodetects gzipped files and outputs uncompressed, we prefer to gzip
        fq_out = '%s/sga_pp.fq.gz' % (self.output_dir)
        cmd += ' | %s > %s' % (self.gzip_exe,fq_out)
        self.submit_cmd(cmd)

        if os.path.isfile(fq_out) is False:
            if self.recover_errors:
                self.log.warn('[Failed to create %s, returning original fq files as recover_errors set to True]' % (fq_out))
                self.output_fq1 = self.input_fq1
                self.output_fq2 = self.input_fq2
                return
            else:
                raise Exception('[Failed to create %s]' % (fq_out))

        # SGA also auto-interleaves, need to undo if paired reads
        if self.input_fq2:
            self.output_fq1 = '%s/%s' % (self.output_dir,os.path.basename(self.input_fq1).replace('fq','sga.fq'))
            self.output_fq2 = '%s/%s' % (self.output_dir,os.path.basename(self.input_fq2).replace('fq','sga.fq'))
        else:
            self.output_fq1 = '%s/%s' % (self.output_dir,os.path.basename(self.input_fq1).replace('fq','sga.001.fq'))
            self.output_fq2 = '%s/%s' % (self.output_dir,os.path.basename(self.input_fq1).replace('fq','sga.002.fq'))

        self.log.info('Splitting interleaved SGAPreprocess output into fastq1:%s, fastq2:%s' % (self.output_fq1,self.output_fq2))

        inf = gzip.open(fq_out, 'rb')
        of1 = gzip.open(self.output_fq1, 'wb')
        of2 = gzip.open(self.output_fq2, 'wb')
        i=0
        for line in inf:
            if i < 4:
                of1.write(line)
            else:
                of2.write(line)
            i += 1
            if i == 8:
                i = 0
        inf.close()
        of1.close()
        of2.close()

