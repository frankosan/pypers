import os
import re
from pypers.steps.genome_annotation.kbase import KbaseStep

class ExportGenome(KbaseStep):
    spec = {
        "name": "ExportGenome",
        "version": "2015.08.31",
        "descr": [
            """
            Export Genome to specified format, default to Genbank format
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_genome",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the name of the input genome file"
                }
            ],
            "outputs": [
                {
                    "name"     : "output_genome",
                    "type"     : "file",
                    "descr"    : "the name of the exported output file"
                }
            ],
            "params": [
                {
                    "name"  : "output_format",
                    "type"  : "str",
                    "descr" : "output format: genbank (default), gff or embl",
                    "value" : "genbank"
                },
                {
                    "name"  : "taxon_ref",
                    "type"  : "file",
                    "descr" : "genome names taxon ref file",
                    "value" : "/nihs/Bioinformatics/NCC/MiSeq/development_II/Scripts/names.dmp"
                },
                {
                    "name"  : "ncc_typestrains_ref",
                    "type"  : "file",
                    "descr" : "NCC typestrains ref file",
                    "value" : "/nihs/Bioinformatics/NCC/MiSeq/development_II/Scripts/typestrains.2.txt"
                }
            ]
        }
    }
    def reformat_gbk(self,input_gbk, output_gbk):

        # Fix the genbank etry, swapping complement positions and adding a taxon
        # For NCC data (filename prefix NCC), make further modifications

        # store non-NCC taxa
        TAXON={}
        refh = open(self.taxon_ref)
        for line in refh:
            #1029822 Lactobacillus salivarius NIAS840
            (taxon,species) = line.rstrip().split('\t')
            TAXON[species] = taxon

        # If NCC dataset, find and store NCC taxon and species name
        ncc_id = None
        ncc_taxon = None
        ncc_name = None
        ncc_organism = None

        match = re.search(r'^(NCC\w*)\.',os.path.basename(input_gbk))
        if match:
            ncc_id = match.group(1)
            # Read in NCC strains ref file
            # Format taxon ID, NCC no, species, ATCC no
            #1167629^INCC282^IBifidobacterium animalis ATCC 27673$

            refh = open(self.ncc_typestrains_ref)
            for ln in refh:
                (ncc_taxon,ncc,ncc_name) = ln.rstrip().split('\t')

                if ncc == ncc_id:
                    ncc_organism = '%s - %s' % (ncc_name, ncc_id)
                    break

        ofh = open(output_gbk,'w')
        inh = open(input_gbk)
        for line in inh:

            # Swap complement positions, eg complement(1818..1114) > complement(1114..1818)
            match = re.search(r'complement\((\d*)\.\.(\d*)\)', line)
            if match:
                line = line.replace(match.group(0),'complement(%s..%s)' % (match.group(2),match.group(1)))
                ofh.write(line)

            elif '/db_xref=' in line:
                # replace /db_xref="RAST2:kb|g.261897.CDS.2041" with /db_xref="RAST2.kb.g.261897.CDS.2041"
                line = line.replace('kb|g','kb.g')
                line = line.replace('RAST2:kb','RAST2.kb')
                ofh.write(line)

            elif '/note=' in line:
                line = line.replace('kb|g','kb.g')
                ofh.write(line)

            else:
                match = re.search(r'/organism="(.*)"', line)
                if match:
                    organism_name = match.group(1)
                    taxid_line = ''
                    if ncc_id:
                        if ncc_organism:
                            # Add /organism NCC id and species name including eg
                            #   /organism="Lactobacillus salivarius ATCC 11741 - NCC1264"
                            line = line.replace(organism_name,ncc_organism)
                            taxid_line = '                     /db_xref="taxon:%s"\n' % ncc_taxon
                        else:
                            line = line.replace(organism_name,"%s %s" % (organism_name, ncc_id))

                            if organism_name in TAXON:
                                taxid_line = '                     /db_xref="taxon:%s"\n' % TAXON[organism_name]
                    else:
                        if organism_name in TAXON:
                            taxid_line = '                     /db_xref="taxon:%s"\n' % TAXON[organism_name]

                    ofh.write(line)

                    # Add a taxid line  /db_xref="taxon:1423799"
                    if taxid_line:
                        ofh.write(taxid_line)
                else:
                    ofh.write(line)

        ofh.close()

    def process(self):

        formats = {'genbank' : 'gbk', 
                   'genbank_merged' : 'gbk', 
                    'feature_data' : 'txt', 
                    'protein_fasta' : 'fa', 
                    'contig_fasta' : 'fa', 
                    'contig_fasta' : 'fa', 
                    'gff' : 'gff', 
                    'embl' : 'embl'
        }

        if not self.output_format in formats:
            raise Exception("Invalid format %s", self.output_format)

        self.output_genome = "%s/%s.%s" % (self.output_dir,os.path.splitext(os.path.basename(self.input_genome))[0],formats[self.output_format])

        cmd = "perl %s/rast_export_genome.pl --input %s --output %s %s" % (self.perl_bin_path, self.input_genome, self.output_genome, self.output_format)
        self.submit_cmd(cmd, extra_env=self.extra_env)

        if self.output_format == 'genbank':
            output_gbk = self.output_genome.replace('.gbk','.fix.gbk')
            self.reformat_gbk(self.output_genome, output_gbk)

            self.output_genome = output_gbk
