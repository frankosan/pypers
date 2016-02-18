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

class ABCPipelineDb():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, name, spec, steps, user, run_id=None, output_dir=None):
        return

    @abc.abstractmethod
    def update_pipeline(self, run_id, data):
        return

    @abc.abstractmethod
    def update_output_dir(self, work_dir, output_dir):
        return

    @abc.abstractmethod
    def update_pipeline_metadata(self, metadata):
        return

    @abc.abstractmethod
    def update_pipeline_status(self, status):
        return

    @abc.abstractmethod
    def update_step_metadata(self, step_name, metadata):
        return

    @abc.abstractmethod
    def update_step_status(self, step_name, step_status, jobs_status=None):
        return

    @abc.abstractmethod
    def start_step(self, step_name, step_config, job_counter=0):
        return

    @abc.abstractmethod
    def set_step_outputs(self, step_name, outputs):
        return
