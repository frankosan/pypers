import os
import re
from pypers.core.step import FunctionStep
from pypers.utils.samplesheet import SampleSheet


class ValidateSampleSheet(FunctionStep):
    """
    Create a validated sample sheet in the output_dir
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns list of files read from a fofn"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_dir",
                    "type"     : "dir",
                    "descr"    : "the input directory",
                },
            ],
            "outputs": [
                {
                    "name"  : "output_files",
                    "type"  : "file",
                    "descr" : "output file names",
                }
            ]
        }
    }

    def process(self):

        # Reduce inputs to only first element
        if hasattr(self.input_dir, '__iter__'):
            self.input_dir = self.input_dir[0]

        if not self.input_dir.endswith('/'):
            self.input_dir += '/'

        (parent_dir, flowcell_dir) = os.path.split(os.path.dirname(self.input_dir))

        parsed = re.search(r'''(?P<DATE>\d{6})_
                               (?P<HISEQ_SN>\w{6})_
                               (?P<RUN_COUNT>\d{4})_
                               (?P<FC_POS>[AB])
                               (?P<FC_ID>.*$)''', flowcell_dir, re.X)

        ss = SampleSheet(os.path.join(self.input_dir, 'SampleSheet.csv'))
        ss_validated = os.path.join(self.output_dir, 'sample_sheet_validated.csv')
        project_name = ss.get_project_name() or 'DefaultProject'

        run_desc = 'Flowcell %s on %s/%s' % (parsed.group('FC_ID'),
                                             os.path.basename(parent_dir),
                                             parsed.group('FC_POS'))

        self.meta.update({
                'pipeline': {
                    'date'         : parsed.group('DATE'),
                    'descr'        : run_desc,
                    'fc_id'        : parsed.group('FC_ID'),
                    'fc_pos'       : parsed.group('FC_POS'),
                    'hiseq'        : os.path.basename(parent_dir),
                    'hiseq_sn'     : parsed.group('HISEQ_SN'),
                    'project_name' : project_name,
                    'run_count'    : int(parsed.group('RUN_COUNT')),
                    'nfiles'       : ss.get_lines_count()
                }
            })

        ss_validated = ss.validate(project_name, ss_validated)

        self.output_files = [ss_validated]
