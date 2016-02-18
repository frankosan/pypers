""" 
 This file is part of Pypers.

 Pypers is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Pypers is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Pypers.  If not, see <http://www.gnu.org/licenses/>.
 """


import argparse
import os
import sys
import traceback
import requests
import json
import pprint
import getpass
import signal
from pypers.core.pipelines import Pipeline
from pypers.config import SERVICE_ROOT_URL
from pypers.pipelines import pipeline_names
from pypers.core.step import Step
import pypers.utils.utils as ut

def stop_pipeline(signum, frame):
    global pi
    ut.pretty_print("Signal received: terminating pipeline")
    pi.stop()
    sys.exit()

signal.signal(signal.SIGTERM, stop_pipeline)

def apply_custom(config,custom):
    """
    Replace/add custom values to that in config.
    Config is a dictionary and is expected to have a 'config' section.
    Custom is a list of custom parameters of the form 'a.b.c=value'
    """
    ut.pretty_print("Setting custom params: %s" % custom)
    for c in custom:
        path,v = c.split('=')
        keys = path.split('.')
        #print " %s : %s" % (keys, v)
        if 'config' not in config:
            config['config'] = {}
        param = config['config']
        for key in keys[:-1]:
            if key not in param:
                ut.pretty_print('*** WARNING: creating new parameter %s (a typo?)' % key)
                param[key]={}
            param=param[key]
        name = keys[-1]
        if name in param:
            # if already set, preserve type
            ptype = type(param[name])
        else:
            ptype = type(v)
        param.update({name:ptype(v)})


if __name__ == '__main__':

    doc="""
    Submit a pipeline to the cluster
    """

    parser = argparse.ArgumentParser(description=doc,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('config_file',
                        type=str,
                        help='the configuration file of the pipeline run')

    parser.add_argument('-l', '--local',
                        action='store_true',
                        dest='local',
                        help='run the pipeline on a local process (no db, no condor)',
                        default=False)

    parser.add_argument('-i', '--interactive',
                        action='store_true',
                        dest='interactive',
                        help='run the pipeline interactively (not through the server).',
                        default=False)

    parser.add_argument('-db',
                        action='store_true',
                        dest='db',
                        help='use db on local run',
                        default=False)

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help='show more information',
                        default=False)

    parser.add_argument('-u', '--user',
                        dest='user',
                        type=str,
                        default=getpass.getuser(),
                        help='user associated with this pipeline run')

    parser.add_argument('custom',
                        nargs=argparse.REMAINDER,
                        type=str,
                        metavar='SECTION.PARAM=VALUE',
                        help="custom configuration to apply on top of configuration file.\n" \
                             "SECTION must be a subsection of the 'config' section\n" \
                             "        (several levels can be specified: SEC.SUBSEC.SUBSUBSEC, etc.)\n" \
                             "PARAM   is any parameter in this section")

    args = parser.parse_args()


    is_step = False
    try:
        config = Pipeline.load_cfg(args.config_file)
        if 'sys_path' not in config:
            config['sys_path'] = os.path.dirname(os.path.realpath(args.config_file))
    except Exception as e1:
        raise e1
        config = Step.load_cfg(args.config_file)
        if 'sys_path' not in config:
            config['sys_path'] = os.path.dirname(os.path.realpath(args.config_file))  

        step = Step.load_step(config)
        is_step = True


    if args.custom:
        apply_custom(config,args.custom)

    if args.local:
        ut.pretty_print("Instantiating the Pipeline...")
        p = Pipeline(config, user=args.user, db=args.db, schedname='SCHED_LOCAL')
        ut.pretty_print("Running the pipeline...")
        p.run(local=True, verbose=args.verbose)
    elif args.interactive:
        global pi
        ut.pretty_print("Instantiating the Pipeline...")
        pi = Pipeline(config, user=args.user)
        ut.pretty_print("Running pipeline %s" % (pi.db.run_id))
        tb = None
        try:
            pi.run(verbose=args.verbose)
        except Exception, e:
            ex_type, ex, tb = sys.exc_info()
            ut.pretty_print("FAILED: %s" % e)
            traceback.print_tb(tb)
        finally:
            if tb:
                del tb
            if os.path.exists(pi.lock):
                os.unlink(pi.lock)
        ut.pretty_print("Done running pipeline %s" % (pi.db.run_id))
    else:

        if is_step:
            address = "%s/api/steps/submit" % SERVICE_ROOT_URL
            output_dir = config.get('output_dir', '')
        else:
            address = "%s/api/pipelines/submit" % SERVICE_ROOT_URL
            output_dir = config['config']['pipeline']['output_dir']

        if not output_dir.startswith('/'):
            raise Exception('Error: output directory %s is not an absolute path' % output_dir)
        if not ut.has_write_access(output_dir):
            raise Exception('Error: directory %s is not writable by %s' % (output_dir, args.user))
        
        data = json.dumps({"config": config, "user": args.user}, indent=4, separators=(',', ': '))
        ut.pretty_print("Sending request...")
        if args.verbose:
            print "%s" % data
        response = requests.put(address, data=data)
        print ''
        ut.pretty_print("Received reponse: %s" %response.text)



