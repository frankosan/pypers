from pypers.core.step import CmdLineStep

class CleanSam(CmdLineStep):
    spec = {
        "version": "1.119",
        "descr": [
            "Runs picard tool CleanSam to set the MAPQ score to 0 for unmapped reads.",
            "Subsequently runs samtools indexing."
        ],
        "args": 
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input sam file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "value" : "{{input_files}}.clean.bam",
                    "descr" : "output file name",
                }
            ],
            "params": [
                {
                    "name"  : "jvm_args",
                    "value" : "-Xmx{{jvm_memory}}g -Djava.io.tmpdir={{output_dir}}",
                    "descr" : "java virtual machine arguments",
                    "readonly" : True
                }
            ]
        },
        "cmd": [
            "/usr/bin/java {{jvm_args}}} -jar /software/pypers/picard-tools/picard-tools-1.119/picard-tools-1.119/CleanSam.jar",
            "INPUT={{input_files}}",
            "OUTPUT={{output_files}}", 
            "; /software/pypers/samtools/samtools-0.1.18/bin/samtools index {{output_files}}"
        ],
        "requirements": { 
            "memory" : "8"
        }
    }
    
