"""A decorator is used to update a function at runtime."""

from __future__ import print_function
import sys
import os
import re
import ast
import linecache
import functools
import traceback
from inspect import getfile, isclass, findsource, getblock

__all__ = ["realtimefunc"]

Decorator = "@realtimefunc"

PY3 = sys.version_info >= (3,)


# The cache

# record, used to record functions decorated by realtimefunc,
# is a dict {filename:{func1, func2}
# refresh, used to to mark functions which source file stat has changed,
# is also a dict {filename:{func1, func2}}

# Note: the filename may be repeated but it doesn't matter.

record = {}
refresh = {}


def _exec(code, filepath, firstlineno, glob, loc=None):
    astNode = ast.parse(code)
    astNode = ast.increment_lineno(astNode, firstlineno)
    code = compile(astNode, filepath, 'exec')
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


def get_func_real_firstlineno(func):
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


def get_source_code(func, func_runtime_name, firstlineno):
    lines = linecache.getlines(func.__code__.co_filename)
    code_lines = getblock(lines[firstlineno:])
    # repalce function name
    code_lines[0] = code_lines[0].replace(func.__name__, func_runtime_name, 1)
    i_indent = code_lines[0].index("def")
    # code indentation
    code_lines = [line[i_indent:] for line in code_lines]
    code = ''.join(code_lines)
    return code


def check_file_stat(filename):
    entry = linecache.cache.get(filename, None)
    change = False
    if not entry:
        change = True
    else:
        size, mtime, _, fullname = entry
        try:
            stat = os.stat(fullname)
        except OSError:
            change = True
            del linecache.cache[filename]
        if size != stat.st_size or mtime != stat.st_mtime:
            change = True
            del linecache.cache[filename]

    if change:
        global refresh
        for f in record[filename]:
            refresh.setdefault(filename, set()).add(f)


def realtimefunc(func):
    # python2 need set __qualname__ by hand
    if not PY3:
        func.__qualname__ = get_qualname(func)
    func_real_name = func.__qualname__.replace('.', '_') + '_realfunc'
    filename = getfile(func)
    filepath = os.path.abspath(filename)
    global record, refresh
    record.setdefault(filename, set()).add(func)
    refresh.setdefault(filename, set()).add(func)


    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        glob = func.__globals__
        check_file_stat(filename)
        if func in refresh[filename]:
            firstlineno = get_func_real_firstlineno(func)
            code_str = get_source_code(func, func_real_name, firstlineno)
            _exec(code_str, filepath, firstlineno, glob)
            refresh[filename].remove(func)
        func_realtime = glob[func_real_name]
        return func_realtime(*args, **kwargs)

    return wrapper

