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

import argparse
import json

if __name__ == '__main__':
    doc='''
    Information about pipelines and steps
    '''

    parser = argparse.ArgumentParser(description=doc,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("category", choices=['step', 'pipeline'], help="category to get information from")
    parser.add_argument("action", choices=['list', 'show'], 
                        help="- list all available pipelines/steps or\n- show details on one pipeline/step")
    parser.add_argument("name", nargs='?', default=None, help="full name of pipeline/step to show details of")

    args = parser.parse_args()

    if args.action=='show' and not args.name:
        print '*** Missing name for "show" action'
        print '    Run with --help for more information'

    if args.category=='step':
        from pypers.steps import step_list
        if args.action=='list':
            print '%-40s %-30s %s' % ('Path', 'Category', 'Class name')
            print '-'*85
            for key in sorted(step_list.keys()):
                fields = key.split('.')
                category = '.'.join(fields[:-1])
                class_name = fields[-1]
                print '%-40s %-30s %s' % (key, category, class_name)
        else:
            print json.dumps(step_list[args.name].spec, indent=4)
    else:
        from pypers.pipelines import pipelines, pipeline_specs
        if args.action=='list':
            print "%-30s %s" % ('Name', 'Label')
            print '-'*50
            for p in sorted(pipelines):
                print "%-30s %s" % (p['name'], p['label'])
        else:
            print json.dumps(pipeline_specs[args.name], indent=4, sort_keys=True)

