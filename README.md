Pypers
======

A lightweight, scalable python-based pipeline execution manager combined with a richly featured web front-end.

### Code structure

The *Pypers* package consists of two main sub-systems located in the following directories:
* `Pypers` - contains the pipelines, steps and all their ancillary code;
* `mithril-ui` - contains the ui framework (aka *bluebird*).

There exist three different environments:
* **production**: corresponds to branch `master` and runs on the production server;
* **development**: corresponds to branch `develop` and runs on the beta server;
* **local**: is run on the local machine where code development is actually carried out and is therefore not bound to a particular branch (although it usually corresponds to a temporary, working branch).

The [local installation](#local-installation) procedure focusses on the latter. 

## Local Installation

The CGI software installation for code development purposes involves 1) setting up a "virtual environment", allowing for the use of concurrent versions of the software and 2) creating a clone (local repository) of the Pypers software.

### Prerequisites

The procedure described below assumes an already fully setup CGI workspace:
* a virtual machine with...
   * `sudo` rights (*)
      *  `requiretty` and `secure_path` should be commented out in the sudoers file (edit it with `sudo visudo`)
   * mongodb [installed](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/):
      * this requires a specific yum repository. Create file ` /etc/yum.repos.d/mongodb-org-3.0.repo` with the following contents:
      ```
[mongodb-org-3.0]
name=MongoDB Repository
baseurl=http://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.0/x86_64/
gpgcheck=0
enabled=1
      ```
      * then run `yum install mongodb-org`
      * edit `/etc/mongod.conf`, adding the following line: `smallfiles = true`, and commenting out the `bind_ip` statement
   * nodejs and dependencies: 
      * install nodejs: `yum install npm`
      * install gulp: `npm install -g gulp`
* commit rights to the Pypers git repository (*)
* JIRA, Bamboo, and wiki access/editing rights (*)

(*) only needed for development and testing

### Creating a new virtual environment

* Create a new ''virtual environment'' based on the central install:
  ```
conda create -p <path to environment> --yes --clone /nihs/Development/cgi/software/Anaconda-2.4.0
  ```
(`path to environment` needs to be empty; example: `/nihs/Bioinformatics_home/<user>/envs/dev`)
* Activate the environment as shown below

### Activating an Existing Environment

After a first installation, the installed environment can easily be setup by running: 
```
export PATH=/nihs/Development/cgi/software/Anaconda-2.4.0/bin:${PATH}
source activate <path to environment>
export ACME_LCL=1
export PATH=${PATH}:/sonas/Software/NIHS/js/bin/
```

### Deploying the software

After modifying the code, one has to deploy the new executables to the virtual environment. This can be done by running (from within the local git repository):
```
python ./setup.py develop
```
Note that this only applies to the `nihspipe` software, not to the front-end.
