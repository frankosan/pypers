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
