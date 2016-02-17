import os
import re
from pypers.core.step import FunctionStep

class PairByRead(FunctionStep):
    """
    Return list of files paired by reads
    Considers the following cases:
    - each R1 has an R2 => return list [R1,R2] pairs
    - only R1s or only R2s => return R1 (resp. R2) list
    - anything else: raise exception
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns list of files paired by reads"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "descr"    : "the input files",
                },
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "output file names",
                }
            ]
        }
    }

    def process(self):
        ret_list = []
        meta_list = []
        store_meta = ('sample_id' in self.meta['job'])

        # Make a table of file:meta
        lookup = {}
        if store_meta:
            for index in xrange(0, len(self.input_files)):
                lookup[self.input_files[index]] = self.meta['job']['sample_id'][index]

        read1s = [f for f in self.input_files if f.find('_R1_') >= 0]
        read2s = [f for f in self.input_files if f.find('_R2_') >= 0]
        if len(read1s) == len(read2s):
            for r1 in read1s:
                r2base = os.path.basename(r1.replace('_R1_', '_R2_'))
                pat = re.compile('.*' + r2base + '$')
                r2 = filter(pat.match, read2s)
                if len(r2) == 0:
                    raise Exception("No matching R2 for %s" % r1)
                elif len(r2) > 1:
                    raise Exception("Too many matching R2s for %s: %s" % (r1, ' '.join(r2)))
                else:
                    ret_list.append([r1, ''.join(r2)])
                    if store_meta:
                        meta_list.append(lookup[r1])
        elif len(read2s) == 0 and len(read1s) > 0:
            ret_list = read1s
            if store_meta:
                   meta_list = [lookup[m] for m in ret_list]
        elif len(read1s) == 0 and len(read2s) > 0:
            ret_list = read2s
            if store_meta:
                meta_list = [lookup[m] for m in ret_list]
        else:
            raise Exception("Different number of R1 and R2 found (%d/%d)" % (len(read1s), len(read2s)))

        self.output_files = ret_list
        self.meta['job']['sample_id'] = meta_list
