from pypers.core.step import Step
import os
import re
import gzip

class SGAErrorCorrection(Step):
    spec = {
        "version": "2015.06.25",
        "descr": [
            "Runs indexing and error correction components of the SGA assembler on fastq files(s)"
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
                    "name"  : "recover_errors",
                    "type"  : "boolean",
                    "descr" : "No exception raised if error encountered",
                    "value" : True
                },
            ]
        },
        "requirements": { },
    }

    def SGA_EC(self, fq):

        if not os.path.exists(fq):
            raise Exception('[Cannot find file %s]' % fq)

        # The indexer is dumb, writes to current working directory, so create a softlink to this stepdir and cd to it

        fq_in = os.path.join(self.output_dir,os.path.basename(fq))
        if not os.path.islink(fq_in):
            os.symlink(fq,fq_in)
        
        cmd = 'cd %s; %s index  %s' % (self.output_dir,self.sga_exe, fq_in)
        self.submit_cmd(cmd)

        fq_re_match = re.match('^(.*).(fastq|fq)($|.gz$)',fq)
        if not fq_re_match:
            raise Exception('[Failed to parse fastq filename, we expect a filename ending in ".fastq|fq[.gz]" ]')

        fq_base = (os.path.basename(fq_re_match.group(1)))
        fq_ft = (os.path.basename(fq_re_match.group(2)))

        # SGA error correction autodetects gzipped files and outputs uncompressed, we prefer to gzip
        fq_out = '%s.ec.%s' % (fq_base,fq_ft)

        cmd = 'cd %s;%s correct %s -o %s;%s -f %s' % (self.output_dir,self.sga_exe, fq, fq_out, self.gzip_exe,fq_out)
        self.submit_cmd(cmd)

        fq_out += '.gz'
        if os.path.isfile(fq_out) is False:
            if self.recover_errors:
                self.log.warn('[Failed to create %s, returning original fq as recover_errors set to True]' % (fq_out))
                return (fq)
            else:
                raise Exception('[Failed to create %s]' % (fq_out))

        return (fq_out)

    def process(self):

        self.log.info('Runnning SGAErrorCorrection on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        if not os.path.exists(self.input_fq1):
            raise Exception('[Cannot find file %s]' % self.input_fq1)

        self.output_fq1 = self.SGA_EC(self.input_fq1)

        if self.input_fq2:
            if not os.path.exists(self.input_fq2):
                raise Exception('[Cannot find file %s]' % self.input_fq2)
            self.output_fq2 = self.SGA_EC(self.input_fq2)
