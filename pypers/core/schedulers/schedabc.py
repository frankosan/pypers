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

import abc

JOB_OUT = 'job.out'
JOB_ERR = 'job.err'

class Scheduler():

    """ An abstract class defining methods for job submission and status reporting for job schedulers
        to run jobs in DRM (Distributed Resource Management) systems
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def submit(self,cmd,cmd_args,reqs=None):
        return

    @abc.abstractmethod
    def stop(self,id):
        return

    @abc.abstractmethod
    def status(self,id):
        return
