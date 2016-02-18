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

from flask import request
from flask.ext.restful import reqparse, Resource
from pypers.utils.utils import subproc
from pypers import pipelines

from supervisor.options import ClientOptions
from supervisor.supervisorctl import Controller


def get_supervisor_status(name):
    """
    Get the status of a supervisor service
    """
    res = subproc("supervisorctl status %s" % name)
    status =  True if res['stdout'].lower().find("running") > -1 else False
    return status


class ServicesApi:
    SERVICES = ['demux']

    class ServicesList(Resource):
        """
        This class return the list of pipelines types
        """
        def get(self):
            service_status = {}
            for s in ServicesApi.SERVICES:
                service_status[s] = get_supervisor_status(s)

            print service_status
            return service_status


    class ServiceStatus(Resource):
        """
        This class is the interface to execute  pipeline
        """

        def get(self, name):
            """
            Return the list of parameter for a specifc pipeline
            """
            return {"status": get_supervisor_status(name)}

        def put(self, name):
            """
            Return the list of parameter for a specifc pipeline
            """


            data = request.get_json()
            status = bool(data.get('status'))

            cmd = "start" if status else "stop"
            res = subproc("supervisorctl %s %s" % (cmd, name))

            print res['stdout']
            ret_code = 200 if res['stdout'].lower().find(cmd) > -1 else 500
            return {"msg" : res['stdout']}, ret_code

    @classmethod
    def connect(cls, api):
        """
        Connect the end points to corresponding classmethod
        """

        api.add_resource(cls.ServicesList,  '/api/services')
        api.add_resource(cls.ServiceStatus, '/api/services/<string:name>')

