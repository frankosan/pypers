from pypers.core.step import CmdLineStep
import glob
import os

class PlotBamCheck(CmdLineStep):
    spec = {
        "name": "PlotBamCheck",
        "version": "0.1.19",
        "descr": [
            "Run the plot-bamcheck utility against a bamcheck file, generating a set of plots"
        ],
        "args": 
        {
            "inputs": [
                {
                    "name"  : "input_files",
                    "type"  : "file",
                    "iterable": True,
                    "descr" : "the bamcheck file to run on",
                }
            ],
            "outputs": [ 
                {
                    "name" : "output_pngs",
                    "type" : "file",
                    "descr": "png of bamcheck plots"
                },
                {
                    "name" : "output_gps",
                    "type" : "file",
                    "descr": "gnuplot file of bamcheck plots"
                }
                ]
        },
        "cmd": [
            "/software/pypers/samtools/samtools-0.1.19/bin/plot-bamcheck -p {{output_dir}}/ {{input_files}}"
        ]
    }

    def postprocess(self):
        """
        Sets the outputs
        """
        self.output_pngs = glob.glob(os.path.join(self.output_dir,'*.png'))
        self.output_gps  = glob.glob(os.path.join(self.output_dir,'*.gp'))

