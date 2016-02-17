from pypers.core.step import CmdLineStep

class Tabix(CmdLineStep):
    spec = {
        "descr": [
            "Tabix indexes a TAB-delimited genome position file and creates an index file.",
            "Since it expects a compressed file, the sister utility bgzip is first used on the input.",
            "The outputs consist of the gzipped input VCF file and its index file."
        ],
        "version": "1.2.1",
        "args": 
        {
            "inputs": [
                {
                    "name"  : "input_files",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "a list of vcf files to be indexed",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_index",
                    "type"  : "file",
                    "value" : "{{input_files}}.tbi",
                    "descr" : "index file",
                },
                {
                    "name"  : "output_vcf",
                    "type"  : "file",
                    "value" : "{{input_files}}.gz",
                    "descr" : "index file",
                }
            ]
        },
        "cmd": [
            "/software/pypers/samtools/samtools-1.2/bin/bgzip -c {{input_files}} > {{output_vcf}}",
            "&& /software/pypers/samtools/samtools-1.2/bin/tabix -p vcf {{output_vcf}}",
        ]
    }

