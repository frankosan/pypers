from pypers.core.step import Step
import os
import re

class MaSuRCA(Step):
    spec = {
        "version": "2015.06.26",
        "descr": [
            """
            Run the MaSuRCA assembler for a single fastq file, or paired read fastq files
            /software/pypers/KBaseExecutables/prod/deployment/lib/ar_server/plugins/masurca.py
            /software/pypers/KBaseExecutables/prod/deployment/lib/ar_server/plugins/masurca.yapsy-plugin
            """
        ],
        "url":"http://www.genome.umd.edu/masurca.html",
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
                    "name"  : "masurca_exe",
                    "type"  : "str",
                    "descr" : "path to MaSuRCA executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/masurca/bin/runSRCA.pl",
                    "readonly" : True
                },
                {
                    "name"  : "jellyfish_path",
                    "type"  : "str",
                    "descr" : "config file JELLYFISH_PATH",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/masurca/bin",
                    "readonly" : True
                },
                {
                    "name"  : "sr_path",
                    "type"  : "str",
                    "descr" : "config file SR_PATH",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/masurca/bin",
                    "readonly" : True
                },
                {
                    "name"  : "ca_path",
                    "type"  : "str",
                    "descr" : "config file CA_PATH",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/masurca/CA/Linux-amd64/bin",
                    "readonly" : True
                },
                {
                    "name"  : "isrt_size_avg",
                    "type"  : "int",
                    "descr" : "read insert size average",
                    "value" : 180
                },
                {
                    "name"  : "isrt_size_sd",
                    "type"  : "int",
                    "descr" : "read insert size SD; if not provided (ie default 0) we try 15% of the average",
                    "value" : 0
                },
                {
                    "name"  : "graph_kmer_size",
                    "type"  : "str",
                    "descr" : "kmer size for super reads, default auto",
                    "value" : "auto"
                },
                {
                    "name"  : "limit_jump_coverage",
                    "type"  : "int",
                    "descr" : "set to 60 for bacteria",
                    "value" : 60
                },
                {
                    "name"  : "ca_parameters",
                    "type"  : "str",
                    "descr" : "params for CA assembler",
                    "value" : "ovlMerSize=30 cgwErrorRate=0.25 ovlMemory=4GB"
                },
                {
                    "name"  : "use_linking_mates",
                    "type"  : "int",
                    "descr" : "set this to 1 for Illumina-only assemblies",
                    "value" : 1
                },
                {
                    "name"  : "kmer_count_threshold",
                    "type"  : "int",
                    "descr" : "minimum count k-mers used in error correction, 1 means all k-mers are used",
                    "value" : 1
                },
                {
                    "name"  : "jf_size",
                    "type"  : "int",
                    "descr" : "jellyfish hash size",
                    "value" : 200000000
                },
                {
                    "name"  : "do_homopolymer_trim",
                    "type"  : "int",
                    "descr" : " do (1) or do not (0) trim long runs of homopolymers",
                    "value" : 0
                },
                {
                    "name"  : "assembly_path",
                    "type"  : "str",
                    "descr" : "workround for RH7/8 problem, new location of standard unix cmds",
                    "value" : "/bin",
                    "readonly" : True
                },
                {
                    "name"  : "lib_path",
                    "type"  : "str",
                    "descr" : "additional setting for LD_LIBRARY_PATH",
                    "value" : "/software/pypers/gcc/gcc-5.1.0/lib64/",
                    "readonly" : True
                },
                {
                    "name"  : "recover_errors",
                    "type"  : "boolean",
                    "descr" : "No exception raised if error encountered",
                    "value" : True
                },
                {
                    "name"  : "num_threads",
                    "type"  : "int",
                    "descr" : "number of cpus to use",
                    "value" : 4,
                    "readonly" : True
                }
            ]
        },
        "requirements": { 
            "cpus" : "4"
        },
    }

    def process(self):

        self.log.info('Runnning MaSuRCA on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        fq_re_match = re.match('^(.*).(fastq|fq)($|.gz$)',self.input_fq1)
        if not fq_re_match:
            raise Exception('[Failed to parse fastq filename, we expect a filename ending in ".fastq|fq[.gz]" ]')

        fq_base = (os.path.basename(fq_re_match.group(1)))
        reads_fa = os.path.join(self.output_dir, '%s.fa' % fq_base)

        # Create config file

        config_fname = os.path.join(self.output_dir, 'config.txt')
        cf = open(config_fname, 'w')

        cf.write('PATHS\n')
        cf.write('JELLYFISH_PATH={}\n'.format(self.jellyfish_path))
        cf.write('SR_PATH={}\n'.format(self.sr_path))
        cf.write('CA_PATH={}\n'.format(self.ca_path))
        cf.write('END\n')

        cf.write('DATA\n')
        # PE= pe 180 20  /FULL_PATH/frag_1.fastq  /FULL_PATH/frag_2.fastq

        # need isrt size average and sd
        if self.isrt_size_sd == 0:
            self.isrt_size_sd = self.isrt_size_avg * .15
            self.log.info('Estimated isrt_size_sd = %.2f' % self.isrt_size_sd)
        data_ln = 'PE = pe %i %.2f %s' % (self.isrt_size_avg, self.isrt_size_sd, self.input_fq1)
        if self.input_fq2:
            data_ln += ' %s' % self.input_fq2

        cf.write('%s\n' % data_ln)
        cf.write('END\n')

        cf.write('PARAMETERS\n')
        cf.write('GRAPH_KMER_SIZE={}\n'.format(self.graph_kmer_size))
        cf.write('USE_LINKING_MATES={}\n'.format(self.use_linking_mates))
        cf.write('LIMIT_JUMP_COVERAGE = {}\n'.format(self.limit_jump_coverage))
        cf.write('CA_PARAMETERS = {}\n'.format(self.ca_parameters))
        cf.write('KMER_COUNT_THREASHOLD = {}\n'.format(self.kmer_count_threshold))
        cf.write('NUM_THREADS = {}\n'.format(self.num_threads))
        cf.write('JF_SIZE={}\n'.format(self.jf_size))
        cf.write('DO_HOMOPOLYMER_TRIM={}\n'.format(self.do_homopolymer_trim))
        cf.write('END\n')
        cf.close()

        # Create assemble.sh script

        os.chdir(self.output_dir)

        cmd = '%s %s' % (self.masurca_exe, config_fname)
        self.submit_cmd(cmd)

        assemble_script = os.path.join(self.output_dir, 'assemble.sh')
        if not os.path.exists(assemble_script):
            raise Exception('Failed to generate %s' % assemble_script)

        # Run assemble.sh script

        os.chmod(assemble_script, 0774)
        cmd = assemble_script
        self.output_contigs = os.path.join(self.output_dir, 'CA/10-gapclose/genome.ctg.fasta')

        extra_env = {'PATH': self.assembly_path, 'LD_LIBRARY_PATH': self.lib_path}

        try:
            self.submit_cmd(cmd, extra_env=extra_env)
        except Exception, e:
            if self.recover_errors:
                self.log.warn('Exception raised %s' % str(e))
                self.log.warn('Continuing as recover_errors is set, contigs file may be null')
                if not os.path.exists(self.output_contigs):
                    open(self.output_contigs, 'a').close()
            else:
                raise Exception(e)

        # In some cases masurca will fail gapclose but create a usable contig in 9-terminator step
        if not os.path.exists(self.output_contigs):
            if self.recover_errors:
                self.log.warn('failed to create %s' % self.output_contigs)
                self.output_contigs = os.path.join(self.output_dir, 'CA/9-terminator/genome.ctg.fasta')
                if os.path.exists(self.output_contigs):
                    self.log.warn('gapclose failed, continuing with %s' % self.output_contigs)
                else:
                    self.log.warn('Continuing as recover_errors is set, contigs file may be null')
                    if not os.path.exists(self.output_contigs):
                        self.output_contigs = os.path.join(self.output_dir, 'dummy.ctg.fasta')
                        open(self.output_contigs, 'a').close()
            else:
                raise Exception('failed to create %s' % self.output_contigs)

