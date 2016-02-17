from pypers.core.step import Step
import os
import json
import re

class Oligos2Map(Step):
    """
        Generates a meta-data map file used for Emperor PCoA and rarefaction plots from an oligos file
    From
        forward CCAGCAGCCGCGGTAA
        barcode ATTACGGCAG  HTSt201c
        ...
    To
        #SampleID   BarcodeSequence LinkerPrimerSequence    Description
        HTSt201c    ATTACGGCAG  CCAGCAGCCGCGGTAA    None
        ...

    The oligos 'forward' line must preceed the 'barcode' lines

    """

    spec = {
        'name'    : 'Oligos2Map',
        'version' : '20150519',
        'descr'   : [
            'Generates a meta-data map file used for Emperor PCoA and rarefaction plots from a qiime-format oligos file'
        ],
        'args' : {
            'inputs'  : [
                    { 
                        'name'     : 'input_oligos',
                        'type'     : 'file',
                        'iterable' : False,
                        'descr'    : 'input qiime format oligos filename'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_map',
                        'type' : 'file',
                        'descr': 'output plotting map filename'
                    }
                ],
            'params'  : [
            ]
        },
        'requirements' : {}
    }

    
    def process(self):
        """
        Implement step process
        """

        fileName, fileExt = os.path.splitext(os.path.basename(self.input_oligos))
        self.output_map = '%s/%s.map.txt' % (self.output_dir,fileName)

        ip_fn = open(self.input_oligos,'ro')
        op_fn = open(self.output_map,'w')

        recs_out = 0
        op_fn.write('%s\n' % '\t'.join(['#SampleID','BarcodeSequence','LinkerPrimerSequence','Description']))

        # Pattern to Look for oligos header with forward primer seq
        # forward CCAGCAGCCGCGGTAA
        hdr_pattern = re.compile('^forward\t(\S+)')
        primer = ''

        for read in ip_fn:

            hdr = hdr_pattern.match(read)
            if hdr:
                primer = hdr.group(1)
            else:
                if read.startswith('barcode'):
                    flds = read.split()
                    sample = flds[2]
                    barcode = flds[1]
                    op_fn.write('%s\n' % '\t'.join([sample,barcode,primer,'None']))
                    recs_out += 1

        ip_fn.close()
        op_fn.close()

        self.log.debug('Wrote %s data lines to %s', recs_out, self.output_map)

