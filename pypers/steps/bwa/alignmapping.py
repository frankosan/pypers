from pypers.core.step import CmdLineStep

class AlignMapping(CmdLineStep):
    spec = {
        "version": "0.6.1",
        "descr": [
            "Runs bwa mapping using the aln algorithm and generates an sai file"
        ],
        "args":
        {
            "inputs": [
                {
                    "name" : "input_files",
                    "type" : "file",
                    "iterable" : True,
                    "descr" : "list of fastq files to be aligned"
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
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "output files containing the alignment results",
                    "value" : "{{input_files}}.sai"
                }
            ],
            "params": [
            ]
        },
        "cmd" : [
            "/software/pypers/bwa/bwa-0.6.1/bwa aln -t {{cpus}} -l 32 -k 2",
            "{{ref_path}} {{input_files}} > {{output_files}}"
        ],
        "requirements" : {
            "cpus" : "6"
        }
    }
