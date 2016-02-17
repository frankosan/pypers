from pypers.core.step import Step
import os

class Mothur(Step):
    """
    The mothur base class
    """

    mothur_exe = '/software/pypers/mothur/mothur-1.35.0-gcc/bin/mothur'
    extra_env = { 'CPATH' : '/software/pypers/gcc/gcc-4.7.1/include/',
                          'LIBRARY_PATH' : '/software/pypers/gcc/gcc-4.7.1/lib64/:/software/pypers/gcc/gcc-4.7.1/lib/',
                          'PATH' : '/bin', # temp fix for RH version probs, so mothur can find /bin/rm
                          'LD_LIBRARY_PATH' : '/software/pypers/gcc/gcc-4.7.1/lib64/:/software/pypers/gcc/gcc-4.7.1/lib/'}

    
    def mk_links(self, files, dstdir):
        """
        As mothur requires all files to be in working dir, make symlinks for each file in list in the output dir
        """
        for path in files:
            link = os.path.join(dstdir, os.path.basename(path))
            if not os.path.exists(link):
                os.symlink(path, link)

    def run_cmd(self, step, extra_params):
        """
        Construct a mothur command from the step params and the filenames
        Change to step output dir and execute
        """

        mothur_cmd = '#%s(' % step
    
        params=[]

        step_params = self.get_param_values(get_req=False)
        for k in step_params:
            params.append('%s=%s' % (k,step_params[k]))
    
        for k in extra_params:
            params.append('%s=%s' % (k,extra_params[k]))

        # some mothur functions will fail if given processors param, so 1 means no param
        if int(self.cpus) > 1:
            params.append('processors=%s' % self.cpus)

        mothur_cmd += ','.join(params)
        mothur_cmd += ')'

        # Not sure how this works ? mothur #sffinfo() somehow runs
        cmd = [self.mothur_exe, str(mothur_cmd)]

        os.chdir(self.output_dir)
        (rc, stderr, stdout) = self.submit_cmd(cmd, shell=False, extra_env=self.extra_env)

        # mothur rc 0 is not necessarily successful, not worch checking
        return rc

