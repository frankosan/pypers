import os
import re

from pypers.core.step import CmdLineStep
from pypers.utils import utils



class FastqScreen(CmdLineStep):
    spec = {
        "name": "FastqScreen",
        "version": "1.119",
        "descr": [
            "Runs picard tool CleanSam to set the MAPQ score to 0 for unmapped reads"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    "iterable" : True,
                    "descr"    : "the input files paired by reads"
                },
            ],
            "outputs": [
                {
                    "name"  : "txt_files",
                    "type"  : "file",
                    "descr" : "fastq screen output files",
                    "value" : "*_screen.txt"
                },
                {
                    "name"  : "png_files",
                    "type"  : "file",
                    "descr" : "png output files",
                    "value" : "*_screen.png"
                }

            ],
            "params": [
                {
                    "name"     : "subset_reads",
                    "type"     : "int",
                    "value"    : 5000,
                    "descr"    : "the subset read region"
                },
                {
                    "name"     : "cfg_data",
                    "type"     : "str",
                    "value"    : '''
BOWTIE2 /software/pypers/bowtie/bowtie-2.0.6/bin/bowtie2
DATABASE    Human       /Public_data/genomes/Homo_sapiens/hg19/bowtie2/human19    BOWTIE2
DATABASE    Mouse       /Public_data/genomes/Mus_musculus/mm9/bowtie2/mouse9      BOWTIE2
DATABASE    H_rRNA      /Public_data/genomes/Homo_sapiens/contamination/rRNA/human_rRNA BOWTIE2
DATABASE    M_rRNA      /Public_data/genomes/Mus_musculus/contamination/rRNA/mouse_rRNA BOWTIE2
DATABASE    H_globin    /Public_data/genomes/Homo_sapiens/contamination/globin/human_globin BOWTIE2
DATABASE    M_globin    /Public_data/genomes/Mus_musculus/contamination/globin/mouse_globin BOWTIE2
DATABASE    Dog         /Public_data/genomes/Dog/bowtie2/dog                      BOWTIE2
DATABASE    Biflongum   /Public_data/genomes/B_longum/bowtie2/B_longum_NCC2705    BOWTIE2
DATABASE    phiX        /Public_data/genomes/phiX/bowtie2/phiX                    BOWTIE2
DATABASE    Adapters    /Public_data/genomes/illumina_adapter/bowtie2/adapters    BOWTIE2
DATABASE    Spike_ERCC  /Public_data/genomes/ERCC/bowtie2/ERCC_140502             BOWTIE2''',
                    "descr"    : "the db path for each species"
                }
            ]        
        },
        "cmd": [
            "/software/pypers/fastq_screen/fastq_screen_v0.4.4/fastq_screen ",
            "--subset {{subset_reads}} {{paired}} --outdir {{output_dir}} --conf {{config_file}} --aligner bowtie2",
            "{{input_r1}} {{input_r2}}"
        ],
        "requirements": {
            "cpus" : "6"
        }       
    }

    def process(self):
        """
        Prepare configuration and set input files
        """
        self.config_file = os.path.join(self.output_dir, 'db_config.cfg')
        with open(self.config_file, 'w') as fh:
            fh.write(self.cfg_data)
        self.paired = " "
        if (type(self.input_files) == list \
           and len(self.input_files) == 2):
            self.paired = "--paired"
            self.input_r1 = self.input_files[0]
            self.input_r2 = self.input_files[1]
        else:
            self.input_r1 = self.input_files
            self.input_r2 = ''

        self.subset_reads = str(self.subset_reads)
        super(FastqScreen,self).process()
