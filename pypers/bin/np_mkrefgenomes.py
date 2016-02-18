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


