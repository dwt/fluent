#!/usr/bin/env python3
# encoding: utf8
# license: ISC (MIT/BSD compatible) https://choosealicense.com/licenses/isc/

# This library is principally created for python 3. However python 2 support may be doable and is welcomed.


"""
To use this module just import it with a short custom name. I recommend:

    >>> import fluentpy as _ # for scripts / projects that don't use gettext
    >>> import fluentpy as _f # for everything else

If you want / need this to be less magical, you can import the main wrapper normally

    >>> from fluentpy import wrap # or `_`, if you're not using gettext

Then to use the module, wrap any value and start chaining off of it. To get started try this:

    $ python3 -m fluentpy '_(_).dir().print()'
    $ python3 -m fluentpy '_(_).help()'

This is incidentally the second way to use this module, as a helper that makes it easier to 
write short fast shell filters in python.

    $ echo "foo\nbar\nbaz" | python3 -m fluentpy "lib.sys.stdin.readlines().map(each.call.upper()).map(print)"

Try to rewrite that in classical python (as a one line shell filter) and see which version spells out what happens in 
which order more clearly.

For further documentation and development see this documentation or the source at https://github.com/dwt/fluent
"""

from fluentpy.wrapper import __all__, __api__, _wrap_alternatives

import fluentpy.wrapper as wrapper
for name in __all__ + __api__:
    locals()[name] = getattr(wrapper, name)
del name
# del wrapper

# Make the module executable via `python -m fluentpy "some fluent using python code"`

import functools, sys
@functools.wraps(wrap)
def executable_module(*args, **kwargs): return wrap(*args, **kwargs)
executable_module.__name__ = __name__ + '.' + wrap.__name__
executable_module.module = sys.modules[__name__]
executable_module.__package__ = __package__
executable_module.__all__ = __all__
executable_module.__api__ = __api__
executable_module.__file__ = __file__
executable_module.__doc__ = __doc__
executable_module.__path__ = __path__
_wrap_alternatives.append(executable_module)
sys.modules[__name__] = executable_module
# _wrapper_is_sealed = True
