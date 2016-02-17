from pypers.core.step import CmdLineStep

class Sam2Bam(CmdLineStep):
    spec = {
        "name": "Sam2Bam",
        "version":"0.1.18",
        "descr": [
            "Converts sam file into a bam file, sorting and indexing the output.",
            "This is done using samtools."
        ],
        "args":
        {
            "inputs": [
                {
                    "name"      : "input_files",
                    "type"      : "file",
                    "iterable" : True,
                    "descr"     : "a list of sam files",
                },
            ],
            "outputs": [
                {
                    "name"      : "output_files",
                    "type"      : "file",
                    "descr"     : "the name of the output file",
                    "value"     : "{{input_files}}.bam"
                },
            ],
            "params": [
                {
                    "name"      : "fraction",
                    "type"      : "float",
                    "descr"     : "fraction of templates to subsample; integer part as seed (e.g., 1.5 for 50%).\nSet to -1 to disable.",
                    "value"     : -1
                },
            ]
        },
        "cmd": [
            "/software/pypers/samtools/samtools-0.1.18/bin/samtools view -bS -s {{fraction}} {{input_files}}",
            "|  /software/pypers/samtools/samtools-0.1.18/bin/samtools sort -o - - > {{output_files}}",
            "&& /software/pypers/samtools/samtools-0.1.18/bin/samtools index {{output_files}}"
        ]
    }
