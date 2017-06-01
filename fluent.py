#!/usr/bin/env python3
# encoding: utf8
# license: ISC (MIT/BSD compatible) https://choosealicense.com/licenses/isc/

# This library is principally created for python 3. However python 2 support may be doable and is welcomed.

import functools
import itertools
import math
import operator
import re
import sys
import types
import typing

__all__ = ['wrap', '_'] # + @public

def wrap(wrapped, *, previous=None, chain=None):
    """Factory method, wraps anything and returns the appropriate Wrapper subclass.
    
    This is the main entry point into the fluent wonderland. Wrap something and 
    everything you call off of that will stay wrapped in the apropriate wrappers.
    
    Use dir to discover the available wrappers.
    
        >>> import fluent; print(dir(fluent))
    
    You can also use fluent as an executable module for shell one offs
    
        >>> python3 -m fluent "lib.sys.stdin.readlines().map($SOMETHING).map(print)"
    
    To see what is available, use:
    
        >>> python3 -m fluent "print(locals().keys())"
    
    For further documentation and development @see https://github.com/dwt/fluent
    """
    if isinstance(wrapped, Wrapper):
        return wrapped
    
    by_type = (
        (types.ModuleType, Module),
        (typing.Text, Text),
        (typing.Mapping, Mapping),
        (typing.AbstractSet, Set),
        (typing.Iterable, Iterable),
        (typing.Callable, Callable),
    )
    
    if wrapped is None and chain is None and previous is not None:
        chain = previous.self.unwrap
    
    decider = wrapped
    if wrapped is None and chain is not None:
        decider = chain
    
    for clazz, wrapper in by_type:
        if isinstance(decider, clazz):
            return wrapper(wrapped, previous=previous, chain=chain)
    
    return Wrapper(wrapped, previous=previous, chain=chain)

wrap.wrap = wrap._ = _ = wrap

def public(something):
    something = protected(something)
    __all__.append(something.__name__)
    return something

def protected(something):
    setattr(wrap, something.__name__, something)
    return something

def wrapped(wrapped_function, additional_result_wrapper=None, self_index=0):
    """
    Using these decorators will take care of unwrapping and rewrapping the target object.
    Thus all following code is written as if the methods live on the wrapped object
    
    Also perfect to adapt free functions as instance methods.
    """
    @functools.wraps(wrapped_function)
    def wrapper(self, *args, **kwargs):
        result = wrapped_function(*args[0:self_index], self.unwrap, *args[self_index:], **kwargs)
        if callable(additional_result_wrapper):
            result = additional_result_wrapper(result)
        return wrap(result, previous=self)
    return wrapper

def unwrapped(wrapped_function):
    """Like wrapped(), but doesn't wrap the result.
    
    Use this to adapt free functions that should not return a wrapped value"""
    @functools.wraps(wrapped_function)
    def forwarder(self, *args, **kwargs):
        return wrapped_function(self.unwrap, *args, **kwargs)
    return forwarder

def wrapped_forward(wrapped_function, additional_result_wrapper=None, self_index=1):
    """Forwards a call to a different object
    
    This makes its method available on the wrapper.
    This specifically models the case where the method forwarded to, 
    takes the current object as its first argument.
    
    This also deals nicely with methods that just live on the wrong object.
    """
    return wrapped(wrapped_function, additional_result_wrapper=additional_result_wrapper, self_index=self_index)

def tupleize(wrapped_function):
    """"Wrap the returned obect in a tuple to force execution of iterators.
    
    Especially usefull to de-iterate methods / function
    """
    @functools.wraps(wrapped_function)
    def wrapper(self, *args, **kwargs):
        return wrap(tuple(wrapped_function(self, *args, **kwargs)), previous=self)
    return wrapper


@protected
class Wrapper(object):
    """Universal wrapper.
    
    This class ensures that all function calls and attribute accesses 
    that can be caught in python will be wrapped with the wrapper again.
    
    This ensures that the fluent interface will persist and everything 
    that is returned is itself able to be chaned from again.
    
    Using this wrapper changes the behaviour of python soure code in quite a big way.
    
    a) If you wrap something, if you want to get at the real object from any 
       function call or attribute access off of that object, you will have to 
       explicitly unwrap it.
    
    b) All returned objects will be enhanced by behaviour that matches the 
       wrapped type. I.e. iterables will gain the collection interface, 
       mappings will gain the mapping interface, strings will gain the 
       string interface, etc.
    """
    
    def __init__(self, wrapped, *, previous, chain):
        assert wrapped is not None or chain is not None, 'Cannot chain off of None'
        self.__wrapped = wrapped
        self.__previous = previous
        self.__chain = chain # REFACT consider rename to __self?
    
    def __str__(self):
        return "fluent.wrap(%s)" % self.unwrap
    
    def __repr__(self):
        return "fluent.wrap(%r)" % (self.unwrap, )
    
    # Proxied methods
    
    __getattr__ = wrapped(getattr)
    __getitem__ = wrapped(operator.getitem)
    
    # Breakouts
    
    @property
    def unwrap(self):
        return self.__wrapped
    _ = unwrap # alias
    
    @property
    def previous(self):
        return self.__previous
    
    @property
    def self(self):
        "Like .unwrap but handles chaining off of methods / functions that return None like SmallTalk does - and returns a wrapper"
        chain = self.unwrap
        if chain is None:
            chain = self.__chain
        return wrap(chain, previous=self)
    
    @property
    def proxy(self):
        """Allow access to shadowed attriutes.
        
        Breakout that allows access to attributes of the wrapped object that are shadowed by 
        methods on the various wrapper classes.
        
        
            >>> class UnfortunateNames(object):
            >>>     def previous(self, *args):
            >>>         return args
            
        This raises TypeError, because Wrapper.previous() shadows UnfortunateNames.previous():
        
            >>> _(UnfortunateNames()).previous('foo')) 
        
        This works as expected:
        
            >>> _(UnfortunateNames()).proxy.previous('foo')._) == ('foo',)
        
        """
        # @public
        class Proxy(object):
            def __init__(self, proxied):
                self.__proxied = proxied
            def __getattr__(self, name):
                return wrap(getattr(self.__proxied.unwrap, name), previous=self.__proxied)
        return Proxy(self)
    
    # Utilities
    
    @wrapped
    def call(self, function, *args, **kwargs):
        "Call function with self as first argument"
        # Different from __call__! Calls function(self, …) instead of self(…)
        return function(self, *args, **kwargs)
    
    setattr = wrapped(setattr)
    getattr = wrapped(getattr)
    hasattr = wrapped(hasattr)
    delattr = wrapped(delattr)
    
    isinstance = wrapped(isinstance)
    issubclass = wrapped(issubclass)
    
    def tee(self, function):
        """Like tee on the shell
        
        Calls the argument function with self, but then discards the result and allows 
        further chaining from self."""
        function(self)
        return self
    
    dir = wrapped(dir)
    vars = wrapped(vars)
    print = wrapped(print)

# REFACT consider to use wrap as the placeholder to have less symbols? Probably not worth it...
virtual_root_module = object()

@protected
class Module(Wrapper):
    """Imports as expressions. Already pre-wrapped.
    
    All attribute accesses to instances of this class are converted to
    an import statement, but as an expression that returns the wrapped imported object.
    
    Example:
    
    >>> lib.sys.stdin.read().map(print)
    
    Is equivalent to
    
    >>> import importlib
    >>> wrap(importlib.import_module('sys').stdin).read().map(print)
    
    But of course without creating the intermediate symbol 'stdin' in the current namespace.
    
    All objects returned from lib are pre-wrapped, so you can chain off of them immediately.
    """
    
    def __getattr__(self, name):
        if hasattr(self.unwrap, name):
            return wrap(getattr(self.unwrap, name))
        
        import importlib
        module = None
        if self.unwrap is virtual_root_module:
            module = importlib.import_module(name)
        else:
            module = importlib.import_module('.'.join((self.unwrap.__name__, name)))
        
        return wrap(module)

lib = Module(virtual_root_module, previous=None, chain=None)
lib.__name__ = 'lib'
public(lib)

@protected
class Callable(Wrapper):
    """Higher order methods for callables."""
    
    def __call__(self, *args, **kwargs):
        """"Call through with a twist.
        
        If one of the args is `wrap` / `_`, then this acts as a shortcut to curry instead"""
        # REFACT consider to drop the auto curry - doesn't look like it is so super usefull
        # REFACT Consider how to expand this so every method in the library supports auto currying
        if wrap in args:
            return self.curry(*args, **kwargs)
        
        result = self.unwrap(*args, **kwargs)
        chain = None if self.previous is None else self.previous.self.unwrap
        return wrap(result, previous=self, chain=chain)
    
    # REFACT rename to partial for consistency with stdlib?
    # REFACT consider if there could be more utility in supporting placeholders for more usecases.
    # examples:
    #   Switching argument order? _._1, _._2 as placeholders with order
    @wrapped
    def curry(self, *curry_args, **curry_kwargs):
        """"Like functools.partial, but with a twist.
        
        If you use `wrap` or `_` as a positional argument, upon the actual call, 
        arguments will be left-filled for those placeholders.
        
        For example:
        
        >>> _(operator.add).curry(_, 'foo')('bar') == 'barfoo'
        """
        placeholder = wrap
        def merge_args(curried_args, args):
            assert curried_args.count(placeholder) == len(args), \
                'Need the right ammount of arguments for the placeholders'
            
            new_args = list(curried_args)
            if placeholder in curried_args:
                index = 0
                for arg in args:
                    index = new_args.index(placeholder, index)
                    new_args[index] = arg
            return new_args
        
        @functools.wraps(self)
        def wrapper(*actual_args, **actual_kwargs):
            return self(
                *merge_args(curry_args, actual_args),
                **dict(curry_kwargs, **actual_kwargs)
            )
        return wrapper
    
    @wrapped
    def compose(self, outer):
        return lambda *args, **kwargs: outer(self(*args, **kwargs))
    # REFACT consider aliasses wrap = chain = cast = compose

@protected
class Iterable(Wrapper):
    """Add iterator methods to any iterable.
    
    Most iterators in python3 return an iterator by default, which is very interesting 
    if you want to build efficient processing pipelines, but not so hot for quick and 
    dirty scripts where you have to wrap the result in a list() or tuple() all the time 
    to actually get at the results (e.g. to print them) or to actually trigger the 
    computation pipeline.
    
    Thus all iterators on this class are by default immediate, i.e. they don't return the 
    iterator but instead consume it immediately and return a tuple. Of course if needed, 
    there is also an i{map,zip,enumerate,...} version for your enjoyment that returns the 
    iterator.
    """
    
    __iter__ = unwrapped(iter)
    
    @wrapped
    def star_call(self, function, *args, **kwargs):
        "Calls function(*self), but allows to prepend args and add kwargs."
        return function(*args, *self, **kwargs)
    
    # This looks like it should be the same as 
    # starcall = wrapped(lambda function, wrapped, *args, **kwargs: function(*wrapped, *args, **kwargs))
    # but it's not. Why?
    
    @wrapped
    def join(self, with_what):
        """"Like str.join, but the other way around. Bohoo!
        
        Also calls str on all elements of the collection before handing 
        it off to str.join as a convenience.
        """
        return with_what.join(map(str, self))
    
    ## Reductors .........................................
    
    len = wrapped(len)
    max = wrapped(max)
    min = wrapped(min)
    sum = wrapped(sum)
    any = wrapped(any)
    all = wrapped(all)
    reduce = wrapped_forward(functools.reduce)
    
    ## Iterators .........................................
    
    imap = wrapped_forward(map)
    map = tupleize(imap)
    
    istar_map = istarmap = wrapped_forward(itertools.starmap)
    star_map = starmap = tupleize(istarmap)
    
    ifilter = wrapped_forward(filter)
    filter = tupleize(ifilter)
    
    ienumerate = wrapped(enumerate)
    enumerate = tupleize(ienumerate)
    
    ireversed = wrapped(reversed)
    reversed = tupleize(ireversed)
    
    isorted = wrapped(sorted)
    sorted = tupleize(isorted)
    
    @wrapped
    def igrouped(self, group_length):
        "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
        return zip(*[iter(self)]*group_length)
    grouped = tupleize(igrouped)
    
    izip = wrapped(zip)
    zip = tupleize(izip)
    
    @wrapped
    def iflatten(self, level=math.inf):
        "Modeled after rubys array.flatten @see http://ruby-doc.org/core-1.9.3/Array.html#method-i-flatten"
        for element in self:
            if level > 0 and isinstance(element, typing.Iterable):
                for subelement in wrap(element).iflatten(level=level-1):
                    yield subelement
            else:
                yield element
        return
    flatten = tupleize(iflatten)
    
    igroupby = wrapped(itertools.groupby)
    def groupby(self, *args, **kwargs):
        # Need an extra wrapping function to consume the deep iterators in time
        result = []
        for key, values in self.igroupby(*args, **kwargs):
            result.append((key, tuple(values)))
        return wrap(tuple(result))
    
    def tee(self, function):
        "This override tries to retain iterators, as a speedup"
        if hasattr(self.unwrap, '__next__'): # iterator
            first, second = itertools.tee(self.unwrap, 2)
            function(wrap(first, previous=self))
            return wrap(second, previous=self)
        else:
            return super().tee(function)

@protected
class Mapping(Iterable):
    """Index into dicts like objects. As JavaScript can."""
    
    def __getattr__(self, name):
        "Support JavaScript like dict item access via attribute access"
        if name in self.unwrap:
            return self[name]
        
        return super().__getattr__(self, name)
    
    # REFACT consider rename to splat_call to differentiate that it does something else tha
    # Callable.star_call
    @wrapped
    def star_call(self, function, *args, **kwargs):
        "Calls function(**self), but allows to add args and set defaults for kwargs."
        return function(*args, **dict(kwargs, **self))

@protected
class Set(Iterable):
    """Fnord"""

# REFACT consider to inherit from Iterable? It's how Python works...
@protected
class Text(Wrapper):
    "Supports most of the regex methods as if they where native str methods"
    
    # Regex Methods ......................................
    
    search = wrapped_forward(re.search)
    match = wrapped_forward(re.match)
    fullmatch = wrapped_forward(re.match)
    split = wrapped_forward(re.split)
    findall = wrapped_forward(re.findall)
    # REFACT consider ifind and find in the spirit of the collection methods?
    finditer = wrapped_forward(re.finditer)
    sub = wrapped_forward(re.sub, self_index=2)
    subn = wrapped_forward(re.subn, self_index=2)

def make_operator(name):
    __op__ = getattr(operator, name)
    @functools.wraps(__op__)
    def wrapper(self, *others):
        return wrap(__op__).curry(wrap, *others).unwrap
    return wrapper

class Each(Wrapper):
    """Create functions from expressions.

    Use `_f.each.foo` to create attrgetters, `_f.each['foo']` to create itemgetters,
    _f.each.call.foo() to create methodcallers or `_f.each == 'foo'` to create callable operators.
    
    Note that all generated functions never wrap their arguments or return values.
    """
    
    for name in dir(operator):
        if not name.startswith('__') or name == '__doc__':
            continue
        locals()[name] = make_operator(name)
    
    def __getattr__(self, name):
        return operator.attrgetter(name)
    
    def __getitem__(self, index):
        return operator.itemgetter(index)
    
    @property
    def call(self):
        class MethodCallerConstructor(object):
            
            _method_name = None
            
            def __getattr__(self, method_name):
                self._method_name = method_name
                return self
            
            def __call__(self, *args, **kwargs):
                assert self._method_name is not None, \
                    'Need to access the method to call first! E.g. _.each.call.method_name(arg1, kwarg="arg2")'
                return operator.methodcaller(self._method_name, *args, **kwargs)
        
        return MethodCallerConstructor()

each_marker = object()
each = Each(each_marker, previous=None, chain=None)
each.__name__ = 'each'
public(each)

# Make the module executable via `python -m fluent "some fluent using python code"`
if __name__ == '__main__':
    assert len(sys.argv) == 2, \
        "Usage: python -m fluent 'some code that can access fluent functions without having to import them'"
    
    exec(sys.argv[1], dict(wrap=wrap, _=wrap, lib=wrap.lib, each=wrap.each))
else:
    wrap.__name__ = __name__
    wrap.module = sys.modules[__name__]
    wrap.__package__ = __package__
    wrap.__all__ = __all__
    sys.modules[__name__] = wrap
