from pypers.core.step import Step
from pypers.steps.genome_annotation import KbaseAnnotation
import os

class KbaseAnnotationHimem(KbaseAnnotation):

    spec = {
        "version": "2015.08.12",
        "descr": [ "Himem version of KbaseAnnotationHimem" ],
        "args": 
        {
            "inputs": [
                {
                    "name"     : "input_genome",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "the input kbase 'genomeTO' file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_genome",
                    "type"  : "file",
                    "descr"    : "the output kbase 'genomeTO' file",
                }
            ],
            "params": [
                {
                    "name"  : "subroutine",
                    "type"  : "str",
                    "descr" : "name of kbase annotation subroutine to run"
                },
                {
                    "name"  : "subroutine_params",
                    "type"  : "str",
                    "descr" : "subroutine params to evaluate as a perl hash or array",
                    "value" : ""
                },
            ]
        },
        "requirements": { 
            "memory": "8", 
            "cpus" : "12" 
        }
    }

