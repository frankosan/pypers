import os
from pypers.steps.qiime import Qiime

class ParallelMultipleRarefactions(Qiime):
    spec = {
        "name"   : "ParallelMultipleRarefactions",
        "version": "20150525",
        "descr": [
            "Performs bootstrap, jackknife, and rarefaction analyses on a subsampled (rarefied) otu table",
            "Warning: We have had problem with this step stalling on the cluster, so prefer to use non-parallel step MultipleRarefactions"
        ],
        "url" : "http://qiime.org/scripts/parallel_multiple_rarefactions.html",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_biom",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input biom OTU table filename",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_metrics_dir",
                    "type"  : "dir",
                    "descr" : "output directory of .biom rarerefied (subsampled) OTU tables"
                }
            ],
            "params": [
                {
                    "name"  : "min",
                    "type"  : "int",
                    "descr" : "Minimum number of seqs/sample for rarefaction",
                    "value" : 10
                },
                {
                    "name"  : "max",
                    "type"  : "int",
                    "descr" : "Mamimum number of seqs/sample for rarefaction",
                    "value" : 50
                },
                {
                    "name"  : "step",
                    "type"  : "int",
                    "descr" : "Size of each steps between the min/max of seqs/sample",
                    "value" : 10
                }
            ]
        },
        "requirements": { 
            'cpus': '6'
        }
    }

    def process(self):
        """
        Run the step as configured.
        """

        if type(self.input_biom) != list:
            self.input_biom = [self.input_biom]

        self.output_metrics_dir = '%s/metrics' % self.output_dir

        for input_biom in self.input_biom:
            cmd = 'parallel_multiple_rarefactions.py -T  -i %s -o %s -m %s -x %s -s %s --jobs_to_start %s' % (input_biom, self.output_metrics_dir, self.min, self.max, self.step, self.cpus)
            self.submit_cmd(cmd,extra_env=self.extra_env)

