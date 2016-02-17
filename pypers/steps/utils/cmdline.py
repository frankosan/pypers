from pypers.core.step import CmdLineStep

class CmdLine(CmdLineStep):
    spec = {
        "version": "0.1",
        "descr": [
            "Runs any script with arguments on the cluster"
        ],
        "args":
        {
            "inputs": [
                {
                    "name"  : "input_script",
                    "type"  : "file",
                    "value" : "",
                    "descr" : "path to the script to run / command to execute"
                },
                {
                    "name"  : "args",
                    "type"  : "str",
                    "value" : "",
                    "descr" : "arguments to pass to the script / full command"
                }               
            ],
            "outputs": [
            ],
            "params": [
                {
                    "name" : "memory",
                    "type" : "enum",
                    "options": [1] + range(5, 60, 5),
                    "value": 1,
                    "descr": "explicit memory requirements for condor (in GB)"
                },
                {
                    "name" : "cpus",
                    "type" : "enum",
                    "options": range(1,16,1),
                    "value": 1,
                    "descr": "explicit cpu requirements for condor"
                }
            ]
        },
        "cmd": [
            "{{input_script}} {{args}}"
        ],
        "requirements": {
        }
    }

    def __init__(self):
        super(CmdLine, self).__init__()
        self.reqs['memory'] = self.memory
        self.reqs['cpus'] = self.cpus

