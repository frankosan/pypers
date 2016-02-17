from pypers.core.step import Step
import os

class KbaseAnnotation(Step):

    spec = {
        "version": "2015.08.12",
        "descr": [
            """
            Runs the perl script to generically call kbase Genome Annotation Service subroutines
            Calls per program 'kbase_annotation.pl which instantiates a Genome Annotation Client

            Inputs and outputs a kbase 'genomeTO' object encoded in a JSON file
            Specify the subroutine to run in the "subroutine" parameter eg "call_features_tRNA_trnascan"
            """
        ],
        "url" : "https://github.com/kbase/genome_annotation/blob/master/GenomeAnnotation.spec",
        "args": 
        {
            "inputs": [
                {
                    "name"     : "input_genome",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the input kbase 'genomeTO' file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_genome",
                    "type"  : "file",
                    "descr"    : "the output kbase 'genomeTO' file",
                }
            ],
            "params": [
                {
                    "name"  : "subroutine",
                    "type"  : "str",
                    "descr" : "name of kbase annotation subroutine to run"
                },
                {
                    "name"  : "subroutine_params",
                    "type"  : "str",
                    "descr" : "subroutine params to evaluate as a perl hash or array",
                    "value" : ""
                },
            ]
        },
        "requirements": { }
    }

    ## NB PERL5LIB needs to pick up a modified GenomeAnnotation Client Implementation 
    extra_env = {
        'KB_TOP' : '/software/pypers/KBaseExecutables/build-Jun022014/deployment',
        'KB_RUNTIME' : '/software/pypers/KBaseExecutables/prod-Nov222013/runtime',
        'PATH' : '/software/pypers/KBaseExecutables/build-Jun022014/deployment/services/genome_annotation/bin:/software/pypers/KBaseExecutables/build-Jun022014/deployment/services/cdmi_api/bin:/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin:/software/pypers/KBaseExecutables/build-Jun022014/deployment/bin:/usr/bin:$PATH:/bin',
        'PERL5LIB' : '/software/pypers/KBaseExecutables/build-Jun022014/deployment/lib:/software/pypers/KBaseExecutables/build-Jun022014/deployment/plbin',
        'LD_LIBRARY_PATH' : '/scratch/rdjoycech/lib/' # Temp workround to get libdb-4.7.so for annotate_proteins_kmer_v1
        }

    # extra_env mechanism puts a colon at the end, this is not what we want for KB_DEPLOYMENT_CONFIG
    # config modified to refect kbase mount on /nihs/Kbase/Kbase
    KB_DEPLOYMENT_CONFIG = '/pypers/develop/kbase/deployment.cfg'

    def process(self):

        self.log.info('Runnning genome annotation %s on %s' % (self.subroutine, self.input_genome))

        # The perl script needs to be in the same dir as the python
        kbase_script = os.path.join(os.path.dirname(__file__),'kbase_annotation.pl')
        self.output_genome = '%s/%s' % (self.output_dir, os.path.basename(self.input_genome))

        cmd =''
        # Due to resetting the env in the kbase scripts, export required vars before running command
        # cmd failures with rc=32512: cd <tmpdir>; env PERL5LIB=  ...
        # Probably the extra_env setting is not EXPORTING varables 
        self.extra_env['PERL5LIB'] = '%s/lib:%s' % (os.path.dirname(__file__),self.extra_env['PERL5LIB'])
        for k in self.extra_env:
            cmd += "export %s=%s\n" % (k, self.extra_env[k])

        cmd += 'export KB_DEPLOYMENT_CONFIG=%s\n' % self.KB_DEPLOYMENT_CONFIG
        tmp_dir = '%s/tmp' % self.output_dir

        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        cmd += 'export TEMPDIR=%s\n' % tmp_dir
        cmd += 'export TMPDIR=%s\n' % tmp_dir

        cmd += 'perl %s -g %s -s %s -o %s' % (kbase_script, self.input_genome, self.subroutine, self.output_genome)

        if self.subroutine_params:
            cmd += ' -p "%s"' % self.subroutine_params

        self.submit_cmd(cmd)

        if not os.path.isfile(self.output_genome) or os.stat(self.output_genome).st_size == 0:
            raise Exception('[Failed to create %s]' % self.output_genome)
