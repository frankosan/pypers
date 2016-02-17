import os
import re
import shutil
import textwrap
from pypers.core.step import Step, STEP_PICKLE
from pypers.utils import utils as ut


class ShiftReference(Step):
    spec = {
        "version": "0.1",
        "descr": [
            "Create a shifted reference from an original reference.",
            "Also indexes it with bwa index"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "ref_genome",
                    "tool"     : "bwa",
                    "descr"    : "the reference to shift"
                }
            ],
            "outputs": [
                {
                    'name' : 'output_files',
                    'type' : 'file',
                    'descr': 'the shifted reference',
                    'value': '{{input_files}}_shifted.fa'
                },
                {
                    'name' : 'shift_pos',
                    'type' : 'str',
                    'descr': 'the number of shifted positions'
                }
            ],
            "params" : [
                {
                    'name':  'shift',
                    'type':  'int',
                    'descr': 'the number of positions to shift the reference with',
                    'value': 8000
                }
            ],
        }
    }

    def process(self):
        if hasattr(self.input_files, '__iter__'):
            reffile = self.input_files[0]
        else:
            reffile = self.input_files

        ref_text = ''
        with open(reffile) as fh:
            title = fh.readline().rstrip()
            for line in (fh):
                ref_text += line.rstrip('\n').rstrip()

        if ref_text:
            new_ref = ref_text[-self.shift:]+ref_text[0:-self.shift]

            if len(new_ref) != len(ref_text):
                raise Exception("Reference lengths do not match: %d (new), %d (old)" 
                                % (len(new_ref), len(ref_text)))

            with open(self.output_files, "w") as fh:
                if len(title)>30:
                    title = title[:30]+'...'
                fh.write("%s shifted to position %d\n" % (title, self.shift))
                fh.write(textwrap.fill(new_ref, width=60))


            self.shift_pos = str(self.shift) # there must be a better way...

            # Now index it
            cmd = ['/software/pypers/bwa/bwa-0.7.6a/bwa index %s' % self.output_files]
            self.submit_cmd(cmd)

