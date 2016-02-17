from pypers.core.step import Step
import os
import shutil

class reapr(Step):
    spec = {
        "version": "2015.06.24",
        "descr": [
            "Run reapr assembly evaluation and contig break pipeline on an assembled contig and the source fastq read pairs",
            "Implemeted from kbase module",
            "Jim says if there are problems runnung reapr with the header, run facheck to fix"
        ],
        "url" : "https://www.sanger.ac.uk/resources/software/reapr/",
        "args": 
        {
            "inputs": [
                {
                    "name"     : "input_contigs",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the input assembly contig file",
                },
                {
                    "name"     : "input_fq1",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the assembled input fastq (single or read pair 1) file"
                },
                {
                    "name"     : "input_fq2",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the optional assembled input fastq read pair 2 file"
                }
            ],
            "outputs": [
                {
                    "name"     : "output_contigs",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the output contig file",
                }
            ],
            "params": [
                {
                    "name"  : "reapr_cmd",
                    "type"  : "str",
                    "descr" : "path to reapr executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin/reapr/reapr",
                    "readonly" : True
                },
                {
                    "name"  : "reapr_perl_lib",
                    "type"  : "str",
                    "descr" : "reapr installation PERL5LIB",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/lib/perl5/site_perl/5.16.2",
                    "readonly" : True
                },
                {
                    "name"  : "reapr_load_lib",
                    "type"  : "str",
                    "descr" : "reapr installation LD_LIBRARY_PATH",
                    "value" : "/software/pypers/gcc/gcc-4.7.1/lib/:/software/pypers/gcc/gcc-4.7.1/lib64/:/software/pypers/KBaseExecutables/prod-Nov222013/runtime/reapr/third_party/pezmaster31-bamtools-7f8b301/lib",
                    "readonly" : True
                },
                {
                    "name"  : "reapr_bin",
                    "type"  : "str",
                    "descr" : "reap installation BIN",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin:/bin",
                    "readonly" : True
                },
                {
                    "name"  : "bwa_exe",
                    "type"  : "str",
                    "descr" : "path to bwa executable",
                    "value" : "/software/pypers/bwa/bwa-0.7.6a/bwa",
                    "readonly" : True
                },
                {
                    "name"  : "samtools_exe",
                    "type"  : "str",
                    "descr" : "path to samtools executable",
                    "value" : "/software/pypers/samtools/samtools-0.1.18/bin/samtools",
                    "readonly" : True
                },
                {
                    "name"  : "aggressive_break",
                    "type"  : "boolean",
                    "descr" : "",
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

    def process(self):

        self.log.info('Running reapr on contig:%s, fastq1:%s, fastq2:%s' % (self.input_contigs,self.input_fq1,self.input_fq2))

        if not self.input_fq2:
            if self.recover_errors:
                self.log.warn('Cannot process single fastq file, skipping reapr')
                self.output_contigs = self.input_contigs
                return 
            else:
                raise Exception('[Cannot process single fastq file, need paired reads]')

        if os.stat(self.input_contigs).st_size == 0:
            if self.recover_errors:
                self.log.warn('Got an empty contig file %s, skipping step' % self.input_contigs)
                self.output_contigs = self.input_contigs
                return 
            else:
                raise Exception('[Got an empty contig file %s]' % self.input_contigs)

        # run facheck and produce fixed contig
        fileName, fileExt = os.path.splitext(os.path.basename(self.input_contigs))
        fixed_contig = '%s/%s_reapr' % (self.output_dir,fileName)
        cmd = '%s facheck %s %s' % (self.reapr_cmd,self.input_contigs,fixed_contig)
        extra_env = {'PERL5LIB': self.reapr_perl_lib,
                     'PATH': self.reapr_bin,
                     'LD_LIBRARY_PATH':self.reapr_load_lib}

        self.submit_cmd(cmd, extra_env=extra_env)
        
        fixed_contig = fixed_contig + '.fa'
        if not os.path.isfile(fixed_contig):
            if self.recover_errors:
                self.log.warn('facheck failed to create %s, skipping reapr' % fixed_contig)
                self.output_contigs = self.input_contigs
                return 
            else:
                raise Exception('[facheck failed to create %s]' % fixed_contig)

        # Create bwa index for the contigs
        cmd_args = '%s index -a is %s' % (self.bwa_exe, fixed_contig) 
        self.submit_cmd(cmd_args)

        # remap the source fq files using the contig as ref

        bamfile = os.path.join(self.output_dir, os.path.basename(self.input_contigs) + '.bam')

        cmd_args = '%s mem -t 8 %s %s %s | %s view -Su - | %s sort -o - - > %s' % (self.bwa_exe, fixed_contig, self.input_fq1, self.input_fq2, self.samtools_exe, self.samtools_exe, bamfile)
        self.submit_cmd(cmd_args)

        if (not os.path.isfile(bamfile)) or os.path.getsize(bamfile) == 0:
            if self.recover_errors:
                self.log.warn('bwa output bamfile not created or zero size %s, skipping reapr' % bamfile)
                self.output_contigs = self.input_contigs
                return 
            else:
                raise Exception('bwa output bamfile not created or zero size %s' % bamfile)
        self.log.info('bwa output bamfile %s' % bamfile)

        # Remove duplicates
        bam_rmdup = bamfile.replace('.bam','.rmdup.bam')
        cmd_args = '%s rmdup %s %s' % (self.samtools_exe, bamfile, bam_rmdup) 
        self.submit_cmd(cmd_args)

        # reapr preprocess
        rpr_outpath = '%s/out' % self.output_dir
        if os.path.isdir(rpr_outpath):
            shutil.rmtree(rpr_outpath) # in case of rerun

        cmd = '%s preprocess %s %s %s' % (self.reapr_cmd,fixed_contig,bam_rmdup,rpr_outpath)
        self.submit_cmd(cmd, extra_env=extra_env)

        # reapr stats
        stats_prefix = '%s/01.stats' % rpr_outpath
        cmd = '%s stats %s %s' % (self.reapr_cmd,rpr_outpath,stats_prefix)
        self.submit_cmd(cmd, extra_env=extra_env)

        # reapr fcdrate
        fcd_prefix = '%s/02.fcdrate' % rpr_outpath
        cmd = '%s fcdrate %s %s %s' % (self.reapr_cmd,rpr_outpath,stats_prefix,fcd_prefix)
        self.submit_cmd(cmd, extra_env=extra_env)

        # reapr score
        fcd_file = open('%s.info.txt' % fcd_prefix, 'r')
        for line in fcd_file:
            pass # read to EOF 
        fcd_cutoff = line.split('\t')[0]

        in_bam = '%s/00.in.bam' % rpr_outpath
        fa_gaps = '%s/00.assembly.fa.gaps.gz' % rpr_outpath
        score_prefix = '%s/03.score' % rpr_outpath
        cmd = '%s score %s %s %s %s %s' % (self.reapr_cmd,fa_gaps,in_bam,stats_prefix,fcd_cutoff,score_prefix)
        self.submit_cmd(cmd, extra_env=extra_env)

        # reapr break
        errors_gff = '%s.errors.gff.gz' % score_prefix
        break_prefix = '%s/04.break' % rpr_outpath
        cmd = '%s break' % self.reapr_cmd
        if self.aggressive_break == 'True':
            cmd += ' -a'
        cmd += ' %s %s %s' % (fixed_contig,errors_gff,break_prefix)
        self.submit_cmd(cmd, extra_env=extra_env)

        broken = '%s.broken_assembly.fa' % break_prefix
        if os.path.exists(broken):
            self.log.info('reapr generated broken contigs file %s' % broken)
            self.output_contigs = broken
        else:
            self.log.info('reapr did not produce broken contigs %s' % broken)
            self.output_contigs = input_contigs
