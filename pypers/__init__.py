"""
The top-level *pypers* package export just one utility function (see below).
The rest of the functionality is in the four sub-packages listed above.
"""


def import_all(namespace, dir):
    """
    Import all Python files in the directory `dir` and add all the symbols
    they define into the namespace `namespace.__name__`.

    This utility function is meant to be called in a __init__.py file in order
    to load all the Python source files in the same directory as the __init__.py
    file itself. In these cases, the input parameter `namespace` is typically
    set to globals().
    """
    from imp import find_module, load_module
    import os
    from sys import modules
    from types import ModuleType

    _this_module_name = namespace['__name__']
    _this_module = modules[_this_module_name]
    assert namespace is _this_module.__dict__

    # Find all the .py files to import...
    _sources = [_f for _f in os.listdir(dir)
                if _f.endswith('.py') and _f != '__init__.py']

    # ...and import them, one by one.
    for _source in _sources:
        _name = _source[:-3]
        _fp, _path, _desc = find_module(_name, [dir, ])
        try:
            _m = load_module(_this_module_name + '.' + _name, _fp, _path, _desc)
        finally:
            if _fp:
                _fp.close()

        # Now add all the Step subclasses to the current package.
        for (_name, _symbol) in _m.__dict__.items():
            if(not isinstance(_symbol, ModuleType) and
               not _name.startswith('_')):
                setattr(_this_module, _name, _symbol)
    return
