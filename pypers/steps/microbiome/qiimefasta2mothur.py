from pypers.core.step import Step
import os
import re


class QiimeFasta2Mothur(Step):
    spec = {
        "version": "19.10.15",
        "descr": [
            """
            Converts qiime fasta file for mothur, reformatting the header, and writing a groups and names file
            Also writes a basic mapping file for use by emperor plots containing sample ids
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_fasta",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "The input qiime fasta file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_fasta",
                    "type"  : "file",
                    "descr" : "Output mothur fasta file"
                },
                {
                    "name"  : "output_groups",
                    "type"  : "file",
                    "descr" : "Output mothur groups file"
                },
                {
                    "name"  : "output_names",
                    "type"  : "file",
                    "descr" : "Output mothur names file, (all lines single-entry)"
                },
                {
                    "name"  : "output_map",
                    "type"  : "file",
                    "descr" : "Output map file with sample nmaes for use by qiime make_emperor"
                }
            ],
            "params": [
            ]
        },
    }


    def process(self):

        fileName, fileExt = os.path.splitext(os.path.basename(self.input_fasta))
        self.output_fasta = '%s/%s.mothur%s' % (self.output_dir,fileName,fileExt)
        self.output_groups = '%s/%s.groups' % (self.output_dir,fileName)
        self.output_names = '%s/%s.names' % (self.output_dir,fileName)
        self.output_map = '%s/%s.map' % (self.output_dir,fileName)

        self.log.info('Formatting %s for mothur' % self.input_fasta)

        ifile = open(self.input_fasta,'ro')
        op_fasta = open(self.output_fasta,'w')
        op_groups = open(self.output_groups,'w')
        op_names = open(self.output_names,'w')

        recs_in = 0
        fasta_recs_out = 0
        sample_ids = set()

        # Look for fasta header with sampleid, readid ...
        # >Golay019.1_0 HWI-M00228:29:000000000-A392V:1:1101:16909:2176 1:N:0: orig_bc=GTCAATTGACCC new_bc=GTCAATTGACCG bc_diffs=1


        pattern = re.compile('^>(\S+)\_\d+\s+(\S+)')

        for read in ifile:
            hdr = pattern.match(read)
            if hdr:
                recs_in += 1
                # Need to sampleid convert eg >D7_60_797 to >D7.60_797 because qiime truncates after underscore
                sampleid = hdr.group(1).replace('_', '.')

                readid = hdr.group(2).replace(':','_')

                op_fasta.write('>%s\n' % readid)
                fasta_recs_out += 1

                op_groups.write('%s\t%s\n' % (readid, sampleid))
                op_names.write('%s\t%s\n' % (readid, readid))

                sample_ids.add(sampleid)
            else:
                op_fasta.write(read)

        ifile.close()
        op_fasta.close()
        op_groups.close()
        op_names.close()

        op_map = open(self.output_map,'w')
        op_map.write('#SampleID\tBarcodeSequence\tLinkerPrimerSequence\tDescription\n')
        for sample in sample_ids:
            op_map.write('%s\tNone\tNone\tNone\n' % sample)
        op_map.close()

        self.log.info('Input fasta seqs: %s Output seqs: %s' %(recs_in, fasta_recs_out))
