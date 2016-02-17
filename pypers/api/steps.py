import os
import sys
import json
import time
import glob
import copy

from bson import json_util
from flask import request, send_file
from flask.ext.restful import reqparse, Resource

from pypers.core.pipelines_manager import pm
from pypers.core.pipelines import Pipeline
from pypers.core.step import Step, JOB_STATUS

from pypers.steps import step_list
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

class StepsApi:
    """
    Pipelines API
    """

    class StepsList(Resource):
        def get(self):
            """
            Get the list of pipeline names
            """
            sl = {}
            for step in step_list.values():
                module = step.__module__.rsplit(".", 1)[0]
                if module not in sl:
                    sl[module] = []
                sl[module].append(step.__name__)
            return sl


    class StepInputs(Resource):
        def get(self, name):
            """
            Get the configuration a given step name
            """
            if name in step_list:

                spec = copy.deepcopy(step_list[name].spec)
                params = spec.get('args').get('params', [])
                for param in copy.deepcopy(Pipeline.params):
                    if param['name'] in ['project_name', 'description']:
                        param['value'] = ''
                    params.append(param)
                for param in params:
                    if param['type'] == 'ref_genome':
                        param['type'] = 'str'
                spec['args']['params'] = params + Step.create(name).get_reqs(no_default=False)
                spec['step_class'] = name
                spec['name'] = step_list[name].__name__
                return spec
            else:
                return "Step '%s' does not exists" %name, 400


    class StepSubmit(Resource):
        def put(self):
            """
            Queue the specific pipeline
            """

            data   = request.get_json(force=True)
            config = data.get('config')
            user   = data.get('user')

            errors = {}
            step = Step.load_step(config)
            errors = step.validate_config(config)
            if not step.output_dir:
                errors['output_dir'] = 'missing value'

            if not errors:
                # Get id from DB
                db_info = dbmodel.PipelineDb(config['name'], config, [step.name], user, output_dir=step.output_dir)
                config['run_id'] = db_info.run_id

                ut.pretty_print("Submitting step %s (ID %d) for user %s" % (config['name'], config['run_id'], user))
                return pm.add_step(config, user)
            else:
                return errors, 400



    class StepsStats(Resource):
        def get(self):
            """
            Get the stats of all the steps
            """
            parser = reqparse.RequestParser()
            parser.add_argument('user', type=str, default=None)

            args = parser.parse_args()

            stats = {'total': db.pipelines.find({'single_step' : True}).count()}
            stats = {'pipelines': [ ], 'totals': { 'stats':{}}}
            step_names = db.pipelines.distinct('name', {'single_step' : True})

            for step_name in step_names:
                stats['pipelines'].append(dbmodel.get_stats({'name': step_name, 'single_step': True}))

            # Get user stat
            if args['user']:
                stats['user'] = dbmodel.get_stats({'user': args['user'], 'single_step': True}, 'user')

            tottot = 0
            for step in stats['pipelines']:
                for stat, value in step['stats'].iteritems():
                    if stat in stats['totals']['stats']:
                        stats['totals']['stats'][stat] += value
                        tottot += value
                    else:
                        stats['totals']['stats'][stat] = value
                        tottot += value
            stats['totals']['total'] = tottot

            return stats


    @classmethod
    def connect(cls, api):
        """
        Connect the end points to corresponding classmethod
        """
        api.add_resource(cls.StepsList,          '/api/steps')
        api.add_resource(cls.StepSubmit,         '/api/steps/submit')
        api.add_resource(cls.StepInputs,         '/api/steps/<string:name>')
        api.add_resource(cls.StepsStats,         '/api/runs/steps/stats')


