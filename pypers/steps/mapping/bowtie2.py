from pypers.core.step import Step
import os
import re

class bowtie2(Step):

    spec = {
        "version": "2015.11.20",
        "descr": [
            "Run bowtie2 mapping for fastq reads, paired or unpaired"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_fq1",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the input fastq (single or read pair 1) file"
                },
                {
                    "name"     : "input_fq2",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the optional input fastq read pair 2 file"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_bam",
                    "type"  : "file",
                    "descr" : "The output bam file"
                }
            ],
            "params": [
                {
                    "name"  : "index_path",
                    "type"  : "str",
                    "descr" : "path to bowtie2 index files",
                    "value" : "/Public_data/genomes/Homo_sapiens/hg19/bowtie2/human19",
                    "readonly": True
                },
                {
                    "name"  : "bowtie2_exe",
                    "type"  : "str",
                    "descr" : "path to bowtie2 executable",
                    "value" : "/software/pypers/bowtie/bowtie-2.0.6/bin/bowtie2",
                    "readonly": True
                },
                {
                    "name"  : "samtools_exe",
                    "type"  : "str",
                    "descr" : "path to samtools executable",
                    "value" : "/software/pypers/samtools/samtools-0.1.19/bin/samtools",
                    "readonly": True
                },
                {
                    "name"  : "mate_id_str",
                    "type"  : "str",
                    "descr" : "Mate pair id strings, ':' delimited, which we want to remove from output bam name , default _R1:_R2",
                    "value" : "_R1:_R2"
                },
                {
                    "name"  : "min_insert",
                    "type"  : "int",
                    "descr" : "minimimum insert size, default 0",
                    "value" : 0
                },
                {
                    "name"  : "max_insert",
                    "type"  : "int",
                    "descr" : "maximimum insert size, default 500",
                    "value" : 500
                },
                {
                    "name"  : "local",
                    "type"  : "boolean",
                    "descr" : "perform local read alignment",
                    "value" : False
                },
                {
                    "name"  : "preset_alignment",
                    "type"  : "str",
                    "descr" : "use packaged preset options, eg --very-sensitive",
                    "value" : ""
                },
                {
                    "name"  : "rgid",
                    "type"  : "str",
                    "descr" : "Read group RG",
                    "value" : "None"
                },
                {
                    "name"  : "rglb",
                    "type"  : "str",
                    "descr" : "Read group LB",
                    "value" : "None"
                },
                {
                    "name"  : "rgpl",
                    "type"  : "str",
                    "descr" : "Read group PL",
                    "value" : "Illumina"
                },
                {
                    "name"  : "rgsm",
                    "type"  : "str",
                    "descr" : "Read group SM",
                    "value" : "None"
                },
                {
                    "name"  : "output_unaligned_reads",
                    "type"  : "boolean",
                    "descr" : "output_unaligned_reads, default",
                    "value" : True
                },
                {
                    "name"  : "sort_output",
                    "type"  : "boolean",
                    "descr" : "sort bam with samtools, default",
                    "value" : True
                }
            ]
        }
    }

    def process(self):

        # fastq file can be compressed or uncompressed
        fq_name = re.match('^(.*).(fastq\.gz$|fastq$|fq$|fq.gz$|fq\.bz2|fastq\.bz2)', self.input_fq1)
        fq_base = fq_name.group(1)

        self.output_bam = os.path.join(self.output_dir, os.path.basename(fq_base)+ '.bam')

        # for paired reads remove the mate string from the filename
        if self.input_fq2:
            mate = self.mate_id_str.split(':')
            self.output_bam = self.output_bam.replace(mate[0], '')
            self.output_bam = self.output_bam.replace(mate[1], '')

            reads = " -1 %s -2 %s" % (self.input_fq1, self.input_fq2)
        else:
            reads = " -U %s" % (self.input_fq1)

        unaligned_reads = ''
        if self.output_unaligned_reads:
            unaligned_reads_path = self.output_bam.replace('.bam',
                                                      '.unaligned.fastq')
            if self.input_fq2:
                unaligned_reads_path = unaligned_reads_path.replace(mate[0], '')
                unaligned_reads = '--un-conc %s' % unaligned_reads_path
            else:
                unaligned_reads = '--un %s' % unaligned_reads_path

        opts = ''
        if self.input_fq2:
            if self.min_insert:
                opts += ' -I %s' % self.min_insert
            if self.max_insert:
                opts += ' -X %s' % self.max_insert

        if self.local:
            opts += ' --local'
        if self.preset_alignment:
            opts += ' --' + self.preset_alignment

        # Read group tags
        if self.rgid:
            if not self.rglb or not self.rgpl or not self.rgsm:
                raise Exception('If you want to specify read groups, you must include the ID, LB, PL, and SM tags.')
            opts += ' --rg-id %s' % self.rgid
            opts += ' --rg %s:%s' % ('LB', self.rglb)
            opts += ' --rg %s:%s' % ('PL', self.rgpl)
            opts += ' --rg %s:%s' % ('SM', self.rgsm)

        # cd to the outdir to ensure temp sort files are generated here

        cmd = 'cd %s; %s %s -x %s %s %s ' % (self.output_dir, self.bowtie2_exe, opts, self.index_path, reads, unaligned_reads)

        if self.sort_output:
            cmd += '| %s view -Su - | %s sort -o - - > %s' % (self.samtools_exe, self.samtools_exe, self.output_bam)
        else:
            cmd += '| %s view -Sb - > %s' % (self.samtools_exe, self.output_bam)

        self.submit_cmd(cmd)
