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

Then to use the module, wrap any value and start chaining off of it. To get started 
lets try to inrospect `fluentpy` using its own fluent interface::

    $ python3 -m fluentpy '_(_).dir().print()'
    $ python3 -m fluentpy '_(_).help()'

This is incidentally the second way to use this module, as a helper that makes it easier to 
write short shell filters quickly in python.::

    $ echo "foo\\nbar\\nbaz" \\
        | python3 -m fluentpy "lib.sys.stdin.readlines().map(each.call.upper()).map(print)"

Try to rewrite that in classical python (as a one line shell filter) and see which version spells out what happens in 
which order more clearly.

For further documentation and development see this documentation or the source at https://github.com/dwt/fluent
"""

import fluentpy.wrapper

# Make the module executable via `python -m fluentpy "some fluent using Python code"`

import functools, sys
# REFACT What would be the best way not to cache all the attributes of fluentpy.wrapperr with functools.wraps
@functools.wraps(fluentpy.wrapper.wrap)
def executable_module(*args, **kwargs): return fluentpy.wrapper.wrap(*args, **kwargs)
# I'ts important that this is not only 'fluent', or sphinx autoapi will try to import and document all submodules
executable_module.__name__ = __name__ + '.' + fluentpy.wrapper.wrap.__name__
executable_module.module = sys.modules[__name__]
executable_module.__package__ = __package__
executable_module.__all__ = fluentpy.wrapper.__all__
executable_module.__api__ = fluentpy.wrapper.__api__
executable_module.__file__ = __file__
executable_module.__doc__ = __doc__
executable_module.__path__ = __path__
# REFACT is there a way to formulate this so that reloading the module doesn't break it?
# That would probably mean recognizing all module wrappers by some of their attributes instead of by identity
fluentpy.wrapper._wrap_alternatives.append(executable_module)
sys.modules[__name__] = executable_module
del executable_module

# _wrapper_is_sealed = True
