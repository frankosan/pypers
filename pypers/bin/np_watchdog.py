""" 
 This file is part of Pypers.

 Pypers is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Pypers is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Pypers.  If not, see <http://www.gnu.org/licenses/>.
 """

import psutil
import sys
import os
import argparse
import sched
import time
import signal
import json

from pypers.utils.utils import pretty_print, format_dict

doc="""
Monitor resources of a given process
"""

global scheduler
global pi

parser = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('pid',type=int,help='pid of the process to monitor')
parser.add_argument('-i', '--interval', default=5, type=int, help='interval between two checks')
parser.add_argument('-v', '--verbose', default=False, help='increase verbosity')


def stop_monitoring(signum, frame):
    global pi
    print json.dumps(pi.stats, sort_keys=True)
    sys.exit()


signal.signal(signal.SIGTERM, stop_monitoring)


class procinfo(object):
    stats = { 'names':[], 'pids':[], 
              'memmax':0, 'memavg':0, 
              'cpupavg':0, 'cpupmax':0, 'cpuusr':0, 
              'iowrite':0, 'ioread':0,
              'time':0
              } 

    def __init__(self, pid, interval, verbose=False):
        self.pid = pid
        self.interval = interval
        self.nsamples = 0
        self.verbose = verbose
        self.sttime = time.time()
        try :
            proc = psutil.Process(self.pid)
        except psutil.NoSuchProcess as err:
            sys.exit(str(err))

    def average(self, key, newval):
        """
        Add new value to average from given key
        """
        self.stats[key] = ((self.nsamples-1)*self.stats[key] + newval)/self.nsamples

    def get_iocounts(self, pid):
        """
        Reimplement psutil's iocount and get the proper information
        """
        fname = "/proc/%s/io" % pid
        rchar = wchar = 0
        try:
            with open(fname, 'rb') as f:
                rchar = wchar = None
                for line in f:
                    if rchar is None and line.startswith(b"rchar"):
                        rchar = int(line.split()[1])
                    elif wchar is None and line.startswith(b"wchar"):
                        wchar = int(line.split()[1])
                for x in (rchar, wchar):
                    if x is None:
                        raise NotImplementedError(
                            "couldn't read all necessary info from %r" % fname)
        except IOError, e:
            #pretty_print('Error trying to get io counts: %s' % e)
            pass
        return (rchar, wchar)


    def accumulate(self):
        """
        Accumulate process resources information
        """
        global scheduler

        self.nsamples += 1
        try:
            parent = psutil.Process(self.pid)
            procs = [parent]
            procs.extend(parent.children(recursive=True))
            self.stats['cpuusr'] = 0
            self.stats['iowrite'] = 0
            self.stats['ioread'] = 0
            self.stats['names'] = []
            self.stats['pids'] = []
            memtot = 0
            cpuperc = 0
            for proc in procs:
                self.stats['names'].append(proc.name())
                self.stats['pids'].append(proc.pid)
                self.stats['cpuusr'] += proc.cpu_times().user
                cpuperc += proc.cpu_percent()
                memtot += proc.memory_info().rss
                io_count = self.get_iocounts(proc.pid)
                self.stats['ioread']  += io_count[0]
                self.stats['iowrite'] += io_count[1]
            if memtot>self.stats['memmax']:
                self.stats['memmax'] = memtot   
            if cpuperc>self.stats['cpupmax']:
                self.stats['cpupmax'] = cpuperc   
            self.average('memavg', memtot)
            self.average('cpupavg', cpuperc)
            self.stats['time'] = time.time()-self.sttime

            # Print stats and schedule next accumulation
            if self.verbose:
                pretty_print(format_dict(self.stats))
            scheduler.enter(self.interval, 1, self.accumulate, [])
        except psutil.NoSuchProcess as err:
            pretty_print('Process exited: dumping statistics')
            print json.dumps(pi.stats, sort_keys=True)


if __name__ == '__main__':
    args = parser.parse_args()

    scheduler = sched.scheduler(time.time, time.sleep)
    pi = procinfo(args.pid, args.interval, args.verbose)
    pi.accumulate()
    scheduler.run()
