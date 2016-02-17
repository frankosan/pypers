from pypers.core.step import Step
import os
import random
import shutil
import itertools


class Humann(Step):
    spec = {
        "version": "0.99",
        "descr": [
            "Uses scons to run the HumanN Metabolic Analysis to determine abundance of microbial pathways",
            "in a community from metagenomic data in tsv format\n",
            "HumanN is python version dependent"
        ],
        "url" : "https://bitbucket.org/biobakery/biobakery/wiki/humann",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_files",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "The input TSV file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_rings",
                    "type"  : "file",
                    "descr" : "output rings file"
                },
                {
                    "name"  : "output_tree",
                    "type"  : "file",
                    "descr" : "ouput tree file"
                }
            ],
            "params": [
                {
                    "name"  : "humann_path",
                    "type"  : "str",
                    "descr" : "The path to the humann installation directory",
                    "value" : '/software/pypers/humann/humann-0.99',
                    "readonly" : True
                },
                {
                    "name"  : "scons_exe",
                    "type"  : "str",
                    "descr" : "The path to the scons executable",
                    "value" : '/software/pypers/scons/scons-2.3.3/bin/scons',
                    "readonly" : True
                },
                {
                    "name"  : "ldlib_path",
                    "type"  : "str",
                    "descr" : "The path to the anaconda installation, (so curl can find libssl.so.1.0.0)",
                    "value" : '/software/pypers/python/Anaconda-2.1.0/lib',
                    "readonly" : True
                }
            ]
        },
        "requirements": { 
            "cpus" : "8"
        },
    }


    def process(self):

        # Create temp copy of humann install
        humann_dir = os.path.join(self.output_dir, os.path.basename(self.humann_path) )
        if os.path.exists(humann_dir):
            shutil.rmtree(humann_dir)
        shutil.copytree (self.humann_path, humann_dir)

        # Essential output files, add more as required
        output_mpms = ['04b-hit-keg-mpm-cop-nul-nve-nve-graphlan_tree.txt',
                       '04b-hit-keg-mpm-cop-nul-nve-nve-graphlan_rings.txt',
                       '04b-hit-keg-mpm-cop-nul-nve-nve.txt']
        output_mtms = ['04b-hit-keg-mpt-cop-nul-nve-nve-graphlan_tree.txt',
                       '04b-hit-keg-mpt-cop-nul-nve-nve-graphlan_rings.txt',
                       '04b-hit-keg-mpt-cop-nul-nve-nve.txt']

        # Copy input tsv to input dir, then go to humann_path and run scons
        shutil.copy(self.input_files, os.path.join(humann_dir, 'input'))

        extra_env = {'LD_LIBRARY_PATH': self.ldlib_path} 

        # Need path fix for RH 6/7 problem, /bin/cp
        # However need to append not prepend else humann fails
        cmd = 'export PATH=$PATH:/bin;'

        cmd += 'cd %s; %s -j %d' % (humann_dir, self.scons_exe, self.cpus)
        self.submit_cmd(cmd,extra_env=extra_env)

        # copy outputs to step output dir
        humann_odir = os.path.join(humann_dir, 'output')
        for fn in itertools.chain(output_mpms, output_mtms):
            fpath = os.path.join(humann_odir, fn)
            if not os.path.isfile(fpath):
                raise Exception('[Failed to create file %s]' % fpath)
            shutil.copy(fpath, os.path.join(self.output_dir, fn))

        shutil.rmtree(humann_dir)

        self.output_rings = os.path.join(self.output_dir,'04b-hit-keg-mpt-cop-nul-nve-nve-graphlan_rings.txt')
        self.output_tree = os.path.join(self.output_dir,'04b-hit-keg-mpt-cop-nul-nve-nve-graphlan_tree.txt')

