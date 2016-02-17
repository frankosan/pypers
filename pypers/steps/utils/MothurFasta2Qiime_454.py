from pypers.core.step import Step
import os
import json
import re

class MothurFasta2Qiime_454(Step):
    """
    Generates a deuniqued fasta file for qiime processing, from input mothur fasta, .names and .groups files
    """

    spec = {
        'name'    : 'MothurFasta2Qiime_454',
        'version' : '20150512',
        'descr'   : [
            'Generates a deuniqued fasta file for qiime processing, from input mothur fasta, .names and .groups files'
        ],
        'args' : {
            'inputs'  : [
                    { 
                        'name'     : 'input_fasta',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input fasta filename'
                    },
                    { 
                        'name'     : 'input_names',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input names filename'
                    },
                    { 
                        'name'     : 'input_groups',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input groups filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_fasta',
                        'type' : 'file',
                        'descr': 'output fasta filename'
                    }
                ],
        },
        'requirements' : {}
    }

    
    def process(self):
        """
        Implement step process
        """

        if type(self.input_fasta) != list:
            self.input_fasta = [self.input_fasta]
        if type(self.input_names) != list:
            self.input_names = [self.input_names]
        if type(self.input_groups) != list:
            self.input_groups = [self.input_groups]

        for idx, input_fasta in enumerate(self.input_fasta):

            self.output_fasta = re.sub('.fasta$','.qiime.fn',os.path.join(self.output_dir,os.path.basename(input_fasta)))

            ip_fn = open(input_fasta,'ro')
            ip_groups = open(self.input_groups[idx],'ro')
            ip_names = open(self.input_names[idx],'ro')
            op_fn = open(self.output_fasta,'w')

            # put Groups file into a dictionary
            # readid / sample
            # HWI-M00228_29_000000000-A392V_1_1101_16909_2176 Golay019.1

            gp_ids = {}
            for read in ip_groups:
                flds = read.rstrip().split('\t')
                gp_ids[flds[0]] = flds[1]
            ip_groups.close()

            # Names file, format READ1 <tab> READ1,READ2,...
            name_ids = {}
            for read in ip_names:
                flds = read.rstrip().split()
                name_ids[flds[0]] = flds[1]
            ip_names.close()

            fasta_recs_in = 0
            fasta_recs_out = 0

            # Pattern to Look for fasta header with read id
            # >HWI-M00228_29_000000000-A392V_1_1101_16909_2176
            gp_ids_pattern = re.compile('^>(\S+)')

            for read in ip_fn:

                hdr = gp_ids_pattern.match(read)
                if hdr:
                    fasta_recs_in += 1
                    readid = hdr.group(1)
                    try:
                        readids = name_ids[readid].split(',')
                    except KeyError:
                        raise Exception('[Cannot find readid %s in %s]' % (readid,input_names))

                else:
                    #Deunique - write a seperate fasta read for each read id in the .names file
                    for rid in readids:
                        # remove 454 fasta . and - from sequences which cause pick_closed_reference_otus to core dump

                        read = read.replace('.', '').replace("-", '')
                        try:
                            op_fn.write('>%s_%i %s\n' % (gp_ids[rid], fasta_recs_out, rid))
                        except KeyError:
                            raise Exception('[Cannot find readid %s in %s]' % (rid,input_groups))
                        op_fn.write(read)
                        fasta_recs_out += 1

            ip_fn.close()
            op_fn.close()


