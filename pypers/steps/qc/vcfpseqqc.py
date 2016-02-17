import os
from pypers.core.step import CmdLineStep


class VcfPseqQc(CmdLineStep):
    spec = {
        "name": "VcfPseqQc",
        "version": "0.08",
        "descr": [
            "Runs VcfPseqQc on the input files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_file",
                    "type"     : "file",
                    "descr"    : "the input vcf file",
                }
            ],
            "outputs": [
                {
                    "name"      : "filtered_vcf",
                    "type"      : "file",
                    "value"     : "*.vcf",
                    "descr"     : "the filtered vcf file"
                },
                {
                    "name"      : "summary",
                    "type"      : "file",
                    "value"     : "*.summary",
                    "descr"     : "the summary report"
                }
            ],
            "params": [
                {
                    "name"     : "pseq_exe",
                    "type"     : "str",
                    "value"    : "/software/pypers/plinkseq/plinkseq-0.08-x86_64/bin/pseq",
                    "descr"    : "the pseq executable",
                    "readonly" : True
                },
                {
                    "name"     : "vcf_exe",
                    "type"     : "str",
                    "value"    : "/software/pypers/vcftools/vcftools_0.1.10/bin/vcftools",
                    "descr"    : "the vcf executable",
                    "readonly" : True

                },
                {
                    "name"     : "sample_exclusion",
                    "type"     : "file",
                    "value"    : "/Public_data/EXTERNAL_DATA/1000G_DATA/phase3/1KG_phase3_processing/list_of_samples.txt",
                    "descr"    : "list of sample to exclude",
                    "readonly" : True

                },
                {
                    "name"     : "resources",
                    "type"     : "dir",
                    "value"    : "/Public_data/EXTERNAL_DATA/PSEQ_HG19",
                    "descr"    : "resource parameter",
                    "readonly" : True

                }
            ]
        },
        "cmd": [
            "{{pseq_exe}} {{pseq_output_dir}} new-project --vcf {{input_file}} --resources {{resources}} && ",
            "{{pseq_exe}} {{pseq_output_dir}} load-vcf --vcf {{input_file}} && ",
            "{{pseq_exe}} {{pseq_output_dir}} v-stats > {{pseq_output_dir}}.variantsQC.txt && ",
            "{{vcf_exe}} --vcf {{input_file}} --out {{output_dir}}/filtered.vcf --recode --remove {{sample_exclusion}} && ",
            "{{pseq_exe}} {{pseq_output_dir}} new-project --vcf {{pseq_output_dir}}/filtered.vcf --resources {{resources}} && ",
            "{{pseq_exe}} {{pseq_output_dir}} load-vcf --vcf {{pseq_output_dir}}/filtered.vcf && ",
            "{{pseq_exe}} {{pseq_output_dir}} v-stats > {{pseq_output_dir}}.variantsQC.final.txt && ",
            "{{pseq_exe}} {{pseq_output_dir}} i-stats > {{pseq_output_dir}}.indsQC.final.txt && ",
            "{{pseq_exe}} {{pseq_output_dir}} write-ped --name {{pseq_output_dir}} && ",
            "{{pseq_exe}} {{pseq_output_dir}} meta-matrix > {{pseq_output_dir}}.indsQC.snpAnnotation.txt && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --site-mean-depth && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --depth && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --freq && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --site-quality && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --geno-depth && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --het && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --hardy && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --missing && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --TsTv 500000 && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --TsTv-by-qual && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --FILTER-summary && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --singletons && ",
            "{{vcf_exe}} --remove {{sample_exclusion}} --vcf {{input_file}} --out {{output_dir}}/VCFTOOLS_QC --site-pi"
        ]
    }

    def process(self):

        self.pseq_output_dir = os.path.join(self.output_dir, 'PSEQ_QC')

        for cmd in [c.strip() for c in self.render().split("&&")]:
            self.submit_cmd(cmd)

        src_name = 'VCFTOOLS_QC.frq'
        dst_name = 'VCFTOOLS_QC.biAllelic.frq'
        if not os.path.exists(src_name):
            self.log.info('%s does not exist: skipping rest of the step.' % src_name)
        else:
            header = 'CHROM\tPOS\tN_ALLELES\tN_CHR\tA1\tA1freq\tA2\tA2freq\n'
            with open(src_name, 'r') as src, open(dst_name, 'w') as dst:
                dst.write(header)
                for line in src.readlines():
                    tokens = line.split()
                    if(tokens[2] == '2'):
                        dst.write(line.replace(':', '\t'))
