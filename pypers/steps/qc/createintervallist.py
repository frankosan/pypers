from pypers.core.step import CmdLineStep

class CreateIntervalList(CmdLineStep):
    spec = {
        "version": "0.1.19",
        "descr": [
            "Creates an interval list file suitable for use by picard tools, e.g., CalculateHsMetrics.",
            "A SAM style header must be present in the file which lists the sequence records against which the intervals are described.",
            "The SAM header is generated from the bam file provided as input.",
            "The intervals input must be an agilent bed file to which a strand col was added"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"  : "input_files",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "the input bam file names",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "{{input_files}}.intervals.txt",
                    "descr" : "text file containing the intervals",
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
            "( /software/pypers/samtools/samtools-0.1.18/bin/samtools view -H {{input_files}}",
            "  && /bin/cat {{baits_file}}",
            "  | /bin/awk 'BEGIN {OFS=\"\t\"};{print $1,$2,$3,\"+\",$4}'",
            " ) > {{output_files}}"
        ]
    }

