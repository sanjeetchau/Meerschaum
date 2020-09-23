#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
"""
Miscellaneous functions go here
"""

def add_method_to_class(
        func : 'function',
        class_def : 'class', 
        method_name : str = None
    ) -> 'function':
    """
    Add function `func` to class `class_def`
    func - function :
        function to be added as a method of the class
    class_def - class :
        class we are modifying
    method_name - str (default None) :
        new name of the method. None will use func.__name__
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(self, *args, **kw):
        return func(*args, **kw)

    if method_name is None: method_name = func.__name__
    setattr(class_def, method_name, wrapper)
    return func

def choose_subaction(
        action : list = [''],
        options : dict = {},
        **kw
    ) -> tuple:
    """
    Given a dictionary of options and the standard Meerschaum actions list,
    check if choice is valid and execute chosen function, else show available
    options and return False
    
    action - list:
        subactions (e.g. `show pipes` -> ['pipes'])
    options - dict:
        Available options to execute
        option (key) -> function (value)
        Functions must accept **kw keyword arguments
        and return a tuple of success code and message
    """
    import inspect
    parent_action = inspect.stack()[1][3]
    if len(action) == 0: action = ['']
    choice = action[0]
    if choice not in options:
        print(f"Cannot {parent_action} '{choice}'. Choose one:")
        for option in options:
            print(f"  - {parent_action} {option}")
        return (False, f"Invalid choice '{choice}'")
    kw['action'] = action
    return options[choice](**kw)

def get_modules_from_package(
        package : 'package',
        names : bool = False,
        recursive : bool = False,
        lazy : bool = False,
        debug : bool = False
    ):
    """
    Find and import all modules in a package.

    Returns: either list of modules or tuple of lists
    
    names = False (default) : modules
    names = True            : (__all__, modules)
    """
    from os.path import dirname, join, isfile, isdir, basename
    import glob, importlib

    if recursive: pattern = '*'
    else: pattern = '*.py'
    module_names = glob.glob(join(dirname(package.__file__), pattern), recursive=recursive)
    _all = [
        basename(f)[:-3] if isfile(f) else basename(f)
            for f in module_names
                if (isfile(f) or isdir(f))
                    and not f.endswith('__init__.py')
                    and not f.endswith('__pycache__')
    ]

    if debug: print(_all)
    modules = []
    for module_name in [package.__name__ + "." + mod_name for mod_name in _all]:
        ### there's probably a better way than a try: catch but it'll do for now
        try:
            if lazy:
                modules.append(lazy_import(module_name))
            else:
                modules.append(importlib.import_module(module_name))
        except Exception as e:
            if debug: print(e)
            pass
    if names:
        return _all, modules
    return modules

def import_children(
        package : 'package' = None,
        package_name : str = None,
        types : list = ['method', 'builtin', 'function', 'class', 'module'],
        lazy : bool = True,
        recursive : bool = False,
        debug : bool = False
    ) -> list:
    """
    Import all functions in a package to its __init__.
    package : package (default None)
        Package to import its functions into.
        If None (default), use parent
    
    package_name : str (default None)
        Name of package to import its functions into
        If None (default), use parent

    types : list
        types of members to return.
        Default : ['method', 'builtin', 'class', 'function', 'package', 'module']

    Returns: list of members
    """
    import sys, inspect
    
    ### if package_name and package are None, use parent
    if package is None and package_name is None:
        package_name = inspect.stack()[1][0].f_globals['__name__']

    ### populate package or package_name from other other
    if package is None:
        package = sys.modules[package_name]
    elif package_name is None:
        package_name = package.__name__

    ### Set attributes in sys module version of package.
    ### Kinda like setting a dictionary
    ###   functions[name] = func
    modules = get_modules_from_package(package, recursive=recursive, lazy=lazy, debug=debug)
    _all, members = [], []
    for module in modules:
        objects = []
        for ob in inspect.getmembers(module):
            for t in types:
                ### ob is a tuple of (name, object)
                if getattr(inspect, 'is' + t)(ob[1]):
                    objects.append(ob)

        if 'module' in types:
            objects.append((module.__name__.split('.')[0], module))
    for ob in objects:
        setattr(sys.modules[package_name], ob[0], ob[1])
        _all.append(ob[0])
        members.append(ob[1])

    if debug: print(_all)
    ### set __all__ for import *
    setattr(sys.modules[package_name], '__all__', _all)
    return members

def generate_password(
        length : int = 12
    ):
    """
    Generate a secure password of given length.
    """
    import secrets, string
    return ''.join((secrets.choice(string.ascii_letters) for i in range(length)))

def yes_no(
        question : str = '',
        options : list = ['y', 'n'],
        default : str = 'y',
        wrappers : tuple = ('[', ']'),
    ) -> bool:
    """
    Print a question and prompt the user with a yes / no input
    
    Returns bool (answer)
    """
    ending = f" {wrappers[0]}" + "/".join(
                [ o.upper() if o == default else o.lower() for o in options ]
                ) + f"{wrappers[1]} "
    print(question, end=ending, flush=True)
    answer = str(input()).lower()
    return answer == options[0].lower()

def reload_package(
        package : 'package',
        lazy : bool = False,
        debug : bool = False,
        **kw
    ):
    """
    Recursively load a package's subpackages, even if they were not previously loaded
    """
    import os
    import types
    import importlib
    assert(hasattr(package, "__package__"))
    fn = package.__file__
    fn_dir = os.path.dirname(fn) + os.sep
    module_visit = {fn}
    del fn

    def reload_recursive_ex(module):
        ### forces import of lazily-imported modules
        module = importlib.import_module(module.__name__)
        importlib.reload(module)

        for module_child in get_modules_from_package(module, recursive=True, lazy=lazy):
            if isinstance(module_child, types.ModuleType) and hasattr(module_child, '__name__'):
                fn_child = getattr(module_child, "__file__", None)
                if (fn_child is not None) and fn_child.startswith(fn_dir):
                    if fn_child not in module_visit:
                        if debug: print("reloading:", fn_child, "from", module)
                        module_visit.add(fn_child)
                        reload_recursive_ex(module_child)

    return reload_recursive_ex(package)

def is_int(s):
    """
    Check if string is an int
    """
    try:
        float(s)
    except ValueError:
        return False
    else:
        return float(s).is_integer()

def get_options_functions():
    """
    Get options functions from parent module
    """
    import inspect
    parent_globals = inspect.stack()[1][0].f_globals
    parent_package = parent_globals['__name__']
    print(parent_package)

def string_to_dict(
        params_string : str
    ) -> dict:
    """
    Parse a string into a dictionary

    If the string begins with '{', parse as JSON. Else use simple parsing

    """

    import ast

    if str(params_string)[0] == '{':
        import json
        return json.loads(params_string)

    params_dict = dict()
    for param in params_string.split(","):
        values = param.split(":")
        try:
            key = ast.literal_eval(values[0])
        except:
            key = str(values[0])

        for value in values[1:]:
            try:
                params_dict[key] = ast.literal_eval(value)
            except:
                params_dict[key] = str(value)
    return params_dict

def parse_config_substitution(
        value : str,
        leading_key : str = 'MRSM',
        begin_key : str = '{',
        end_key : str = '}',
        delimeter : str = ':'
    ):
    """
    Parse Meerschaum substitution syntax
    E.g. MRSM{value1:value2} => ['value1', 'value2']
    NOTE: Not currently used. See `search_and_substitute_config` below
    """
    if not value.beginswith(leading_key):
        return value
    
    return leading_key[len(leading_key):][len():-1].split(delimeter)
    
def search_and_substitute_config(
        config : dict,
        leading_key : str = "MRSM",
        delimiter : str = ":",
        begin_key : str = "{",
        end_key : str = "}"
    ) -> dict:
    """
    Search the config for Meerschaum substitution syntax and substite with value of keys

    Example:
        MRSM{meerschaum:connectors:main:host} => cf['meerschaum']['connectors']['main']['host']
    """
    import yaml
    needle = leading_key
    haystack = yaml.dump(config)
    mod_haystack = list(str(haystack))
    buff = str(needle)
    max_index = len(haystack) - len(buff)

    patterns = dict()

    begin, end, floor = 0, 0, 0
    while needle in haystack[floor:]:
        ### extract the keys
        hs = haystack[floor:]

        ### the first character of the keys
        ### MRSM{value1:value2}
        ###       ^
        begin = hs.find(needle) + len(needle) + len(begin_key)

        ### number of characters to end of keys
        ### (really it's the index of the beginning of the end_key relative to the beginning
        ###     but the math works out)
        ### MRSM{value1}
        ###       ^     ^  => 6
        length = hs[begin:].find(end_key)

        ### index of the end_key (end of `length` characters)
        end = begin + length

        ### advance the floor to find the next leading key
        floor += end + len(end_key)
        keys = hs[begin:end].split(delimiter)

        ### follow the pointers to the value
        c = config
        for i, k in enumerate(keys):
            try:
                c = c[k]
            except KeyError:
                print(f"WARNING: Invalid keys in config: {keys}")
        value = c

        ### pattern to search and replace
        pattern = leading_key + begin_key + delimiter.join(keys) + end_key
        ### store patterns and values
        patterns[pattern] = value

    ### replace the patterns with the values
    for pattern, value in patterns.items():
        haystack = haystack.replace(pattern, str(value))

    ### parse back into dict
    return yaml.safe_load(haystack)

def is_installed(
        name : str
    ) -> bool:
    """
    Check whether a package is installed.
    name : str
        Name of the package in question
    """
    import importlib
    return importlib.util.find_spec(name) is None

def attempt_import(
        *names : list,
        lazy : bool = True
    ) -> 'module or tuple of modules':
    """
    Raise a warning if packages are not installed; otherwise import and return modules.
    If lazy = True, return lazy-imported modules.

    Returns tuple of modules if multiple names are provided, else returns one module.

    Examples:
        pandas, sqlalchemy = attempt_import('pandas', 'sqlalchemy')
        pandas = attempt_import('pandas')
    """
    from meerschaum.utils.warnings import warn
    import importlib

    modules = []
    for name in names:
        if importlib.util.find_spec(name) is None:
            warn(
                (f"\n\nMissing package '{name}'; features will not work correctly. "
                f"\n\nRun `pip install meerschaum[full]` to install the complete version of Meerschaum.\n"),
                ImportWarning,
                stacklevel = 2
            )
            modules.append(None)
        else:
            if not lazy:
                mod = importlib.import_module(name)
            else:
                mod = lazy_import(name)
            modules.append(mod)
    modules = tuple(modules)
    if len(modules) == 1: return modules[0]
    return modules

def lazy_import(
        name : str,
        local_name : str = None
    ):
    """
    Lazily import a package
    Uses the tensorflow LazyLoader implementation (Apache 2.0 License)
    """
    from meerschaum.utils.lazy_loader import LazyLoader
    if local_name is None:
        local_name = name
    return LazyLoader(local_name, globals(), name)

def edit_file(
        path : 'pathlib.Path',
        default_editor : str = 'pyvim',
        debug : bool = False
    ):
    """
    Open a file for editing. Attempts to use the user's defined EDITOR,
    otherwise uses pyvim.
    """
    import os
    from subprocess import call
    try:
        EDITOR = os.environ.get('EDITOR', default_editor)
        if debug: print(f"Opening file '{path}' with editor '{EDITOR}'") 
        call([EDITOR, path])
    except Exception as e: ### can't open with default editors
        if debug: print(e)
        if debug: print('Failed to open file with system editor. Falling back to pyvim...')
        run_python_package('pyvim', [path])

def run_python_package(
        package_name : str,
        args : list = []
    ):
    """
    Runs an installed python package.
    E.g. Translates to `/usr/bin/python -m [package]`
    """
    import sys
    from subprocess import call
    command = [sys.executable, '-m', package_name] + args
    return call(command)

def parse_connector_keys(keys : str) -> 'meerschaum.connectors.Connector':
    """
    Parse connector keys and return Connector object
    """
    from meerschaum.connectors import get_connector
    try:
        vals = keys.split(':')
        conn = get_connector(vals[0], vals[1])
    except Exception as e:
        return False
    return conn