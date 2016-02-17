import os
from pypers.steps.genome_annotation.kbase import KbaseStep

class Rast_call_tRNAs(KbaseStep):
    spec = {
        "name": "Rast_call_tRNAs",
        "version": "2015.07.30",
        "descr": [
            """
            DEPRECATED use kbase_annotation.py 
            Runs kbase call_features_tRNA_trnascan workflow, rast_call_tRNAs.pl, to find transfer RNAs in the input genome
            http://www.theseed.org
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_genome",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the name of the input genome file in Genbank JSON format",
                }
            ],
            "outputs": [
                {
                    "name"     : "output_genome",
                    "type"     : "file",
                    "descr"    : "the name of the output genome file",
                }
            ],
            "params": [
            ],
        }
    }

    def process(self):

        output_genome = os.path.basename(self.input_genome.replace('genome','tRNAs.genome'))
        self.output_genome = os.path.join(self.output_dir,output_genome)

        run_script = os.path.join(self.output_dir,'cmd.sh')
        fh = open(run_script,'w')

        # Due to weirdess caused by resetting the env in call_tRNAs
        # cmd failed with rc=32512: cd /var/lib/condor/execute/dir_15124/tmpdir_search_for_rnas_D0acYv0x; env PERL5LIB= search_for_rnas ...
        # ...need to creat a script to set the env variables and run the cmd...
        for k in self.extra_env:
            fh.write("export %s=%s\n" % (k, self.extra_env[k]))

        fh.write("perl %s/rast_call_tRNAs.pl --input %s --output %s --tmpdir %s\n" % (self.perl_bin_path, self.input_genome, self.output_genome, self.output_dir))
        fh.close()
        os.chmod(run_script,0755)

        self.submit_cmd(run_script)
