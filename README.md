Pypers
======

![submission page](/docs/images/pypers_submission.png)

A lightweight, scalable python-based pipeline execution manager combined with a richly featured web front-end.

Some of the main featurs:

* general purpose automated pipeline for computational workflows
* massive parallel execution of pipelines 
* command line and web interface
* library of reusable configurable steps (parameter driven)
* ability to run pipelines either on computing clusters or locally on user workstations
* no programming required for pipeline DAG definition
* plugin architecture to work with different job schedulers
* configurable ldap authentication



### Code structure

The *Pypers* package consists of two main sub-systems located in the following directories:
* `Pypers` - contains the pipelines, steps and all their ancillary code;
* `mithril-ui` - contains the ui front-end 


### Installation

[How to install pypers](docs/installation.md)



### Examples

##### Step definition

This is an example of a simple command line step

```python
from nespipe.core.step import CmdLineStep

class Split(CmdLineStep):
    spec = {
        "version": "1.0",
        "local" : True,
        "descr": [
            "Splits an input file in several chuncks"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"      : "input_file",
                    "type"      : "file",
                    "descr"     : "input file name"
                },
                {
                    "name"      : "nchunks",
                    "type"      : "int",
                    "value"     : 100,
                    "descr"     : "number of chunks in which the input file get splitted"
                },
            ],
            "outputs": [
                {
                    "name"      : "output_files",
                    "type"      : "file",
                    "value"     : "*.fa",
                    "descr"     : "output file names"
                }
            ],
            "params" : [
                {
                    "name"      : "prefix",
                    "type"      : "str",
                    "value"     : "chunk_",
                    "descr"     : "string prefix on the output files",
                    "readonly"  : True
                },
                {
                    "name"      : "suffix",
                    "type"      : "str",
                    "value"     : ".fa",
                    "descr"     : "suffix added to the splitted files",
                    "readonly"  : True
                }
            ]
        },
        "cmd": [
            "split -n {{nchunks}} --suffix-length=4 -d --additional-suffix {{suffix}} {{input_file}} {{output_dir}}/{{prefix}}"
        ]
    }
```

A command line step execute the command in the "cmd" section rendering all the variables in {{}} with the corresponding value passed to the "input" and "params" keys


#### Pipeline definition

This is an example of pipeline with 3 steps:
* split : split an input file in 100 chunks
* count : count the occurrency of a string in parallel in each chunk
* collect : collect the result from count and sum them all 

```json
{
    "name" : "distributed_count",
    "label": "Distributed count of string in file",
    "dag": {
        "nodes": {
            "split":   "steps.split.Split",
            "count":   "steps.count.Count",
            "collect": "steps.collect.Collect"
        },
        "edges": [
            {
                "from"     : "split",
                "to"       : "count",
                "bindings" : { "count.input_files" : "split.output_files" }
            },
            {
                "from"     : "count",
                "to"       : "collect",
                "bindings" : { "collect.input_files" : "count.output_files" }
            }
        ]
    },
    "config" : {
        "steps": {
                "split": {
                    "nchunks": 100,
                    "suffix": ".txt"
                }
        }
    }
}
```

##### Pipeline submission

Once the server is up and running, to submit a pipeline, type

```{r, engine='bash', count_lines}
np_submit.py pipeline_name.cfg
```
