import abc

JOB_OUT = 'job.out'
JOB_ERR = 'job.err'

class Scheduler():

    """ An abstract class defining methods for job submission and status reporting for job schedulers
        to run jobs in DRM (Distributed Resource Management) systems
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def submit(self,cmd,cmd_args,reqs=None):
        return

    @abc.abstractmethod
    def stop(self,id):
        return

    @abc.abstractmethod
    def status(self,id):
        return
