import os
import argparse
from datetime import datetime
from pypers.utils.utils import pretty_print

parser = argparse.ArgumentParser(description='Start API server.')
parser.add_argument('-r', '--enable-reload', dest='reloader', action='store_true',
                   help='enable hot reload of server.py on any source code change')

if __name__ == '__main__':
    pretty_print('===========================')
    pretty_print('STARTING SERVER')
    from pypers.api import app
    from pypers.config import ACME_PROD, SERVICE_PORT, HOST_NAME
    now = datetime.utcnow()
    if ACME_PROD:
        pretty_print('Flask API server start at port %s in PRODUCTION mode' % (SERVICE_PORT))
        app.run(host=HOST_NAME, port=SERVICE_PORT)
    else:
        args = parser.parse_args()
        if args.reloader: use_reloader=True
        else: use_reloader=False

        pretty_print('Flask API server start at port %s in DEVELOPMENT mode (with%s reloader)' % (SERVICE_PORT, 'out' if not use_reloader else ''))
        # app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True, use_reloader=use_reloader)
        app.run(host=HOST_NAME, port=SERVICE_PORT, debug=True, use_reloader=use_reloader)
