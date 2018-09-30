"""A decorator is used to update a function at runtime"""
import sys
import re
import functools
import linecache
from inspect import getsource, getfile

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
    code = getsource(func)
    code_lines = code.split(split)

    func_pat = re.compile(r'^\s*def\s+'+func.__name__)
    #rm decorators
    while not func_pat.match(code_lines[0]):
        code_lines.pop(0)

    indent = code_lines[0].index("def")
    # the raw function will be called rather than the one decorated, sometime.
    code_lines[0] = code_lines[0].replace(func.func_name, func.func_name+suffix, 1)

    # code indentation
    code_lines = [line[indent:] for line in code_lines]
    code = split.join(code_lines)
    return code

def realtimefunc(func):
    """Decorator for update a function at runtime"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        filename = getfile(func)
        # inspect use linecache to do file cache, so do checkcache first
        linecache.checkcache(filename)
        code_str = _handle_real_time_func_code(func)
        _exec_in(code_str,func.__globals__, func.__globals__)
        return func.__globals__[func.__name__+suffix](*args, **kwargs)
    return wrapper



