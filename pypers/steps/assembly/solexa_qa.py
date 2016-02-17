from pypers.core.step import Step
import os
import re
import gzip

class SolexaQA(Step):
    spec = {
        "version": "2015.06.25",
        "descr": [
            "Runs SolexaQA to calculate sequence quality statistics for a single fastq file, or paired read fastq files"
        ],
        "url" : "http://solexaqa.sourceforge.net",
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
                    "name"  : "solexaqa_cmd",
                    "type"  : "str",
                    "descr" : "path to SolexaQA executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/solexa/SolexaQA.pl",
                    "readonly": True
                },
                {
                    "name"  : "r_path",
                    "type"  : "str",
                    "descr" : "path to R nd binaries called by Solexa",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin/",
                    "readonly": True
                },
                {
                    "name"  : "recover_errors",
                    "type"  : "boolean",
                    "descr" : "No exception raised if error encountered",
                    "value" : True
                },
            ]
        },
        "requirements": { },
    }

    def run_solexa(self, fq):

        if not os.path.exists(fq):
            raise Exception('[Cannot find file %s]' % fq)

        # fastq file can be gzipped in which case we need to decompress first

        fq_re_match = re.match('^(.*).(fastq|fq)($|.gz$)',fq)
        if not fq_re_match:
            raise Exception('[Failed to parse fastq filename, we expect a filename ending in ".fastq|fq[.gz]" ]')

        fq_base = (os.path.basename(fq_re_match.group(1)))

        if fq_re_match.group(3):
            fq_decompressed = '%s/%s.fq' % (self.output_dir,fq_base)
            self.log.info('Decompressing fq to %s' % (fq_decompressed))
            with gzip.open(fq, 'rb') as f_in:
                with open(fq_decompressed, 'w') as f_out:
                    f_out.writelines(f_in)
            fq = fq_decompressed

        # Delete any existing outputs in case of rerun
        outfile_ext = ['quality','matrix','segments']
        for ext in outfile_ext:
            fn = '%s/%s.%s' % (self.output_dir,os.path.basename(fq),ext)
            if os.path.exists(fn):
                self.log.warn('[Deleting existing file %s]' % (fn))
                os.remove(fn)

        extra_env = {'PATH': self.r_path}
        cmd = '%s  %s -d %s' % (self.solexaqa_cmd, fq, self.output_dir)

        self.submit_cmd(cmd, extra_env=extra_env)

        output_qual = '%s/%s.quality' % (self.output_dir, os.path.basename(fq))
        if os.path.isfile(output_qual) is False:
            if self.recover_errors:
                self.log.warn('[Failed to create output %s, continuing pipeline as recover_errors set to True]' % (output_qual))
            else:
                raise Exception('[Failed to create %s]' % (output_qual))

        return 0

    def process(self):

        self.log.info('Runnning SolexaQA on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        self.run_solexa(self.input_fq1)
        if self.input_fq2:
            self.run_solexa(self.input_fq2)

        # This is a preassembly step which may be chained with other preassemblers, for Solexa QA we just return the input fq name(s)
        self.output_fq1 = self.input_fq1
        self.output_fq2 = self.input_fq2

