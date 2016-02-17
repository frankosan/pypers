import getpass
import subprocess
from pypers.config import DB_ENV
from pypers.core.logger import logger


def run_as(cmd, user=None, pythonpath=None, shell=False, rc_ok=0):
    """
    Run the given command `cmd` as the given UNIX username `user`. This assumes
    that the current UNIX user is allowed to do so (i.e. there is an appropriate
    entry in /etc/sudoers or equivalent).

    `cmd` is a list of the form [executable, arg1, arg2, ...]
    `user` is a string. If None, run as the current user.

    return (exit code, job id list)
    """
    # Make sure that we convert all Unicode str in cmd to simple strings.
    cmd = [str(ch) for ch in cmd]

    if user is None or user == getpass.getuser():
        sudoed_cmd = cmd
    else:
        #environment variable to passed with the sudo command
        sudoed_cmd = ['sudo', '-E', '-su', str(user), ] + DB_ENV + cmd

    logger.get_log().info("Executing %s" % sudoed_cmd)

    proc = subprocess.Popen(sudoed_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=shell)

    (out, err) = proc.communicate()
    ec = proc.returncode
    proc.stdout.close()
    proc.stderr.close()

    return (ec, err, out)
