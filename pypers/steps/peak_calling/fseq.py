from pypers.core.step import Step
import os

class Fseq(Step):
    spec = {
        "version": "0.0.1",
        "descr": [
            "Call F-seq peak calling"
        ],
        "url" : "http://fureylab.web.unc.edu/software/fseq/",
        "args": 
        {
            "inputs": [
                {
                    "name"  : "input_bed",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "input bed file"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_peaks",
                    "type"  : "file",
                    "descr" : "the output file of called peaks"
                }
            ],
            "params": [
                {
                    "name"  : "fseq_exe",
                    "type"  : "str",
                    "descr" : "The path to the F-seq executable",
                    "value" : "/software/pypers/f-seq/F-seq_nihs/bin/fseq",
                    "readonly" : True
                },
                {
                    "name"  : "output_format",
                    "type"  : "str",
                    "descr" : "The output file fomat, <wig | bed | npf>, default bed",
                    "value" : "bed",
                    "readonly" : True
                },
                {
                    "name"  : "feature_length",
                    "type"  : "int",
                    "descr" : "feature length (default=600)",
                    "value" : 600,
                    "readonly" : True
                },
                {
                    "name"  : "threshold",
                    "type"  : "float",
                    "descr" : "threshold (standard deviations) (default=4.0)",
                    "value" : 4.0,
                    "readonly" : True
                }
            ]
        }
    }
    extra_env = { 'PATH' : '/bin' } # fix for RH version probs, so we can find /bin/cat

    
    def process(self):

        self.output_peaks = os.path.join(self.output_dir, os.path.basename(self.input_bed).replace('.bed', '.fseq.%s' % self.output_format))

        tmp_dir = '%s/temp' % self.output_dir
        if not os.path.exists(tmp_dir):  
            os.makedirs(tmp_dir) 

        # The extra_env mechanism is failing, does it to a proper export to allow for child procs?
        cmd = 'export PATH=/bin:$PATH;%s -of %s -o %s -f %s -t %s %s -v' % (self.fseq_exe, self.output_format, tmp_dir, self.feature_length, self.threshold, self.input_bed)

        self.submit_cmd(cmd)

        # concat the per-contig results
        cmd = 'cat %s/* > %s' % (tmp_dir, self.output_peaks)
        self.submit_cmd(cmd, extra_env=self.extra_env)

