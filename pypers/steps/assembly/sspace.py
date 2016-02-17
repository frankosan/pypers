from pypers.core.step import Step
import os
import re
import itertools
import gzip
import math
import glob

class SSPACE(Step):
    spec = {
        "version": "2015.06.24",
        "descr": [
            "Run SSPACE scaffolding for pre-assembled contigs",
            "Implemeted from kbase module"
        ],
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
                    "name"  : "sspace_cmd",
                    "type"  : "str",
                    "descr" : "path to SSPACE executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/a5/bin/SSPACE/sspace",
                    "readonly": True
                },
                {
                    "name"  : "insertsize_script",
                    "type"  : "str",
                    "descr" : "path to kbase getinsertsize python script",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin/getinsertsize.py",
                    "readonly": True
                },
                {
                    "name"  : "minimum_overlap",
                    "type"  : "int",
                    "descr" : "Min overlap for extension, decision shouuld be based on A5 results",
                    "value" : 15
                },
                {
                    "name"  : "insert_size",
                    "type"  : "int",
                    "descr" : "read insert size; if not provided (ie default 0) we estimate by mapping the reads to the contig",
                    "value" : 0
                },
                {
                    "name"  : "genome_size",
                    "type"  : "int",
                    "descr" : "Estimated genome size",
                    "value" : 4000000
                },
                {
                    "name"  : "max_pair_ratio",
                    "type"  : "float",
                    "descr" : "maximum ratio between best 2 contig pairs, -a param",
                    "value" : 0.4
                },
                {
                    "name"  : "min_links",
                    "type"  : "int",
                    "descr" : "minimum number of links (read pairs) for a valid contig pair, -k param (calculate if -1)",
                    "value" : -1
                },
                {
                    "name"  : "min_overlap",
                    "type"  : "int",
                    "descr" : "Min overlap for extension, -m param (calculate if -1)",
                    "value" : -1
                },
                {
                    "name"  : "min_merge_overlap",
                    "type"  : "int",
                    "descr"  : "Min overlap for merging, -n param (calculate if -1)",
                    "value" : -1
                },
                {
                    "name"  : "contig_ext",
                    "type"  : "int",
                    "descr" : "contig extension, -x param",
                    "value" : 0
                },
                {
                    "name"  : "bwa_exe",
                    "type"  : "str",
                    "descr" : "path to bwa executable",
                    "value" : "/software/pypers/bwa/bwa-0.7.6a/bwa",
                    "readonly": True
                },
                {
                    "name"  : "samtools_exe",
                    "type"  : "str",
                    "descr" : "path to samtools executable",
                    "value" : "/software/pypers/samtools/samtools-0.1.18/bin/samtools",
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

    def estimate_insert_size(self, contig_file, fq1, fq2, min_lines=4000):
        """
        Maps a subset of fastq reads to contigs using bwa to estimate insert size
        Lifted from kbase ar_server/plugins.py
        """
        self.log.info('Estimating fastq insert size')
        min_reads = min_lines * 4
        sub_reads = []
        for fq in [fq1,fq2]:
            sub_name = os.path.join(self.output_dir, '%s.sub' % os.path.basename(fq))
            sub_file = open(sub_name, 'w')

            # take a subset of reads
            if fq.endswith(".gz"):
                fq_fn = gzip.open(fq, 'rb')
            else:
                fq_fn = open(fq, 'r')
            for line in itertools.islice(fq_fn, min_reads):
                sub_file.write(line)
            sub_file.close()
            sub_reads.append(sub_name)

        # Create bwa index for the contigs
        cmd_args = '%s index -a is %s' % (self.bwa_exe, contig_file)
        self.submit_cmd(cmd_args)

        # run bwa on the fq files against the contig
        samfile = os.path.join(self.output_dir, 'bwa.sam')
        cmd_args = '%s mem %s %s %s > %s' % (self.bwa_exe, contig_file, sub_reads[0], sub_reads[1],samfile )
        self.submit_cmd(cmd_args)

        if os.path.getsize(samfile) == 0:
            self.log.error('bwa output samfile is zero size %s' % samfile)
            return 0

        cmd_args = '%s %s' % (self.insertsize_script, samfile)
        self.submit_cmd(cmd_args)

        insertsize_out = glob.glob(os.path.join(self.output_dir, '*sspace.log.txt'))
        if len(insertsize_out) == 0:
            self.log.error('Cannot find log from %s' % (self.insertsize_script))
            return 0

        # Serch for estimated insert size in output line, eg
        # Read length: mean 101.0, STD=0.0
        for line in open(insertsize_out[0], 'r'):
            line_match = re.search('Read length: mean (\d+.\d+),', line)
            if line_match:
                return float(line_match.group(1))
            else:
                self.log.error('Cannot find Read Length line in %s' % (insertsize_out[0]))
                return 0


    def calculate_read_info(self, fq1, fq2):
        """
        Counts number of reads and determimes max read length from a fastq read file pair
        """

        read_count = 0
        max_read_length = -1

        for r in [fq1,fq2]:
            f = open(r, 'r')
            for line in f:
                read_count += 1
                if read_count % 4 == 2 and len(line) > max_read_length:
                    max_read_length = len(line)
            f.close()
        read_count /= 4
        read_count += read_count

        return max_read_length, read_count

    def process(self):

        self.log.info('Running SSPACE on fastq1:%s, fastq2:%s contig:%s' % (self.input_fq1,self.input_fq2,self.input_contigs))

        if not self.input_fq2:
            if self.recover_errors:
                self.log.warn('Cannot process single fastq file, skipping SSPACE')
                self.output_contigs = self.input_contigs
                return
            else:
                raise Exception('[Cannot process single fastq file, need paired reads to scaffold]')

        if os.stat(self.input_contigs).st_size == 0:
            if self.recover_errors:
                self.log.warn('Got an empty contig file %s, skipping step' % self.input_contigs)
                self.output_contigs = self.input_contigs
                return
            else:
                raise Exception('[Got an empty contig file %s]' % self.input_contigs)

        if self.insert_size == 0:
            self.insert_size = int(self.estimate_insert_size(self.input_contigs, self.input_fq1, self.input_fq2)) # must be an int
            if self.insert_size == 0:
                if self.recover_errors:
                    self.log.warn('Failed to estimate insert size, skipping SSPACE')
                    self.output_contigs = self.input_contigs
                    return
                else:
                    raise Exception('Failed to estimate insert size')

            self.log.info('Estimated insert size is %i' % self.insert_size)

        # Min overlap for extension, decision based on A5
        if  self.min_overlap == -1:
            min_overlap = max(self.minimum_overlap,
                              int(math.log(self.genome_size, 2) + 3.99))
        else:
            min_overlap = int(self.min_overlap)

        # Min overlap for merging, decision based on A5
        if self.min_merge_overlap == -1:
            min_merge_overlap = int(math.log(self.insert_size, 2) * 1.25 + 0.99)
        else:
            min_merge_overlap = int(self.min_merge_overlap)

        # K minimal links, based on A5
        if self.min_links == -1:
            try:
                max_read_length, read_count = self.calculate_read_info(self.input_fq1,self.input_fq2)
                coverage = max_read_length * read_count / self.genome_size
                expected_links = coverage * self.insert_size / max_read_length
                min_links = int(math.log(expected_links)/math.log(1.4)-11.5)
            except ValueError:
                if self.recover_errors:
                    self.log.warn('Failed to estimate minimal links, skipping SSPACE')
                    self.log.warn('max_read_length:%s read_count:%s' % (max_read_length,read_count))
                    self.output_contigs = self.input_contigs
                    return
                else:
                    raise Exception('Failed to estimate mimimal links, max_read_length:%s read_count:%s' % (max_read_length,read_count))
        else:
            min_links = int(self.min_links)

        # Create library file
        self.log.warn('We assume fastq1 and fastq2 are forward/reverse read pairs repectively')
        lib_filename = os.path.join(self.output_dir,'libs.txt')
        lib_file = open(lib_filename, 'w')
        lib_data = 'lib1 %s %s %i %.1f %s' % (self.input_fq1,self.input_fq2,self.insert_size,0.2,'FR') # insert error ratio '0.2'
        lib_file.write(lib_data)
        lib_file.close()

        cmd_args = ' '.join([self.sspace_cmd,
                   '-m', str(min_overlap),
                    '-n', str(min_merge_overlap),
                    '-k', str(min_links),
                    '-a', str(self.max_pair_ratio),
                    '-l', lib_filename,
                    '-s', self.input_contigs,
                    '-d', self.output_dir,
                    '-x', str(self.contig_ext)])

        self.submit_cmd(cmd_args)

        self.output_contigs = os.path.join(self.output_dir, 'standard_output.final.scaffolds.fasta')

        if not os.path.exists(self.output_contigs):
            raise Exception('[Failed to create %s]' % (self.output_contigs))

