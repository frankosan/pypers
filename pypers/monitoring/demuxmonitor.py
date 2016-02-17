import time
import argparse
import os
import re
import getpass
import time
from pypers.utils.execute import run_as
from configobj import ConfigObj
from pypers.utils.utils import which
from pypers.pipelines import pipeline_names

class DemuxMonitor(object):
    """
    This class is monitoring the flow cell IDs inside the hiseq directories.
    When a flow cell IDs is not contained in the demultiplexing directory,
    then the demultiplexing process for the flow cell is triggered

    This class is designed to be executed using the python-daemon class

    Example of how to use this class to monitor 4 Hiseq directories:
    """

    def __init__(self, hiseq_dirs, demu_dir, notify="Always", email=None):
        """
        Get a list of hiseq directories and check they are all in the demultiplexed
        directory.
        On each hiseq directory which is not in the demultiplexing directory the
        demultiplexing pipeline is executed

        Args:
            hiseq_dirs:
                Is a string containing all the hiseq directories to be monitored
                All the directory are separated by spaces

            demu_dir:
                Is the directory containing the demultiplexed flow cells grouped in directories
        """

        self.notify = notify
        self.email = email
        self.user = 'demux'
        #self.user = getpass.getuser()

        self.demu_dir = demu_dir.strip()
        #print "demultiplexed dir: %s" % self.demu_dir
        if not os.path.exists(self.demu_dir):
            raise Exception("Demultiplexed dir does not exist: %s" % self.demu_dir)

        #self.hiseq_dirs = hiseq_dirs.split()
        #for hiseq_dir in self.hiseq_dirs:
        self.hiseq_dirs = hiseq_dirs
        for hiseq_dir in self.hiseq_dirs:
            #print "hiseq dir: %s" % hiseq_dir
            if not os.path.exists(hiseq_dir):
                raise Exception("Hseq dir is not existing: %s" % hiseq_dir)


    def exec_monitoring(self):
        """
        Check if all the flow cell IDs have been demultiplexed
        For each flow cell which has not been demultiplexed,
        then the demultiplexing pipeline is submitted to the cluster
        """
        #Create a dictionary with {"Fw cell ID" : "path"}
        fw_cell_dirs = {}
        missing_ss_list = []
        for hiseq_dir in self.hiseq_dirs:
            #Parse all the hiseq dirs and create a list of data directories
            #Only the directorise with the "RTAComplete.txt" file are considered
            for fwcell in os.listdir(hiseq_dir):
                fwcell_path = os.path.join(hiseq_dir, fwcell)

                if (re.search(".+_.+_.+_.+", fwcell) \
                and "Temp" not in fwcell \
                and os.path.exists(os.path.join(fwcell_path, "RTAComplete.txt"))):
                    ss_found = False
                    #search for the sample sheet in the fwcell_path
                    for filename in os.listdir(fwcell_path):
                        if ("SampleSheet" in filename) and (".csv" in filename):
                            ss_found = True
                            break
                    if ss_found:
                        fw_cell_dirs[fwcell] = os.path.join(hiseq_dir, fwcell)
                    #otherwise add the directory to the list of missing sample sheet
                    else:
                        missing_ss_list.append(os.path.join(hiseq_dir, fwcell))

        #log all the missing sample sheets detected
        if missing_ss_list:
            print ("******************************************************")
            for missing_ss in missing_ss_list:
                print ("Missing sample sheet in %s "% missing_ss)


        #create a set for the hiseq dirs and a set for the demultiplexed dirs
        hiseq_flow_cells = set([key for key in fw_cell_dirs])
        demu_flow_cells = set(os.listdir(self.demu_dir))
        if not hiseq_flow_cells.issubset(demu_flow_cells):
            #get the difference
            fwcell_diff = hiseq_flow_cells.difference(demu_flow_cells)
            if fwcell_diff:
                for fwcell_id in fwcell_diff:
                    submit_cmd = which('np_submit.py')
                    cmd = [
                        submit_cmd,
                        pipeline_names['demultiplexing'],
                        'pipeline.output_dir=%s' % os.path.join(self.demu_dir, fwcell_id),
                        'pipeline.project_name=Demux',
                        'pipeline.description=Demultiplexing',
                        'steps.inputs.input_dir=%s' % fw_cell_dirs[fwcell_id]
                    ]
                    run_as(cmd=cmd, user=self.user)

                    print("******************************************************")
                    print(" %s Queued demux  with:" % time.ctime())
                    print("   Input dir  : %s" % fw_cell_dirs[fwcell_id])
                    print("   Output dir : %s" % os.path.join(self.demu_dir, fwcell_id))
                    print("   Cmd : %s" % ' '.join(cmd))
                    print("******************************************************")

