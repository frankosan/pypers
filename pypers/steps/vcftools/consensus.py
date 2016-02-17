from pypers.core.step import CmdLineStep

class Consensus(CmdLineStep):
    spec = {
        "version":"0.1.10",
        "descr": [
            "Apply VCF variants to a fasta file to create consensus sequence."
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input vcf consensus file",
                },
                {
                    "name"  : "ref_path",
                    "type"  : "ref_genome",
                    "tool"  : "bwa",
                    "descr" : "path to the directory containing the reference genome"
                }
            ],
            "outputs": [
                {
                    "name"      : "output_files",
                    "type"      : "file",
                    "descr"     : "the output vcf consensus file",
                    "value"     : "{{input_files}}.consensus_ref.fasta"
                },
            ],
            "params": [
             ]
        },
        "extra_env": {
            "PERLLIB": "/software/pypers/vcftools/vcftools_0.1.10/perl",
            "PATH"   : "/software/pypers/samtools/samtools-1.2/bin"  # For tabix, needed by vcf-consensus
        },
        "cmd": [
            "cat {{ref_path}} | /software/pypers/vcftools/vcftools_0.1.10/bin/vcf-consensus {{input_files}} > {{output_files}}"
        ]
    }
