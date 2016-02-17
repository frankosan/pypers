from pypers.core.step import Step
import os
import re

class QUAST(Step):
    spec = {
        "version": "2015.06.28",
        "descr": [
            """
            Run the QUAST Quality Assessment Tool for Genome Assemblies
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_contigs",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "fasta contig assemblies to evaluate",
                }
            ],
            "outputs": [
                {
                    "name"  : "report_file",
                    "type"  : "file",
                    "descr" : "Assembly quality assessment report"
                }
            ],
            "params": [
                {
                    "name"  : "quast_exe",
                    "type"  : "str",
                    "descr" : "path to QUAST executable",
                    "value" : "/software/pypers/KBaseExecutables/prod-Nov222013/runtime/quast/quast.py",
                    "readonly" : True
                },
                {
                    "name"  : "scaffolds",
                    "type"  : "boolean",
                    "descr" : "Input contigs are scaffolds",
                    "value" : False
                },
                {
                    "name"  : "min_contig",
                    "type"  : "int",
                    "descr" : "Minimum contig length",
                    "value" : 500
                },
                {
                    "name"  : "ref_contig",
                    "type"  : "str",
                    "descr" : "Optional path to reference contigs",
                    "value" : ""
                },
                {
                    "name"  : "labels",
                    "type"  : "str",
                    "descr" : "Optional comma-delimited list of labels for input contigs",
                    "value" : ""
                }
            ]
        },
        "requirements": { },
    }

    def process(self):

        self.log.info('Runnning QUAST on %s' % str(self.input_contigs))

        cmd = '%s -o %s/results --gene-finding --min-contig %i' % (self.quast_exe, self.output_dir, self.min_contig)

        # If ref genome, also use GAGE
        if self.ref_contig:
            cmd += ' -R %s' % self.ref_contig

        if self.scaffolds:
            cmd += ' --scaffolds'


        # try to create useful labels, ideally we would pass step name metadata for this
        labels = []

        if isinstance(self.input_contigs,basestring): # gets passed a string if only on fie
            cmd += ' %s' % self.input_contigs
        else:
            commonprefix = os.path.commonprefix(self.input_contigs)
            ctgs = 0
            for idx, ctg in enumerate(self.input_contigs):
                if os.stat(ctg).st_size == 0:
                    self.log.warn("Excluding zero-length contig file %s from results" % ctg)
                else:
                    ctgs += 1
                    cmd += ' %s' % ctg
                    lbl = ctg.replace(commonprefix,'').split('/')[0] # lowest level subdir, eg 'velvet_reapr'
                    labels.append(lbl)

            if ctgs == 0:
                raise Exception('No valid contigs to process')

        if self.labels:
            cmd += ' --labels %s' % self.labels
        else:
            if ','.join(labels) != '':
                cmd += ' --labels "%s"' % ','.join(labels)

        self.submit_cmd(cmd)

        self.report_file = os.path.join(self.output_dir, 'results/report.html')
        if not os.path.exists(self.report_file):
            raise Exception('Failed to generate %s' % self.report_file)


        # make visible to ui
        scr_re = re.compile(r'script.*text\/javascript.*src=\"(.*)\"')
        css_re = re.compile(r'link.*text\/css.*href=\"(.*)\"')

        flock_file = os.path.join(self.output_dir, 'report.html')
        with open(self.report_file, 'r') as o_file, open(flock_file, 'w') as t_file:
            for line in o_file:
                try:
                    line.decode('ascii')
                    scr_match = scr_re.search(line)
                    css_match = css_re.search(line)

                    if scr_match:
                        matched = scr_match.group(1)
                        line = line.replace(matched, os.path.join('/api/fs/txt?path=%s' % self.output_dir, 'results', matched))
                    if css_match:
                        matched = css_match.group(1)
                        line = line.replace(matched, os.path.join('/api/fs/css?path=%s' % self.output_dir, 'results', matched))
                except:
                    pass

                t_file.write(line)

