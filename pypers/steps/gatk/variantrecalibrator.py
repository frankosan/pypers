import os
import glob
from pypers.core.step import CmdLineStep


class VariantRecalibrator(CmdLineStep):
    spec = {
        "name": "VariantRecalibrator",
        "version": "2.3-9",
        "descr": [
            "Runs gatk vcf VariantRecalibrator,",
            "generating recal and tranches files to be used by ApplyRecalibration"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"  : "input_file",
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
                    "name"  : "output_recal",
                    "type"  : "file",
                    "value" : "{{input_file}}.recal.txt",
                    "descr" : "variant recal file",
                },
                {
                    "name"  : "output_tranches",
                    "type"  : "file",
                    "value" : "{{input_file}}.tranches.txt",
                    "descr" : "variant trache file",
                }
            ],
            "params" : [
                {
                    "name"     : "jvm_args",
                    "value"    : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr"    : "java virtual machine arguments",
                    "readonly" : True
                },
                {
                    'name'  : 'gatk_jar',
                    'type'  : 'file',
                    'value' : '/software/pypers/GATK/GenomeAnalysisTKLite-2.3-9-gdcdccbb/GenomeAnalysisTKLite.jar',
                    'descr' : 'gatk genome analyser jar file',
                    "readonly" : True
                },
                {
                    'name'  : 'annotation_params',
                    'type'  : 'str',
                    'value' : '-an QD -an HaplotypeScore -an MQRankSum -an ReadPosRankSum -an FS -an MQ',
                    'descr' : 'extra parameter for the gatk genome analysis',
                    "readonly" : True
                },
                {
                    'name'  : 'max_gaussian',
                    'type'  : 'int',
                    'value' : 4,
                    'descr' : 'the max gaussian param'
                },
                {
                    'name'  : 'percent_bad',
                    'type'  : 'int',
                    'value' : 0.05,
                    'descr' : 'the percentBad param'
                },
                {
                    'name'  : 'mode',
                    'type'  : 'str',
                    'value' : 'SNP',
                    'descr' : 'the mode param'
                },
                {
                    'name'  : 'resources',
                    'type'  : 'str',
                    'value' : "--resource:hapmap,known=false,training=true,truth=true,prior=15.0 \
                              /Public_data/EXTERNAL_DATA/1000G_GENOME_REFERENCES/v37/GATK_bundle_v1.5/1.5/b37/hapmap_3.3.b37.sites.vcf \
                              --resource:omni,known=false,training=true,truth=false,prior=12.0 \
                              /Public_data/EXTERNAL_DATA/1000G_GENOME_REFERENCES/v37/GATK_bundle_v1.5/1.5/b37/1000G_omni2.5.b37.sites.vcf \
                              --resource:dbsnp,known=true,training=false,truth=false,prior=6.0 \
                              /Public_data/EXTERNAL_DATA/1000G_GENOME_REFERENCES/v37/GATK_bundle_v1.5/1.5/b37/dbsnp_135.b37.vcf",
                    'descr' : 'extra parameter add to the gatk genome analysis command',
                    "readonly" : True
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar {{gatk_jar}} ",
            "-T VariantRecalibrator -R {{ref_path}} ",
            "-input {{input_file}} -recalFile {{output_recal}} -tranchesFile {{output_tranches}} ",
            "{{annotation_params}} --maxGaussians {{max_gaussian}} -percentBad {{percent_bad}} ",
            "-mode {{mode}} {{resources}}"

        ],
        "requirements": {
            "memory": "8"
        }
    }

    def process(self):

        self.submit_cmd(self.render())
        if not os.path.exists(self.output_recal):
            raise Exception("Output file not existing: %s" % self.output_recal)
        elif not os.path.exists(self.output_tranches):
            raise Exception("Output file not existing: %s" % self.output_tranches)
        else:
            self.log.info("Step successfully completed")
