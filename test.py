import sys
import functools
import traceback

PY3 = sys.version_info >= (3,)

Decorator = "@dec"

def get_qualname(func):
    qualname= []
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

def dec(func):
    if not PY3:
        func.__qualname__ = get_qualname(func)
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        print(func.__qualname__)
        func(*args, **kwargs)
    return wrap

@dec
def test():
    pass

class A(object):
    class B(dict):
        @dec
        def get(self):
            pass
    @dec
    def get(self):
        print("get")

a = A()
a.get()
b = A.B()
b.get()
