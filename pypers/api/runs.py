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

import copy
import os
import sys
import json
import time

from bson import json_util
from collections import defaultdict
from py2cytoscape import util as cy
from flask import request, send_file
from flask.ext.restful import reqparse, Resource
from nespipe.utils.execute import run_as

from nespipe.core.pipelines_manager import pm
from nespipe.core.pipelines import Pipeline
from nespipe.core.constants import JOB_STATUS
from nespipe.core.step import Step
from nespipe.pipelines import pipeline_specs, pipelines
from nespipe.db.models import mongo as dbmodel
from nespipe.db.models.mongo import PipelineDbConnector
from nespipe.utils import utils as ut
from collections import defaultdict
from nespipe.api.authentication import auth, auth_get_username

db = PipelineDbConnector()


class RunsApi:
    class Runs(Resource):
        @auth.login_required
        def get(self, type):
            """
            Get the list of runs
            """

            parser = reqparse.RequestParser()
            parser.add_argument('user'  , type=str, default=None)
            parser.add_argument('name'  , type=str, default=None)
            parser.add_argument('status', type=str, default=[], action='append')
            parser.add_argument('offset', type=int, default=0)
            parser.add_argument('limit' , type=int, default=50)

            args = parser.parse_args()

            query = {}
            if type == 'steps':
                query = {
                    'single_step' : True,
                }
            elif type == 'pipelines':
                query = {
                    'single_step' : {'$nin': [True]},
                    'name' :  args['name']
                }

            query['user'] = args['user']
            arg_status = args.get('status', [])
            if arg_status:
                query['status'] = {"$in": arg_status}

            # filter None values from query
            query = {k: v for k, v in query.items() if not v == None}
            fields = {'config':0}

            offset = args['offset']
            limit  = args['limit']

            result = json_util.dumps(db.pipelines.find(query, fields).sort('run_id', -1)[offset: offset + limit],
                                     sort_keys=True,
                                     indent=4,
                                     default=json_util.default)

            return json.loads(result)

    class RunsCount(Resource):
        def get(self, type):

            parser = reqparse.RequestParser()
            parser.add_argument('user'  , type=str, default=None)
            parser.add_argument('name'  , type=str, default=None)
            parser.add_argument('status', type=str, default=[], action='append')

            args = parser.parse_args()


            query = {}
            if type == 'steps':
                query = {
                    'single_step' : True,
                }
            elif type == 'pipelines':
                query = {
                    'single_step' : {'$nin': [True]},
                    'name' :  args['name']
                }

            query['user'] = args['user']
            arg_status = args.get('status', [])
            if arg_status:
                query['status'] = {"$in": arg_status}

            # filter None values from query
            query = {k: v for k, v in query.items() if not v == None}

            return db.pipelines.find(query).count()


    class RunsStats(Resource):
        def get(self):
            """
            Get the number of runs (useful for pagination)
            """
            parser = reqparse.RequestParser()
            parser.add_argument('user'  , type=str, default=None)

            args = parser.parse_args()

            #stats =  {'total': db.pipelines.find({}).count()}
            stats = { 'pipelines': [ ], 'totals': { 'stats':{}}}

            for pipeline in pipelines:
                stats['pipelines'].append(dbmodel.get_stats({'name':pipeline['name']}))

            # Get user stat
            if args['user']:
                stats['user'] = dbmodel.get_stats({'user': args['user']}, 'user')

            # compute totals
            tottot = 0
            for pipeline in stats['pipelines']:
                for stat, value in pipeline['stats'].iteritems():
                    if stat in stats['totals']['stats']:
                        stats['totals']['stats'][stat] += value
                        tottot += value
                    else:
                        stats['totals']['stats'][stat] = value
                        tottot += value
            stats['totals']['total'] = tottot

            return stats


    class RunDag(Resource):
        def get(self, run_id):
            """
            Return the dag of the given run
            """
            pipeline = db.pipelines.find_one({'run_id': run_id}, {'config':1, 'single_step':1, '_id':0})
            config = json.loads(pipeline['config'])
            if 'single_step' in pipeline:
                dag = Pipeline.create_dag(config, one_step=True)
            else:
                dag = Pipeline.create_dag(config)
            cy_network = cy.from_networkx(dag)
            return cy_network


    class RunOutputs(Resource):
        @auth.login_required
        def get(self, run_id):
            """
            Return the dag of the given run
            """

            pipeline = db.pipelines.find_one({'run_id': run_id}, {'config': 1, 'file_registry':1})
            file_registry = pipeline.get('file_registry', [])
            if file_registry:
                file_registry = json.loads(file_registry)

            conf_str = json.loads(pipeline['config'])
            config = Pipeline.load_cfg(conf_str);
            result_steps = config.get('config', {}).get('pipeline', {}).get('results', [])
            delete_steps = config.get('config', {}).get('pipeline', {}).get('delete', [])
            delete_steps.append('finalize')
            delete_steps.append('inputs')

            steps = list(db.steps.find(
                {"run_id":run_id, "name": {"$nin": delete_steps}, "jobs": {"$elemMatch": {"outputs": {"$exists": True}}}},
                {"name":1, "jobs":1, "outputs.output_dir": 1, "step_config": 1}))

            outputs = {}
            for step in steps:
                if step.get('step_config', {}):
                    s = Step.load_step(step['step_config'])
                    output_files = []
                    for job_id, job in enumerate(step['jobs']):
                        for key in job['outputs']:
                            if key in s.keys(key_groups='outputs', key_filter={'type':'file'}):
                                for i, filename in enumerate(job['outputs'][key]):
                                    output = { 'path': filename }

                                    if not isinstance(filename, list):
                                        output['archived'] = (filename in file_registry)
                                    else:
                                        output['archived'] = False
                                    output_files.append(output)

                    if output_files:
                        outputs[step['name']] = defaultdict(list)
                        outputs[step['name']]['archive'] = step['name'] in result_steps

                        outputs[step['name']]['dir'] = step.get('outputs', {}).get('output_dir')
                        outputs[step['name']]['files'] = copy.deepcopy(output_files)


            return outputs



    class RunArchive(Resource):
        @auth.login_required
        def post(self, run_id):
            """
            Pushes files into iRODS
            """

            data = request.get_json(force=True)

            runmeta   = data.get('meta')
            selection = data.get('selection')
            user      = auth_get_username(request.authorization, data.get('user'))

            npdis = dbmodel.get_npdi_projects()
            npdi = runmeta.get('Project NPDI ID', '')
            study_nickname = runmeta.get('Study nickname', 'Required field missing')
            if (npdi + study_nickname) not in npdis:
                return {'pipeline': {
                            'Project': '%s (%s)' %(npdi, study_nickname)
                        }}, 400

            run = db.pipelines.find_one({'run_id': run_id}, {'meta':1, 'run_id':1})

            steps_names = selection.keys()
            steps = list(db.steps.find(
                {"run_id":run_id, "name": {'$in': steps_names}, "jobs": {"$elemMatch": {"outputs": {"$exists": True}}}},
                {"name":1, "jobs":1, "outputs.output_dir": 1, "step_config": 1}))

            outputs = {}
            for step in steps:
                if step.get('step_config', {}):
                    s = Step.load_step(step['step_config'])
                    output_files = {}
                    for job_id, job in enumerate(step['jobs']):
                        for key in job['outputs']:
                            if key in s.keys(key_groups='outputs', key_filter={'type':'file'}):
                                for i, filename in enumerate(job['outputs'][key]):
                                    filemeta = {'step': step['name'], 'job_id': job_id}
                                    ext = os.path.splitext(filename)[1][1:].upper()
                                    for key in job.get('meta', {}):
                                        meta = job['meta'][key]                                       
                                        if key == 'sample_id':
                                            okey = 'Operational sample accession'
                                        else:
                                            okey = key

                                        if isinstance(meta, list):
                                            filemeta[okey] = meta[i]
                                        else:
                                            filemeta[okey] = meta

                                    filemeta['File type'] = 'Processed data file'
                                    filemeta['File format'] = ext

                                    output_files[filename] = filemeta

                    if output_files:
                        outputs[step['name']] = output_files


            input_files = []
            meta_data   = []
            for step_name, step_selection in selection.iteritems():
                for filepath in step_selection:
                    input_files.append(filepath)

                    filemeta = outputs[step_name][filepath]
                    filemeta.update(runmeta)
                    meta_data.append(filemeta)

            cfg = Pipeline.load_cfg(pipeline_specs['irods_lz'])
            cfg['config']['steps']['irods_mvtolz'] = {
                'input_files' : input_files,
                'meta_data'   : meta_data
            }
            cfg['config']['steps']['irods_monitorlz'] = {
                'prun_id' : run['run_id']
            }

            cfg['config']['pipeline']['project_name'] = run['meta']['project_name']
            cfg['config']['pipeline']['description'] = 'Archive data for run %s' %run['run_id']
            cfg['config']['pipeline']['output_dir'] = '/scratch/cgi/irods'

            # Get id from DB
            db_info = dbmodel.PipelineDb(cfg['name'], cfg, Pipeline.ordered_steps(cfg), user)
            cfg['run_id'] = db_info.run_id

            ut.pretty_print("Submitting pipeline %s (ID %d) for user %s" % (cfg['label'], cfg['run_id'], user))
            return pm.add_pipeline(cfg, user)


    class RunMeta(Resource):
        @auth.login_required
        def get(self, run_id):
            """
            Return the meta of the given run
            """
            run = db.pipelines.find_one({'run_id': run_id}, {'meta': 1, 'user':1});
            run['meta']['Project'] = run['meta'].pop('project_name')
            #run['meta']['Project NPDI ID'] = run['meta'].pop('project_name')
            #run['meta']['Study nickname'] = 'Test Study'
            run['meta']['Assay platform'] = 'Genomics'
            run['meta']['Hardware platform'] = 'Illumina hiseq'
            run['meta']['Assay technique'] = run['meta'].pop('label')
            run['meta']['Author'] = run['user']
            return run['meta']


    class RunDetails(Resource):
        @auth.login_required
        def get(self, run_id):
            """
            Get the list of runs
            """
            query = {"run_id" : run_id}
            pipeline = db.pipelines.find_one(query, {'steps': 0})
            config = json.loads(pipeline['config'])
            steps  = list(db.steps.find(query, {'run_id': 1, 'name': 1, 'status': 1, 'job_counter': 1}).sort('_id', 1))

            if pipeline:
                pipeline['steps'] = steps
            return json.loads(json_util.dumps(pipeline))


    class RunActions(Resource):
        @auth.login_required
        def put(self, run_id, action):
            """
            Delete / stop / start a run
            """
            parser = reqparse.RequestParser()
            parser.add_argument('user',  type=str, default=None)
            parser.add_argument('force', action='store_true', default=False)
            args      = parser.parse_args()
            arg_user  = auth_get_username(request.authorization, args.get('user'))
            arg_force = args.get('force')
            errors = ''

            query = {'run_id' : run_id}
            keys  = {'work_dir':1, 'output_dir':1, 'status':1, 'user':1}
            pipeline = db.pipelines.find_one(query, keys)

            if not pipeline:
                errors = 'ERROR: Run ID %s not found' % str(run_id)
            elif pipeline['user'] != arg_user:
                errors = 'ERROR: cannot modify pipeline %s: permission denied' % str(run_id)
            elif action.lower() == "delete":
                if pipeline['status'] != JOB_STATUS.FAILED:
                    errors = 'ERROR: Run status is %s: cannot delete' % pipeline['status'].upper()
                else:
                    db.steps.delete_many({'run_id': run_id})
                    db.pipelines.find_one_and_delete({'run_id': run_id})
                    errors = pm.delete_pipeline(run_id, arg_user,
                                                pipeline.get('output_dir'), pipeline.get('work_dir')
                                               )
            elif action.lower() == "resume":
                if pipeline['status'] != JOB_STATUS.INTERRUPTED:
                    errors = 'ERROR: Run status is %s: cannot resume' % pipeline['status'].upper()
                else:
                    db.pipelines.update({'run_id': run_id},
                                        {'$set': {'status': JOB_STATUS.QUEUED}})
                    errors = pm.resume_pipeline(run_id, arg_user, pipeline.get('work_dir'))
            elif action.lower() == "pause":
                if pipeline['status'] != JOB_STATUS.RUNNING:
                    errors = 'ERROR: Run status is %s: cannot pause' % pipeline['status'].upper()
                else:
                    errors = pm.pause_pipeline(run_id, arg_user)
            else:
                errors = "Uknown action requested: %s" % str(action)

            if errors:
                ut.pretty_print(errors)
                return errors, 400
            else:
                return 200


    class RunStats(Resource):
        def get(self, run_id):
            """
            Get the DB stats
            """
            query = {"run_id" : run_id}
            fields = {'stats':1, 'created_at':1, 'completed_at':1, 'meta':1, 'name':1, 'run_id':1}
            results = db.pipelines.find_one(query, fields)

            return json.loads(json_util.dumps(results))


    class RunStep(Resource):

        def get(self, run_id, step_name):
            """
            Get the run step details
            """
            step = db.steps.find_one({'run_id': run_id,
                                      'name': step_name})
            return json.loads(json_util.dumps(step))


    class RunStepJob(Resource):

        def get(self, run_id, step_name, job_id, user):
            """
            Get the details of a particular job in a step
            Returns a list of outputs
            """

            query = { 'run_id': run_id,
                      'name': step_name }
            fields = { 'jobs': {"$slice": [job_id, 1]}, 'run_id':1 }

            bson = db.steps.find_one(query, fields)
            jobs = json.loads(json_util.dumps(bson))['jobs']
            results = {}
            if jobs:
                job = jobs.pop(0)

                output_dir = job['output_dir']

                _size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                _web_friendly_ext = ['png', 'txt', 'pdf', 'html', 'log', 'out', 'err']

                for e in _web_friendly_ext:
                    results[e] = []

                results['output_dir'] = output_dir
                results['misc'] = []
                results['meta'] = [] # to contain the __%file files

                cmd = ['find', '-L', output_dir, '-maxdepth', '1', '-not', '-type', 'd', '-printf', '%s ', '-print']

                (ec, err, out) = run_as(cmd=cmd, user=user)
                if ec == 0 and out:
                    for output in out.rstrip('\n').split('\n'):
                        (fsize, path) = output.split()
                        fext = os.path.splitext(path)[1].lstrip('.').lower()
                        # compute human readable file size
                        hsize = int(fsize)
                        idx = 0
                        while hsize/1024.>1.:
                            idx += 1
                            hsize = hsize/1024.

                        file_info = {
                            'path': path,
                            'bytes': fsize,
                            'size': '%.2f%s' % (hsize, _size_name[idx])
                        }

                        if not path.startswith('.'):
                            if fext not in _web_friendly_ext:
                                if os.path.basename(path) == '%s.cfg' % step_name:
                                    results['meta'].append(file_info)
                                elif os.path.basename(path).startswith('condor.'):
                                    results['log'].append(file_info)
                                else:
                                    results['misc'].append(file_info)
                            else:
                                if os.path.basename(path).startswith('__'):
                                    results['meta'].append(file_info)
                                else:
                                    results[fext].append(file_info)

            return results


    class Projects(Resource):
        def get(self):
            """
            Get the list of npdi project
            """
            return json.loads(json_util.dumps(db.projects.find({'Study nickname':{'$ne':None}}, {'_id':0})))


    @classmethod
    def connect(cls, api):
        api.add_resource(cls.Runs,          '/api/runs/<string:type>')
        api.add_resource(cls.RunsStats,     '/api/runs/pipelines/stats')
        api.add_resource(cls.RunsCount,     '/api/runs/<string:type>/count')
        api.add_resource(cls.RunDetails,    '/api/runs/pipelines/<int:run_id>')
        api.add_resource(cls.RunActions,    '/api/runs/pipelines/<int:run_id>/<string:action>')
        api.add_resource(cls.RunMeta,       '/api/runs/pipelines/<int:run_id>/meta')
        api.add_resource(cls.RunDag,        '/api/runs/pipelines/<int:run_id>/dag')
        api.add_resource(cls.RunOutputs,    '/api/runs/pipelines/<int:run_id>/outputs')
        api.add_resource(cls.RunArchive,    '/api/runs/pipelines/<int:run_id>/archive')
        api.add_resource(cls.RunStats,      '/api/runs/pipelines/<int:run_id>/stats')
        api.add_resource(cls.RunStep,       '/api/runs/pipelines/<int:run_id>/<string:step_name>')
        api.add_resource(cls.RunStepJob,    '/api/runs/pipelines/<int:run_id>/<string:step_name>/<int:job_id>/<string:user>')
        api.add_resource(cls.Projects,      '/api/projects')
