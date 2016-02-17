import os
from pypers.core.step import CmdLineStep

class AddReadGroups(CmdLineStep):
    spec = {
        "version": "0.0.1",
        "descr": [
            "Runs picard AddOrReplaceReadGroups"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_bam",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input bam file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_bam",
                    "type"  : "file",
                    "value" : "dummy",
                    "descr" : "the reordered output bam",
                }
            ],
            "params": [
                {
                    "name"     : "jvm_args",
                    "value"    : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr"    : "java virtual machine arguments",
                    "readonly" : True
                },
                {
                    "name"  : "sort_order",
                    'type' : 'enum',
                    'options' : ['unsorted','queryname','coordinate'],
                    'value' : 'coordinate',
                    "descr" : "Sort order of output file. Possible values: {unsorted, queryname, coordinate}"
                },
                {
                    "name"  : "rgid",
                    'type' : 'str',
                    'value' : '1',
                    "descr" : "read group id"
                },
                {
                    "name"  : "rglb",
                    'type' : 'str',
                    'value' : 'undef',
                    "descr" : "read group library"
                },
                {
                    "name"  : "rgpu",
                    'type' : 'str',
                    'value' : 'undef',
                    "descr" : "read group platform unit"
                },
                {
                    "name"  : "rgpl",
                    'type' : 'str',
                    'value' : 'Illumina',
                    "descr" : "read group platform"
                },
                {
                    "name"  : "rgsm",
                    'type' : 'str',
                    'value' : 'undef',
                    "descr" : "read group sample id"
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/AddOrReplaceReadGroups.jar",
            " I={{input_bam}} O={{output_bam}} CREATE_INDEX=True SORT_ORDER={{sort_order}}",
            " RGID={{rgid}} RGLB={{rglb}} RGPU={{rgpu}} RGPL={{rgpl}} RGSM={{rgsm}}"
        ],
        "requirements": {
            "memory": '8'
        }
    }

    def preprocess(self):
        """
        Set output bam name and sample id if present in meta and not overwritten
        """
        if self.meta['job']['sample_id'] and self.rgsm == 'undef':
            self.rgsm = self.meta['job']['sample_id']

        file_name = os.path.basename(self.input_bam)
        self.output_bam = file_name.replace('.bam','.rg.bam')
        super(AddReadGroups, self).preprocess()

