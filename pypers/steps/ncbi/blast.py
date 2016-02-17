from pypers.core.step import CmdLineStep

class Blast(CmdLineStep):
    spec = {
        "version": "2.2.28+",
        "descr": [
            "Nucleotide-Nucleotide BLAST 2.2.28+"
        ],
        "args":
        {
            "inputs": [
                {
                    "name" : "input_files",
                    "type" : "file",
                    "iterable" : True,
                    "descr" : "list of fasta files to be blasted"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "output files containing the blast results",
                    "value" : "{{input_files}}.out"
                }
            ],
            "params": [
                {
                    "name"  : "database",
                    "type"  : "file",
                    "descr" : "BLAST database name"
                },
                {
                    "name"  : "task",
                    "type"  : "enum",
                    "options": ['blastn', 'blastn-short', 'dc-megablast', 'megablast', 'rmblastn'],
                    "value" : 'megablast',
                    "descr" : "the task to execute"
                },
                {
                    "name" : "evalue",
                    "type" : "float",
                    "descr": "expectation value threshold for saving hits",
                    "value": 10
                },
                {
                    "name" : "outformat",
                    "type" : "enum",
                    "options" : range(12),
                    "descr": "alignment view options"
                }
            ]
        },
        "cmd" : [
            "/software/pypers/ncbi-blast/ncbi-blast-2.2.28+/bin/blastn -query  {{input_files}} ",
            "-db {{database}} -task {{task}} -evalue {{evalue}} -outfmt {{outformat}} ",
            "-out {{output_files}} -num_threads {{cpus}}"
        ],
        "requirements": {
            "cpus" : "5"
        }    
    }



