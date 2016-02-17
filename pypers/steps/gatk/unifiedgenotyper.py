import os
import glob
from pypers.core.step import CmdLineStep
from pypers.utils import utils


class UnifiedGenotyper(CmdLineStep):
    spec = {
        "name": "UnifiedGenotyper",
        "version": "2.3-9",
        "descr": [
            "Runs gatk UnifiedGenotyper on a deduplicated, realigned, matefixed, sorted and recalibrated bam file."
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "descr"    : "input bam files",
                },
                {
                    "name"     : "input_intervals",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "a list of input target intervals"
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
                    "name"  : "output_vcf",
                    "type"  : "file",
                    "value" : "all_bam_ug.{{input_intervals}}.vcf",
                    "descr" : "output vcf files",
                },
                {
                    "name"  : "output_vcf_idx",
                    "type"  : "file",
                    "value" : "all_bam_ug.{{input_intervals}}.vcf.idx",
                    "descr" : "output vcf files index",
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
                    'name'  : 'dbsnp',
                    'type'  : 'file',
                    'value' : '/Public_data/EXTERNAL_DATA/1000G_GENOME_REFERENCES/v37/GATK_bundle_v1.5/1.5/b37/dbsnp_135.b37.vcf',
                    'descr' : 'dbsnp'
                },
                {
                    'name'  : 'extra_params',
                    'type'  : 'str',
                    'value' : '-stand_call_conf 50 -stand_emit_conf 10 -dcov 200',
                    'descr' : 'extra parameter for the gatk genome analysis',
                    "readonly" : True
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar {{gatk_genomeanalysis}} ",
            "-l INFO -T UnifiedGenotyper -R {{ref_path}} -o {{output_vcf}} ",
            "--dbsnp {{dbsnp}} -glm BOTH ",
            "-L {{input_intervals}} -I {{input_bams}} {{extra_params}}"
        ],
        "requirements": {
            "memory": "8"
        }
    }

    def process(self):

        self.input_bams = [""]
        self.input_bams.extend(self.input_files)
        self.input_bams = ' -I '.join(self.input_bams)

        self.submit_cmd(self.render())
        self.output_vcf = glob.glob(self.output_vcf)
        self.output_vcf_idx = glob.glob(self.output_vcf_idx)
        if not (self.output_vcf and self.output_vcf_idx):
            raise Exception("output VCF file not existing")
