import os
import sys
import subprocess
import copy
import re
from subprocess import Popen, PIPE,STDOUT
import schedabc
import time
import psutil
import tempfile
import collections
from schedabc import Scheduler, JOB_OUT, JOB_ERR
from nespipe.config import ACME_PROD
from nespipe.core.step import JOB_STATUS
from nespipe.core.constants import LOG_NAME
from nespipe.core.logger import logger
from nespipe.utils.utils import format_dict

if ACME_PROD:
    TARGET_ENV = "PROD"
else:
    TARGET_ENV = "DEV"

#from src/condor_includes/proc.h 
LSF_JOB_STATUS = {
    "PEND" : JOB_STATUS.QUEUED,
    "PSUSP" : JOB_STATUS.QUEUED,
    "SSUSP" : JOB_STATUS.QUEUED,
    "RUN" : JOB_STATUS.RUNNING,              
    "EXIT" : JOB_STATUS.FAILED,
    "DONE" : JOB_STATUS.SUCCEEDED            
}

class LSFScheduler(Scheduler):

    def __init__(self):
        self.log = logger.get_log()

    def submit(self,cmd,cmd_args,work_dir,reqs={}):
        """  
        Submit job to lsf, return job id
        """

        bsub_args = collections.OrderedDict([
            ('-o',     str(os.path.join(work_dir, 'lsf.log'))),
            ('-e',     str(os.path.join(work_dir, 'lsf.err'))),
        ])

        #-R rusage[mem=6] -R span[hosts=1] -n 8
        if reqs.get('cpus') and reqs['cpus'] > 1:
            bsub_args.update({'-n' : str(reqs['cpus'])})
            bsub_args.update({'-R' : 'span[hosts=1]'})

        if reqs.get('memory') and reqs['memory'] > 1:
            bsub_args.update({'-R' : 'rusage[mem=%s]' % reqs['memory']})

        submit_cmd = ['bsub'] 
        for k,v in bsub_args.iteritems():
            submit_cmd.append(k)
            submit_cmd.append(v)

        submit_cmd.append(str(cmd))
        for a in cmd_args:
            submit_cmd.append(a)

        self.log.debug('submitting %s' % submit_cmd)
        try:
            out = subprocess.check_output(submit_cmd)
        except subprocess.CalledProcessError, e:
            self.log.error('Failed to run command %s: %s' % (' '.join(submit_cmd), e))
            raise

        jobId = -1
        match = re.search("Job <(\d+)> is submitted to queue",out)
        if match:
            jobId = match.group(1)
        else:
            self.log.error('Unable to derive jobId from bsub output: "%s"' % out)

        self.log.info('returning jobid %s' % jobId)
        return jobId

    def stop(self, job_ids):
        """
        Stop all jobs in list of job IDs
        """
        job_ids = set(job_ids)
        if job_ids:
            rm_cmd = ['bkill']
            rm_cmd.extend(job_ids)
            try:
                out = subprocess.check_output(rm_cmd)
                self.log.info(out)
            except subprocess.CalledProcessError, e:
                self.log.error('Problem running command %s: %s' % (' '.join(rm_cmd), e))
        else:
            self.log.info('No job needs to be stopped')


    def status(self, job_ids):
        """  
        Return the status of LSF Job id using bjobs and bhist
        """

        job_ids = set(job_ids)
        status_map = dict.fromkeys(job_ids,'Unknown')

        cmd = 'bjobs ' + ' '.join(job_ids)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        remaining_ids = copy.copy(job_ids)

        for line in p.stdout:
            #JOBID   USER    STAT  QUEUE      FROM_HOST   EXEC_HOST   JOB_NAME   SUBMIT_TIME
            #513     rdjoyce DONE  normal     rddor-rdjoy rddoridt52  *abels.cfg Feb 27 12:07

            if line.startswith('JOBID'):
                continue
            flds = line.split() 
            job_id = flds[0]
            if job_id in job_ids:
                job_status = flds[2]
                if job_status not in LSF_JOB_STATUS.keys():
                    raise('Unknown lsf status %s' % job_status)

                status_map[job_id] = LSF_JOB_STATUS[job_status]
                remaining_ids.remove(job_id)

        if remaining_ids:
            cmd = 'bhist ' + ' '.join(remaining_ids)
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            remaining_ids = copy.copy(job_ids)

            for line in p.stdout:
                #JOBID   USER    JOB_NAME  PEND    PSUSP   RUN     USUSP   SSUSP   UNKWN   TOTAL
                #491     rdjoyce foo.sh    1       0       1       0       0       0       2

                if line.startswith('JOBID') or len(line) == 0:
                    continue

                flds = line.split() 

                job_id = flds[0]
                if job_id in job_ids:
                    pend = int(flds[3])
                    run = int(flds[5])
                    if pend > 0:
                        if run > 0:
                            status_map[job_id] = JOB_STATUS.SUCCEEDED
                        else:
                            status_map[job_id] = JOB_STATUS.QUEUED

        self.log.debug('returning status_map %s' % status_map)
        return status_map
