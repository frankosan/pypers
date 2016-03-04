import json
from os import path
import os
import socket

ACME_PROD = bool(os.environ.get('ACME_PROD', False))
ACME_DEV  = bool(os.environ.get('ACME_DEV' , False))
ACME_CI   = bool(os.environ.get('ACME_CI'  , False))
ACME_LCL  = bool(os.environ.get('ACME_LCL' , False))




LDAPS_ADDRESS = "" # ldap address of your company e.g 'ldaps://ldap.company.com:port'"
MONGODB_HOST        = socket.gethostname()
MONGODB_NAME        = 'pypers_db'
WORK_DIR            = ROOT_DIR + '/lcl'

SOCKET_SERVICE_PORT = 5002
SERVICE_PORT = 5001
HOST_NAME = '0.0.0.0'
SERVICE_ROOT_URL    = "http://%s:%s" % (MONGODB_HOST, SERVICE_PORT)
MONGODB_PORT = 27017
MONGODB_MAXPOOL_SIZE = 2
MONGO_DEFAULT_ALIAS = "default"

#DB environment variables
DB_ENV = [
    'MONGODB_HOST=%s' % MONGODB_HOST,
    'MONGODB_NAME=%s' % MONGODB_NAME
]

###############################
# Demultiplexing config files
###############################
home = path.expanduser("~")
DEMUX_CFG_FILE = 'demultiplexing.cfg'
HOME_CFG_DIR = path.join(home, '.pypers')
PCKG_CFG_DIR = path.dirname(path.abspath(__file__))


def load_demux(cfg_file):
    """
    Load the config file for demultiplexing
    """
    with open(cfg_file) as fh:
        cfg_data = json.load(fh)
        valid_keys = set(["hiseq_dirs", "demu_dir", "sleep_time", "notify", "email"])
        for key in cfg_data.keys():
            if key not in valid_keys:
                raise Exception("Invalid demultiplexing cfg file")
        return cfg_data


def search_cfg_file(file_name):
    """
    Reaturn the location of the first valid config file in the following order
        #1) search in the home dir
        #2) search in central installed
    """
    if os.path.exists(path.join(HOME_CFG_DIR, file_name)):
        return path.join(HOME_CFG_DIR, file_name)
    elif path.join(PCKG_CFG_DIR, file_name):
        return path.join(PCKG_CFG_DIR, file_name)


def get_file_path(file_name):
    return os.path.join(os.path.dirname(__file__),file_name)
