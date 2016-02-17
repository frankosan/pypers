from pypers.core.step import Step
import os
import re
import gzip

class TagDust(Step):
    spec = {
        "version": "2015.06.24",
        "descr": [
            "Runs TagDust assembly preprocessor to remove sequencing artifacts(adaptors) from NGS fastq files(s)",
            "Implemeted from kbase module"
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
                    "name"  : "tagdust_exe",
                    "type"  : "str",
                    "descr" : "path to tagdust executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/a6/bin/tagdust",
                    "readonly": True
                },
                {
                    "name"  : "sync_exe",
                    "type"  : "str",
                    "descr" : "path to kbase sync_paired_end_reads python script",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/sync_paired_end_reads.py",
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
                    "name"  : "lib_fa",
                    "type"  : "str",
                    "descr" : "path to Library [artifact] sequences fasta file",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/a6/adapter.fasta",
                    "readonly": True
                },
                {
                    "name"  : "fdr",
                    "type"  : "float",
                    "descr" : "False discovery rate cutoff",
                    "value" : 0.01
                },
                {
                    "name"  : "singleline",
                    "type"  : "boolean",
                    "descr" : "sequences are written in a single line",
                    "value" : True
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

    def tagdust_fq(self, fq):
        # Run tagdust on an fq file

        if not os.path.exists(fq):
            raise Exception('[Cannot find file %s]' % fq)

        self.log.info('Runnning TagDust on %s' % (fq))

        fq_re_match = re.match('^(.*).(fastq|fq)($|.gz$)',fq)
        if not fq_re_match:
            raise Exception('[Failed to parse fastq filename, we expect a filename ending in ".fastq|fq[.gz]" ]')

        fq_base = (os.path.basename(fq_re_match.group(1)))
        fq_ft = (os.path.basename(fq_re_match.group(2)))

        # fastq file can be gzipped in which case we need to decompress first
        if fq_re_match.group(3):
            fq_decompressed = '%s/%s.fq' % (self.output_dir,fq_base)
            self.log.info('Decompressing fq to %s' % (fq_decompressed))
            with gzip.open(fq, 'rb') as f_in:
                with open(fq_decompressed, 'w') as f_out:
                    f_out.writelines(f_in)
            fq = fq_decompressed

        cmd = '%s -f %s' % (self.tagdust_exe, self.fdr)

        if self.singleline:
            cmd += ' -singleline'

        fq_out = '%s/%s.tag.fq' % (self.output_dir,fq_base)
        cmd += ' %s %s -o %s' % (self.lib_fa,fq,fq_out)

        self.submit_cmd(cmd)

        if os.path.isfile(fq_out) is False:
            if self.recover_errors:
                self.log.warn('[Failed to create %s, continuing pipeline as recover_errors set to True]' % (fq_out))
                return fq
            else:
                raise Exception('[Failed to create %s]' % (fq_out))

        return fq_out


    def process(self):

        fq1_tag = self.tagdust_fq(self.input_fq1)
        if not self.input_fq2:
            self.log.warn('[No read pair]')
            self.output_fq1 = fq1_tag
            return

        fq2_tag = self.tagdust_fq(self.input_fq2)

        # For read pairs, need to now sync the paired end reads

        # Syncer also requires an uncompressed original file
        fq_re_match = re.match('^(.*).(fastq|fq)($|.gz$)',self.input_fq1)
        fq_base = (os.path.basename(fq_re_match.group(1)))
        fq_ft = (os.path.basename(fq_re_match.group(2)))
        if fq_re_match.group(3):
            fq_orig = '%s/%s.fq' % (self.output_dir,fq_base)
        else:
            fq_orig = self.input_fq1

        fq1_sync = fq1_tag.replace('.tag.fq','.tag.sync.fq')
        fq2_sync = fq2_tag.replace('.tag.fq','.tag.sync.fq')
        self.log.info('Syncing TagDust outpust into fastq1:%s, fastq2:%s' % (fq1_sync,fq2_sync))

        cmd = '%s %s %s %s %s %s' % (self.sync_exe, fq_orig, fq1_tag, fq2_tag, fq1_sync, fq2_sync)
        self.submit_cmd(cmd)

        self.output_fq1 = fq1_sync
        self.output_fq2 = fq2_sync
