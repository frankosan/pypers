import argparse
import os
import re
import glob
import json
import subprocess
import shutil
import tempfile
import getpass
from pypers.core.step import Step
from pypers.utils.execute import run_as
from pypers.utils.utils import import_class



WATCHDOG_EXE = 'np_watchdog.py'

if __name__ == '__main__':

    doc="""
    Execute a step class
    """

    parser = argparse.ArgumentParser(description=doc,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('cfg_file',
                        type=str,
                        help='config file of the step')

    args = parser.parse_args()
    user = getpass.getuser()

    # create a step    
    step = Step.load_step(args.cfg_file)
    if not os.path.exists(step.output_dir):
        os.makedirs(step.output_dir, 0775)

    # remove existing files, except step config and condor files
    full_list = glob.glob(step.output_dir + "/*")
    regex = re.compile("(job\.*|condor\.*|.*\.cfg)")
    to_remove = filter(lambda f: not regex.search(f), full_list)
    for entry in to_remove:
        cmd = ['rm', '-rvf', entry]
        (ec, err, out) = run_as(cmd=cmd, user=user)
        if ec:
            print "WARNING: failed to remove file %s: %s, %s" % (entry, err, out)
        else:
            print "Removed %s" % entry

    # launch watchdog
    mypid = os.getpid()
    cmd = [WATCHDOG_EXE, str(mypid)]
    watchlog = os.path.join(step.output_dir, 'watchdog.log')
    wp = subprocess.Popen(cmd, stdout=open(watchlog,'w'), stderr=open(watchlog,'a'))
    
    # run step
    step.run()

    # stop watchdog
    wp.terminate()
    wp.wait()
