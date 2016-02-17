from pypers.core.step import Step
import os

class RnaSeqQC(Step):
    spec = {
        "version": "0.0.1",
        "descr": [
            "Runs the Broad Institute RNA-SeQC utility for a group of bams files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_bams",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "The input RNA-Seq bam files",
                },
                {
                    "name"  : "reference",
                    "type"  : "ref_genome",
                    "tool"  : "reordersam",
                    "descr" : "Reference whole genome fasta"
                }
            ],
            "outputs": [
                    {
                        'name' : 'index_html',
                        'type' : 'file',
                        'descr': 'output index html file'
                    }
            ],
            "params": [
                {
                    "name"  : "transcript_gtf",
                    'type'    : 'enum',
                    'options' : [ '/Public_data/genomes/Homo_sapiens/hs_GRCh38.p2/Annotation/gencode.v21.annotation.gtf'
                                  '/Public_data/genomes/Homo_sapiens/hs_GRCh37_r66/Annotation/gencode.v19.annotation.gtf' ],
                    "descr" : "GTF File defining transcripts, gencode v19=hs_GRCh37_r66, v21=GRCh38",
                    "readonly": True
                },
                {
                    "name"  : "rnaseqc_jar",
                    "type"  : "str",
                    "descr" : "path to RNA-SeQC jar file",
                    "value" : "/pypers/develop/rna-seqc//RNA-SeQC_v1.1.8.jar",
                    "readonly": True
                }
            ]
        },
        "requirements": { 
        },
    }


    def process(self):

        sample_file = '%s/sample.txt' % (self.output_dir)

        op_fn = open(sample_file,'w')
        op_fn.write('Sample\tBam\tNotes\n')

        for idx,bam in enumerate(self.input_bams):

            if self.meta['job']['sample_id']:
                sample = self.meta['job']['sample_id'][idx]
            else:
                sample = 'sample%i' % idx    

            op_fn.write('%s\t%s\tNone\n' % (sample,bam))
        op_fn.close()

        cmd_args = 'java -jar %s -o %s -s %s -r %s -t %s' % (self.rnaseqc_jar, self.output_dir, sample_file, self.reference, self.transcript_gtf)

        self.index_html = '%s/index.html' % (self.output_dir)

        self.submit_cmd(cmd_args)
