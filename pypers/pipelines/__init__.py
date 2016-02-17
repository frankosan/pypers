import glob
import json
import os

# Create a dictionary of files and pipeline names
pipeline_names = {}
pipeline_specs = {}
pipelines = []

dir = os.path.dirname(os.path.realpath(__file__))

def raise_KeyError(msg=''): raise KeyError(msg)

for file in glob.glob('%s/*.json' % dir):
    with open(os.path.join(dir,file)) as fh:
        try:
            config = json.load(fh)
            name  = config.get('name')  or raise_KeyError('name not found in %s' % file)
            label = config.get('label') or raise_KeyError('label not found in %s' % file)

            pipelines.append({'name'   : name,
                              'label'  : label})

            if name:
                pipeline_names[name] = fh.name
                pipeline_specs[name] = config

        except ValueError as e:
            print '*** Problem with file %s:' % file
            raise

pipelines = sorted(pipelines)



