import os
import re
import vcf
import textwrap
import pandas as pd

from pypers.core.step import Step


class LfvMerge(Step):
    spec = {
        "version": "0.1.0",
        "descr": [
            "Merge results of low frequency variant calling obtained using a double reference (shifted/non-shifted).",
            "Outputs an excel file with one sheet per sample and stores the sample-by-sample consensus in fasta files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_orig",
                    "type"     : "file",
                    "descr"    : "the summary excel sheet from the original (non-shifted) reference",
                },
                {
                    "name"     : "input_shifted",
                    "type"     : "file",
                    "descr"    : "the summary excel sheet from the shifted reference",
                },
                {
                    "name"     : "shift",
                    "type"     : "str",
                    "descr"    : "the number of shifted positions"
                }
            ],
            "outputs": [
                {
                    "name"  : "output_summary",
                    "type"  : "file",
                    "descr" : "output file names",
                    "value" : "merged_summary.xls"
                },
                {
                    "name"  : "output_fasta",
                    "type"  : "file",
                    "descr" : "consensus fasta files (one per sample)",
                    "value" : ""
                }
            ],
            "params": [
                {
                    "name" : "minfreq",
                    "type" : "float",
                    "descr": "minimum frequency for alteration to be used in consensus",
                    "value": 0.5
                },
                {
                    "name" : "mincov",
                    "type" : "float",
                    "descr": "minimum fraction of average coverage for position to be considered known",
                    "value": 0.01
                }
            ]
        }
    }


    def process(self):
        fields = [ 
                    "Chrom",  "Position", "Covmp", "Ref", "Var", "Cons", "Fasta",
                    "Qdepth", "Reads1", "Reads2", "Freq", "P-value", 
                    "StrandFilter", "R1+", "R1-", "R2+", "R2-" 
                 ]
        self.output_fasta = []
        shift = int(self.shift.pop(0))
        input_orig = self.input_orig.pop(0)
        input_shifted = self.input_shifted.pop(0)

        all_orig    = pd.read_csv(input_orig,    sep='\t', header=[0,1], na_values='-').fillna(-1)
        all_shifted = pd.read_csv(input_shifted, sep='\t', header=[0,1], na_values='-').fillna(-1)
        contents = {}
        for sample_id in all_orig.columns.levels[0]:
            fasta = ''
            df_orig    = all_orig[sample_id]
            df_shifted = all_shifted[sample_id]
            contents[sample_id] = pd.DataFrame(columns=df_orig.columns)
            nrows = df_orig.index.size
            for idx in df_orig.index:
                shifted_idx = (idx+shift)%nrows
                # Check the two are aligned. Take into account missing positions in one of them
                if df_orig.loc[idx, 'Ref'] != df_shifted.loc[shifted_idx, 'Ref']:
                    if df_orig.loc[idx, 'Ref'] != -1 and df_shifted.loc[shifted_idx, 'Ref'] != -1:
                        print 'index =', idx, df_orig.loc[idx:idx+3, 'Ref'], df_shifted.loc[shifted_idx:shifted_idx+3, 'Ref']
                        raise Exception("Shifted and non-shifted summaries are not aligned")
                if df_orig.loc[idx, 'Qdepth'] > df_shifted.loc[shifted_idx, 'Qdepth']:
                    contents[sample_id].loc[idx] = df_orig.loc[idx]
                else:
                    contents[sample_id].loc[idx] = df_shifted.loc[shifted_idx]
                    contents[sample_id].loc[idx, 'Position'] = df_orig.loc[idx, 'Position']
                if contents[sample_id].loc[idx, 'Fasta']>-1:
                    fasta += contents[sample_id].loc[idx, 'Fasta']
                else:
                    contents[sample_id].loc[idx, 'Fasta'] = ''


            output_fasta = sample_id+'.fasta'
            self.output_fasta.append(output_fasta)
            with open(output_fasta, 'w') as fh:
                fh.write('>'+sample_id+'\n')
                fh.write(textwrap.fill(fasta, width=60))

            #THIS DOES NOT ALWAYS WORK: EXCEL FAILS TO READ OUTPUT FILE     
            #with pd.ExcelWriter(self.output_summary, engine='openpyxl') as writer:
            #    df.to_excel(writer, sheet_name=sample_id, index=False, columns=fields)
            #    writer.save()

        all_samples = pd.concat(contents.values(), keys=contents.keys(), axis=1)
        all_samples.dropna(axis=0, how='all', inplace=True)
        ordered = all_samples.reindex(columns=fields, level=1)
        ordered.to_csv(self.output_summary, sep='\t', index=False)


