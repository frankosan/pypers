from pypers.core.step import CmdLineStep

class Coverage(CmdLineStep):
    spec = {
        "version" : "2.16.2",
        "descr": [
            "Runs the bedtools coverage annotation tool"
        ],
        "args" : 
        {
            "inputs" : [
                {
                    "name"  : "input_files",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "a list of bam files to be annotated against a reference file",
                },
                {
                    "name"  : "ref_file",
                    "type"  : "ref_genome",
                    "descr" : "reference file to use in the annotation",
                    "tool"  : "bedtools"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "the name of the output annotation files",
                    "value" : "annotation_count.gff"
                }
            ],
            "params": [
            ],
        },
        "cmd" : [
            "/software/pypers/bedtools/bedtools-2.16.2/bin/bedtools coverage",
            "-abam {{input_files}} -b {{ref_file}}",
            "> {{output_files}}"
        ]
    }
