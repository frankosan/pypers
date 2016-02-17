from flask import Flask
from flask.ext.restful import Resource
from flask.ext.restful import Api
app = Flask(__name__)

from pypers.api.pipelines import PipelinesApi
from pypers.api.steps import StepsApi
from pypers.api.services import ServicesApi
from pypers.api.assembly import AssemblyApi
from pypers.api.annotation import AnnotationApi

class Empty(Resource):
    """
    tell nosy people to go away
    """
    def get(self):
        return('Nothing to see here.')

api = Api(app)
######################################
api.add_resource(Empty, '/')
PipelinesApi.connect(api)
StepsApi.connect(api)
ServicesApi.connect(api)
AssemblyApi.connect(api)
AnnotationApi.connect(api)
