from .abstract import ABCPipelineDb
from pypers.core.logger import logger
import inspect
import json


class PipelineDbStub(ABCPipelineDb):

    def __init__(self, name, spec, steps, user, run_id=None, output_dir=None):
        self.log = logger.get_log()

    def update_pipeline(self, run_id, data):
        if not run_id:
            run_id = -1
        self.log.debug("Call %s with run_id=%d, data=%s" % (inspect.stack()[0][3], run_id, json.dumps(data)))

    def update_output_dir(self, work_dir, output_dir):
        self.log.debug("Call %s with %s, %s" % (inspect.stack()[0][3], work_dir, output_dir))

    def update_pipeline_status(self, status):
        self.log.debug("Call %s with %s" % (inspect.stack()[0][3], status))

    def update_pipeline_metadata(self, metadata):
        self.log.debug("Call %s with %s" % (inspect.stack()[0][3], metadata))

    def update_step_metadata(self, step_name, metadata):
        self.log.debug("Call %s with %s" % (inspect.stack()[0][3], metadata))

    def update_step_status(self, step_name, step_status, jobs_status=None):
        self.log.debug("Call %s with %s %s %s" % (inspect.stack()[0][3], step_name, step_status, jobs_status))

    def start_step(self, step_name, step_config, job_counter=0):
        self.log.debug("Call %s with %s %s %s" % (inspect.stack()[0][3], step_name, step_config, job_counter))

    def set_step_outputs(self, step_name, outputs):
        self.log.debug("Call %s with %s %s" % (inspect.stack()[0][3], step_name, ','.join(outputs)))
