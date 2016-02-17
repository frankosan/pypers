import pymongo
import json
import os
from pypers.db.models.mongo import PipelineDbConnector
from pypers import config

cfg_file = config.get_file_path('ref_genomes.json')

post = ''
with open(cfg_file) as fh:
    post = json.load(fh)

db = PipelineDbConnector()
try:
    result = db.refgenomes.delete_many({})
    print 'Deleted:',result.deleted_count
    #result = db.refgenomes.insert_many(post)
    result = db.refgenomes.insert_many(post)
    print 'Inserted:',result.inserted_ids
except pymongo.errors.BulkWriteError as bwe:
    print '*** Bulk insert returned an error:\n'
    print json.dumps(bwe.details, indent=4)
    raise bwe


