import os
import inspect
import pkgutil
from collections import defaultdict
from os.path import realpath, dirname
from pypers.core.step import Step


for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
    if is_pkg:
        module = loader.find_module(module_name).load_module(module_name)
        exec('%s = module' % module_name)

def all_subclasses(cls):
        return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                         for g in all_subclasses(s)]

def get_step_list(all_list):
    step_list = defaultdict(dict)

    for sub_class in all_list:
        if 'pypers.' not in sub_class.__module__:
            step_list[sub_class.__module__.rsplit(".", 1)[0]  + "." + sub_class.__name__] = sub_class

    return step_list

all_list = all_subclasses(Step)
step_list = get_step_list(all_list)
