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

#!/usr/bin/env python
import os
import sys
import subprocess
from subprocess import Popen, PIPE,STDOUT
import datetime
import psutil
import tempfile

from pypers.core.step import JOB_STATUS
from schedabc import Scheduler, JOB_OUT, JOB_ERR
from pypers.core.logger import logger
from pypers.utils.utils import format_dict

FAILED_FILE = '__failed'

class LocalScheduler(Scheduler):

    """ Methods for job submission and status reporting for a 'Local' scheduler
        In the context of pipelines this is mainly for testing purposes
    """

    log = logger.get_log()
    job_ids = {}

    def submit(self, cmd, cmd_args, work_dir, reqs=None):

        """  submits a command 'locally' in the background
             Returns the pid as job id
        """

        if os.path.exists(os.path.join(work_dir, FAILED_FILE)):
            os.remove(os.path.join(work_dir, FAILED_FILE))

        newpid = os.fork()
        if newpid == 0:
            self.__submit(cmd, cmd_args, work_dir)
            return
        else:
            self.job_ids[newpid] = { 'cwd': work_dir }
        return newpid


    def __submit(self, cmd, cmd_args, work_dir):

        self.log.info('cmd_args: %s, cmd: %s, work_dir: %s' % (cmd_args, cmd, work_dir))
        cmd_args.insert(0,cmd)
        err = open(os.path.join(work_dir, JOB_ERR), 'w')
        out = open(os.path.join(work_dir, JOB_OUT), 'w')
        err = subprocess.call(cmd_args, stderr=err, stdout=out)
        if err != 0:
            with open(os.path.join(work_dir, FAILED_FILE),'w') as fh:
                fh.write('[%s] Failed with error code %d\n' % (datetime.datetime.now(), err))
        os._exit(err)  
              

    def stop(self, job_ids):
        """
        Stop all jobs
        """
        job_ids = set(job_ids)
        for job_id in job_ids:
            p = psutil.Process(job_id)
            p.terminate()


    def status(self,job_ids):

        """  Returns the status of a pid from a local background 'job'
        """

        job_ids = set(job_ids)
        status_map = dict.fromkeys(job_ids,'Unknown')

        for job_id in job_ids:
            job_failed_file = os.path.join(self.job_ids.get(job_id, {}).get('cwd'), FAILED_FILE)
            if not psutil.pid_exists(int(job_id)):
                if os.path.exists(job_failed_file):
                    status_map[job_id] = JOB_STATUS.FAILED
                else:
                    status_map[job_id] = JOB_STATUS.SUCCEEDED
            elif psutil.Process(job_id).status() == psutil.STATUS_ZOMBIE:
                if os.path.exists(job_failed_file):
                    status_map[job_id] = JOB_STATUS.FAILED
                else:
                    status_map[job_id] = JOB_STATUS.SUCCEEDED
            else:
                status_map[job_id] = JOB_STATUS.RUNNING

        return status_map



