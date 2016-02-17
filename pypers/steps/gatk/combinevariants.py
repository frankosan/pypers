import os
import glob
from pypers.core.step import CmdLineStep


class CombineVariant(CmdLineStep):
    spec = {
        "name": "CombineVariant",
        "version": "2.3-9",
        "descr": [
            "Merge the variant files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"  : "input_files",
                    "type"  : "file",
                    "descr" : "input vcf files",
                },
                {
                    'name'  : 'ref_path',
                    'type'  : 'ref_genome',
                    'tool'  : 'gatk',
                    'descr' : 'path to the directory containing the reference genome'
                }
            ],
            "outputs": [
                {
                    "name"  : "output_file",
                    "type"  : "file",
                    "value" : "all_bam_ug.initalCall.vcf",
                    "descr" : "output merged vcf files",
                }
            ],
            "params" : [
                {
                    "name"  : "jvm_args",
                    "value" : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr" : "java virtual machine arguments",
                    "readonly" : True
                },
                {
                    'name'  : 'gatk_genomeanalysis',
                    'type'  : 'file',
                    'value' : '/software/pypers/GATK/GenomeAnalysisTKLite-2.3-9-gdcdccbb/GenomeAnalysisTKLite.jar',
                    'descr' : 'gatk genome analyser jar file',
                    "readonly" : True
                },
                {
                    'name'  : 'extra_params',
                    'type'  : 'str',
                    'value' : '--assumeIdenticalSamples -nt 4',
                    'descr' : 'extra parameter for the gatk genome analysis',
                    "readonly" : True
                }
            ]
        },
        "requirements": {
            "cpus"   : "4",
            "memory" : "5"
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar {{gatk_genomeanalysis}} ",
            "-l INFO -T CombineVariants -R {{ref_path}} -o {{output_file}} ",
            "{{input_variant}} {{extra_params}}"
        ]
    }

    def process(self):

        self.input_variant = [""]
        self.input_variant.extend(self.input_files)
        self.input_variant = ' --variant '.join(self.input_variant)

        self.submit_cmd(self.render())
        self.output_file = glob.glob(self.output_file)
        if not self.output_file:
            raise Exception("output file is not existing")
