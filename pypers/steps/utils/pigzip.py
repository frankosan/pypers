import os
import json

from pypers.core.step import Step

class PigZip(Step):
    """
    Unzip the input files.
    The output name is of the form [basename(input)].fastq
    """

    spec = {
        'version' : '1.0',
        'descr'   : [
            'Runs parallelized g[un]zip tool pigzip'
        ],
        'args' : {
            'inputs'  : [
                    {
                        'name'      : 'input_files',
                        'type'      : 'file',
                        'iterable'  : True,
                        'descr'     : 'input zip file names'
                    }
                ],
            'outputs' : [
                    {
                        'name'      : 'output_files',
                        'type'      : 'file',
                        'descr'     : 'output file name'
                    }
                ],
            'params'  : [
                    {
                        'name'      : 'executable',
                        'type'      : 'str',
                        'descr'     : 'full path to pigz',
                        'value'     : 'pigz',
                        'readonly'  : True
                    }
                ]
        },
        'requirements' : {}
    }

    def process(self):
        """
        Run the step as configured.
        """
        if type(self.input_files) != list:
            self.input_files = [self.input_files]

        self.output_files = []
        for input_file in self.input_files:
            # Form output
            print '[PigZip] Unzipping',input_file
            basename = os.path.basename(input_file).replace('.fastq.gz', '')
            basename = basename.replace('.fq.gz', '')
            basename = basename.replace('.fq', '')
            output_file = os.path.join(self.output_dir,basename+'.fastq')
            self.output_files.append(output_file)

            cmd = '{executable} -dc {input} > {output_file}'.format(
                       executable=self.executable,
                       input=input_file,
                       output_file=output_file)
            self.submit_cmd(cmd)
