#!/usr/bin/env python

import glob
import subprocess
import time
import os
import getpass
import sys
from pypers.utils.utils import which

NP_SUBMIT = which("np_submit.py")

if __name__ == '__main__':
    testdir = os.path.dirname(os.path.realpath(__file__))
    user = getpass.getuser()
    output_root = '/scratch/%s/pypers/test_suite/%.0f' % (user, time.time())

    if len(sys.argv)>1:
        tests = sys.argv[1:]
    else:
        tests = glob.glob('%s/*.json' %testdir)

    for test in tests:
        output_dir = os.path.join(output_root, os.path.basename(test).split('.')[0])
        cmd = [NP_SUBMIT, test, 'pipeline.output_dir=%s' % output_dir]
        #print ' '.join(cmd)
        subprocess.call(cmd)
