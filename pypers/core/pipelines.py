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
import os
import pwd
import time
import sys
import networkx as nx
import copy
import shutil

from collections import defaultdict

#from nespipe.core.jobscheduler import JobScheduler
from nespipe.core.logger import logger
from nespipe.core.step import Step, set_scheduler
from nespipe.core.constants import *
from nespipe.utils import utils as ut
from nespipe.pipelines import pipeline_names
from nespipe.db.models import db_models
from nespipe.db.models import mongo
from nespipe.config import WORK_DIR
from nespipe.pipelines import pipeline_specs

LOCK_FILE = 'LOCK'
FINAL_STEP = 'finalize'


class Pipeline(Step):
    """
    Pipeline object: takes care of the execution of a whole pipeline
    """

    __version__ = "$Format:%H$"

    params = [
        {
            "type": "str",
            "name": "project_name",
            "descr": "the project name (will be displayed in the run list)"
        },
        {
            "type": "str",
            "name": "description",
            "descr": "description of the pipeline (will be displayed in the run list)"
        },
        {
            "type": "dir",
            "name": "output_dir",
            "descr": "output directory"
        }
    ]

    def __init__(self, cfg, user='Unknown', db=True, schedname="SCHED_CONDOR"):
        """
        Read in the pipeline graph and load the configuration.
        """
        self.all_ok = True
        self.user = user
        self.status = JOB_STATUS.QUEUED
        self.lock = ''

        self.completed = []
        self.running = {}
        self.outputs = {}
        self.schedname = schedname
        db_model_name = "MONGO_DB" if db else "STUB_DB"

        # Load configuration
        self.one_step = False
        try:
            self.cfg = Pipeline.load_cfg(cfg)
        except Exception as e1:
            print('Failed to load config as pipeline (error=%s). Trying as step' % e1)
            try:
                self.cfg = Step.load_cfg(cfg)
                self.step = Step.load_step(self.cfg)
                self.one_step = True
            except Exception as e2:
                 Exception("Unable to load config file %s:\n" \
                           "pipeline load: %s\n" \
                           "step load: %s" % (cfg, e1, e2))

        # Set all additional information
        self.run_id = self.cfg.get('run_id')
        if self.one_step:
            self.name  = self.step.name
            self.label = self.step.name
            self.project_name = self.cfg.get('project_name', '')
            self.description  = self.cfg.get('description', '')
            self.output_dir   = self.step.output_dir
            self.ordered      = [self.step.name]
        else:
            self.name  = self.cfg['name']
            self.label = self.cfg['label']
            self.project_name = self.cfg['config']['pipeline'].get('project_name', '')
            self.description  = self.cfg['config']['pipeline'].get('description', '')
            self.output_dir   = self.cfg['config']['pipeline']['output_dir']
            if not self.output_dir.startswith('/scratch'):
                self.cfg['dag']['nodes'][FINAL_STEP] = 'utils.Finalize' #TODO: Make it work for one_step as well
            self.ordered      = Pipeline.ordered_steps(self.cfg)


        self.sys_path = self.cfg.get('sys_path')
        if self.sys_path:
            sys.path.insert(0, self.sys_path)

        self.dag = self.create_dag(self.cfg, one_step=self.one_step)

        self.meta = {
            'pipeline': {
                'label': self.label,
                'project_name': self.project_name,
                'descr': self.description,
                'run_id': self.run_id
            },
            'steps': {},
            'job' : {}
        }

        self.db = db_models[db_model_name](self.name, self.cfg, self.ordered, self.user, output_dir=self.output_dir)
        if hasattr(self.db, 'run_id'):
            self.run_id = self.db.run_id
            self.cfg['run_id'] = self.run_id

        # Define the output directories
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, 0775)

        # Use default output dir under /scratch/cgi/nespipe (linked to user-defined dir.)
        # if: a) this run is using the db (so we have a run ID); b) it is not a demux. run;
        # and c) the user-defined directory is not already under /scratch
        if self.run_id and not (self.name == 'demultiplexing'):
            dirname = '%s_%d' % (self.name, self.db.run_id)
            self.output_dir = os.path.join(self.output_dir, dirname)
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, 0775)
            # In case of /scratch, do not create an additional sub-directory
            if self.output_dir.startswith('/scratch'):
                self.work_dir = self.output_dir
            else:
                self.work_dir = os.path.join(WORK_DIR, self.user, dirname)
                if not os.path.exists(self.work_dir):
                    os.makedirs(self.work_dir, 0775)
                symlink = os.path.join(self.output_dir, 'work_area')
                if not os.path.exists(symlink):
                    os.symlink(self.work_dir, symlink)
        else:
            self.work_dir = self.output_dir

        ut.pretty_print('Output directories: output_dir=%s, work_dir=%s' % (self.output_dir, self.work_dir))
        self.db.update_pipeline(self.run_id, {'output_dir': self.output_dir,
                                              'work_dir':   self.work_dir })


    @staticmethod
    def create_dag(cfg, one_step=False):
        """
        Create and return a dag object
        """

        dag = nx.DiGraph()
        if one_step:
            dag.add_node(cfg['name'], class_name=cfg["step_class"])
        else:
            if cfg.get('inputs', ''):
                dag.add_node('inputs')
            for step in cfg['dag']['nodes']:
                dag.add_node(step, class_name=cfg['dag']['nodes'][step])
            for edge in cfg['dag']['edges']:
                dag.add_edge(edge['from'], edge['to'], edge)

        return dag

    @classmethod
    def validate_config(cls, cfg, user):
        """
        Check if all the config params are ok
        """

        retval = defaultdict(dict)
        s_errors = defaultdict(dict)

        #try:
        cfg = cls.load_cfg(cfg)
        params = cls.get_params(cfg)
        unb_inputs = cls.get_unbound_inputs(cfg)

        #validate step section
        for stepname in params['steps']:
            if stepname is not 'inputs':
                classname = cfg['dag']['nodes'][stepname]
                stepobj = Step.create(classname)
                if stepname in cfg['config']['steps']:
                    required_keys = []
                    required_keys.extend(unb_inputs.get(stepname, []))
                    required_keys.extend(stepobj.keys(['params'], req_only=True))
                    stepcfg = cfg['config']['steps'][stepname]
                    for key in required_keys:
                        if key in stepcfg:
                            param_spec = stepobj.key_spec(key)
                            error_msg = stepobj.validate_value(stepcfg[key], param_spec['type'], param_spec['name'])
                            if error_msg:
                                s_errors[stepname][key] = error_msg
                        else:
                            s_errors[stepname][key] = 'missing value'
                else:
                    for key in stepobj.keys(['params'], req_only=True):
                        s_errors[stepname][key] = 'missing value'
                    if stepname in unb_inputs:
                        for key in unb_inputs[stepname]:
                            s_errors[stepname][key] = 'missing value'


        #validate pipeline section
        p_errors = {}
        if not cfg['config']['pipeline']['project_name']:
            p_errors['project_name'] = 'missing value'

        if not cfg['config']['pipeline']['description']:
            p_errors['description'] = 'missing value'

        if not cfg['config']['pipeline']['output_dir']:
            p_errors['output_dir'] = 'missing value'
        else:
            output_dir = cfg['config']['pipeline']['output_dir']
            if not output_dir.startswith('/'):
                p_errors['output_dir'] = '%s : not an absolute path' % output_dir
            if not isinstance(output_dir, basestring):
                p_errors['output_dir'] = '%s : invalid type, found %s, expected %s' % (output_dir, type(output_dir), 'str')
            #elif not ut.has_write_access(output_dir):
            #    p_errors['output_dir'] = '%s : not writable by user' % (output_dir)

        if s_errors:
            retval['steps'] = s_errors

        if p_errors:
            retval['pipeline'] = p_errors

        return retval

    @classmethod
    def get_unbound_inputs(cls, cfg):
        """
        Get the unbound inputs
        """

        cfg = cls.load_cfg(cfg)
        dag = cls.create_dag(cfg)

        # Step parameters
        uinputs = defaultdict(dict)
        for stepname, classname in cfg['dag']['nodes'].iteritems():
            step = Step.create(classname)
            input_keys = step.keys('inputs', req_only=True)
            if input_keys:
                for pred in dag.predecessors(stepname):
                    # Remove any key that is already bound
                    for binding in dag[pred][stepname].get('bindings', []):
                        key = binding.split('.')[1]
                        #maybe it has been already removed
                        if key in input_keys:
                            input_keys.remove(key)

                if input_keys:
                    uinputs[stepname] = input_keys

        return uinputs

    @staticmethod
    def create_steps(cfg):
        stepobjs = {}
        if 'sys_path' in cfg:
            sys.path.insert(0, cfg['sys_path'])
        for stepname, classname in cfg['dag']['nodes'].iteritems():
            stepobjs[stepname] = Step.create(classname)
        if 'sys_path' in cfg:
            del sys.path[0]

        return stepobjs

    @classmethod
    def get_params(cls, cfg):
        """
        Return the list of required parameters for all the configurable steps in the pipeline.
        Parses the config file to look for all step parameters as well as unconnected input keys.
        """
        cfg = cls.load_cfg(cfg)
        # Step parameters
        params = defaultdict(dict)
        params['steps'] = defaultdict(dict)
        params['pipeline'] = defaultdict(dict)
        params['steps_order'] = nx.topological_sort(cls.create_dag(cfg))

        #create all the steps objects
        stepobjs = Pipeline.create_steps(cfg)

        #get the configuration of the steps
        steps_config = {}

        if cfg.get('config', {}).get('steps', {}):
            steps_config = copy.deepcopy(cfg['config']['steps'])


        #add the parameters and unbound inputs
        for stepname in stepobjs:
            params['steps'][stepname]['descr'] = stepobjs[stepname].spec.get('descr')
            params['steps'][stepname]['url'] = stepobjs[stepname].get_url()
            step_params = stepobjs[stepname].keys_specs(['params', 'requirements'])
            if step_params:
                params['steps'][stepname]["params"] = copy.deepcopy(step_params)
                if stepname in steps_config:
                    for key in steps_config[stepname]:
                        for i, param in enumerate(params['steps'][stepname]["params"]):
                            if param['name'] == key:
                                params['steps'][stepname]["params"][i]['value'] = copy.deepcopy(steps_config[stepname][key])
                                #params['steps'][stepname]["params"][i]['readonly'] = True

        if cfg.get('inputs', ''):
            params['steps']['inputs'] = {}
            params['steps']['inputs']['descr'] = ["Dispatch inputs to subsequent steps"]
            params['steps']['inputs']['inputs'] = cfg.get('inputs', '')

        #get unbound inputs
        steps_inputs = cls.get_unbound_inputs(cfg)

        for stepname in steps_inputs:
            params['steps'][stepname]['inputs'] = []
            for input_key in steps_inputs[stepname]:
                inputspec = copy.deepcopy(stepobjs[stepname].key_spec(input_key))
                #overwrite the value with the value set in the config section
                cfg_value = steps_config.get(stepname, {}).get(input_key, {})
                if cfg_value:
                    inputspec['value'] = cfg_value
                params['steps'][stepname]['inputs'].append(inputspec)

        # Mandatory pipeline parameters
        params['pipeline']['params'] = cls.params

        refgenomes = cls.get_refgenomes(cfg, steps_inputs)
        if refgenomes:
            params['pipeline']['refgenomes'] = refgenomes

        return dict(params)


    @classmethod
    def get_refgenomes(cls, cfg, unbound=None):
        """
        Return a 2 level dictionary containing the path of the reference
        genome grouped by labels.
        A label is a combination of species, version and variation
            {
                "label1": {
                    "stepname1" : { "input_key1" : "/path1"},
                    "stepname2" : { "input_key1" : "/path2"}
                }
                "label2": {
                    "stepname1" : { "input_key1  : "/path3"},
                    "stepname2" : { "input_key1" : "/path4"}
                }
            }
        The "unbound" dictionary contains the steps that have unbound inputs:
        if set, only those steps will be considered
        """

        refs = defaultdict(dict)
        tools = set()

        # Collect all tools that require a ref. genome
        for stepname, classname in cfg['dag']['nodes'].iteritems():
            if unbound==None or stepname in unbound:
                step = Step.create(classname)
                for ref in step.get_refgenome_tools():
                    tools.add(ref['tool'])
                    refs[stepname][ref['name']] = ref['tool']

        # Get corresponding ref genomes
        refs_by_label = {}
        for ref in mongo.get_refgenomes(tools):
            label = "%s %s" % (ref['_id']['species'], ref['_id']['version'])
            if 'variation' in ref['_id']:
                label += " (%s)" % ref['_id']['variation']
            for stepname in refs:
                if not label in refs_by_label:
                    refs_by_label[label] = {}
                refs_by_label[label][stepname] = {}
                for param_key in refs[stepname]:
                    tool = refs[stepname][param_key]
                    if tool in ref['paths']:
                        refs_by_label[label][stepname][param_key] = ref['paths'][tool]

        return refs_by_label


    @staticmethod
    def extend_cfg(cfg1, cfg2):
        """
        Merge the 2 pipeline configuration
        """
        cfg2_nodes = cfg2.get('dag', {}).get('nodes', {})
        cfg2_edges = cfg2.get('dag', {}).get('edges', {})
        cfg2_config = cfg2.get('config', {}).get('steps', {})

        if cfg2_nodes:
            cfg1['dag']['nodes'].update(cfg2_nodes)

        if cfg2_edges:
            cfg1['dag']['edges'].extend(cfg2_edges)

        if cfg2_config:
            cfg1['config']['steps'].update(cfg2_config)

        return cfg1


    @classmethod
    def ordered_steps(cls, cfg):
        """
        Return ordered steps from config
        """
        return nx.topological_sort(cls.create_dag(cfg))

    @classmethod
    def load_cfg(cls, cfg):
        """
        Return the json cfg
        Is expecting as input one between a file, a json text or a dictionary
        """

        cfg_load = None
        try:
            if type(cfg) == dict:
                cfg_load = copy.deepcopy(cfg)
            elif isinstance(cfg, basestring):
                if os.path.exists(cfg):
                    with open(cfg) as fh:
                        cfg_load = json.load(fh)
                        if 'sys_path' not in cfg_load:
                            cfg_load['sys_path'] = os.path.dirname(os.path.realpath(cfg))
                else:
                    cfg_load = json.load(cfg)
        except Exception as e:
            raise Exception("Unable to load config file %s: %s" % (cfg, e))
        else:
            #load the spec_type or spec_file into the json_spec
            #if they exists
            cfg_data = { 'config' : {'steps': {}, 'pipeline' : {'project_name' : '', 'description' : '', 'output_dir': ''}}}
            ut.dict_update(cfg_data, cfg_load)

            if 'sys_path' in cfg_data:
                sys.path.insert(0, cfg_data['sys_path'])

            pipeline_to_load = cfg_data['dag'].pop("load") if "load" in cfg_data['dag'] else None
            if pipeline_to_load:
                try:
                    if os.path.exists(pipeline_to_load):
                        spec_file = pipeline_to_load
                    else:
                        if pipeline_to_load in pipeline_names:
                            spec_file = pipeline_names[pipeline_to_load]
                        else:
                            raise Exception("Pipeline %s not found in list of pipelines: [%s]"
                                            % (pipeline_to_load, ','.join(pipeline_names)))

                    with open(spec_file) as fh:
                        ut.pretty_print("Loading pipeline spec from %s" % spec_file)
                        spec = json.load(fh)
                        stepobjs = Pipeline.create_steps(spec)
                        steps_defaults = {}
                        for step in stepobjs:
                            step_default = stepobjs[step].keys_values(['params', 'requirements'])
                            if step_default:
                                steps_defaults[step] = step_default

                        spec.setdefault('config', {})
                        spec['config'].setdefault('pipeline', {})
                        spec['config'].setdefault('steps', {})
                        ut.dict_update(spec['config']['steps'], steps_defaults, replace=False)
                        ut.dict_update(spec['config'], cfg_data.get('config', ''))
                        cfg_data = spec
                except:
                    raise


            if cfg_data.get('config', {}).get('pipeline', {}).get('refgenome',{}):
                key_refgenome = cfg_data['config']['pipeline'].pop('refgenome')
                try:
                    ref_genomes = Pipeline.get_refgenomes(cfg_data)
                    if key_refgenome in ref_genomes:
                        # set refgenome parameters in each step (update config if already exists)
                        for step in ref_genomes[key_refgenome]:
                            if step in cfg_data['config']['steps']:
                                cfg_data['config']['steps'][step].update(ref_genomes[key_refgenome][step])
                            else:
                                cfg_data['config']['steps'][step] = ref_genomes[key_refgenome][step]
                    else:
                        raise Exception("unable to load ref genome paths for %s " % key_refgenome)
                except Exception, e:
                    raise

            if 'sys_path' in cfg_data:
                del sys.path[0]

            return cfg_data

    def plot(self, file_name=None):
        """
        Plot the DAG of the pipeline
        """
        import matplotlib.pyplot as plt
        nx.draw_networkx(self.dag)
        if not file_name:
            file_name = os.path.join(self.output_dir, self.name + '.png')
        plt.savefig(file_name)


    def get_next_steps(self):
        """
        Get the list of steps that are ready to run
        """
        next_steps = set()
        for node in self.ordered:
            if node not in self.completed and node not in self.running:
                ready = True
                for parent in self.dag.predecessors(node):
                    if parent not in self.completed:
                        ready = False
                if ready:
                    next_steps.add(node)


        # delay final step till the end
        remaining = len(self.dag.nodes()) - len(self.completed)

        if remaining > 1 and (FINAL_STEP in next_steps):
            next_steps.remove(FINAL_STEP)

        if len(next_steps) > 0:
            self.log.info('Next steps to run: [%s]' % ','.join(next_steps))
        return next_steps


    def run_step(self, step_name):
        """
        Configure and run a job for the given step
        """

        #skip the input step
        if step_name == 'inputs':
            self.completed.append(step_name)
            self.outputs[step_name] = self.cfg['config']['steps'].get(step_name, {})
            self.outputs[step_name]['output_dir'] = ''
            self.db.update_step_status(step_name, JOB_STATUS.RUNNING)
            self.db.update_step_status(step_name, JOB_STATUS.SUCCEEDED)
            self.db.set_step_outputs(step_name, self.outputs[step_name])
        else:
            if self.one_step:
                step_config = self.cfg
                step_config['sys_path'] = self.sys_path
                step_config['output_dir'] = self.output_dir
                step_config['meta'] = { 'meta' : { 'pipeline':{}, 'step':{}, 'job':{} }}
                ut.dict_update(step_config['meta']['pipeline'], self.meta['pipeline'])
            elif step_name == FINAL_STEP:
                step_config = { 'meta' : { 'pipeline':{}, 'step':{}, 'job':{} } }
                ut.dict_update(step_config['meta']['pipeline'], self.meta['pipeline'])
                step_config['name'] = FINAL_STEP
                step_config['step_class'] = self.dag.node[step_name]['class_name']
                step_config['target_dir'] = self.output_dir
                step_config['source_dir'] = self.work_dir
                step_config['output_dir'] = os.path.join(self.work_dir, step_name)
                self.configure_finalstep(step_config)
            else:
                step_config = { 'meta' : { 'pipeline':{}, 'step':{}, 'job':{} } }
                ut.dict_update(step_config['meta']['pipeline'], self.meta['pipeline'])
                step_class = self.dag.node[step_name]['class_name']
                step_config['name'] = step_name
                step_config['sys_path'] = self.sys_path
                step_config['step_class'] = step_class
                step_config['output_dir'] = os.path.join(self.work_dir, step_name)

                # 1. Form input keys
                # Remember: edges are labelled by 'from' keys
                for pred in self.dag.predecessors(step_name):
                    edge = self.dag[pred][step_name]
                    # Not an actual loop: just get key/value
                    for bind_to, bind_from in edge.get('bindings', {}).iteritems():
                        to_key = bind_to.split('.')[1]
                        if hasattr(bind_from, '__iter__'):
                            for from_key in bind_from:
                                key = from_key.split('.')[1]
                                out = self.outputs[pred][key]
                                if to_key in step_config:
                                    if isinstance(step_config[to_key], basestring):
                                        step_config[to_key] = [step_config[to_key]]
                                    step_config[to_key].extend(out)
                                else:
                                    step_config[to_key] = out
                        else:
                            from_key = bind_from.split('.')[1]
                            out = self.outputs[pred][from_key]
                            if to_key in step_config:
                                if isinstance(step_config[to_key], basestring):
                                    step_config[to_key] = [step_config[to_key]]
                                step_config[to_key].extend(out)
                            else:
                                step_config[to_key] = out

                    # Transfer metadata of previous step to next step
                    for key in self.meta['steps'].get(pred, {}):
                        step_config['meta'][key] = self.meta['steps'][pred][key]

            # 2. Form step config.
            if not self.one_step:
                ut.dict_update(step_config, self.cfg['config']['steps'].get(step_name, {}), replace=False)
                if step_name == FINAL_STEP:
                    # final step: pass full pipeline metadata
                    step_config['meta'].update(self.meta)
                else:
                    self.update_metadata(step_name, step_config[KEY_META])

            # 3. Submit step
            self.log.info('Executing step %s' % str(step_name))
            self.log.debug('  step configuration:\n %s' % ut.format_dict(step_config, indent=4))
            self.log.info('  step %s queued ' % str(step_name))

            self.running[step_name] = Step.load_step(step_config)
            job_counter = self.running[step_name].distribute()
            self.db.start_step(step_name, step_config, job_counter)

    def update_metadata(self, step_name, step_meta):
        """
        Store step metadata (if any) and pull out global metadata from it
        """
        self.meta['steps'][step_name] = step_meta
        modified = False
        if 'pipeline' in step_meta:
            ut.dict_update(self.meta['pipeline'], step_meta['pipeline'])
            #self.log.debug('Pulled metadata from step: %s' % ut.format_dict(self.meta))
            self.db.update_pipeline_metadata(copy.deepcopy(self.meta['pipeline']))
        self.db.update_step_metadata(step_name, copy.deepcopy(self.meta['steps'][step_name]['step']))


    def update_status(self):
        """
        Update list of completed jobs
        """
        for step_name in copy.copy(self.running):
            self.log.debug('Running jobs: %s' % ','.join(self.running))
            step_status, jobs_status = self.running[step_name].get_status()
            self.db.update_step_status(step_name, step_status, jobs_status)
            if self.status == JOB_STATUS.QUEUED and step_status == JOB_STATUS.RUNNING:
                self.status = JOB_STATUS.RUNNING
            if step_status == JOB_STATUS.SUCCEEDED:
                self.completed.append(step_name)
                self.log.info("Step %s completed" % step_name)
                self.outputs[step_name] = self.running[step_name].keys_values('outputs')
                self.outputs[step_name]['output_dir'] = self.running[step_name].output_dir
                
                self.update_metadata(step_name, self.running[step_name].meta)
                self.db.set_step_outputs(step_name, self.outputs[step_name])
                self.log.debug('Got outputs:\n%s' % ut.format_dict(self.outputs[step_name], indent=4))
                self.running.pop(step_name)
                self.log.info('Completed jobs: (%s)' % ','.join(self.completed))
            elif step_status == JOB_STATUS.FAILED:
                self.log.error('Step %s failed' % step_name)
                self.log.error('+++ Stopping pipeline %s +++' % self.name)
                self.status = JOB_STATUS.FAILED
                self.all_ok = False
            elif step_status == JOB_STATUS.INTERRUPTED:
                self.log.error('Step %s interrupted' % step_name)
                self.log.error('+++ Stopping pipeline %s +++' % self.name)
                self.status = JOB_STATUS.INTERRUPTED
                self.all_ok = False

            self.db.update_pipeline_status(self.status)

    def get_metainfo(self, step_name):
        """
        Return a dictionary with generic information about pipeline and step
        """
        info = {}
        info['pipeline'] = { 'name':    self.name,
                             'version': self.__version__ }
        info['user'] = { 'login':    self.user,
                         'fullname': pwd.getpwnam(self.user).pw_gecos }
        step_class = self.dag.node[step_name]['class_name']
        stepobj = Step.create(step_class)
        info['step'] = { 'name': step_name,
                         'class': step_class,
                         'version': stepobj.__version__ }
        return info


    def configure_finalstep(self, config):
        """
        Configure copy and deletion in final step
        """

        ### 1. Result files
        results_keys = self.cfg["config"].get("pipeline", {}).get("results", [])
        results_files = []
        for key in results_keys:
            # Allow for "step" or "step.output_key"
            path = key.split('.')
            step_name = path[0]
            if len(path)==1:
                output_keys = self.outputs[step_name].keys()
                if 'output_dir' in output_keys:
                    output_keys.remove('output_dir')
            else:
                output_keys = [path[1]]
            for okey in output_keys:
                files = self.outputs[step_name].get(okey)
                if not files:
                    self.log.warning('Did not find any file corresponding to %s' % okey)
                else:
                    while type(files[0]) == list:
                        files = [item for sublist in files for item in sublist]
                    if hasattr(files, '__iter__'):
                        results_files.extend(files)
                    else:
                        results_files.append(files)

        ### 2. File deletion (also resets corresponding step)
        del_keys  = self.cfg["config"].get("pipeline", {}).get("delete", [])
        delete_files = []
        for key in del_keys:
            # Allow for "step" or "step.output_key"
            path = key.split('.')
            step_name = path[0]
            if len(path)==1:
                output_keys = self.outputs[step_name].keys()
                if 'output_dir' in output_keys:
                    output_keys.remove('output_dir')
            else:
                output_keys = [path[1]]
            for okey in output_keys:
                files = self.outputs[step_name].get(okey)
                if not files:
                    self.log.warning('Did not find any file corresponding to %s' % okey)
                else:
                    while type(files[0]) == list:
                        files = [item for sublist in files for item in sublist]
                    if hasattr(files, '__iter__'):
                        delete_files.extend(files)
                    else:
                        delete_files.append(files)

        config['results_files'] = results_files
        config['delete_files'] = delete_files


    def stop(self):
        """
        Interrupt currently running pipeline
        """
        self.log.info('Stopping pipeline...')
        self.all_ok = False
        for step_name in self.running:
            #stop the jobs
            self.running[step_name].stop()
            #get the job status and update the db
            step_status, jobs_status = self.running[step_name].get_status()
            self.db.update_step_status(step_name, step_status, jobs_status)

            #if self.running[step_name].status != JOB_STATUS.FAILED:
            #    self.db.update_step_status(step_name, JOB_STATUS.INTERRUPTED, [{}], 0)
        return 0


    def run(self, local=False, verbose=False):
        """
        Run a node of the pipeline
        If the pipeline is completed return False otherwise True

        The 'local' switch turns on the configuration for local running (no server)
        """

        # Setup the logger
        logger.add_file(os.path.join(self.work_dir, 'pipeline.log'))
        if local or verbose:
            logger.set_stdout_level(logger.DEBUG if verbose else logger.INFO)
        self.log = logger.get_log()

        set_scheduler(self.schedname)

        # Check and create lock file
        self.lock = os.path.join(self.work_dir, LOCK_FILE)
        if os.path.exists(self.lock):
            raise Exception('Directory already in use: remove %s first' % self.lock)
        else:
            with open(self.lock, 'w') as fh:
                pass

        # Store config file and log some information
        with open(os.path.join(self.work_dir, 'pipeline.cfg'), 'w') as fh:
            self.log.info('Saving configuration to file %s' % fh.name)
            json.dump(self.cfg, fh, indent=4, sort_keys=True)

        #self.log.info('Environment:\n %s' % os.environ)

        self.all_ok = True
        while self.all_ok:
            self.update_status()
            if self.all_ok: # because update_status takes time...
                if (len(self.dag.nodes()) - len(self.completed))>0:
                    for step_name in self.get_next_steps():
                        self.run_step(step_name)
                else:
                    if self.work_dir != self.output_dir:
                        self.db.update_output_dir(self.work_dir, self.output_dir)
                    self.log.info('')
                    self.log.info('')
                    self.log.info('+++ Pipeline %s completed +++' % self.name)
                    self.status = JOB_STATUS.SUCCEEDED
                    self.db.update_pipeline_status(self.status)
                    return 0
            else:
                self.stop()

