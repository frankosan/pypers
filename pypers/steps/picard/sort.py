import re
import os
from pypers.core.step import CmdLineStep

class Sort(CmdLineStep):
    spec = {
        "version": "1.119",
        "descr": [
            "Runs picard tool to sort a sam or bam file"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input sam/bam file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "dummy",
                    "descr" : "the sorted sam/bam output file name (defined in pre-process function)",
                }
            ],
            "params": [
                {
                    "name" : "sort_order",
                    'type' : 'enum',
                    'options' : [ 'unsorted', 'queryname', 'coordinate' ],
                    'value' : 'coordinate',
                    "descr" : "Sort order of output file. Possible values: {unsorted, queryname, coordinate}"
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
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/SortSam.jar",
            " I={{input_files}} O={{output_files}}",
            " SO={{sort_order}} VALIDATION_STRINGENCY={{validation_stringency}}"
        ],
        "requirements": {
            "memory" : "8"
        }
    }

    def preprocess(self):
        """
        Set output name depending on whether the input is a sam or a bam.
        """
        file_name = os.path.basename(self.input_files)
        if re.search('.sam$', self.input_files) is None:
            self.output_files = file_name.replace('.bam','.sort.bam')
        else:
            self.output_files = file_name.replace('.sam','.sort.sam')
        super(Sort, self).preprocess()


