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


import cPickle
import os
from datetime import datetime

from pypers.core.step import STEP_PICKLE, JOB_STATUS


class Job(object):
    """
    Handles the job submission data (one per actual job)
    """
    def __init__(self, job_id, output_dir, status=JOB_STATUS.QUEUED):
        self.job_id = job_id
        self.output_dir = output_dir
        self.status = status

    def is_completed(self):
        """
        Return true if the job has fully completed
        """
        completed = False

        if os.path.exists(os.path.join(self.output_dir, STEP_PICKLE)):
            completed = True
        return completed

    def load_output(self):
        """
        Load in memory the step object
        """
        stepobj = None
        if os.path.exists(os.path.join(self.output_dir, STEP_PICKLE)):
            with open(os.path.join(self.output_dir, STEP_PICKLE), "r") as fh:
                stepobj = cPickle.load(fh)
                self.inputs = {}
                for key in stepobj.get_input_keys():
                    self.inputs[key] = getattr(stepobj, key)

                self.outputs = {}
                for key in stepobj.get_output_keys():
                    if hasattr(stepobj, key):
                        self.outputs[key] = getattr(stepobj, key)

                self.params = {}
                for key in stepobj.get_param_keys():
                    if hasattr(stepobj, key):
                        self.params[key] = getattr(stepobj, key)

                self.meta = stepobj.meta['job']

        return stepobj

    def set_status(self, status):
        """
        Update the status and time data
        """
        if self.status != status:
            if status == JOB_STATUS.RUNNING:
                self.running_at = datetime.utcnow()
            elif status == JOB_STATUS.SUCCEEDED or status == JOB_STATUS.FAILED:
                self.completed_at = datetime.utcnow()
            self.status = status
