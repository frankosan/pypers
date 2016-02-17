from pypers.core.step import Step
import os
import re
import gzip

class IDBA(Step):
    spec = {
        "version": "2015.06.25",
        "descr": [
            """
            Run the IDBA deBruijn graph based assembler for a single fastq file, or paired read fastq files
            /software/pypers/KBaseExecutables/prod/deployment/lib/ar_server/plugins/idba.py
            As the idba ssembler is prone to core dumps, by default we capture thrown errros and return a possibly null contigs file

            Also we use an istallation recompiled with kMaxShortSequence = 250 in short_sequence.h instead of the kbase install
                /software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin/idba/idba_ud
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
                    "name"  : "idba_cmd",
                    "type"  : "str",
                    "descr" : "path to idba executable, by default we use IDBA-UD for data with highly uneven depth, recompiled with kMaxShortSequence = 250",
                    "value" : "/pypers/develop/idba/idba-1.1.1/bin/idba_ud",
                    "readonly": True
                },
                {
                    "name"  : "fq2fa_cmd",
                    "type"  : "str",
                    "descr" : "path to idba fq2fa executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin/idba/fq2fa",
                    "readonly": True
                },
                {
                    "name"  : "gunzip_exe",
                    "type"  : "str",
                    "descr" : "path to gunzip",
                    "value" : "/usr/bin/gunzip",
                    "readonly": True
                },
                {
                    "name"  : "max_k",
                    "type"  : "int",
                    "descr" : "maximum k value",
                    "value" : 100
                },
                {
                    "name"  : "lib_path",
                    "type"  : "str",
                    "descr" : "additional setting for LD_LIBRARY_PATH for GLIBC_2.14",
                    "value" : "/software/pypers/gcc/gcc-5.1.0/lib64/",
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

        self.log.info('Runnning IDBA on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        fq_re_match = re.match('^(.*).(fastq|fq)($|.gz$)',self.input_fq1)
        if not fq_re_match:
            raise Exception('[Failed to parse fastq filename, we expect a filename ending in ".fastq|fq[.gz]" ]')

        fq_base = (os.path.basename(fq_re_match.group(1)))
        reads_fa = '%s.fa' % fq_base

        # Convert input fq to fa, merging read pairs if necessary
        # fq2fa needs unzipped files else core dumps
        if self.input_fq1.endswith('.gz'):
            fq1 = '%s/%s' % (self.output_dir, os.path.basename(os.path.splitext(self.input_fq1)[0]))
            inF = gzip.open(self.input_fq1, 'rb')
            outF = open(fq1, 'wb')
            outF.write( inF.read() )
            inF.close()
            outF.close()
        else:
            fq1 = self.input_fq1

        if self.input_fq2:
            # Need to merge the read pairs
            if self.input_fq2.endswith('.gz'):
                fq2 = '%s/%s' % (self.output_dir, os.path.basename(os.path.splitext(self.input_fq2)[0]))
                inF = gzip.open(self.input_fq2, 'rb')
                outF = open(fq2, 'wb')
                outF.write( inF.read() )
                inF.close()
                outF.close()
            else:
                fq2 = self.input_fq2
            cmd = 'cd %s;%s --merge --filter %s %s %s' % (self.output_dir,self.fq2fa_cmd,fq1,fq2,reads_fa)
        else:
            cmd = 'cd %s;%s %s %s' % (self.output_dir,self.fq2fa_cmd,fq1,reads_fa)

        self.submit_cmd(cmd)

        # Note we use -r with recompiled idba
        cmd = 'cd %s;%s -r %s -o %s --maxk %s' % (self.output_dir, self.idba_cmd,reads_fa,self.output_dir,self.max_k)

        self.output_contigs = os.path.join(self.output_dir, '%s/contig.fa' % self.output_dir)
        self.log.warn('%s' % str(self))

        extra_env = {'LD_LIBRARY_PATH': self.lib_path}

        try:
            self.submit_cmd(cmd, extra_env=extra_env)
        except Exception, e:
            if self.recover_errors:
                self.log.warn('Exception raised %s' % str(e))
                self.log.warn('Continuing as recover_errors is set, output contigs file may be null')
                if not os.path.exists(self.output_contigs):
                    open(self.output_contigs, 'a').close()
            else:
                raise Exception(e)
