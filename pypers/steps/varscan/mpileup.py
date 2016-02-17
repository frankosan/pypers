import re
from pypers.core.step import CmdLineStep

class MPileup(CmdLineStep):
    spec = {
        "version": "2.3.9",
        "descr": [
            "Runs varscan for variant detection (SNPs and indels) in mpileup file.",
            "The output are vcf files."
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input mpileup file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_snps",
                    "type"  : "file",
                    "value" : "{{input_files}}.SNP",
                    "descr" : "the vcf file containing the SNP information",
                },
                {
                    "name"  : "output_indels",
                    "type"  : "file",
                    "value" : "{{input_files}}.INDEL",
                    "descr" : "the vcf file containing the indel information"
                },
                {
                    "name"  : "output_cns",
                    "type"  : "file",
                    "value" : "{{input_files}}.CNS",
                    "descr" : "the vcf file containing the consensus information"
                }
            ],
            "params": [
                {
                    "name"  : "do_vcf",
                    "type"  : "boolean",
                    "descr" : "Create vcf output",
                    "value" : False
                },
                {
                    "name"  : "variants",
                    "type"  : "boolean",
                    "descr" : "Report only variant positions",
                    "value" : False
                },
                {
                    "name"  : "pvalue",
                    "type"  : "float",
                    "descr" : "Default p-value threshold for calling variants",
                    "value" : 0.001
                },
                {
                    "name"  : "minvarfreq",
                    "type"  : "float",
                    "descr" : "Minimum variant allele frequency threshold",
                    "value" : 0.001
                }
            ]
        },
        "cmd": [
            "/usr/bin/java -Djava.io.tmpdir={{output_dir}} -jar /software/pypers/varscan/VarScan.v2.3.9.jar mpileup2snp",
            "   {{input_files}} --p-value {{pvalue}} --min-var-freq {{minvarfreq}} {{cmd_params}} > {{output_snps}}",
            "&& /usr/bin/java -Djava.io.tmpdir={{output_dir}} -jar /software/pypers/varscan/VarScan.v2.3.9.jar mpileup2indel",
            "   {{input_files}} --p-value {{pvalue}} --min-var-freq {{minvarfreq}} {{cmd_params}} > {{output_indels}}",
            "&& /usr/bin/java -Djava.io.tmpdir={{output_dir}} -jar /software/pypers/varscan/VarScan.v2.3.9.jar mpileup2cns",
            "   {{input_files}} --p-value {{pvalue}} --min-var-freq {{minvarfreq}} {{cmd_params}} > {{output_cns}}",
        ]
    }

    def preprocess(self):
        """
        Output name extension depends on input params
        Also process some command line parameters
        """
        self.cmd_params = ""
        if self.do_vcf:
            self.cmd_params += "--output-vcf "
            for output, value in self.get_outputs().iteritems():
                setattr(self, output, value+".vcf")
        if self.variants:
            self.cmd_params += "--variants "


