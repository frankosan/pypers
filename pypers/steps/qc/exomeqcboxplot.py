import os
import re
from pypers.core.step import RStep
from pypers.utils import utils

class ExomeQcBoxPlot(RStep):
    spec = {
        "version": "0.1",
        "descr": [
            "Run the qplot program to calculate summary statistics for illumina"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "hsmetrics_dir",
                    "type"     : "dir",
                    "descr"    : "the output of hs metrics step",
                },
                {
                    "name"     : "qplot_dir",
                    "type"     : "dir",
                    "descr"    : "the output of qplot step",
                }
            ],
            "outputs": [
                {
                    "name"  : "hsmetrics",
                    "type"  : "file",
                    "value" : "HsMetric.csv",
                    "descr" : "hs metrics csv file",
                },
                {
                    "name"  : "qplot",
                    "type"  : "file",
                    "value" : "qplot.csv",
                    "descr" : "qplot csv file",
                }
            ],
        },
        "cmd" : [
            "R --save < {{rscript}} --args {{hsmetrics_dir}} {{qplot_dir}} {{output_dir}}"
        ]
    }