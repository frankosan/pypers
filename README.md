Pypers
======

![submission page](/images/pypers_submission.png)

A lightweight, scalable python-based pipeline execution manager combined with a richly featured web front-end.

Some of the main featurs:

* general purpose automated pipeline for computational workflows
* robust and scalable capable of batching pipeline runs for multiple inputs 
* command line and web interface  
* library of reusable configurable steps (parameter driven)
* ability to run pipelines either on computing clusters or locally on user workstations
* no programming required for pipeline DAG definition
* easy output data provenance
* configurable ldap authentication




### Code structure

The *Pypers* package consists of two main sub-systems located in the following directories:
* `Pypers` - contains the pipelines, steps and all their ancillary code;
* `mithril-ui` - contains the ui front-end 


## Local Installation

The software installation for code development purposes involves 1) setting up a "virtual environment", allowing for the use of concurrent versions of the software and 2) creating a clone (local repository) of the Pypers software.

### Prerequisites

The procedure described below assumes an already fully setup workspace:
* a machine with...
   * `sudo` rights (*)
      *  `requiretty` and `secure_path` should be commented out in the sudoers file (edit it with `sudo visudo`)
   * `node and npm` installed
   * `bower` installed
   * mongodb 
   
(*) only needed for development and testing

### Creating a new virtual environment

* Create a new ''virtual environment'' based on the central install:
  ```
conda create -p <path to environment> --yes --clone <path to anaconda>
  ```
* Activate the environment as shown below

### Activating an Existing Environment

After a first installation, the installed environment can easily be setup by running: 
```
export PATH=<path to anaconda>/bin:${PATH}
source activate <path to environment>
export ACME_LCL=1
```

### Deploying the software

After modifying the code, one has to deploy the new executables to the virtual environment. This can be done by running (from within the local git repository):
```
python ./setup.py develop
```
Note that this only applies to the `pypers` software package, not to the front-end.



### Examples

This is an example of a simple step which split and input file in chunck

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