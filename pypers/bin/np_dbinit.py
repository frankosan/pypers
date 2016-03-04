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
import pandas as pd
from nespipe.db.models.mongo import PipelineDbConnector
from nespipe import config as cf

db = PipelineDbConnector()

#############################
# insert project data from csv
#############################
if os.path.exists(cf.get_file_path('projects.csv'):
    df = pd.read_csv(cf.get_file_path('projects.csv'), sep=";")
    data = [json.loads(row[1].to_json()) for row in df.iterrows()]
    db.projects.delete_many({})
    result = db.projects.insert_many(data)
    print 'Inserted:',result.inserted_ids

#############################
# insert refgenomes from json
#############################
collections = ['refgenomes']
for collection in collections:
    with open(cf.get_file_path(collection + '.json')) as fh:
        try:
            data = json.load(fh)
            c = getattr(db, collection)
            print "deleting collection %s" % collection

            c.delete_many({})
            print "inserting data into %s" % collection
            result = c.insert_many(data)
            print 'Inserted:',result.inserted_ids

        except pymongo.errors.BulkWriteError as bwe:
            print '*** Bulk insert returned an error:\n'
            print json.dumps(bwe.details, indent=4)
            raise bwe





