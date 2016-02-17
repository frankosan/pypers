import os
import re
import vcf
import textwrap
import pandas as pd

from pypers.core.step import Step


class LfvSummary(Step):
    spec = {
        "version": "0.5.0",
        "descr": [
            "Summarize results of low frequency variant calling on various samples into one single excel file",
            "and store the sample-by-sample consensus in fasta files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_cns",
                    "type"     : "file",
                    "descr"    : "the vcf consensus input files from varscan",
                },
                {
                    "name"     : "input_mpileups",
                    "type"     : "file",
                    "descr"    : "the mpileup files from samtools mpileup (for initialisation)",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_summary",
                    "type"  : "file",
                    "descr" : "output file names",
                    "value" : "summary.xls"
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
                    "Chrom",        "Position", "Covmp",  "Ref",  "Var",     "Cons", "Fasta",
                    "Qdepth",  "Reads1",   "Reads2", "Freq", "P-value", 
                    "StrandFilter", "R1+",      "R1-",    "R2+",  "R2-" 
                 ]
        self.output_fasta = []

        # Get all positions from the samtools mpileup files
        contents = dict()
        for i, fmpileup in enumerate(self.input_mpileups):
            sample_id = self.meta['job']['sample_id'][i]
            # Need to use iterator, else crashes
            tp = pd.read_csv(fmpileup, sep='\t', index_col=None, header=None, names=fields[0:4], usecols=fields[0:4], chunksize=100)
            tmpconts = pd.concat(tp, ignore_index=True)
            # 3rd and 4th column are swapped w.r.t. varscan output
            tmpconts[['Ref', 'Covmp']] = tmpconts[['Covmp','Ref']]
            # add all missing columns
            contents[sample_id] = pd.concat([tmpconts, pd.DataFrame(columns=fields[4:])])

        # Get average depth (used to remove sudden drops)
        avg_cov = {}
        for sample_id in contents:
            avg_cov[sample_id] = contents[sample_id]['Covmp'].mean()
        
        # Get all the rest from the varscan files
        idel = [0, 0, 0] # special treatment for deletions
        for i, fcns in enumerate(self.input_cns):
            sample_id = self.meta['job']['sample_id'][i]
            fasta = ''
            with open(fcns) as fh:
                reader = vcf.Reader(fh)
                for irow, record in enumerate(reader):
                    sample = record.samples[0]
                    filter_result = ','.join(record.FILTER) if record.FILTER else "Pass"
                    frequency = float(sample['FREQ'].strip('%'))/100. if sample['FREQ'] else 0
                    depth = float(sample['DP']) if sample['DP'] else 0
                    if len(record.ALT)>1:
                        raise Exception("Not designed to handle multiple variations: %s" % record.ALT)

                    # Do some compatibility checks with mpileup contents
                    if str(record.CHROM) != str(contents[sample_id].loc[irow, 'Chrom']) \
                      or int(record.POS) != int(contents[sample_id].loc[irow, 'Position']): 
                        raise Exception("VCF / mpileup mismatch:\n"
                                        "VCF:     %s\n"
                                        "MPILEUP: %s" % (record, contents[sample_id].loc[irow].to_string()))

                    # Treat variation information
                    variations = record.ALT[0].sequence if record.ALT[0] else ''
                    contents[sample_id].loc[irow, 'Var'] = variations if variations else '.'
                    if variations:
                        if record.is_deletion:
                            # In that case, the REF contains all the deleted bases, starting with the last non-deleted one
                            # while the variations contain only the last non-deleted one
                            contents[sample_id].loc[irow, 'Cons'] = '*/-'+record.REF.lstrip(variations)
                            contents[sample_id].loc[irow, 'Fasta'] = variations
                            idel[0] = len(record.REF)-len(variations)
                            idel[1] = frequency
                            idel[2] = depth
                        elif record.is_indel: # insert
                            contents[sample_id].loc[irow, 'Cons'] = '*/+'+variations.lstrip(record.REF)
                            if frequency>self.minfreq:
                                contents[sample_id].loc[irow, 'Fasta'] = variations
                            else:
                                contents[sample_id].loc[irow, 'Fasta'] = record.REF
                        elif record.is_snp:
                            contents[sample_id].loc[irow, 'Cons'] = variations
                            if frequency>self.minfreq:
                                contents[sample_id].loc[irow, 'Fasta'] = variations
                            else:
                                contents[sample_id].loc[irow, 'Fasta'] = record.REF
                    else:
                        contents[sample_id].loc[irow, 'Cons'] = record.REF
                        if idel[0]>0: # An indel has been previously found
                            idel[0] -= 1
                            if idel[1]<=self.minfreq:
                                contents[sample_id].loc[irow, 'Fasta'] = record.REF
                            else:
                                contents[sample_id].loc[irow, 'Fasta'] = ''
                        else:
                            contents[sample_id].loc[irow, 'Fasta'] = record.REF

                    # Special treatment for positions with low coverage => uncertain
                    if depth/avg_cov[sample_id]<self.mincov:
                        if contents[sample_id].loc[irow, 'Fasta']: # do not replace deleted positions
                            contents[sample_id].loc[irow, 'Fasta'] = 'N'

                    # Fill remaining info
                    if not sample['DP']:
                        contents[sample_id].loc[irow] = contents[sample_id].loc[irow].fillna(0)
                    else:
                        contents[sample_id].loc[irow, 'Qdepth'] = sample['DP']
                        contents[sample_id].loc[irow, 'Reads1'] = sample['RD']
                        contents[sample_id].loc[irow, 'Reads2'] = sample['AD']
                        contents[sample_id].loc[irow, 'Freq'] = frequency
                        contents[sample_id].loc[irow, 'P-value'] = float(sample['PVAL'])
                        contents[sample_id].loc[irow, 'StrandFilter'] = filter_result
                        contents[sample_id].loc[irow, 'R1+'] = sample['RDF']
                        contents[sample_id].loc[irow, 'R1-'] = sample['RDR']
                        contents[sample_id].loc[irow, 'R2+'] = sample['ADF']
                        contents[sample_id].loc[irow, 'R2-'] = sample['ADR']

                    # Append to fasta output
                    fasta += contents[sample_id].loc[irow, 'Fasta']


            output_fasta = sample_id+'.fasta'
            with open(output_fasta, 'w') as fh:
                fh.write('>'+sample_id+'\n')
                fh.write(textwrap.fill(fasta, width=60))
            self.output_fasta.append(output_fasta)

            # Add missing positions
            last_pos = contents[sample_id]['Position'].tail(1)
            contents[sample_id] = contents[sample_id].set_index('Position').reindex(xrange(1, last_pos+1), fill_value='-')
            contents[sample_id]['Position'] = contents[sample_id].index

        #THIS DOES NOT ALWAYS WORK: EXCEL FAILS TO READ OUTPUT FILE
        #with pd.ExcelWriter(self.output_summary, engine='openpyxl') as writer:
        #    for sample in contents:
        #        contents[sample].to_excel(writer, sheet_name=sample, index=False, columns=fields)
        #    writer.save()

        all_samples = pd.concat(contents.values(), keys=contents.keys(), axis=1)
        all_samples.dropna(axis=0, how='all', inplace=True)
        ordered = all_samples.reindex(columns=fields, level=1)
        ordered.to_csv(self.output_summary, sep='\t', index=False)

