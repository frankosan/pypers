from pypers.steps.qiime import Qiime

class CollateAlpha(Qiime):
    spec = {
        "version": "2015.05.20",
        "descr": [
            """
            Collates the results of alpha_diversity calculations on samples in an OTU table
            Note : The input directory should contain only alpha_diversity metrics .txt files
            """
        ],
        "url" : "http://qiime.org/scripts/collate_alpha.html",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_dir",
                    "type"     : "dir",
                    "iterable" : True,
                    "descr"    : "the input directory, should contain only alpha_diversity metrics .txt files"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_metrics_dir",
                    "type"  : "dir"
                }
            ],
            "params": [
            ]
        },
        "requirements": { 
        }
    }

    def process(self):

        self.output_metrics_dir = '%s/metrics' % self.output_dir

        cmd = 'collate_alpha.py -i %s -o %s' % (self.input_dir, self.output_metrics_dir)
        self.submit_cmd(cmd,extra_env=self.extra_env)
