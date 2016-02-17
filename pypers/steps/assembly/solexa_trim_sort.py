from pypers.core.step import Step
import os
import re
import gzip
import glob

class SolexaTrimSort(Step):
    spec = {
        "version": "2015.07.15",
        "descr": [
            "Runs Solexa DynamicTrim and LengthSort on single fastq file, or paired read fastq files"
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
                    "name"  : "solexatrim_cmd",
                    "type"  : "str",
                    "descr" : "path to Solexa DynamicTrim.pl executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/solexa/DynamicTrim.pl",
                    "readonly" : True
                },
                {
                    "name"  : "solexasort_cmd",
                    "type"  : "str",
                    "descr" : "path to SolexaQA executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/solexa/LengthSort.pl",
                    "readonly" : True
                },
                {
                    "name"  : "lib_path",
                    "type"  : "str",
                    "descr" : "prefix to LD_LIBRARY_PATH, prevents 'undefined symbol: PC' error message",
                    "value" : "/usr/lib64",
                    "readonly" : True
                },
                {
                    "name"  : "prob_cutoff",
                    "type"  : "str",
                    "descr" : "base call quality cutoff, default 0.05",
                    "value" : 0.05
                },
                {
                    "name"  : "sortlen_cutoff",
                    "type"  : "int",
                    "descr" : "sort length cutoff, default 25 nucleotides",
                    "value" : 25
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

    def trim_fq(self, fq):
        """
        Run DynamicTrim.pl against a fq and return the result file
        """

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
            f_in.close()
            f_out.close()
            fq = fq_decompressed

        # Delete any existing outputs in case of rerun
        outfile_ext = ['trimmed','trimmed_segments','trimmed_segments.hist.pdf']
        for ext in outfile_ext:
            fn = '%s/%s.%s' % (self.output_dir,os.path.basename(fq),ext)
            if os.path.exists(fn):
                self.log.warn('[Deleting existing file %s]' % (fn))
                os.remove(fn)

        # trim
        extra_env = {'LD_LIBRARY_PATH': self.lib_path}
        cmd = '%s %s -p %s -d %s' % (self.solexatrim_cmd, fq, self.prob_cutoff, self.output_dir)

        self.submit_cmd(cmd, extra_env=extra_env)

        fq_trim = '%s/%s.trimmed' % (self.output_dir, os.path.basename(fq))
        if os.path.isfile(fq_trim) is False:
            if self.recover_errors:
                self.log.warn('[Failed to create output %s, continuing pipeline as recover_errors set to True]' % (fq_trim))
                return fq
            else:
                raise Exception('[Failed to create %s]' % (fq_trim))

        return fq_trim

    def recompress_fq(self, fq):
        """
        Check and recompress fq file
        """

        if os.path.isfile(fq) is False:
            if self.recover_errors:
                self.log.warn('[Failed to create output %s, continuing pipeline as recover_errors set to True]' % (fq))
                return fq
            else:
                raise Exception('[Failed to create %s]' % (fq))

        fq_compressed = '%s.fq.gz' % fq
        self.log.info('Compressing fq to %s' % (fq_compressed))
        with open(fq, 'r') as f_in:
            with gzip.open(fq_compressed, 'wb') as f_out:
                f_out.writelines(f_in)
        f_in.close()
        f_out.close()
        return fq_compressed

    def process(self):

        self.log.info('Runnning Solexa trim/sort on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        trim_fq1 = self.trim_fq(self.input_fq1)

        if self.input_fq2:
            trim_fq2 = self.trim_fq(self.input_fq2)

        # LengthSort.
        # Delete any existing outputs in case of rerun
        outfile_ext = ['discard','summary.txt','single','paired1','paired2']
        for ext in outfile_ext:
            fn = '%s.%s' % (trim_fq1,ext)
            if os.path.exists(fn):
                self.log.warn('[Deleting existing file %s]' % (fn))
                os.remove(fn)

        # Paired reads must LengthSort'ed together

        cmd = '%s %s' % (self.solexasort_cmd, trim_fq1)

        if self.input_fq2:
            cmd += '  %s' % trim_fq2

        cmd += ' -l %i -d %s' % (self.sortlen_cutoff, self.output_dir)

        self.submit_cmd(cmd)

        if self.input_fq2:
            self.output_fq1 = self.recompress_fq('%s.paired1' % trim_fq1)
            self.output_fq2 = self.recompress_fq('%s.paired2' % trim_fq1) # yes, trim_fq1
        else:
            self.output_fq1 = self.recompress_fq('%s.single' % trim_fq1)

