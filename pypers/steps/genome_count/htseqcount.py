from pypers.core.step import CmdLineStep

class HtseqCount(CmdLineStep):
    spec = {
        "version" : "2.16.2",
        "descr": [
            "Runs the htseq-count annotation tool",
            "Given a file with aligned sequencing reads and a list of genomic features,", 
            "htseq-count counts how many reads map to each feature"
        ],
        "url" : 'http://www-huber.embl.de/users/anders/HTSeq/doc/count.html',
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
                    "tool"  : "htseq"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "the name of the output annotation files",
                    "value" : "annotation.txt"
                }
            ],
            "params": [
                {
                    "name"  : "mode",
                    "type"  : "enum",
                    "options" : ["union", "intersection-strict", "intersection-nonempty"], 
                    "value" : "union",
                    "descr" : "mode to handle reads overlapping more than one feature"
                },
                {
                    "name"  : "stranded",
                    "type"  : "enum",
                    "options" : ["yes", "no", "reverse"], 
                    "value" : "reverse",
                    "descr" : "whether the data is from a strand-specific assay"
                },
                {
                    "name"  : "minequal",
                    "type"  : "int",
                    "value" : 10,
                    "descr" : "skip all reads with alignment quality lower than the minimal value"
                },
                {
                    "name"  : "order",
                    "type"  : "enum",
                    "options" : ["pos", "name"],
                    "value" : "pos",
                    "descr" : "Paired-end sequencing data must be ordered by name or position. Ignored for single-end data"
                },
                {
                    "name"  : "format",
                    "type"  : "enum",
                    "options" : ["sam", "bam"],
                    "value" : "bam",
                    "descr" : "type of <alignment_file> data, either 'sam' or 'bam'"
                }
            ],
        },
        "cmd" : [
            "htseq-count -m {{mode}} -s {{stranded}} -r {{order}} -a {{minequal}} -f {{format}} ",
            "{{input_files}} {{ref_file}} > {{output_files}}"
        ],
        "requirements": {
            "cpus"   : "2"
        }       
    }
