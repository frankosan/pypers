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

import json
from datetime import datetime
from pypers.core.step import JOB_STATUS
from .abstract import ABCPipelineDb
from bson.objectid import ObjectId
from bson import json_util
from pypers import config as cfg
from pypers.utils import utils as ut
from pymongo import MongoClient


db = None


def get_db():
    """
    Connect to the db if it is not already connected
    """

    global db
    if not db:
        client = MongoClient(cfg.MONGODB_HOST,cfg.MONGODB_PORT)
        db = client[cfg.MONGODB_NAME]
        ut.pretty_print("Connected to MONGO_HOST %s on PORT %s" % (cfg.MONGODB_HOST, cfg.MONGODB_PORT))
    return db


class PipelineDbConnector(object):

    def __init__(self):
        "Initialize the db collections"
        self.db = get_db()
        self.pipelines   = db['Pipelines']
        self.steps       = db['Steps']
        self.counters    = db['Counters']
        self.refgenomes  = db['RefGenomes']


def get_refgenomes(tools):
    """
    Find all the ref genome paths corresponding to the list of tools

    Returns dictionary of the form: { "label": { "tool1":"path", "tool2":"path" }, ... }
    """
    db = PipelineDbConnector()
    query = {}
    for tool in tools:
        query["paths.%s" % tool] = {"$exists":1}
    result = json.loads(json_util.dumps(db.refgenomes.find(query)))
    return result



class PipelineDb(ABCPipelineDb):

    def __init__(self, name, config, steps, user, output_dir=None):

        #import the DB here because it creates the connection
        self.db = PipelineDbConnector()

        run_id = config.get('run_id')
        doc = self.db.pipelines.find_one({"run_id": run_id}, {"steps": 0})
        # If rerunning pipeline, re-use same id and config, but reset step data
        if doc:
            self.run_id = run_id
            run_count = doc.get("run_count", 0)
            run_count += 1
            doc["run_count"] = run_count
            self._id = doc["_id"]
            self.db.steps.update_many(
                {"run_id": self.run_id},
                {"$set": {"run_id": "%d_%d" % (run_id, run_count)}}
            )
        else:
            if not self.db.counters.find_one():
                #create the first entry in the DB
                self.db.counters.insert_one({"run_id_cnt":0})

            counters = self.db.counters.find_one_and_update({}, {"$inc": {"run_id_cnt":1}})
            self.run_id = counters["run_id_cnt"]
            self._id = ObjectId()
            doc = {
                "_id"        : self._id,
                "run_id"     : self.run_id,
                "created_at" : datetime.utcnow(),
                "user"       : user,
                "name"       : name,
            }

        doc["config"] = json.dumps(config)
        if not output_dir:
            doc["output_dir"] = config['config']['pipeline']['output_dir']
        else:
            doc["output_dir"] = output_dir
        doc["steps"] = []
        doc["status"] = JOB_STATUS.QUEUED
        doc["stats"]  = {
            "total"       : len(steps),
            "queued"      : [],
            "running"     : [],
            "succeeded"   : [],
            "interrupted" : [],
            "failed"      : []
        }
        if len(steps) == 1:
            doc["single_step"] = True
        self.steps = {}
        self.queued = set(steps)
        self.running = set()
        self.interrupted = set()
        self.succeeded = set()
        self.failed = set()
        self.jobs = {}

        for step in steps:
            step_data = {
                "_id"           : ObjectId(),
                "run_id"        : self.run_id,
                "name"          : step,
                "status"        : JOB_STATUS.QUEUED,
                "job_counter"   : 0,
                "jobs"          : []
            }
            self.steps[step] = step_data
            self.jobs[step] = {}
            doc["steps"].append(step_data)
            self.db.steps.insert_one(step_data)

        if run_id:
            self.db.pipelines.find_one_and_replace({"run_id": self.run_id}, doc)
        else:
            self.db.pipelines.insert_one(doc)


    def update_pipeline(self, run_id, data):
        """
        Generic utility function to update pipeline information based on its run id
        """
        self.db.pipelines.find_one_and_update(
            {"run_id"  : run_id},
            {"$set" : data}
        )


    def update_pipeline_status(self, status):
        """
        Update the status of the pipeline
        """
        data = {"status" : status}
        if (status == JOB_STATUS.SUCCEEDED
        or status == JOB_STATUS.FAILED
        or status == JOB_STATUS.INTERRUPTED):
            data['completed_at'] = datetime.utcnow()

            data = self.db.pipelines.find_one({"_id":self._id})
            data['status'] = status
            data['completed_at'] = datetime.utcnow()

            data['exec_time'] = ut.format_tdiff(
                data['completed_at'],
                data['created_at']
            )

        self.db.pipelines.find_one_and_update(
            {"_id"  : self._id},
            {"$set" : data}
        )

    def update_output_dir(self, work_dir, output_dir):
        """
        Update the steps and jobs output directories
        """
        query = {"run_id": self.run_id}
        filt  = {"outputs":1, "jobs":1}
        for step in self.db.steps.find(query, filt):
            step_id = step.pop('_id')
            step['outputs'] = json.loads(json.dumps(step['outputs']).replace(work_dir, output_dir))
            for i, job in enumerate(step['jobs']):
                if 'outputs' in job:
                    step['jobs'][i]['outputs'] = json.loads(json.dumps(job['outputs']).replace(work_dir, output_dir))
                if 'output_dir' in job:
                    step['jobs'][i]['output_dir'] = job['output_dir'].replace(work_dir, output_dir)
            self.db.steps.update_one({'_id': step_id}, {"$set": step})


    def update_pipeline_metadata(self, metadata):
        """
        Update the status of the pipeline
        """
        data = {"meta" : metadata}
        self.db.pipelines.find_one_and_update(
            {"_id"  : self._id},
            {"$set" : data}
        )


    def update_step_metadata(self, step_name, metadata):
        """
        Update the metadata of the step
        """
        data = {"meta" : metadata}
        self.db.steps.find_one_and_update(
            {"_id" : self.steps[step_name]["_id"]},
            {"$set" : data}
        )

    def update_step_status(self, step_name, step_status, jobs_status=None, job_counter=None):
        """
        Update the step and jobs status
        """

        set_step_status = {"status" : step_status}
        if jobs_status and self.jobs[step_name] != jobs_status:
            self.jobs[step_name] = jobs_status
            set_step_status["jobs"] = jobs_status

        self.db.steps.find_one_and_update(
            {"_id" : self.steps[step_name]["_id"]},
            {"$set" : set_step_status }
        )

        #update the status only if is changed
        if self.steps[step_name]["status"] != step_status:
            self.steps[step_name]["status"] = step_status
            set_data = {}
            if step_status == JOB_STATUS.SUCCEEDED:
                self.running.discard(step_name)
                self.queued.discard(step_name)
                self.succeeded.add(step_name)
                set_data["steps.$.completed_at"] = datetime.utcnow()
            elif step_status == JOB_STATUS.RUNNING:
                self.running.add(step_name)
                set_data["steps.$.running_at"] = datetime.utcnow()
            elif step_status == JOB_STATUS.INTERRUPTED:
                self.running.discard(step_name)
                self.queued.discard(step_name)
                self.interrupted.add(step_name)
                self.update_pipeline_status(JOB_STATUS.INTERRUPTED)
            elif step_status == JOB_STATUS.FAILED:
                self.running.discard(step_name)
                self.queued.discard(step_name)
                self.failed.add(step_name)
                self.interrupted = self.queued
                self.queued = []
                set_data["steps.$.completed_at"] = datetime.utcnow()
                self.queued = set()
                self.update_pipeline_status(JOB_STATUS.FAILED)

            self.queued -= set.union(self.running, self.failed, self.succeeded)
            set_data["stats.queued"] = list(self.queued)
            set_data["stats.running"] = list(self.running)
            set_data["stats.interrupted"] = list(self.interrupted)
            set_data["stats.failed"] = list(self.failed)
            set_data["stats.succeeded"] = list(self.succeeded)
            set_data["steps.$.status"] = step_status
            if job_counter:
                set_data["steps.$.job_counter"] = job_counter
            self.db.pipelines.find_one_and_update(
                {"steps._id" : self.steps[step_name]["_id"]},
                {"$set": set_data}
            )


    def set_step_outputs(self, step_name, outputs):
        """
        Store the outputs of a step
        """

        set_data = {}
        # for key in outputs:
        #     if key is not 'meta':
        #         set_data['outputs.%s' % key] = outputs[key]

        set_data['outputs.output_dir'] = outputs.get('output_dir','')
        if set_data:
            self.db.steps.find_one_and_update(
                {"_id"  : self.steps[step_name]["_id"]},
                {"$set" : set_data }
            )


    def start_step(self, step_name, step_config, job_counter=0):
        """
        Add a step to the document
        """

        self.db.steps.find_one_and_update(
            {"_id"  : self.steps[step_name]["_id"]},
            {
                "$set" : {
                    "job_counter"   : job_counter,
                    "step_config"   : step_config,
                }
            }
        )

        self.update_step_status(step_name, JOB_STATUS.RUNNING, None, job_counter)


def get_stats(condition, group='name'):
    """
    Get stats by name (or any other grouping, e.g., by user)
    """
    db = PipelineDbConnector()
    key = [ group ]

    initial = {
        group: condition[group],
        'total': 0,
        'stats': {
            JOB_STATUS.RUNNING: 0,
            JOB_STATUS.QUEUED: 0,
            JOB_STATUS.SUCCEEDED: 0,
            JOB_STATUS.FAILED: 0,
            JOB_STATUS.INTERRUPTED: 0
        }
    }
    reduce = ('function(doc, out) { \
                  out.total += 1; \
                  out.stats[doc.status] += 1; \
               }')

    result = (
        db.pipelines.group(key, condition, initial, reduce)
        or
        [ initial ]
    ).pop()

    return result

