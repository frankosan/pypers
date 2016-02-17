import re
import os
from pypers.core.step import CmdLineStep

class Merge(CmdLineStep):
    spec = {
        "version": "1.119",
        "descr": [
            "Runs picard tool to merge a set of sam or bam files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "descr"    : "the list of input sam/bam files",
                    "iterable" : True
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "dummy",
                    "descr" : "the merged sam/bam output file name (defined in pre-process function)",
                }
            ],
            "params": [
                {
                    "name"  : "use_threading",
                    "type"  : "boolean",
                    "value" : "True",
                    "descr" : "Whether to run part of the job in a thread."
                },
                {
                    "name"  : "validation_stringency",
                    "type"  : "enum",
                    'options' : [ 'STRICT', 'LENIENT', 'SILENT'],
                    "value" : "LENIENT",
                    "descr" : "Validation stringency for all SAM files read by this program. Possible values: {STRICT, LENIENT, SILENT}"
                },
                {
                    "name"  : "jvm_args",
                    "value" : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr" : "java virtual machine arguments",
                    "readonly" : True
                }  
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/MergeSamFiles.jar",
            " I={{input_files}} O={{output_files}}",
            " USE_THREADING={{use_threading}}"
        ],
        "requirements": { 
            "memory" : "8"
        },
    }

    def preprocess(self):
        """
        Set output name depending on whether the input are sam or bam files.
        Also concatenate input_files (because each needs to be passed to the I= option)
        """
        file_name = os.path.basename(self.input_files[0])
        if re.search('.sam$', self.input_files[0]) is None:
            self.output_files = file_name.replace('.bam','.merged.bam')
        else:
            self.output_files = file_name.replace('.sam','.merged.sam')

        if hasattr(self.input_files, '__iter__'): # Is a list
            self.input_files = ' I='.join(self.input_files)

        super(Merge, self).preprocess()


