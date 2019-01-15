# realtimefunc
A decorator is used to update a function at runtime.

### install
```
pip install realtimefunc
```

### usage
```
from realtimefunc import realtimefunc

@coroutine
@realtimefunc
def test():
    # function body
```

### NOTE
`super()` is not allowed while `super(kls, obj)` is ok.

### TODO
- [x] beautify stack info
- [x] support log
- [x] cache
- [ ] support `super()`
