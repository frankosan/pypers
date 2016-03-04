Pypers
======


A lightweight, scalable python-based pipeline execution manager combined with a richly featured web front-end.

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
