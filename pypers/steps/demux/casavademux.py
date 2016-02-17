import os
from pypers.core.step import CmdLineStep
from pypers.utils import utils
from pypers.utils.samplesheet import SampleSheet


class CasavaDemux(CmdLineStep):
    spec = {
        "name": "CasavaDemux",
        "version": "1.8.2",
        "descr": [
            "Runs Casava demultiplexing"
        ],
        "url": "https://support.illumina.com/sequencing/sequencing_software/casava.html",
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_dir",
                    "type"     : "dir",
                    "descr"    : "the name of the input directory",
                },
                {
                    "name"     : "sample_sheet",
                    "type"     : "file",
                    "descr"    : "the path to the validated sample sheet",
                },
            ],
            "params" : [
                {
                    "name"  : "threads",
                    "type"  : "int",
                    "value" : 4,
                    "descr" : "the number of threads used by the process",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "output file names",
                }
            ]
        },
        "cmd": [
            "/software/pypers/casava/casava-1.8.2/bin/configureBclToFastq.pl",
            "--input-dir {{input_dir}}",
            "--output-dir {{output_dir}}",
            "--sample-sheet {{sample_sheet}}",
            "--use-bases-mask {{use_base_mask}}",
            "--fastq-cluster-count 1000000000",
            "--force",
            "--with-failed-reads",
            "--ignore-missing-bcl",
            "--ignore-missing-control",
            " && make -j {{threads}} -C {{output_dir}} all",
        ],
        "extra_env": {
            'LD_LIBRARY_PATH' : '/software/pypers/python/Anaconda-2.1.0/lib'
        },
        "requirements": {
            "cpus": "8"
        }
    }


    def process(self):

        # Reduce inputs to only first element
        if hasattr(self.input_dir, '__iter__'):
            self.input_dir = self.input_dir[0]

        self.input_dir = os.path.join(self.input_dir, "Data/Intensities/BaseCalls/")
        if type(self.sample_sheet) == list:
            if len(self.sample_sheet) > 1:
                raise Exception('Too many sample sheet files: %s' % ','.join(self.sample_sheet))
            else:
                self.sample_sheet = self.sample_sheet[0]
            
        ss = SampleSheet(self.sample_sheet) 
        mask_length, double_idx = ss.get_mask_length()

        if double_idx:
            self.use_base_mask = "y*,I{0},I{0},Y*".format(mask_length)
        else:
            self.use_base_mask = "y*,I{0},Y*".format(mask_length)

        self.use_base_mask = str(self.use_base_mask)
        super(CasavaDemux, self).process()

        prj_dir = os.path.join(self.output_dir, 'Project_' + self.meta['pipeline']['project_name'])
        self.output_files = utils.find(prj_dir, "*.fastq.gz")

        #set the metadata
        self.meta['job']['sample_id'] = []
        sample_ids = ss.get_sample_ids()
        for output_file in self.output_files:
            for sample_id in sample_ids:
                if os.path.basename(output_file).startswith("%s_" % sample_id):
                    self.meta['job']['sample_id'].append(sample_id)
                    break



