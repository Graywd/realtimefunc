# -*- coding: iso-8859-1 -*-
import sys
import linecache
import re
from inspect import getsource, getfile

# A decorator is used to update a function at runtime.

DecoratorName = 'realtimefunc'
suffix = '_runtime'

PY3 = sys.version_info >= (3,)
if PY3:
    basestring_type = str
else:
    basestring_type = basestring  # noqa

def _exec_in(code, glob, loc=None):
    # type: (Any, Dict[str, Any], Optional[Mapping[str, Any]]) -> Any
    if isinstance(code, basestring_type):
        # exec(string) inherits the caller's future imports; compile
        # the string first to prevent that.
        code = compile(code, '<string>', 'exec', dont_inherit=True)
    exec(code, glob, loc)

def _handle_real_time_func_code(func, split='\n'):
    linecache.clearcache()
    code = getsource(func)
    i_indent = 0
    i_decorator = 0
    code_lines = code.split(split)
    func_pat = re.compile(r'^\s*def\s+'+func.__name__)
    for i, line in enumerate(code_lines):
        if "@"+DecoratorName in line:
            i_decorator = i

        if  func_pat.match(line):
            i_indent = line.index("def")
            # the raw function will be called rather than the one decorated, sometime.
            code_lines[i] = code_lines[i].replace(func.func_name, func.func_name+suffix, 1)
            break
    # rm realtimefunc decorator
    code_lines.pop(i_decorator)
    # code indentation
    code_lines = [line[i_indent:] for line in code_lines]
    code = split.join(code_lines)
    return code

def realtimefunc(func):
    def wrapper(*args, **kwargs):
        filename = getfile(func)
        # inspect use linecache to do file cache, so do checkcache first
        linecache.checkcache(filename)
        code_str = _handle_real_time_func_code(func)
        _exec_in(code_str,func.__globals__, func.__globals__)
        # A return expected when is work, if not yield instead.
        return func.__globals__[func.__name__+suffix](*args, **kwargs)
    return wrapper



