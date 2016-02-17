from pypers.core.step import CmdLineStep

class MPileup(CmdLineStep):
    spec = {
        "descr": [
            "Generate BCF or pileup for one or multiple BAM files."
        ],
        "version":"0.1.19",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_bams",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "one or more bam files",
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
                    "descr"     : "the output mpileup file",
                    "value"     : "{{input_bams}}.mpileup"
                },
            ],
            "params": [
                {
                    "name"      : "coefficient",
                    "type"      : "int",
                    "descr"     : "Mapping quality adjustment",
                    "value"     : 50
                },
                {
                    "name"      : "minq",
                    "type"      : "int",
                    "descr"     : "Minimum mapping quality for an alignment to be used",
                    "value"     : 50
                },
                {
                    "name"      : "minQ",
                    "type"      : "int",
                    "descr"     : "Minimum base quality for a base to be considered",
                    "value"     : 35
                },
                {
                    "name"      : "maxreads",
                    "type"      : "int",
                    "descr"     : "Maximum number of reads to be read from BAM at a position",
                    "value"     : 2000000
                },
             ]
        },
        "cmd": [
            "/software/pypers/samtools/samtools-0.1.19/bin/samtools mpileup",
            " -C {{coefficient}} -q {{minq}} -Q {{minQ}} -d {{maxreads}}",
            " -f {{ref_path}}  {{input_bams}}  > {{output_files}}",
        ]
    }
