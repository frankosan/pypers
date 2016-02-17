#!/usr/bin/env python
import os
import subprocess
import sys
import time
import signal


doc="""
Start the node server for bluebird.

Usage:

    $ run.py
"""

# Catch kill signals to gracefully terminate child
global all_ok
def handler(signum,frame):
    print 'Received %d signal: exiting gracefully' % signum
    global all_ok
    all_ok = False

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGQUIT, handler)
signal.signal(signal.SIGINT,  handler)


IS_ACME_PROD = bool(os.environ.get('ACME_PROD', False))
IS_ACME_DEV = bool(os.environ.get('ACME_DEV' , False))
IS_ACME_LCL  = bool(os.environ.get('ACME_LCL' , False))

WORKBENCH_DIR = os.path.realpath(os.path.dirname(__file__))
DISTAPP_DIR = os.path.os.path.join(WORKBENCH_DIR, 'dist')

procedure_name = 'gulp' if IS_ACME_LCL else 'node'

if IS_ACME_PROD:
    env = 'production'
elif IS_ACME_DEV:
    env = 'beta'
else:
    env = 'development'

sys.stdout.write('Starting an new %s process...\n' % procedure_name)
if IS_ACME_LCL:
    ENV_DIR = WORKBENCH_DIR
    cmd = ['/usr/bin/gulp', '--no-color', 'watch']
else:
    if not os.path.isdir(DISTAPP_DIR):
        raise Exception('ERROR: could not find the dist directory under ' +
                        'workbench.\n       ' +
                        'looks like gulp build did not succeed.')
    ENV_DIR = DISTAPP_DIR
    cmd = ['node', 'server']

os.chdir(ENV_DIR)
sys.stdout.write('Current directory: %s\n' % (ENV_DIR))

os.environ['NODE_ENV'] = env
sys.stdout.write('cmd = %s, env = %s \n' % (cmd, sorted(os.environ.items())))

# Need to watch the child process, otherwise it won't
# be terminated when this process is terminated
all_ok = True
print "=========================="
print cmd
proc = subprocess.Popen(cmd, env=os.environ)
while all_ok:
    returnCode = proc.poll()
    if returnCode == None: # Child is running
        time.sleep(2)
    else:
        print 'Child process exited',
        if returnCode != 0:
            print 'with error:',returnCode,
        print
        sys.exit(returnCode)

# Only called if child didn't exit already
print 'Killing child process...'
proc.send_signal(signal.SIGINT) # interrupt so that gulp kills its child
proc.wait()
print 'done.'
