from pypers.core.step import CmdLineStep

class DseqCount(CmdLineStep):
    spec = {
        "version" : "0.1.1.2",
        "descr": [
            "Runs DSEQ Count script which implements a method to test for differential exon usage",
            "in comparative RNA-Seq experiments"
        ],
        'url': 'http://bioconductor.org/packages/release/bioc/vignettes/DEXSeq/inst/doc/DEXSeq.pdf',
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
                    "value" : "exons_count.txt"
                }
            ],
            "params": [
                {
                    "name"  : "paired",
                    "type"  : "enum",
                    "options" : ["yes", "no"], 
                    "value" : "yes",
                    "descr" : "'yes' or 'no': Indicates whether the data is paired-end"
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
                    "name"  : "format",
                    "type"  : "enum",
                    "options" : ["sam", "bam"],
                    "value" : "bam",
                    "descr" : "Format of <alignment file>"
                },
                {
                    "name"  : "order",
                    "type"  : "enum",
                    "options" : ["pos", "name"],
                    "value" : "pos",
                    "descr" : "Paired-end sequencing data must be ordered by name or position. Ignored for single-end data"
                },
                {
                    "name"  : "dseq_script",
                    "type"  : "file",
                    "value" : "/pypers/develop/R_LIBS/DEXSeq/python_scripts/dexseq_count.py",
                    "descr" : "Path to the dseq python script"
                }
            ],
        },
        "cmd" : [
            "python {{dseq_script}} -p {{paired}} -s {{stranded}} -a {{minequal}} -f {{format}} -r {{order}} ",
            "{{ref_file}} {{input_files}} {{output_files}}"
        ]
    }
