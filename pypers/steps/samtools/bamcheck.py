from pypers.core.step import CmdLineStep

class BamCheck(CmdLineStep):
    spec = {
        "version": "0.1.19",
        "descr": [
            "Run the samtools bamcheck utility against a bam file,",
            "generating a text stats file suitable for plot-bamcheck.",
            "If a target file is provided, also creates stats for the target regions only"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"  : "input_files",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "a list of bam files to be checked",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "{{input_files}}.bamcheck.txt",
                    "descr" : "text file with qc on bam file",
                },
                {
                    "name"  : "output_targets",
                    "type"  : "file",
                    "value" : "{{input_files}}.bamcheck.target.txt",
                    "descr" : "text file with qc on bam file in target regions",
                    "required" : False
                }
            ],
            "params": [
                {
                    'name' : 'baits_file',
                    'type' : 'str',
                    'value': '',
                    'descr': 'agilent baits file. It is a file containing regions to plot (format: chr start end label)'
                },
            ]
        },
        "cmd": [
            "/software/pypers/samtools/samtools-0.1.19/bin/bamcheck {{input_files}} > {{output_files}}",
            " && if [ -f \"{{baits_file}}\" ]; then /software/pypers/samtools/samtools-0.1.19/bin/bamcheck -t {{baits_file}} {{input_files}} > {{output_targets}}; fi"
        ]
    }

