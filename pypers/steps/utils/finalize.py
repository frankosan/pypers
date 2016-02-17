import os
import re
import shutil
from pypers.core.step import Step, STEP_PICKLE
from pypers.utils import utils as ut


class Finalize(Step):
    spec = {
        "version": "0.1",
        "descr": [
            "Final step to copy back results, create manifest file, and delete temporary files."
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "results_files",
                    "type"     : "file",
                    "descr"    : "the files to copy",
                    "value"    : ""
                },
                {
                    "name"     : "delete_files",
                    "type"     : "file",
                    "descr"    : "the temporary files to delete",
                    "value"    : ""
                }
            ],
            "outputs": [
                {
                    'name'      : 'copied_files',
                    'type'      : 'file',
                    'descr'     : 'copied file names'
                },
                {
                    'name'      : 'manifest_files',
                    'type'      : 'file',
                    'descr'     : 'manifest files corresponding to each copied file'
                },
                {
                    'name'      : 'deleted_files',
                    'type'      : 'file',
                    'descr'     : 'deleted file names'
                }
            ],
            "params" : [
                {
                    "name"     : "target_dir",
                    "type"     : "dir",
                    "descr"    : "the copy directory",
                    "value"    : ""
                },
                {
                    "name"     : "source_dir",
                    "type"     : "dir",
                    "descr"    : "the source directory (for copy_all)",
                    "value"    : ""
                },
                {
                    "name"     : "copy_all",
                    "type"     : "bool",
                    "descr"    : "If true, copy back all the steps",
                    "value"    : True
                }
            ],
        }
    }

    def process(self):
        if type(self.results_files) != list:
            self.results_files = [self.results_files]

        destdir = os.path.join(self.target_dir, '_results')
        if not os.path.exists(destdir):
            os.makedirs(destdir, 0775)

        # 1. Result files
        self.copied_files = []
        self.manifest_files = []
        for f in self.results_files:
            if not os.path.exists(f):
                self.log.warn('File %s not found: skipping' % f)
            else:
                # Rename file as: step.jobid.file
                names = f.split('/')[-3:]
                step_name = names[0]
                job_id = names[1]
                destf = os.path.join(destdir, '.'.join(names))
                if os.path.exists(destf):
                    self.log.warn('Overwriting file %s' % destf)
                shutil.copy2(f, destf)

                #job_meta      = self.meta['steps'][step_name]['job'].get(job_id)
                step_meta     = self.meta['steps'][step_name]['step']
                pipeline_meta = self.meta['pipeline']
                manifestfile =  destf + '.irods_manifest'
                with open(manifestfile,'w') as fh:
                    for k, v in pipeline_meta.iteritems():
                        fh.write('pipeline %s = %s\n' % (k,v))
                    for k, v in step_meta.iteritems():
                        fh.write('step %s = %s\n' % (k,v))
                self.copied_files.append(destf)
                self.manifest_files.append(manifestfile)
                self.log.info('Copied file %s to %s' % (f, destf))

        # 2. Delete files
        if type(self.delete_files) != list:
            self.delete_files = [self.delete_files]
        for f in self.delete_files:
            try:
                os.remove(f)
            except OSError, e:
                self.log.warn('Failed to delete %s: %s' %(f, e))
            self.log.info('Deleted file %s' % f)
            # Also remove job status
            status_file = os.path.join(os.path.dirname(f), STEP_PICKLE)
            if os.path.exists(status_file):
                os.remove(status_file)
                self.log.info('Also removed %s' % status_file)

        # 3. Copy all
        if self.copy_all and (self.target_dir != self.source_dir):
            self.log.warn('Copying everything from %s to %s' 
                           % (self.target_dir, self.source_dir))
            source = self.source_dir.rstrip('/') + '/'
            target = self.target_dir.rstrip('/') + '/'
            cmd = ['rsync', '-auv', '--exclude LOCK', source, target]
            self.submit_cmd(' '.join(cmd))

