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

import time
import psutil
import copy
import os
import sys
import json
import logging
import multiprocessing as mp
import tempfile
from threading import Thread, Lock
from datetime import datetime
import signal
from pypers.core.constants import *
from pypers.core.pipelines import Pipeline
from pypers.utils.utils import pretty_print, which
from pypers.utils.execute import run_as
from pypers.core.logger import PipeFormatter

MAX_PIPELINES=20
MAX_STEPS=30

def init_worker():
    """
    Fix for the keyboard interrupt problem: childs will ignore interrupts...
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def submit(config, user, run_id, pids):
    """
    Submits pipeline defined by 'config' as user 'user'.
    Dumps the config in a temp. file that is removed after succesful completion.
    Returns exit code, stdout, and stderr.
    """
    pids[run_id] = mp.current_process().pid
    (fd, tmp_cfg) = tempfile.mkstemp(prefix='pypers_', suffix='.cfg', text=True)
    os.fchmod(fd, 0644)
    with os.fdopen(fd, 'w') as fh:
        json.dump(config, fh)
    cmd = [which('np_submit.py'), '-i', tmp_cfg]
    (ec, err, out) = run_as(cmd=cmd, user=user)
    if ec == 0:
        os.unlink(tmp_cfg)
        return (err, out)
    else:
        raise Exception('Unable to execute cmd %s:\n%s\n%s' % (cmd, err, out))


def delete(user, output_dir, work_dir):
    """
    Deletes the output directory of a pipeline.
    Returns exit code, stdout, and stderr.
    """
    if not work_dir:
        cmd = ['rm', '-rf', output_dir]
    else:
        cmd = ['rm', '-rf', work_dir]
        if work_dir != output_dir:
            cmd.extend([';', 'rm', '-rf', output_dir])
    (ec, err, out) = run_as(cmd, user=user)
    out = ' '.join(cmd)+'\n'+out
    if ec == 0:
        return (err, out)
    else:
        raise Exception('Unable to execute cmd %s:\n %s' % (cmd, err))


def resume(user, cfg, run_id, pids):
    """
    Resumes as user 'user' a pipeline defined by the given config
    Returns exit code, stdout, and stderr.
    """
    pids[run_id] = mp.current_process().pid
    cmd = [which('np_submit.py'), cfg]
    (ec, err, out) = run_as(cmd=cmd, user=user)
    if ec == 0:
        return (err, out)
    else:
        raise Exception('Unable to execute cmd %s:\n %s' % (cmd, err))



class PipelineManager(object):
    """
    Handle multiple pipelines
    """

    def __init__(self):
        """
        Initialize the manager
        """
        self.logger = mp.log_to_stderr()
        self.logger.handlers[0].setFormatter(PipeFormatter())

        self.submitted = []
        self.actions = []
        self.process_thread = Thread(target=self.process)
        self.lock = Lock()
        self.pool = {'steps': '', 'pipelines': ''}

        self.pool['pipelines'] = mp.Pool(processes=MAX_PIPELINES,
                                         initializer=init_worker,
                                         maxtasksperchild=1)

        self.pool['steps'] = mp.Pool(processes=MAX_STEPS,
                                     initializer=init_worker,
                                     maxtasksperchild=1)

        self.manager = mp.Manager()
        self.pids = self.manager.dict()
        self.count = 0


    def print_pipelines(self):
        for p in self.submitted:
            label_user = '%s (%s)' % (p['label'], p['user'])
            print '   [%03d]  %-40s %s' % (p['id'], label_user, p['output_dir'])


    def add_pipeline(self, spec, user):
        """
        Add a pipeline to the running list
        """
        try:
            output_dir = spec['config']['pipeline']["output_dir"]
            self.count += 1
            run_id = spec.get('run_id', self.count)
            pretty_print(
                "Queuing pipeline: id=%d, label=%s, user=%s, dir=%s"
                %(run_id, spec['label'], user, output_dir)
            )
            p_dict = {
                'id'         : run_id,
                'label'      : spec['label'],
                'output_dir' : output_dir,
                'user'       : user,
                'spec'       : spec,
                'result'     : self.pool['pipelines'].apply_async(submit, (spec, user, run_id, self.pids))
            }
            self.submitted.append(p_dict)
            return "Pipeline %s (ID %d) has been queued" % (p_dict['label'], run_id)
        except Exception, e:
            return "Exception caught creating the pipeline: %s" % e


    def add_step(self, spec, user):
        """
        Add a step to the running list
        """

        try:
            output_dir = spec["output_dir"]
            self.count += 1
            run_id = spec.get('run_id', self.count)
            pretty_print(
                "Queuing step: id=%d, name=%s, user=%s, dir=%s"
                %(run_id, spec['name'], user, output_dir)
            )
            p_dict = {
                'id'         : run_id,
                'label'      : spec['name'],
                'output_dir' : output_dir,
                'user'       : user,
                'spec'       : spec,
                'result'     : self.pool['steps'].apply_async(submit, (spec, user, run_id, self.pids))
            }
            self.submitted.append(p_dict)
            return "Pipeline %s (ID %d) has been queued" % (p_dict['label'], run_id)
        except Exception, e:
            return "Exception caught creating the pipeline: %s" % e


    def delete_pipeline(self, run_id, user, output_dir, work_dir):
        """
        Wipe out a pipeline directory
        """
        try:
            pretty_print("Deleting pipeline: id=%d, user=%s, output_dir=%s, work_dir=%s"
                    % (run_id, user, output_dir, work_dir))
            p_dict = {
                'id'      : run_id,
                'user'    : user,
                'label'   : 'deletion',
                'result'  : self.pool['pipelines'].apply_async(delete, [user, output_dir, work_dir])
            }
            self.actions.append(p_dict)
        except Exception, e:
            return "Exception caught queuing pipeline for deletion: %s" % e


    def pause_pipeline(self, run_id, user):
        """
        Interrupt pipeline by sending signal to corresponding worker's children
        """
        pid = self.pids.get(run_id)
        if pid:
            pretty_print("Pausing pipeline: id=%d, user=%s" % (run_id, user))
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    run_as(cmd=['kill', child.pid], user=user)
            except psutil.NoSuchProcess:
                pretty_print("Error pausing pipeline: no process with ID %d" % int(pid))
        else:
            pretty_print("Error pausing pipeline: ID %d not found" % run_id)



    def resume_pipeline(self, run_id, user, work_dir):
        """
        Resume a pipeline residing in given directory
        """
        try:
            config = os.path.join(work_dir,'pipeline.cfg')
            pretty_print("Resuming pipeline: id=%d, user=%s, work_dir=%s" % (run_id, user, work_dir))
            p_dict = {
                'id'      : run_id,
                'user'    : user,
                'label'   : 'resuming',
                'result'  : self.pool['pipelines'].apply_async(resume, (user, config, run_id, self.pids))
            }
            self.actions.append(p_dict)
        except Exception, e:
            return "Exception caught queuing pipeline for resuming: %s" % e


    def start(self):
        """
        Start the processing of the pipelines
        """
        self.lock.acquire()
        self.running = True
        self.process_thread.start()
        self.lock.release()


    def stop(self):
        """
        Stop the processing of the pipelines
        """
        pretty_print('Stopping pool')
        self.lock.acquire()
        self.pool['pipelines'].terminate()
        self.pool['pipelines'].join()
        self.running = False
        self.lock.release()


    def check_result(self, p_dict):
        """
        Retrieve result of pipeline and dump some information
        """
        (err, out) = p_dict['result'].get() # Re-raises exception if submit failed
        if len(err):
            pretty_print('*** Pipeline [%03d] %s terminated with ERROR:'
                         % (p_dict['id'], p_dict['label']))
            print('-----\n%s-----' % err)
            if len(out):
                pretty_print('Pipeline OUTPUT:')
                print('-----\n%s-----' % out)
        elif len(out):
            pretty_print('Pipeline [%03d] %s terminated SUCCESSFULLY:'
                         % (p_dict['id'], p_dict['label']))
            print('-----\n%s-----' % out)


    def process(self):
        """
        Process all the pipelines in the list
        """
        while self.running:
            ###############################################
            # Pipeline handling
            ###############################################
            for p_dict in copy.copy(self.submitted):
                if p_dict['result'].ready():
                    try:
                        self.check_result(p_dict)
                    except Exception as e:
                        pretty_print('*** Pipeline %s with id %d terminated with EXCEPTION:'
                                     % (p_dict['label'], p_dict['id']))
                        print('-----\n%s\n-----' % e)
                    finally:
                        self.submitted.remove(p_dict)
                        if p_dict['id'] in self.pids:
                            self.pids.pop(p_dict['id'])
            for p_dict in copy.copy(self.actions):
                if p_dict['result'].ready():
                    try:
                        self.check_result(p_dict)
                    except Exception as e:
                        pretty_print('*** Pipeline %s %s terminated with EXCEPTION:'
                                     % (p_dict['id'], p_dict['label']))
                        print('-----\n%s\n-----' % e)
                    finally:
                        self.actions.remove(p_dict)
            # Log every minute
            if (int(time.time()/10))%6==0:
                npipes = len(self.submitted)
                if npipes:
                    pretty_print('INFO: %d pipeline%s currently running:' % (npipes, ['','s'][npipes>1]))
                    self.print_pipelines()
                else:
                    pretty_print('INFO: no pipeline currently running')


            ###############################################
            # Step handling
            ###############################################


            time.sleep(10)


pm = PipelineManager()
pm.start()

def handler(signum,frame):
    global pm
    pretty_print('Received signal %d' % signum)
    pm.stop()
    pretty_print('Collecting garbage and exiting')
    sys.exit()

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
