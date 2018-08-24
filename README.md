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

#### note

If you are work with an old tornado version,  change the keyword `return` to `yield`  in realtimefunc.py where the place has been commented.

