import os
import sys
import json
import time
import glob

from bson import json_util
from flask import request, send_file
from flask.ext.restful import reqparse, Resource
from py2cytoscape import util as cy

from pypers.core.pipelines_manager import pm
from pypers.core.pipelines import Pipeline
from pypers.core.step import JOB_STATUS

from pypers.pipelines import pipeline_specs, pipelines
from pypers.db.models import mongo as dbmodel
from pypers.db.models.mongo import PipelineDbConnector
from pypers.utils import utils as ut
from pypers.utils.execute import run_as

db = PipelineDbConnector()

def debug(name, args):
    argstr = ', '.join(['%s=%s' % (k, str(v)) for (k, v) in args.items()])
    print('[*] %s.get(%s): %.02fs' % (name,
                                    argstr,
                                    time.time()))

class PipelinesApi:
    """
    Pipelines API
    """

    class List(Resource):
        def get(self):
            """
            Get the list of pipeline names
            """
            return pipelines

    class Inputs(Resource):
        def get(self, name):
            """
            Return the list of input parameters for a specifc pipeline and all of its steps
            """
            config =  Pipeline.get_params(pipeline_specs[name])
            return config

    class Dag(Resource):
        def get(self, name):
            """
            Return the dag of a pipeline
            """
            cy_network = cy.from_networkx(Pipeline.create_dag(pipeline_specs[name]))
            return cy_network

    class Stats(Resource):
        def get(self, name):
            """
            Get the stats of pipeline names
            """
            return dbmodel.get_stats({'name':name})

    class Submit(Resource):
        def put(self):
            """
            Queue the specific pipeline
            """
            data   = request.get_json(force=True)
            config = data.get('config')
            user   = data.get('user')

            errors = Pipeline.validate_config(config, user)
            if not errors:
                config = Pipeline.load_cfg(config)
                # Get id from DB
                db_info = dbmodel.PipelineDb(config['name'], config, Pipeline.ordered_steps(config), user)
                config['run_id'] = db_info.run_id

                ut.pretty_print("Submitting pipeline %s (ID %d) for user %s" % (config['label'], config['run_id'], user))
                return pm.add_pipeline(config, user)
            else:
                return errors, 400


    class Runs(Resource):
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


    class RunDetails(Resource):
        def get(self, run_id):
            """
            Get the list of runs
            """
            query = {"run_id" : run_id}
            pipeline = db.pipelines.find_one(query, {'steps': 0})
            config = json.loads(pipeline['config'])
            steps    = list(db.steps.find(query, {'run_id': 1, 'name': 1, 'status': 1, 'job_counter': 1}).sort('_id', 1))

            if pipeline:
                pipeline['steps'] = steps
            return json.loads(json_util.dumps(pipeline))


    class RunActions(Resource):
        def put(self, run_id, action):
            """
            Delete / stop / start a run
            """
            parser = reqparse.RequestParser()
            parser.add_argument('user',  type=str, default=None)
            parser.add_argument('force', action='store_true', default=False)
            args      = parser.parse_args()
            arg_user  = args.get('user')
            arg_force = args.get('force')
            errors = ''

            query = {'run_id' : run_id}
            keys  = {'work_dir':1, 'output_dir':1, 'status':1, 'user':1}
            pipeline = db.pipelines.find_one(query, keys)

            print args, arg_force

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

            query = { 'run_id': run_id,
                      'name': step_name }

            step = db.steps.find_one(query)

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

                        if path.find('status.pickle')==-1:
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



    @classmethod
    def connect(cls, api):
        """
        Connect the end points to corresponding classmethod
        """
        api.add_resource(cls.List,          '/api/pipelines')
        api.add_resource(cls.Inputs,        '/api/pipelines/<string:name>/config')
        api.add_resource(cls.Dag,           '/api/pipelines/<string:name>/dag')

        api.add_resource(cls.Stats,         '/api/runs/pipelines/<string:name>/stats')

        # api.add_resource(cls.RunsUsers,   '/pipelines/runs/users')
        # api.add_resource(cls.RunsTypes,   '/pipelines/runs/types')

        api.add_resource(cls.Submit,        '/api/pipelines/submit')

        api.add_resource(cls.Runs,          '/api/runs/<string:type>')
        api.add_resource(cls.RunsStats,     '/api/runs/pipelines/stats')
        api.add_resource(cls.RunsCount,     '/api/runs/<string:type>/count')

        api.add_resource(cls.RunDetails,    '/api/runs/pipelines/<int:run_id>')

        api.add_resource(cls.RunActions,    '/api/runs/pipelines/<int:run_id>/<string:action>')

        api.add_resource(cls.RunDag,        '/api/runs/pipelines/<int:run_id>/dag')
        api.add_resource(cls.RunStats,      '/api/runs/pipelines/<int:run_id>/stats')
        api.add_resource(cls.RunStep,       '/api/runs/pipelines/<int:run_id>/<string:step_name>')
        api.add_resource(cls.RunStepJob,    '/api/runs/pipelines/<int:run_id>/<string:step_name>/<int:job_id>/<string:user>')
