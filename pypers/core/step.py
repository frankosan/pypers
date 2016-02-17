import json
import re
import os
import sys
import cPickle
import subprocess
import socket
import copy
from pypers.utils import utils as ut
from pypers.utils.utils import import_class
from pypers.core.logger import logger
from pypers.core.constants import *

#from pypers.utils.utils import list2cmdline


STEP_PICKLE = '.status.pickle'
ITERABLE_TYPE = 'input_key_iterable'

class JOB_STATUS(object):
    """
    List of possible job statuses
    """
#    NEW         = 'New'   # Not used!!!
    QUEUED      = 'queued'
    RUNNING     = 'running'
    SUCCEEDED   = 'succeeded'
    FAILED      = 'failed'
    INTERRUPTED = 'interrupted'
    SKIPPED     = 'skipped'

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
        self.status = JOB_STATUS.QUEUED
        self.meta = { 'pipeline':{}, 'step':{}, 'job':{}}
        self.reqs = {'memory' : '1', 'cpus' : '1'}
        self.output_dir = '.'
        self.cmd_count = 0

        # parse specs and create keys
        self.spec["name"] = self.__module__.replace('pypers.steps.','').split('.')[-1]
        self.name = self.spec["name"]
        self.__version__ = self.spec['version']

        self.local_step = self.spec.get('local', False)

        for input in self.spec["args"]["inputs"]:
            setattr(self, input["name"], input.get('value', None))
        for output in self.spec["args"]["outputs"]:
            setattr(self, output["name"], output.get('value', []))
        for param in self.spec["args"].get("params",[]):
            setattr(self, param["name"], param.get('value', None))
        
        ut.dict_update(self.reqs, self.spec.get('requirements', {'memory' : '1', 'cpus' : '1'}))
        for key in self.reqs:
            setattr(self, key, int(self.reqs[key]))

        #set the jvm memory
        if 'memory' in self.reqs:
            self.jvm_memory = int(int(self.reqs['memory']) * 0.9)
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

    def get_output_keys(self):
        """
        Return list of output key strings
        """
        return [k["name"] for k in self.spec["args"]["outputs"]]

    def get_outputs(self):
        """
        Return dictionary: { output key: output file name[s] }
        """
        outputs = {}
        for okey in self.get_output_keys():
            outputs[okey] = getattr(self,okey)
        return outputs

    def get_input_keys(self, required_only=False):
        """
        Return list of input key strings.
        If all is true return only the required parameters without a default
        """
        input_keys = []
        for input_key in self.spec["args"]["inputs"]:
            if (required_only and not 'value' in input_key) or (not required_only):
                input_keys.append(input_key["name"])
        return input_keys

    def get_param_values(self, get_req=True):
        """
        Return dictionary of parameter definitions including memory and cpus requirements
        If 'get_req' is set to false then memory and cpus requirements are not returned
        """
        ret_dict = {}
        for param in self.spec["args"].get("params", []):
            ret_dict[param["name"]] = getattr(self, param["name"])

        if get_req:
            for key in self.reqs:
                if self.reqs.get(key) != 1:
                    ret_dict[key] = self.reqs.get(key) 

        return ret_dict


    def get_param_keys(self, required_only=False):
        """
        Return a list of keys parameters.
        If required is True return only a list of the required parameters
        """
        params = []
        for param in self.get_params():
            if (required_only and not 'value' in param) or (not required_only):
                params.append(param["name"])
        return params


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


    def get_params(self):
        """
        Return definition of the parameters
        """
        return self.spec["args"].get("params", [])


    def find_param(self, name):
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
        required_key = self.get_input_keys(required_only=True)
        required_key.extend(self.get_param_keys(required_only=True))
        for key in required_key:
            if key in cfg:
                key_spec = self.find_param(key)
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


    def get_url(self):
        """
        Return the spec url
        """
        url = self.spec.get('url')
        if url and not url.startswith('http'):
            url = 'http://'+url
        return url


    def get_iterable(self):
        """
        Return the names of the iterable inputs, if any, or an empty list.
        """
        iterables = []
        for input in self.spec["args"]["inputs"]:
            if input.get('iterable', False):
                iterables.append(input["name"])
        return iterables

    def print_params(self):
        """
        Pretty-print all parameters
        """
        self.log.info(json.dumps(self.spec, sort_keys=True, indent=4))

    def set_param(self, name, value):
        # Values are only stored in the step itself
        setattr(self,name,value)

    def store_pickle(self):
        """
        Store myself in a pickle file
        """
        self.log = '' # Cannot be pickled...
        pickle_file = os.path.join(self.output_dir, STEP_PICKLE)
        with open(pickle_file, 'wb') as fh:
            cPickle.dump(self, fh)
        os.chmod(pickle_file, 0644)

        #for debug store also the output keys in a output file
        output_file = os.path.join(self.output_dir, "outputs.log")
        with open(output_file, 'w') as fh:
            logdata = {'outputs' : {}, 'meta': {}}
            logdata['meta'] = self.meta
            for key in self.get_output_keys():
                logdata['outputs'][key] = getattr(self, key)
            fh.write(json.dumps(logdata) + '\n')


    def run(self):
        """
        Pre-process, process and post-process.
        This is the routine called to actually run any step.
        """
        logger.set_stdout_level(logger.DEBUG)
        self.log = logger.get_log()
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
        os.chdir(this_dir)


    def set_outputs(self):
        """
        Set the output to a absolute paths and also check if they exists
        """

        # Outputs: convert relative to absolute paths and make sure it's a list
        for key in self.get_output_keys():
            value = getattr(self, key)
            if type(value) != list and isinstance(value, basestring):
                if "*" in value:
                    val = ut.find(self.output_dir, value)
                    if not val:
                        raise Exception('%s error: reg ex %s does not match any file in the output directory' % (key, value))
                    else:
                        setattr(self, key, val)
                else:
                    setattr(self, key, [value])

            abs_outputs = []
            if self.find_param(key).get("type") == 'file':
                value = getattr(self, key)
                if isinstance(value, basestring):
                    value = [value]
                if isinstance(value, (list, tuple)):
                    for filename in value:
                        #chech the value exists
                        if self.find_param(key).get("required", True):
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
            if not step_name.startswith('pypers.steps.'):
                step_name = 'pypers.steps.' + step_name
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
                if key in step.reqs:
                    #cast memory and cpus to int since they are not validated
                    setattr(step, key, int(cfg_data[key]))
                    step.reqs[key] = int(cfg_data[key])
                else:
                    setattr(step, key, cfg_data[key])
            if 'name' not in cfg_data:
                step.name = cfg_data.get('step_class', '').rsplit(".", 1)[1]
        except:
            raise Exception("Unable to load step class %s " % (cfg_data.get('step_class', '')))
        else:
            del sys.path[0]
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
                if value and type(value) is not list and not isinstance(value,(int, float)):
                    matches = self.tpl_reg.findall(value)
                    for match in matches: # value is templated
                        subst_val = getattr(self, match)
                        # If this is a list, take the first element
                        if type(subst_val)==list:
                            subst_val = str(subst_val[0])
                        else:
                            subst_val = str(subst_val)
                        # If this is a file, take the bare file name
                        if self.find_param(match).get("type") in ['file', 'ref_genome']:
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
               'PATH' : '/software/pypers/R/R-3.0.0/bin/',
               'LD_LIBRARY_PATH' : '/software/pypers/R/R-3.0.0/lib64/R/lib',
               'R_HOME' : '/software/pypers/R/R-3.0.0/lib64/R'
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
        os.chdir(this_dir)


base_classes = [Step, CmdLineStep, RStep, FunctionStep]
