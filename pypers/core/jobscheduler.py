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

import cPickle
import os
import collections
import json
import copy
import time
from collections import OrderedDict

from pypers.utils import utils as ut
from pypers.core.logger import logger
from pypers.core.schedulers import get_scheduler
from pypers.core.step import Step, STEP_PICKLE, JOB_STATUS
from pypers.core.job import Job
from pypers.core.constants import *

STEP_RUNNER = ut.which("np_runstep.py")


scheduler = get_scheduler()


class JobScheduler(object):
    """
    Class to handle the step execution
    """

    def __init__(self, step_config):
        """
        Submit the jobs to the cluster
        """
        global scheduler
        self.status = JOB_STATUS.QUEUED
        self.log = logger.get_log()
        self.step_config = step_config
        self.output_dir = step_config['output_dir']
        self.jobs = OrderedDict()
        self.stepobj = Step.load_step(step_config)
        if self.stepobj.local_step:
            self.stepobj.scheduler = get_scheduler("SCHED_LOCAL")
        else:
            self.stepobj.scheduler = scheduler
        self.iterable_params = self.stepobj.get_iterable()
        for iterable in copy.deepcopy(self.iterable_params):
            if not self.step_config.get(iterable):
                self.log.info("Iterable input %s not set: removing" % iterable)
                self.iterable_params.remove(iterable)

    @classmethod
    def set_scheduler(cls, schedname):
        global scheduler
        scheduler = get_scheduler(schedname)


    def start(self):
        """
        Submit all the jobs
        """

        self.status = JOB_STATUS.QUEUED
        self.log.info('*********************************')
        self.log.info('Starting step %s' % self.step_config['name'])

        if self.iterable_params:
            # Step needs to be distributed
            for iterable in self.iterable_params:
                # If this is a file, convert it to list from file contents
                iterable_input = self.step_config[iterable]
                if not hasattr(iterable_input, '__iter__') \
                   and os.path.exists(iterable_input):
                    with open(iterable_input) as f:
                        self.step_config[iterable] = f.read().splitlines()
            for index in range(0, len(self.step_config[self.iterable_params[0]])):
                #copy the config file
                job_config = copy.deepcopy(self.step_config)
                #copy the iterable specific to the job
                for iterable in self.iterable_params:
                    if iterable in self.step_config and self.step_config[iterable]: # permit a null file
                            job_config[iterable] = self.step_config[iterable][index]
                job_config['meta']['pipeline'] = self.step_config['meta']['pipeline']
                job_config['meta']['step'] = self.step_config['meta']['step']
                for key, value in self.step_config['meta']['job'].iteritems():
                    job_config['meta']['job'][key] = value[index]
                self.submit_job(job_config)
        else:
            job_config = copy.deepcopy(self.step_config)
            self.submit_job(job_config)

        return len(self.jobs)

    def submit_job(self, step_config):
        """
        Submit a job step
        """

        status = JOB_STATUS.QUEUED
        job_index = str(len(self.jobs))
        step_config['output_dir'] = os.path.join(step_config["output_dir"], job_index)
        dump_file = os.path.join(step_config["output_dir"], STEP_PICKLE)

        self.log.debug('Configuring step %s %s' % (step_config['name'], len(self.jobs)))

        if not os.path.exists(step_config['output_dir']):
            os.makedirs(step_config['output_dir'], 0775)

        if os.path.exists(dump_file):
            with open(dump_file, "r") as fh:
                step = cPickle.load(fh)
                status = step.status

        if status == JOB_STATUS.SUCCEEDED:
            self.log.info('Step %s in %s already completed: skipping' % (step_config['name'], step_config['output_dir']))
            job_id = job_index
        else:
            cfg_file = os.path.join(step_config['output_dir'], step_config['name'] + ".cfg")
            with open(cfg_file, "w") as fh:
                fh.write(json.dumps(step_config))

            job_id = self.stepobj.scheduler.submit(STEP_RUNNER, [cfg_file], step_config['output_dir'], self.stepobj.reqs)

        self.jobs[job_id] = Job(job_id, step_config['output_dir'], status)


    def load_jobs_output(self):
        """
        Load the output of each job and merge them
        """
        paramsVal = {}
        paramsMeta = { 'pipeline':{}, 'step':{}, 'job':{} }
        self.log.debug('Loading job outputs for step %s...' % self.stepobj.spec['name'])
        for param in self.stepobj.get_output_keys():
            paramsVal[param]  = []

        for job_id in self.jobs:
            stepobj = self.jobs[job_id].load_output()
            for param in self.stepobj.get_output_keys():
                job_outputs = getattr(stepobj, param)
                paramsVal[param].extend(job_outputs)
            paramsMeta['pipeline'] = stepobj.meta['pipeline']
            paramsMeta['step'] = stepobj.meta['step']
            for key, value in stepobj.meta['job'].iteritems():
                if key in paramsMeta['job']:
                    if not hasattr(paramsMeta['job'][key], '__iter__'):
                        paramsMeta['job'][key] = [paramsMeta['job'][key]]
                    paramsMeta['job'][key].append(value)
                else:
                    if self.iterable_params:
                        paramsMeta['job'][key] = [value]
                    else:
                        paramsMeta['job'][key] = value

        self.log.debug('Job outputs found:')
        for param in self.stepobj.get_output_keys():
            self.stepobj.set_param(param, paramsVal[param])
            self.log.debug('   output for key %s : %s' % (param, str(paramsVal[param])))
        self.stepobj.meta = paramsMeta
        self.log.debug('Metadata found: %s' % (ut.format_dict(paramsMeta)))


    def get_outputs(self):
        """
        Returns all output_key:files of the step
        """
        outputs = self.stepobj.get_outputs()
        outputs['output_dir'] = self.output_dir
        return outputs


    def stop(self):
        """
        Interrupt all running jobs
        """
        self.log.info('Stopping incomplete jobs')
        incomplete_jobs = [job_id for job_id in self.jobs if self.jobs[job_id].status == JOB_STATUS.RUNNING]
        if incomplete_jobs:
            self.stepobj.scheduler.stop(incomplete_jobs)

        for job_id in incomplete_jobs:
            self.jobs[job_id].set_status(JOB_STATUS.INTERRUPTED)

        if self.status != JOB_STATUS.FAILED:
            self.status = JOB_STATUS.INTERRUPTED


    def get_status(self):
        """
        Return step status and jobs status
        """

        running     = False
        failed      = False
        interrupted = False
        succeeded   = True

        if self.stepobj.local_step:
            time.sleep(1)
        else:
            time.sleep(5)

        incomplete_jobs = [job_id for job_id in self.jobs if self.jobs[job_id].status != JOB_STATUS.SUCCEEDED]
        if incomplete_jobs:
            for job_id, job_status in self.stepobj.scheduler.status(incomplete_jobs).iteritems():
                if (job_status == JOB_STATUS.SUCCEEDED
                and not self.jobs[job_id].is_completed()):
                    job_status = JOB_STATUS.RUNNING

                self.jobs[job_id].set_status(job_status)

                running         |= (job_status == JOB_STATUS.RUNNING)
                failed          |= (job_status == JOB_STATUS.FAILED)
                interrupted     |= (job_status == JOB_STATUS.INTERRUPTED)
                succeeded       &= (job_status == JOB_STATUS.SUCCEEDED)

                if job_status   != JOB_STATUS.RUNNING:
                    running |= not self.jobs[job_id].is_completed()

        if failed:
            self.status = JOB_STATUS.FAILED
        elif interrupted:
            self.status = JOB_STATUS.INTERRUPTED
        elif running:
            self.status = JOB_STATUS.RUNNING
        elif succeeded:
            self.status = JOB_STATUS.SUCCEEDED

        if self.status == JOB_STATUS.SUCCEEDED:
            self.load_jobs_output()

        return self.status, [self.jobs[index].__dict__.copy() for index in self.jobs]
