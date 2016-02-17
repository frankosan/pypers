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
from pypers.utils.annotation import AnnotationServices


def debug(name, args):
    argstr = ', '.join(['%s=%s' % (k, str(v)) for (k, v) in args.items()])
    print('[*] %s.get(%s): %.02fs' % (name,
                                    argstr,
                                    time.time()))


class AnnotationApi(Resource):
    def get(self):
        """
        Return list of kbase annotation services subroutines
        """

        ann_srv = AnnotationServices()
        return ann_srv.subroutines()


    def put(self):

        """
        Build an annotation pipeline config from a set of configuration params and submit
        example config:

        {
            "subroutines" : ["call_features_rRNA_SEED","call_features_tRNA_trnascan"] ,
            "output_dir" : "/scratch/rdjoycech/annotation_test",
            "input_fasta" : "/scratch/cgi/integration_tests/genome_annotation/P2_Ki.mis_contigs.fa"
            "genus": "EColi",
            "input_fofn" : ""
        }
        Provide either input_fasta and genus, or input_fofn which is a fasta/genus list file
        """

        data = request.get_json(force=True)
        cfg = data.get('config')
        user = data.get('user')

        pretty_print(data)

        # Pass run spec (label and subroutine list) to AnnotationServices to gen a pipeline config
        spec =    {
            "label": "annotation",
            "subroutines": cfg["subroutines"]
        }
        ann_srv = AnnotationServices()
        pipeline_config = ann_srv.create_pipeline_config(spec)

        # Create the run config section and submit
        pipeline_config["config"]["pipeline"] = {
                    "output_dir"   : cfg['output_dir'],
                    "project_name" : "annotation",
                    "description"  : "annotation"
                }

        init_step = ann_srv.PRE_PROCESSOR.keys()[0]

        ctgs = []
        genus = []
        if cfg["input_fasta"] == '':
            (ctgs,genus) = ann_srv.parse_fofn(cfg["input_fofn"])
        else:
            ctgs.append(cfg["input_fasta"])
            if cfg['genus'] == '':
                genus.append('Unspecified')
            else:
                genus.append(cfg['genus'])

        pipeline_config["config"]["steps"][init_step] = {"input_fasta" : ctgs, "genus" : genus}

        print json.dumps(pipeline_config,indent=4)
        pretty_print("Submitting pipeline for user %s" % user)
        return pm.add_pipeline(pipeline_config, user)

    @classmethod
    def connect(cls, api):
        """
        Connect the end points to corresponding classmethod
        """
        api.add_resource(cls,   '/api/annotation')


