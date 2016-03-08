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

import json
import re
import os
import sys
import cPickle
import subprocess
import socket
import copy
import glob
import time
from datetime import datetime
from collections import OrderedDict, defaultdict
from nespipe.utils import utils as ut
from nespipe.utils.utils import import_class
from nespipe.core.logger import logger
from nespipe.core.constants import *
from nespipe.core.schedulers import get_scheduler
from nespipe.core.constants import *



NOT_DB_ATTR = ['cfg', 'reqs', 'jvm_memory', 'memory', 'cpus', 
               'jobs', 'sys_path', 'step_class', 'cmd_count'
               'name', 'local_step', '__version__', 'scheduler', 'log']


STEP_PICKLE = '.status.pickle'
ITERABLE_TYPE = 'input_key_iterable'

STARTUP_CYCLE = 50


scheduler = get_scheduler()

def set_scheduler(schedname):
    global scheduler
    scheduler = get_scheduler(schedname)


class Step(object):
    """
    Base class for any step

    Members:
    - status: current status of the step
    - parameters: dictionary containing the definition of the parameters
                  N.B. The actual values are stored as members
    - meta: dictionary containing the metadata information
    - reqs: job submission requirements
    - cmd_count: counter for distributed step
    """

    #flag to enable local step execution
    local_step = False
    spec = {
        "version": None,
        "args": {
            "inputs": [{}],
            "outputs": [{}],
            "params": [{}]
        },
        "requirements" : {
            "memory" : '1',
            "cpus" : '1'
        }
    }

    req_spec = {
        'memory' : {
            'name'      : 'memory',
            'descr'     : 'the amount of memory allocated to the step in GB',
            'type'      : 'int',
            "value"     : 1
        },
        "cpus" : {
            'name'      : 'cpus',
            'descr'     : 'the amount of CPUs allocated to the step',
            'type'      : 'enum',
            "options"   : range(1,17,1),
            "value"     : 1
        }
    }

    tpl_reg = re.compile('{{\s*([^\s\}]+)\s*}}')

    def __init__(self):
        self.bootstrap = STARTUP_CYCLE
        self.status = JOB_STATUS.QUEUED
        self.meta = { 'pipeline':{}, 'step':{}, 'job':{}}
        self.requirements = {'memory' : '1', 'cpus' : '1'}
        self.output_dir = '.'
        self.jobs = OrderedDict()
        self.cmd_count = 0

        logger.set_stdout_level(logger.DEBUG)
        self.log = logger.get_log()

        # parse specs and create keys
        self.spec["name"] = self.__module__.replace('nespipe.steps.','').split('.')[-1]
        self.name = self.spec["name"]
        self.__version__ = self.spec['version']

        self.local_step = self.spec.get('local', False)
        global scheduler
        if self.local_step:
            self.scheduler = get_scheduler("SCHED_LOCAL")
        else:
            self.scheduler = scheduler

        for k, v in self.spec["args"].iteritems():
            for param in v:
                if param.get('name', None):
                    setattr(self, param['name'], param.get('value', []))

        ut.dict_update(self.requirements, self.spec.get('requirements', {'memory' : '1', 'cpus' : '1'}))
        for k, v in self.requirements.iteritems():
            setattr(self, k, int(v))

        #set the jvm memory
        if 'memory' in self.requirements:
            self.jvm_memory = int(int(self.requirements['memory']) * 0.9)
            if not self.jvm_memory:
                self.jvm_memory = 1


    def get_refgenome_tools(self):
        """
        Return a dictionary of {key:tool}
        """
        reftools = []
        for p in self.spec["args"].get("inputs", []):
            param_type = p.get("type", None)
            if param_type == TYPE_REFGENOME:
                reftools.append({"name": p["name"], "tool": p["tool"]})
        return reftools

    def get_reqs(self, no_default=True):
        """
        Return a dictionary with the list of requirements
        If nodefault is set to True, keys setted to the default value '1' are not returned
        """
        reqs = []
        for key in self.req_spec:
            val = getattr(self, key)
            req = copy.deepcopy(self.req_spec[key])
            req['value'] = val
            if (val == 1 and not no_default) or val != 1:
                reqs.append(req)
        return reqs


    def __validate_key_groups(self, key_groups):
        """
        Check if the key_groups are valid
        key_groups mut be in [inputs, outputs, params, requirements]
        """        
        spec_groups = set(['inputs', 'outputs', 'params', 'requirements'])
        if isinstance(key_groups, basestring):
            if not key_groups in spec_groups:
                raise Exception("Invalid key_groups %s" %key_groups)
            else:
                return set([key_groups])
        elif type(key_groups) == list or type(key_groups) == set:
            key_groups = set(key_groups)
            if not key_groups.issubset(spec_groups):
                raise Exception ("%s: Invalid key_groups %s" %(self.name, key_groups))
            else:
                return key_groups
        else:
            raise Exception ("Invalid key_groups type %s" %type(key_groups))


    def keys_values(self, key_groups=None, key_filter={}, req_only=False):
        """
        Return dictionary of parameter definitions
        
        """
        if not key_groups:
            key_groups=set(['inputs', 'outputs', 'params', 'requirements'])
        else:
            key_groups = self.__validate_key_groups(key_groups)

        key_vals = {}
        if 'requirements' in key_groups:
            key_groups.remove('requirements')
            key_vals = getattr(self, 'requirements')

        for key_group in key_groups:
            for key_spec in self.keys_specs(key_group):
                if (req_only and not 'value' in key_spec) or (not req_only):
                    if key_filter:
                        for k, v in key_filter.iteritems():
                            if key_spec.get(k, []) == v:
                                key_vals[key_spec["name"]] = getattr(self, key_spec["name"])
                    else:
                        key_vals[key_spec["name"]] = getattr(self, key_spec["name"])

        return key_vals


    def keys(self, key_groups=None, key_filter={}, req_only=False):
        """
        Return a list of keys defined in the spec
        If req_only is True, then default values are not returned
        """
        if not key_groups:
            key_groups=set(['inputs', 'outputs', 'params', 'requirements'])
        else:
            key_groups = self.__validate_key_groups(key_groups)

        keys = []
        for key_group in key_groups:
            for key_spec in self.keys_specs(key_group):
                if (req_only and not 'value' in key_spec) or (not req_only):
                    if key_filter:
                        for k, v in key_filter.iteritems():
                            if key_spec.get(k, []) == v:
                                keys.append(key_spec['name'])
                    else:
                        keys.append(key_spec['name'])
        return keys

    def keys_specs(self, key_groups):
        """
        Returna list with the specification of the keys 
        """

        key_groups = self.__validate_key_groups(key_groups)
        keys_specs = []
        if 'requirements' in key_groups:
            key_groups.remove('requirements')
            keys_specs.extend(self.get_reqs())

        for key_group in key_groups:
            keys_specs.extend(self.spec["args"].get(key_group, []))
        return keys_specs


    def key_spec(self, name):
        """
        Return specification of param, input, or output with given name
        """
        ret_val = {}
        for category in ["inputs", "outputs", "params"]:
            for entry in self.spec["args"].get(category, []):
                if entry["name"] == name:
                    ret_val = entry
                    break
        return ret_val


    def validate_config(self, cfg):
        """
        validate a config file
        """
        errors = {}
        required_key = self.keys(['inputs', 'params'], req_only=True)
        for key in required_key:
            if key in cfg:
                key_spec = self.key_spec(key)
                error_msg = Step.validate_value(
                    cfg[key],
                    key_spec.get('type', ''),
                    key_spec.get('name', '')
                )
                if error_msg:
                    errors[key] = error_msg
            else:
                errors[key] = 'missing value'

        return errors

    @classmethod
    def validate_value(cls, pvalue, ptype, pname):
        """
        Check if the value has the right type
        """
        ret_val = ''
        if pvalue == '' and ptype != 'str':
            ret_val = 'missing value'
        elif ptype == 'file':
            if isinstance(pvalue, (list, tuple)):
                for filename in pvalue:
                    if not os.path.exists(filename):
                        ret_val += '%s : no such file\n' % filename
            elif isinstance(pvalue, basestring):
                if not os.path.exists(pvalue):
                    ret_val = '%s : no such file' % pvalue
            else:
                ret_val = '%s : invalid type, found %s, expected %s' % (pvalue, type(pvalue), 'str or list')
        elif ptype == 'dir' and pname != 'output_dir':
            if isinstance(pvalue, (list, tuple)):
                for dirname in pvalue:
                    if not isinstance(dirname, basestring):
                        ret_val = '%s : invalid type, found %s, expected %s' % (dirname, type(dirname), 'str')
                    elif not os.path.isdir(dirname):
                        ret_val += '%s : no such directory' % dirname
            elif isinstance(pvalue, basestring):
                if os.path.isfile(pvalue):
                    with open(pvalue) as fh:
                        for dirname in fh.read().splitlines():
                            if not os.path.isdir(dirname) and dirname:
                                ret_val += '%s : no such directory' % dirname
                elif not os.path.isdir(pvalue):
                    ret_val = '%s : no such directory' % pvalue
            else:
                 ret_val = '%s : invalid type, found %s, expected %s' % (pvalue, type(pvalue), 'str or list')
        elif ptype == 'int':
            if not isinstance(pvalue, int):
                ret_val = '%s : invalid type, found %s, expected %s' % (pvalue, type(pvalue), 'int')
        elif ptype == 'float':
            if not isinstance(pvalue, float):
                ret_val = '%s : invalid type, found %s, expected %s' % (pvalue, type(pvalue), 'float')
        elif ptype == 'ref_genome':
            if not isinstance(pvalue, basestring):
                ret_val = '%s : invalid type, found %s, expected %s' % (pvalue, type(pvalue), 'str')
            #TODO: Figure it out...
            #elif not os.path.exists(value):
            #    ret_val = '%s : no such directory' % value
        return ret_val


    def store_outputs(self):
        """
        Stores the outputs in json format
        """
        #for debug store also the output keys in a output file
        output_file = os.path.join(self.output_dir, "outputs.log")
        with open(output_file, 'w') as fh:
            logdata = {'outputs' : {}, 'meta': {}}
            logdata['meta'] = self.meta
            for key in self.keys('outputs'):
                logdata['outputs'][key] = getattr(self, key)
            fh.write(json.dumps(logdata) + '\n')

    def store_pickle(self):
        """
        Store myself in a pickle file
        """
        #remvoe all the elements which can not be pickled
        not_ser = {'log': '', 'scheduler': ''}
        for attr in not_ser:
            if self.__dict__.get(attr):
                not_ser[attr] = self.__dict__.pop(attr)
        pickle_file = os.path.join(self.output_dir, STEP_PICKLE)
        with open(pickle_file, 'wb') as fh:
            cPickle.dump(self, fh)
        os.chmod(pickle_file, 0644)
        for attr in not_ser:
            setattr(self, attr, not_ser[attr])

    def load_pickle(self):
        """
        Load the pickle file
        """
        #pickle_file = os.path.join(self.output_dir, STEP_PICKLE)
        with open(os.path.join(self.output_dir, STEP_PICKLE), 'r') as fh:
            obj = cPickle.load(fh)
            for key in obj.__dict__:
                setattr(self, key, getattr(obj, key))


    def is_pickled(self):
        """
        Check if the picke file exists (it also to prevent nfs glitches)
        """
        return  True if os.path.exists(os.path.join(self.output_dir, STEP_PICKLE)) else False


    def distribute(self):
        """
        Submit the step to the scheduler parallelizing the iterable inputs
        """

        self.status = JOB_STATUS.QUEUED
        #initialize the scheduler
        if self.local_step:
            self.scheduler = get_scheduler("SCHED_LOCAL")
        else:
            self.scheduler = scheduler

        if Step.__cfg_is_changed(self.cfg):
            Step.__write_cfg_file(self.cfg)
            Step.__remove_pickle(self.cfg)
        elif self.is_pickled():
            self.load_pickle()
            if self.status == JOB_STATUS.SUCCEEDED:
                self.log.info('Skipping step %s: configuration has not been changed' % self.name)
                return len(self.jobs)

        iterables = self.get_iterables()
        if iterables:
            # Step needs to be distributed
            for iterable in iterables:
                # If this is a file, convert it to list from file contents
                iterable_input = self.cfg.get(iterable,[])
                if not hasattr(iterable_input, '__iter__') \
                   and os.path.exists(iterable_input):
                    with open(iterable_input) as f:
                        self.cfg[iterable] = f.read().splitlines()
            for index in range(0, len(self.cfg[iterables[0]])):
                #copy the config file
                job_cfg = copy.deepcopy(self.cfg)
                #copy the iterable specific to the job
                for iterable in iterables:
                    if iterable in self.cfg and self.cfg[iterable]: # permit a null file
                        job_cfg[iterable] = self.cfg[iterable][index]
                job_cfg['meta']['pipeline'] = self.cfg['meta']['pipeline']
                job_cfg['meta']['step'] = self.cfg['meta']['step']
                for key, value in self.cfg['meta']['job'].iteritems():
                    job_cfg['meta']['job'][key] = value[index]
                self.submit_job(job_cfg)
        else:
            job_cfg = copy.deepcopy(self.cfg)
            self.submit_job(job_cfg)
        return len(self.jobs)


    def submit_job(self, cfg):
        """
        Submit a job step
        """
        job_cnt = str(len(self.jobs))
        status = JOB_STATUS.QUEUED
        self.log.debug('Configuring step %s %s' % (cfg['name'], job_cnt))

        cfg['output_dir'] = os.path.join(cfg["output_dir"], job_cnt)
        job = Step.load_step(cfg)
        job.status = JOB_STATUS.QUEUED

        if Step.__cfg_is_changed(cfg):
            Step.__write_cfg_file(cfg)
            Step.__remove_pickle(cfg)
        elif job.is_pickled():
            job.load_pickle()

        job.__to_db_format()

        if job.status == JOB_STATUS.SUCCEEDED:
            self.log.info('Job %s in %s already completed: skipping' % (cfg['name'], cfg['output_dir']))
            job_id = job_cnt
        else:
            cfg_file = os.path.join(cfg['output_dir'], cfg['name'] + ".cfg")
            self.log.info('Submitting config file %s'% cfg_file)
            job_id = self.scheduler.submit(ut.which('np_runstep.py'), [cfg_file], cfg['output_dir'], self.requirements)

        job.job_id = job_id
        self.jobs[job_id] = job


    @staticmethod
    def __cfg_is_changed(cfg):
        """
        Check if the config of the step is different from the one stored 
        on the file system
        For step disable the diff config since does not wor
        """
        retval = True
        cfg_file = os.path.join(cfg['output_dir'], cfg['name'] + ".cfg")
        if os.path.exists(cfg_file):
            with open(cfg_file, "r") as fh:
                stored_cfg = json.load(fh)
            if not ut.DictDiffer(OrderedDict(stored_cfg), OrderedDict(cfg)).changed():
                retval = False
        return retval


    @staticmethod
    def __write_cfg_file(cfg):
        """
        Write a new config file in the output directory and remove the pickle file
        """
        if not os.path.exists(cfg['output_dir']):
            os.makedirs(cfg['output_dir'], 0775)

        cfg_file = os.path.join(cfg['output_dir'], cfg['name'] + ".cfg")
        with open(cfg_file, "w") as fh:
            fh.write(json.dumps(OrderedDict(cfg)))
                

    @staticmethod
    def __remove_pickle(cfg):
        """
        Remove the pickle file
        """
        pickle_file = os.path.join(cfg['output_dir'], STEP_PICKLE)
        if os.path.exists(pickle_file):
            os.remove(pickle_file)



    def get_status(self):
        """
        Return step and jobs status
        """
        running     = False
        failed      = False
        interrupted = False
        succeeded   = True

        if self.bootstrap:
            self.bootstrap -= 1

        if not self.bootstrap:
            if self.status != JOB_STATUS.SUCCEEDED:
                if self.local_step:
                    time.sleep(1)
                else:
                    time.sleep(5)

        incomplete_jobs = [job_id for job_id in self.jobs if self.jobs[job_id].status != JOB_STATUS.SUCCEEDED]
        if incomplete_jobs:
            for job_id, job_status in self.scheduler.status(incomplete_jobs).iteritems():
                if (job_status == JOB_STATUS.SUCCEEDED
                and not self.jobs[job_id].is_pickled()):
                    job_status = JOB_STATUS.RUNNING

                self.jobs[job_id].set_status(job_status)

                running         |= (job_status == JOB_STATUS.RUNNING)
                failed          |= (job_status == JOB_STATUS.FAILED)
                interrupted     |= (job_status == JOB_STATUS.INTERRUPTED)
                succeeded       &= (job_status == JOB_STATUS.SUCCEEDED)

                if job_status != JOB_STATUS.RUNNING:
                    running |= not self.jobs[job_id].is_pickled()

        if failed:
            self.status = JOB_STATUS.FAILED
        elif interrupted:
            self.status = JOB_STATUS.INTERRUPTED
        elif running:
            self.status = JOB_STATUS.RUNNING
        elif succeeded:
            self.status = JOB_STATUS.SUCCEEDED

        if self.status == JOB_STATUS.SUCCEEDED:
            #if self.stepobj.status != JOB_STATUS.SUCCEEDED:
            self.fetch_results()
            self.store_pickle()
            self.store_outputs()

        return self.status, [self.jobs[idx].__dict__.copy() for idx in self.jobs]


    def fetch_results(self):
        """
        Load the output of each job and merge them
        """

        #check if stepobj has been already loaded
        outputs_val = defaultdict(list)
        outputs_meta = { 'pipeline':{}, 'step':{}, 'job':{} }
        self.log.debug('Loading jobs outputs for step %s...' % self.name)

        for job_id in self.jobs:
            self.jobs[job_id].load_pickle()
            job = self.jobs[job_id]
            outputs_meta['pipeline'] = job.meta['pipeline']
            outputs_meta['step'] = job.meta['step']
            for param in self.keys('outputs'):
                outputs_val[param].extend(getattr(job, param))
            for key, value in job.meta['job'].iteritems():
                if key in outputs_meta['job']:
                    if not hasattr(outputs_meta['job'][key], '__iter__'):
                        outputs_meta['job'][key] = [outputs_meta['job'][key]]
                    outputs_meta['job'][key].append(value)
                else:
                    if self.get_iterables():
                        outputs_meta['job'][key] = [value]
                    else:
                        outputs_meta['job'][key] = value

        for key in self.keys('outputs'):
            setattr(self, key, outputs_val[key])
        self.meta = outputs_meta

        #format the data for the database
        for job_id, job in self.jobs.iteritems():
            job.__to_db_format()


    def __to_db_format(self):
        """
        Convert the Step data to a format specific for a Job
        All the unserializable data needs to be removed
        """
        
        self.meta = self.meta['job']

        #remove all the attributes not needed before store 
        #the jobs object in the db 
        for attr in NOT_DB_ATTR:
            if hasattr(self, attr):
                delattr(self, attr)

        self.inputs = {}
        for key in self.keys('inputs'):
            if hasattr(self, key):
                self.inputs[key] = getattr(self, key)
                delattr(self, key)

        self.outputs = {}
        for key in self.keys('outputs'):
            if hasattr(self, key):
                self.outputs[key] = getattr(self, key)
                delattr(self, key)

        #job.params = {}
        for key in self.keys('params'):
            if hasattr(self, key):
                #job.params[key] = getattr(job, key)
                delattr(self, key)


    def stop(self):
        """
        Interrupt all running jobs
        """
        self.log.info('Stopping incomplete jobs')
        running_jobs = [job_id for job_id in self.jobs if self.jobs[job_id].status == JOB_STATUS.RUNNING]
        if running_jobs:
            self.scheduler.stop(running_jobs)

        for job_id in running_jobs:
            self.jobs[job_id].set_status(JOB_STATUS.INTERRUPTED)

        if self.status != JOB_STATUS.FAILED:
            self.status = JOB_STATUS.INTERRUPTED


    def get_url(self):
        """
        Return the spec url
        """
        url = self.spec.get('url')
        if url and not url.startswith('http'):
            url = 'http://'+url
        return url


    def get_iterables(self):
        """
        Return the names of the iterable inputs, if any, or an empty list.
        """
        iterables = []
        for input in self.spec["args"]["inputs"]:
            if input.get('iterable', False):
                iterables.append(input["name"])
                #if not input.get('required',True):
                #    if input.get('value'): 
                #        iterables.append(input["name"])
                #else:
                #    iterables.append(input["name"])
        return iterables

    def print_params(self):
        """
        Pretty-print all parameters
        """
        self.log.info(json.dumps(self.spec, sort_keys=True, indent=4))

    def set_status(self, status):
        """
        Update the status and time data
        """
        if self.status != status:
            if status == JOB_STATUS.RUNNING:
                self.running_at = datetime.utcnow()
            elif status == JOB_STATUS.SUCCEEDED or status == JOB_STATUS.FAILED:
                self.completed_at = datetime.utcnow()
            self.status = status

    def run(self):
        """
        Pre-process, process and post-process.
        This is the routine called to actually run any step.
        """
        self.status = JOB_STATUS.RUNNING

        this_dir = os.getcwd()
        os.chdir(self.output_dir)

        self.log.info(' running %s on host %s:' %(self.name, socket.gethostname()))
        self.configure_params()
        self.preprocess()
        self.process()
        self.postprocess()
        self.set_outputs()

        self.meta.update({'step': {'name': self.name, 'version': self.__version__}})

        self.status = JOB_STATUS.SUCCEEDED

        self.log.info(' step  %s successfully completed!' % self.name)
        self.store_pickle()
        self.store_outputs()
        os.chdir(this_dir)


    def set_outputs(self):
        """
        Set the output to a absolute paths and also check if they exists
        """

        # Outputs: convert relative to absolute paths and make sure it's a list
        for key in self.keys('outputs'):
            value = getattr(self, key)

            #convert all the outputs to list objects
            is_file_type = self.key_spec(key).get("type") == 'file'
            if type(value) != list:
                if "*" in value and isinstance(value, basestring) and is_file_type:
                    val = [os.path.join(self.output_dir, f) for f in glob.glob(value)]
                    if not val:
                        raise Exception('%s error: reg ex %s does not match any file in the output directory' % (key, value))
                    else:
                        setattr(self, key, val)
                else:
                    setattr(self, key, [value])

            abs_outputs = []
            if is_file_type:
                value = getattr(self, key)
                if isinstance(value, basestring):
                    value = [value]
                if isinstance(value, (list, tuple)):
                    for filename in value:
                        #chech the value exists
                        if self.key_spec(key).get("required", True):
                            if not os.path.exists(filename):
                                raise Exception('File not found: %s' % filename)

                        #convert relative path to absolute path
                        if not os.path.isabs(filename):
                            abs_outputs.append(os.path.normpath(os.path.join(self.output_dir, filename)))
                        else:
                            abs_outputs.append(filename)

                setattr(self, key, abs_outputs)


    def prestart(self):
        """
        Run before the job manager starts splitting into distributed steps.
        """
        pass

    def preprocess(self):
        """
        Pre-process hook: to be run just before process
        """
        pass

    def postprocess(self):
        """
        Post-process hook: to be run just after process
        """
        pass


    def submit_cmd(self, cmd, rc_ok=0, extra_env=None, raise_exception=True, shell=True):
        """
        Subprocess a command and logs the execution
        In case the subprocess return a value different than rc_ok an
        exception is raised
        Args:
            cmd:       the command to submit
            rc_ok:     the expected return code
            extra_env: a dictionary of environment variables to append
        """
        rc = rc_ok
        stderr=''
        stdout=''
        if self.status == JOB_STATUS.SUCCEEDED:
            #if the status is succeded return directly
            self.log.info(' cmd: [%s]' % cmd)
            self.log.info(' cmd skipped because already successfully completed')
            return (rc, stderr, stdout)
        else:
            # construct the command's environment
            step_env = os.environ.copy()

            # clean the LD_LIBRARY_PATH path for the step environment
            if step_env.get('LD_LIBRARY_PATH'):
                del step_env['LD_LIBRARY_PATH']

            # augment with the given extra stuff
            for k in extra_env or {}:
                step_env[k] = '%s:%s' % (extra_env[k], step_env.get(k, ''))

            # create a txt file that contains the command to be executed
            # and the extra_env passed with the current resulting env
            # useful for debugging!
            self.cmd_count += 1
            cmdline_file = os.path.join(self.output_dir,
                                        '__%s.cmd_%s.txt' % (
                                            self.name, self.cmd_count))
            with open(cmdline_file, 'w+') as file:
                file.write('COMMAND\n')
                file.write('--------------------\n')
                if type(cmd) == list:
                    file.write(' '.join(cmd))
                else:
                    file.write(cmd)

                file.write('\n')
                file.write('\n')

                file.write('EXTRA ENV\n')
                file.write('--------------------\n')
                for k in extra_env or {}:
                    file.write('%s=%s\n' % (k, extra_env[k]))

                file.write('\n')
                file.write('\n')

                file.write('CURRENT ENV\n')
                file.write('--------------------\n')
                for k in step_env:
                    file.write('%s=%s\n' % (k, step_env[k]))

            self.log.info('Executing command [%s]' % cmd)

            proc = subprocess.Popen(cmd,
                                    shell=shell,
                                    env=step_env,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

            (stdout, stderr) = proc.communicate()

            rc = proc.returncode
            proc.stdout.close()
            proc.stderr.close()

            # write the tool output/error in an output file
            if stdout or stderr:
                tool_output = os.path.join(self.output_dir, '__%s.log.txt' % (self.name))
                with open(tool_output, 'w+') as file:
                    if stdout:
                        file.write(stdout)
                        file.write('\n')
                        file.write('\n')
                        file.write('--------------------\n')
                        file.write('\n')
                        file.write('\n')

                    if stderr:
                        file.write(stderr)

            if rc != rc_ok:
                # non 0 return code, throw error
                if raise_exception:
                    raise Exception('Non 0 return code: [%s] RC: %s \n\n %s' % (cmd, rc, stdout))
                else:
                    self.log.error('Non 0 return code: [%s] RC: %s' % (cmd, rc))

            return (rc, stderr, stdout)


    def run_cfg(self, cfg):
        """
        Execute the pipeline with the config file
        """

        try:
            if type(cfg) == dict:
                cfg_data = cfg
            else:
                if os.path.exists(cfg):
                    with open(cfg) as fh:
                        cfg_data = json.load(fh)
                else:
                    cfg_data = json.load(cfg)
        except Exception, error:
            raise Exception("Unable to load step cfg: %s" % error)
        else:
            for key in cfg_data:
                setattr(self, key, cfg_data[key])
            self.run()

    @staticmethod
    def import_class(step_name):
        """
        Import and return the step class
        """

        class_name = ''
        try:
            #try to load the step from local
            class_name = import_class(step_name)
        except Exception:
            #try to load the step from step library
            if not step_name.startswith('nespipe.steps.'):
                step_name = 'nespipe.steps.' + step_name
            class_name = import_class(step_name)
        return class_name

    @classmethod
    def create(cls, step_name):
        """
        Create a step object from the step name
        """

        if type(step_name) == type:
            class_name = step_name
        else:
            class_name = cls.import_class(step_name)
        return class_name()


    @classmethod
    def load_cfg(cls, cfg):
        """
        Load and return the step configuration
        """

        try:
            if type(cfg) == dict:
                cfg_data = copy.deepcopy(cfg)
            else:
                if os.path.exists(cfg):
                    with open(cfg) as fh:
                        cfg_data = json.load(fh)
                else:
                    cfg_data = json.load(cfg)
        except Exception, error:
            raise Exception("Unable to load step cfg %s: %s" % (cfg, error))
        else:
            return cfg_data


    @classmethod
    def load_step(cls, cfg):
        """
        Load a the step configuration and instanciate a step
        """

        cfg_data = cls.load_cfg(cfg)
        if 'sys_path' in cfg_data:
            sys.path.insert(0, cfg_data['sys_path'])
        else:
            sys.path.insert(0, os.getcwd())
        try:
            step = cls.create(cfg_data.get('step_class', ''))
            for key in cfg_data:
                if key in step.requirements:
                    #cast memory and cpus to int since they are not validated
                    setattr(step, key, int(cfg_data[key]))
                    step.requirements[key] = int(cfg_data[key])
                else:
                    setattr(step, key, cfg_data[key])
            if 'name' not in cfg_data:
                step.name = cfg_data.get('step_class', '').rsplit(".", 1)[1]
        except:
            raise Exception("Unable to load step class %s " % (cfg_data.get('step_class', '')))
        else:
            del sys.path[0]
            step.cfg = cfg_data
            return step

    def configure_params(self):
        """
        Configure the templated parameters, if any

        Note that it treats replacement by a file parameter in a special way.
        E.g., if input_file is defined as '/foo/bla.txt', {{input_file}} will
        be replace by the raw basename, without extension, of input_file:
        {{input_file}} => 'bla'
        """
        for category in ["inputs", "outputs", "params"]:
            for entry in self.spec["args"].get(category, []):
                # Loop over all entries of all categories of parameters
                name  = entry["name"]
                value = getattr(self, name)
                if value and isinstance(value, basestring):
                    matches = self.tpl_reg.findall(value)
                    for match in matches: # value is templated
                        subst_val = getattr(self, match)
                        # If this is a list, take the first element
                        if type(subst_val)==list:
                            subst_val = str(subst_val[0])
                        else:
                            subst_val = str(subst_val)
                        # If this is a file, take the bare file name
                        if self.key_spec(match).get("type") in ['file', 'ref_genome']:
                            subst_val = os.path.basename(subst_val).split('.')[0]
                        if subst_val:
                            newval = re.sub('{{\s*' + match + '\s*}}', subst_val, value)
                            setattr(self, name, newval)
                            value = newval
                        else:
                            raise Exception("Couldn't replace parameter %s: %s not found" % (entry,match))


class CmdLineStep(Step):
    """
    Fully configurable step
    """

    def __init__(self):
        # Call the base class' initialization
        super(CmdLineStep, self).__init__()

        self.cmd = self.spec['cmd']
        if type(self.cmd) == list:
            self.cmd = ' '.join(self.cmd)

        # Search for all the parameters in the command line
        #TODO: check that all cmd_args correspond to a param
        self.cmd_args = self.tpl_reg.findall(self.cmd)

    def render(self):
        """
        Loop through each cmd_args and render the command line
        """
        cmd = self.cmd
        for arg in self.cmd_args:
            #print 'arg =', arg
            if not hasattr(self, arg):
                raise Exception("Argument {{%s}} has not been set in cmd: %s" % (arg, self.cmd))
            arg_value = getattr(self, arg)
            #print 'value =', arg_value
            if type(arg_value) == list:
                arg_value = ' '.join(arg_value)
            if isinstance(arg_value,(int, float)):
                arg_value = str(arg_value)
            cmd = re.sub('{{\s*' + arg + '\s*}}', arg_value, cmd)
        return cmd

    def preprocess(self):
        """
        Configure the templated parameters
        """
        self.configure_params()


    def process(self):
        """
        Run the step as configured.
        """
        this_dir = os.getcwd()
        os.chdir(self.output_dir)
        self.log.info('[CmdLineStep] moving to %s: %s'% (self.output_dir, os.getcwd()))

        self.submit_cmd(self.render(), extra_env=self.spec.get('extra_env'))
        os.chdir(this_dir)



class RStep(CmdLineStep):
    def __init__(self):
        # Call the base class' initialization
        super(RStep, self).__init__()


        if not self.spec.get('extra_env', ''):
            self.spec["extra_env"] = {
               'PATH' : '/sonas/Software/R/R-3.0.0/bin/',
               'LD_LIBRARY_PATH' : '/sonas/Software/R/R-3.0.0/lib64/R/lib',
               'R_HOME' : '/sonas/Software/R/R-3.0.0/lib64/R'
            }


        pyfilename = sys.modules[self.__module__].__file__
        basename = os.path.splitext(pyfilename)[0]
        for ext in ['.r', '.R']:
            if os.path.exists(basename + ext):
                self.rscript = basename + ext
                break

        self.rscript =os.path.splitext(pyfilename)[0] + '.r'

        self.cmd = self.spec['cmd']
        if type(self.cmd) == list:
            self.cmd = ' '.join(self.cmd)

        # Search for all the parameters in the command line
        #TODO: check that all cmd_args correspond to a param
        self.cmd_args = self.tpl_reg.findall(self.cmd)




class FunctionStep(Step):
    #flag to enable local step execution
    local_step = True

    def __init__(self):
        # Call the base class' initialization
        super(FunctionStep, self).__init__()
        self.local_step = True

    def run(self):
        self.status = JOB_STATUS.RUNNING
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, 0775)

        this_dir = os.getcwd()
        os.chdir(self.output_dir)

        self.configure_params()
        self.process()
        #TODO check how to convert abs path without break groupBySample
        #self.set_outputs()
        self.status = JOB_STATUS.SUCCEEDED
        self.store_pickle()
        self.store_outputs()
        os.chdir(this_dir)


base_classes = [Step, CmdLineStep, RStep, FunctionStep]
