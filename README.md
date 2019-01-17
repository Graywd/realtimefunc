# realtimefunc
A decorator is used to update a function at runtime to easy correct code in development.

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

### WARNING
Code that below the decorated function could not map to the correct line anymore.

### TODO
- [x] beautify stack info
- [x] support log
- [x] cache
- [ ] support `super()`
- [ ] solve warning mentioned
