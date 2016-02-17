from distutils.core import setup
from distutils import sysconfig
from setuptools import find_packages
import glob
import os
import pip
from pip.req import parse_requirements
from collections import defaultdict
import site
import shutil
import uuid

__version__ = '0.1.0'

PCKG_NAME = "pypers"
CODE_ROOT = PCKG_NAME
SCRIPTS = glob.glob(CODE_ROOT + '/bin/*')


def find_package_data(code_root):
    """
    Return a all the package data
    """
    #get all the data files
    package_data = defaultdict(list)
    for root, dirs, files in os.walk(code_root):
        for f in files:
            fullpath = os.path.join(root, f)
            ext = os.path.splitext(fullpath)[1]
            if ext != ".py" and ext != ".pyc":
                package_path = root.replace("/", ".")
                package_data[package_path].append(os.path.basename(fullpath))

    return package_data

if __name__ == "__main__":
    #install additional git repository with pip
    with open('requirements.pip') as pip_reqs:
        for pip_req in pip_reqs:
            pip.main(['install', pip_req])

    #########################################
    #specific for picrust -- not very nice
    picrust_data_dir = os.path.join(site.getsitepackages()[0], 'picrust/data')
    picrust_data_root  = '/software/pypers/picrust'
    picrust_data_files = ['ko_13_5_precalculated.tab.gz',
                          '16S_13_5_precalculated.tab.gz']
    if not os.path.exists(picrust_data_dir):
        os.mkdir(picrust_data_dir, 0777)
    for f in picrust_data_files:
        path = os.path.join(picrust_data_root, f)
        if not os.path.exists(os.path.join(picrust_data_dir, f)):
            print("Copying data file %s to %s" % (path, picrust_data_dir))
            shutil.copy(path, picrust_data_dir)

    install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
    reqs = [str(ir.req) for ir in install_reqs]

    setup(name=PCKG_NAME,
          description="Pypers package",
          author="NIHS Bioinformatics Team",
          version=__version__,
          install_requires=reqs,
          packages=find_packages(include=[PCKG_NAME + '*']),
          package_data=find_package_data(CODE_ROOT),
          package_dir={PCKG_NAME : CODE_ROOT},
          scripts=SCRIPTS,
          data_files = [ ( sysconfig.PREFIX+'/etc', ['supervisord.conf', os.path.join(PCKG_NAME + '/config/gunicorn.py'] ) ]
         )
