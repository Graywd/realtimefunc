# realtimefunc
A decorator is used to update a function at runtime.

### usage
```
from /path/to/realtimefunc import realtimefunc

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
