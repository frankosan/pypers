from pypers.core.step import Step
import os
import re
import json

class OnTargetBam(Step):
    """
    Run the bamcheck utility against a bam file, generating a text stats file suitable for plot-bamcheck
    """

    spec = {
        'version' : '0.0.1',
        'descr'   : [
            'Run the bamcheck utility against a bam file, generating a text stats file suitable for plot-bamcheck'
        ],
        'args' : {
            'inputs'  : [
                    { 
                        'name'     : 'input_checks',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input global bamcheck file names'
                    },
                    { 
                        'name'     : 'input_targets',
                        'type'     : 'file',
                        'iterable' : True,
                        'descr'    : 'input bamcheck on target file names'
                    }
                ],
            'outputs' : [
                    {
                        'name' : 'output_files',
                        'type' : 'file',
                        'descr': 'output file name'
                    }
                ],
            'params'  : [ ]
        },
        'requirements' : {}
    }
    
    def __init__(self):
        super(OnTargetBam,self).__init__()

    def process(self):
        """
        Run the step as configured.
        """
        bam_name = os.path.basename(self.input_checks).split('.')[0]
        self.output_files = bam_name + '.ontarget.txt'

        # get the reads mapped from bam_file
        reads_mapped = 0
        with open(self.input_checks, 'r') as file:
            for line in file:
                m = re.match(r'^.*reads\smapped:\s*(\d+)$', line)
                if m:
                    (reads_mapped, ) = m.groups()
                    break

        # get the reads mapped on target from target_file
        reads_target_mapped = 0
        with open(self.input_targets, 'r') as file:
            for line in file:
                m = re.match(r'^.*reads\smapped:\s*(\d+)$', line)
                if m:
                    (reads_target_mapped, ) = m.groups()
                    break

        ratio_mapped = float(reads_target_mapped) / float(reads_mapped)
        with open(self.output_files, 'w+') as file:
            file.write('reads mapped on target: %s' % reads_target_mapped)
            file.write('\n')
            file.write('reads mapped total:     %s' % reads_mapped)
            file.write('\n')
            file.write('---------------------------------------')
            file.write('\n')
            file.write('percentage on target:   %0.2f%%' % (ratio_mapped * 100))
