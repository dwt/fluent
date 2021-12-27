# Integration with other libraries

Integration of other libraries or just your own custom functions, typically involves `.call()`.

Lets take the shell integration library [sh](https://pypi.org/project/sh/) as an example. This library adds a function like interface to shell callouts like this: `ifconfig()`, `sed('s/^/>> /', _in='foo\nbar\baz')`. This is problematic, as function call chains want callables, that get one input argument - in our case stdin, or the `_in` parameter. To support this library, you can manually curry what you need, or create a small adapter object, that does this currying:

```python
#!/usr/bin/env python

import typing
import sh

import fluentpy as _

class SHWrapper(object):
    def __getattr__(self, command):
        
        def _prepare_stdin(stdin):
            if isinstance(stdin, (typing.Text, sh.RunningCommand)):
                return stdin  # use immediately
            elif isinstance(stdin, typing.Iterable):
                return _(stdin).map(str).join('\n')._
            else:
                return str(stdin)  # just assume the caller wants to process it as string
        
        def command_wrapper(*args, **kwargs):
            def command_with_arguments_wrapper(stdin):
                return getattr(sh, command)(*args, **kwargs, _in=_prepare_stdin(stdin))
            return command_with_arguments_wrapper
        
        return command_wrapper

pipe = SHWrapper()

_(range(10)).call(pipe.sed('s/^/>> /')).call(pipe.sort('-r')).print()
```

This library is wrapped in the `SHWrapper`object, that a) adapting the way stdin is handled, to adapt various input types to serve as `stdin`, as well as b) adapt the interface to create simple callables in two steps via currying, instead of requiring stdin in the same call that defines the arguments.

With that `.call()` can be used, to insert sh callouts in call chains:

```python
_(range(10)).call(pipe.sed('s/^/>> /')).call(pipe.sort('-r')).print()
```

So to summarize: If you want to adapt your own libraries to serve inside of call chains:

* If the interface is allready plain callables, you are in luck, just use them.
* If not, you might need to adapt the interface of the library to single input functions.
