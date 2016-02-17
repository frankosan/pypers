from schedcondor import CondorScheduler
from schedlocal import LocalScheduler

schedulers = {
    "SCHED_LOCAL"  : LocalScheduler, 
    "SCHED_CONDOR" : CondorScheduler
}


DEFAULT_SCHEDULER = "SCHED_CONDOR"

def get_scheduler(schedname=DEFAULT_SCHEDULER):
    return schedulers[schedname]()