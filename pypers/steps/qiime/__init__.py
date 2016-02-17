from os.path import realpath, dirname
from pypers import import_all
from pypers.core.step import Step

class Qiime(Step):
    """
    The qiime base class
    """

    extra_env = { 'PYTHONPATH':'/software/pypers/qiime/qiime-1.8.0/lib/python2.7/site-packages',
                  'PATH':'/software/pypers/qiime/qiime-1.8.0/bin/'}

# Import all Steps in this directory.
import_all(namespace=globals(), dir=dirname(realpath(__file__)))
