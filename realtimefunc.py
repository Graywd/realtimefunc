"""A decorator is used to update a function at runtime."""

from __future__ import print_function
import sys
import os
import re
import linecache
import functools
import traceback
from inspect import isclass, findsource, getblock

Decorator = "@realtimefunc"

# referenced from tornado util.py
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


def _findclass(func):
    cls = sys.modules.get(func.__module__)
    if cls is None:
        return None
    for name in func.__qualname__.split('.')[:-1]:
        cls = getattr(cls, name)
    if not isclass(cls):
        return None
    return cls


def get_qualname(func):
    '''return qualname by look through the call stack.'''
    qualname = []
    stacks = traceback.extract_stack(f=None)
    begin_flag = False
    for stack in stacks[::-1]:
        if stack[3].strip() == Decorator:
            qualname.append(func.__name__)
            begin_flag = True
        if stack[2] == '<module>':
            break
        if begin_flag:
            qualname.append(stack[2])
    return '.'.join(qualname[::-1])


def print_exception(etype, value, frames, file=None, chain=True):
    '''print exception with traceback.'''
    if file is None:
        file = sys.stderr
    if frames:
        print("Traceback (most recent call last):\n", file=file, end="")
        traceback.print_list(frames, file)
    lines = traceback.format_exception_only(etype, value)
    for line in lines:
        print(line, file=file, end="")


def raise_exc_info(func, firstlineno, func_runtime_name):
    '''raise exe info and map <string> location to corresponding file location that func defined.'''
    exc_type, value, tb = sys.exc_info()
    frames = traceback.extract_tb(tb)
    if PY3:
        for frame in frames:
            if frame.name == func_runtime_name and frame.filename == '<string>':
                frame.name = func.__name__
                frame.filename = os.path.normcase(os.path.abspath(func.__code__.co_filename))
                frame.lineno += firstlineno
    else:
        # frams = [(filename, lineno, name, line)), ...]
        for i, frame in enumerate(frames):
            if frame[2] == func_runtime_name and frame[0] == '<string>':
                frames[i] = (
                    os.path.normcase(os.path.abspath(func.__code__.co_filename)),
                    frame[1] + firstlineno,
                    func.__name__,
                    frame[3],
                )
    print_exception(exc_type, value, frames)


def correct_func_co_firstlineno(func):
    '''correct co_firstlineno when some change happen around func'''
    start_lineno = 0
    lines = linecache.getlines(func.__code__.co_filename)
    cls = _findclass(func)
    if cls:
        lines, lnum = findsource(cls)
        lines = getblock(lines[lnum:])
        start_lineno = lnum

    #  referenced from inspect _findclass
    pat = re.compile(r'^(\s*)def\s*' + func.__name__ + r'\b')
    candidates = []
    for i in range(len(lines)):
        match = pat.match(lines[i])
        if match:
            # if it's at toplevel, it's already the best one
            if lines[i][0] == 'd':
                return (i + start_lineno)
            # else add whitespace to candidate list
            candidates.append((match.group(1), i))
    if candidates:
        # this will sort by whitespace, and by line number,
        # less whitespace first
        candidates.sort()
        return start_lineno + candidates[0][1]
    else:
        raise OSError('could not find function definition')


def _handle_real_time_func_code(func, func_runtime_name, firstlineno):
    '''handle the <string> code that used to define a memory function.'''
    lines = linecache.getlines(func.__code__.co_filename)
    code_lines = getblock(lines[firstlineno:])
    # repalce function name
    code_lines[0] = code_lines[0].replace(func.__name__, func_runtime_name, 1)
    i_indent = code_lines[0].index("def")
    # code indentation
    code_lines = [line[i_indent:] for line in code_lines]
    code = ''.join(code_lines)
    return code


def realtimefunc(func):
    # python2 need set __qualname__ by hand
    if not PY3:
        func.__qualname__ = get_qualname(func)
    func_runtime_name = func.__qualname__.replace('.', '_') + '_runtime'

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # inspect use linecache to do file cache, so do checkcache first
        linecache.checkcache(func.__code__.co_filename)
        firstlineno = correct_func_co_firstlineno(func)
        code_str = _handle_real_time_func_code(func, func_runtime_name, firstlineno)
        _exec_in(code_str, func.__globals__)
        try:
            return func.__globals__[func_runtime_name](*args, **kwargs)
        except Exception:
            raise_exc_info(func, firstlineno, func_runtime_name)

    return wrapper
