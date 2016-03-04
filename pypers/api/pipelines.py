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

import os
import sys
import json
import time


from bson import json_util
from flask import request, send_file
from flask.ext.restful import reqparse, Resource
from py2cytoscape import util as cy

from nespipe.core.pipelines_manager import pm
from nespipe.core.pipelines import Pipeline
from nespipe.core.constants import JOB_STATUS

from nespipe.pipelines import pipeline_specs, pipelines
from nespipe.db.models import mongo as dbmodel
from nespipe.db.models.mongo import PipelineDbConnector
from nespipe.utils import utils as ut


from nespipe.api.authentication import auth, auth_get_username

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
        @auth.login_required
        def put(self):
            """
            Queue the specific pipeline
            """
            data   = request.get_json(force=True)
            config = data.get('config')
            user   = auth_get_username(request.authorization, data.get('user'))

            errors = None # Pipeline.validate_config(config, user)
            if not errors:
                config = Pipeline.load_cfg(config)
                # Get id from DB
                db_info = dbmodel.PipelineDb(config['name'], config, Pipeline.ordered_steps(config), user)
                config['run_id'] = db_info.run_id

                ut.pretty_print("Submitting pipeline %s (ID %d) for user %s" % (config['label'], config['run_id'], user))
                return pm.add_pipeline(config, user)
            else:
                return errors, 400


    @classmethod
    def connect(cls, api):
        """
        Connect the end points to corresponding classmethod
        """
        api.add_resource(cls.List,          '/api/pipelines')
        api.add_resource(cls.Inputs,        '/api/pipelines/<string:name>/config')
        api.add_resource(cls.Dag,           '/api/pipelines/<string:name>/dag')
        api.add_resource(cls.Stats,         '/api/runs/pipelines/<string:name>/stats')
        api.add_resource(cls.Submit,        '/api/pipelines/submit')

