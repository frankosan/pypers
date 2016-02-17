from pypers.core.step import Step
import os
import yaml

class BayesHammer(Step):
    spec = {
        "version": "2015.06.25",
        "descr": [
            "Run the spades BayesHammer read error correction tool for Illumina reads in fastq format",
            "The single fastq file may be interleaved"
        ],
        "url" : "http://spades.bioinf.spbau.ru/release3.5.0/manual.html",
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
                    "name"     : "output_fq1",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the output fastq (single or read pair 1) file",
                },
                {
                    "name"     : "output_fq2",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the optional output fastq read pair 2 file",
                }
            ],
            "params": [
                {
                    "name"     : "spades_cmd",
                    "type"     : "str",
                    "descr"    : "path to the spades executable",
                    "value"    : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/SPAdes-3.1.1-Linux/bin/spades.py",
                    "readonly" : True
                },
                {
                    "name"  : "interleaved",
                    "type"  : "boolean",
                    "descr" : "Single input fq file is interleaved",
                    "value" : False
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

        self.log.info('Runnning BayesHammer on fastq1:%s, fastq2:%s' % (self.input_fq1,self.input_fq2))

        if self.input_fq2 and self.interleaved:
            self.log.warn('Runnning with interleaved option, ignoring the fastq2 parameter')

        cmd_args = self.spades_cmd

        if self.interleaved:
            cmd_args += ' --12 %s' % self.input_fq1
        elif self.input_fq2:
            cmd_args += ' -1 %s -2 %s' % (self.input_fq1,self.input_fq2)
        else:
            cmd_args += ' -s %s' % self.input_fq1
            
        cmd_args += ' --only-error-correction -o %s' % self.output_dir

        self.submit_cmd(cmd_args)

        yaml_out = os.path.join(self.output_dir, 'corrected','corrected.yaml')
        if not os.path.exists(yaml_out):
            if self.recover_errors:
                self.log.warn('[Failed to generate %s, continuing pipeline as recover_errors is set]' % yaml_out)
                self.output_fq1 = self.input_fq1
                self.output_fq2 = self.input_fq2
                return
            else:
                raise Exception('[Failed to generate %s]' % yaml_out)

        yaml_file = open(yaml_out)
        yaml_corr = yaml.load(yaml_file)[0]

        if 'left reads' in yaml_corr and 'right reads' in yaml_corr:
            self.output_fq1 = yaml_corr['left reads'][0]
            self.output_fq2 = yaml_corr['right reads'][0]
            self.log.info('Returning paired read files %s,%s' % (self.output_fq1,self.output_fq2))
        elif 'single reads' in yaml_corr:
            self.output_fq1 = yaml_corr['single reads'][0]
            self.output_fq2 = None
            self.log.warn('No paired reads, returning unpaired file %s' % self.output_fq1)
        else:
            if self.recover_errors:
                self.log.warn('[Failed to find read file in %s, continuing pipeline as recover_errors is set]' % yaml_out)
                self.output_fq1 = self.input_fq1
                self.output_fq2 = self.input_fq2
                return
            else:
                raise Exception('[Failed to find read file in %s]' % yaml_out)

