import os
import sys
import json
import time
import os

from bson import json_util
from flask import request, send_file
from flask.ext.restful import reqparse, Resource

from pypers.api import app
from pypers.core.pipelines_manager import pm
from pypers.core.pipelines import Pipeline

from pypers.pipelines import pipeline_names, pipeline_specs, pipelines
from pypers.utils.utils import pretty_print
from pypers.utils.assembly import AssemblyServices


def debug(name, args):
    argstr = ', '.join(['%s=%s' % (k, str(v)) for (k, v) in args.items()])
    print('[*] %s.get(%s): %.02fs' % (name,
                                    argstr,
                                    time.time()))


class AssemblyApi(Resource):
    def get(self):
        """
        Return lists of Pre-Assembler, Assembler and Post-Assembler step names
        """

        ass_srv = AssemblyServices()

        return {
            'pre_assemblers': ass_srv.PRE_ASSEMBLERS.keys(),
            'assemblers' : ass_srv.ASSEMBLERS.keys(),
            'post_assemblers' : ass_srv.POST_ASSEMBLERS.keys()
        }

    def put(self):
        """
        Build an assembly pipeline config from a set of configuration params and submit
        example config:

        {
            "name": "assembly",
            "pre_assemblers" : ["bayes_hmer","tagdust"] ,
            "assemblers" : ["IDBA","A6"] ,
            "post_assemblers" : ["sspace"],
            "output_dir" : "/scratch/rdjoycech/assembly_test",
            "input_files" : ["/nihs/Bioinformatics_home/rdjoycech/acme/test_data/Lactobacillus_fermentum_2001.fq.gz", "/nihs/Bioinformatics_home/rdjoycech/acme/test_data/Lactobacillus_fermentum_2002.fq.gz"]

            "input_fofn" : ""
        }
        Provide either fastq file pair, or input_fofn, a list file of fq pairs
        """

        data = request.get_json(force=True)
        spec = data.get('config')
        user = data.get('user')

        pretty_print(data)

        ass_srv = AssemblyServices()
        # although we are passing the whole config as a spec, some cfg parmas are not used here
        (pipeline_config, pipeline_init) = ass_srv.create_pipeline_config(spec)

        # Add the run config section and submit

        fq1 = []
        fq2 = []
        if spec["input_fofn"] != '':
            (fq1,fq2) = ass_srv.parse_fofn(spec["input_fofn"])
        else:
            fq1.append(spec["fastq_r1"])
            if len(spec["fastq_r2"]) > 0:
                fq2.append(spec["fastq_r2"])

        run_config = {
            "pipeline"       : {
                "output_dir"   : spec['output_dir'],
                "project_name" : "assembly",
                "description" : "assembly"
            },
            "steps": {}
        }

        # set up input files for pipeline entry point(s)
        for step in pipeline_init:
            run_config["steps"][step] = {"input_fq1" : fq1, "input_fq2" : fq2}

        pipeline_config["config"]  = run_config

        pretty_print("Submitting assembly pipeline for user %s" % user)
        print json.dumps(pipeline_config, indent=4)

        return pm.add_pipeline(pipeline_config, user)


    @classmethod
    def connect(cls, api):
        """
        Connect the end points to corresponding classmethod
        """
        api.add_resource(cls,   '/api/assembly')


