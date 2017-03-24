#!/usr/bin/env python3
# encoding: utf8
# license: ISC (MIT/BSD compatible) https://choosealicense.com/licenses/isc/

# This library is principally created for python 3. However python 2 support may be doable and is welcomed.

"""Use python in a more object oriented, saner and shorter way.

# WARNING
First: A word of warning. This library is an experiment. It is based on a wrapper that aggressively 
wraps anything it comes in contact with and tries to stay invisible from then on (apart from adding methods).
However this means that this library is probably quite unsuitable for use in bigger projects. Why? 
Because the wrapper will spread in your runtime image like a virus, 'infecting' more and more objects 
causing strange side effects. That being said, this library is perfect for short scripts and especially 
'one of' shell commands. Use it's power wisely!

# Introduction

This library is heavily inspired by jQuery and underscore / lodash in the javascript world. Or you 
could say that it is inspired by SmallTalk and in extension Ruby and how they deal with collections 
and how to work with them.

In JS the problem is that the standard library sucks very badly and is missing many of the 
most important convenience methods. Python is better in this regard, in that it has (almost) all 
those methods available somewhere. BUT: quite a lot of them are available on the wrong object or 
are free methods where they really should be methods. Examples: `str.join` really should be on iterable.
`map`, `zip`, `filter` should really be on iterable. Part of this problem comes from the design 
choice of the python language, to provide a strange kind of minimal duck typing interface with the __*__ 
methods that the free methods like `map`, `zip`, `filter` then use. This however has the unfortunate
side effect in that writing python code using these methods often requires the reader to mentally skip 
back and forth in a line to parse what it does. While this is not too bad for simple usage of these 
functions, it becomes a nightmare if longer statements are built up from them.

Don't believe me? Try to parse this simple example as fast as you can:

>>> map(print, map(str.upper, sys.stdin.read().split('\n')))

How many backtrackings did you have to do? To me this code means, finding out that it starts in the 
middle at `sys.stdin.read().split('\n')`, then I have to backtrack to `map(str.upper, …)`, then to 
`map(print, …)`. Then while writing, I have to make sure that the number of parens at the end are 
correct, which is something I usually have to use editor support for as it's quite hard to accurately 
identify where the matching paren is.

The problem with this? This is hard! Hard to write, as it doesn't follow the way I think about this 
statement. Literally, this means I usually write these statements from the inside out and wrap them
using my editor as I write them. As demonstrated above, it's also hard to read - requireing quite a 
bit of backtracking.

So, what's the problem you say? Just don't do it, it's not pythonic you say! Well, Python has two 
main workarounds available for this mess. One is to use list comprehension / generator 
statements like this:

>>> [print(line.upper()) for line in sys.stdin.read().split('\n')]

This is clearly better. Now you only have to skip back and forth once instead of twice Yay! Win! 
To me that is not a good workaround. Sure it's nice to easily be able to create generators this 
way, but it still requires of me to find where the statement starts and to backtrack to the beginning 
to see what is happening. Oh, but they support filtering too!

>>> [print(line.upper()) for line in sys.stdin.read().split('\n') if line.upper().startswith('FNORD')]

Well, this is little better. For one thing, this doesn't solve the backtracking problem, but more 
importantly, if the filtering has to be done on the processed version (here artificially on 
`line.upper().startswith()`) then the operation has to be applied twice - which sucks because you have to write it twice, but also because it is computed twice.

The solution? Nest them!

[print(line) for line in (line.upper() for line in sys.stdin.read().split('\n')) if line.startswith('FNORD')]

Do you start seing the problem?

Compare it to this:

>>> for line in sys.stdin.read().split('\n'):
>>>     uppercased = line.upper()
>>>     if uppercased.startswith('FNORD'):
>>>         print(uppercased)

Almost all my complaints are gone. It reads and writes almost completely in order it is computed.
Easy to read, easy to write - but one drawback. It's not an expression - it's a bunch of statements.
Which means that it's not easily combinable and abstractable with higher order methods or generators. 
Also (to complain on a high level), you had to invent two variable names `line` and `uppercased`. 
While that is not bad, especially if they explain what is going on - in this case it's not really 
helping _and_ (drummroll) it requires some backtracking and buildup of mental state to read. Oh well.

Of course you can use explaining variables to untangle the mess of using higher order functions too:

Consider this code:

>>> cross_product_of_dependency_labels = \
>>>     set(map(frozenset, itertools.product(*map(attrgetter('_labels'), dependencies))))

That certainly is hard to read (and write). Pulling out explaining variables, makes it better. Like so:

>>> labels = map(attrgetter('_labels'), dependencies)
>>> cross_product_of_dependency_labels = set(map(frozenset, itertools.product(*labels)))

Better, but still hard to read. Sure, those explaining variables are nice and sometimes 
essential to understand the code. - but it does take up space in lines, and space in my head 
while parsing this code. The question would be - is this really easier to read than something 
like this?

>>> cross_product_of_dependency_labels = _(dependencies) \
>>>     .map(_.each._labels) \
>>>     .star_call(itertools.product) \
>>>     .map(frozenset) \
>>>     .call(set)

Sure you are not used to this at first, but consider the advantages. The intermediate variable 
names are abstracted away - the data flows through the methods completely naturally. No jumping 
back and forth to parse this at all. It just reads and writes exactly in the order it is computed.
What I think that I want to accomplish, I can write down directly in order. Oh, and I don't have 
to keep track of extra closing parantheses at the end of the expression.

So what is the essence of all of this?

Python is an object oriented language - but it doesn't really use what object orientation has tought 
us about how we can work with collections and higher order methods in the languages that came before it
(especially SmallTalk, but more recently also Ruby). Why can't I make those beautiful fluent call chains 
that SmallTalk could do 20 years ago in Python today?

Well, now you can.

# Features

To enable this style of coding this library has some features that might not be so obvious at first.

## Aggressive (specialized) wrapping

The most important entry point for this library is the function `wrap` or the perhaps preferrable and 
shorter alias `_`:

>>> _(something)
>>> # or
>>> wrap(something)

`wrap` is a factory function that returns a subclass of Wrapper, the basic and main object of this library.

This does two things: First it ensures that every attribute access, item access or method call off of 
the wrapped object will also return a wrapped object. This means that once you wrap something, unless 
you unwrap it explicitly via `.unwrap` or `._` it stays wrapped - pretty much no matter what you do 
with it. The second thing this does is that it returns a subclass of Wrapper that has a specialized set 
of methods depending on the type of what is wrapped. I envision this to expand in the future, but right 
now the most usefull wrappers are: Iterable, where we add all the python collection functions (map, 
filter, zip, reduce, …) as well as a good batch of methods from itertools and a few extras for good 
measure. Callable, where we add `.curry()` and `.compose()` and Text, where most of the regex methods 
are added.

## Imports as expressions

Import statements are (ahem) statements in python. This is fine, but can be really annoying at times.
Consider this shell text filter written in python:

$ curl -sL 'https://www.iblocklist.com/lists.php' | egrep -A1 'star_[345]' | python3 -c "import sys, re; from xml.sax.saxutils import unescape; print('\n'.join(map(unescape, re.findall(r'value=\'(.*)\'', sys.stdin.read()))))" 

Sure it has all the backtracking problems I talked about already. Using fluent this would already be much better.

$ curl -sL 'https://www.iblocklist.com/lists.php' \
    | egrep -A1 'star_[345]' \
    | python3 -c "from fluent import *; import sys, re; from xml.sax.saxutils import unescape; _(sys.stdin.read()).findall(r'value=\'(.*)\'').map(unescape).map(print)"

But this still leaves the problem that it has to start with this fluff 

`from fluent import *; import sys, re; from xml.sax.saxutils import unescape;`

This doesn't really do anything to make it easier to read and write and is almost half the characters 
it took to achieve the wanted effect. Wouldn't it be nice if you could have 
some kind of object (lets call it `lib` for lack of a better word), where you could just access the whole 
python library via attribute access and let it's machinery handle importing behind the scenes?

Like this:

$ curl -sL 'https://www.iblocklist.com/lists.php' | egrep -A1 'star_[345]' | python3 -m fluent "lib.sys.stdin.read().findall(r'value=\'(.*)\'').map(lib.xml.sax.saxutils.unescape).map(print)"

How's that for reading and writing if all the imports are inlined? Oh, and of course everything imported 
via `lib` comes already pre-wrapped, so your code becomes even shorter.

More formally:The `lib` object, which is a wrapper around the python import machinery, allows to import 
anything that is accessible by import to be imported as an expression for inline use.

So instead of

>>> import sys
>>> input = sys.stdin.read()

You can do

>>> input = lib.sys.stdin.read()

As a bonus, everything imported via lib is already pre-wrapped, so you can chain off of it immediately.

`lib` is also available on `_` which is itself just an alias for `wrap`. This is usefull if you want 
to import fewer symbols from fluent or want to import the library under a custom name

>>> from fluent import _ # alias for wrap
>>> _.lib.sys.stdin.split('\n').map(str.upper).map(print)

>>> from fluent import _ as fluent # alias for wrap
>>> fluent.lib.sys.stdin.split('\n').map(str.upper).map(print)

Not sure if that is so super usefull though, as you could also just do:

>>> import fluent
>>> fluent.lib.sys.stdin.split('\n').map(str.upper).map(print)

## Generating lambda's from expressions

`lambda` is great - it's often exactly what the doctor ordered. But it can also be a bit annyoing
 if you have to write it down everytime you just want to get an attribute or call a method on every 
object in a collection.

>>> _([dict(fnord='foo'), dict(fnord='bar')]).map(lambda each: each['fnord']) == ['foo', 'bar]
>>> class Foo(object):
>>>     attr = 'attrvalue'
>>>     def method(self, arg): return 'method+'+arg
>>> _([Foo(), Foo()]).map(lambda each: each.attr) == ['attrvalue', 'attrvalue']
>>> _([Foo(), Foo()]).map(lambda each: each.method('arg')) == ['method+arg', 'method+arg']

Sure it works, but wouldn't it be nice if we could save a variable and do this a bit shorter? 
I mean, python does have attrgetter, itemgetter and methodcaller - they are just a bit 
inconvenient to use:

>>> from operator import itemgetter, attrgetter, methodcaller
>>> _([dict(fnord='foo'), dict(fnord='bar')]).map(itemgetter('fnord')) == ['foo', 'bar]
>>> class Foo(object):
>>>     attr = 'attrvalue'
>>>     def method(self, arg): return 'method+'+arg
>>> _([Foo(), Foo()]).map(attrgetter(attr)) == ['attrvalue', 'attrvalue']
>>> _([Foo(), Foo()]).map(methodcaller(method, 'arg')) == ['method+arg', 'method+arg']

So there is an object `_.each` that just exposes a bit of syntactic shugar for these 
(and a few operators). Basically, everything you do to `_.each` it will do to each object
in the collection:

>>> _([1,2,3]).map(_.each + 3) == [4,5,6]
>>> _([1,2,3]).filter(_.each < 3) == [1,2]
>>> _([1,2,3]).map(- _.each) == [-1,-2,-3]
>>> _([dict(fnord='foo'), dict(fnord='bar')]).map(_.each['fnord']) == ['foo', 'bar]
>>> class Foo(object):
>>>     attr = 'attrvalue'
>>>     def method(self, arg): return 'method+'+arg
>>> _([Foo(), Foo()]).map(_.each.attr) == ['attrvalue', 'attrvalue']
>>> _([Foo(), Foo()]).map(_.each.call.method('arg')) == ['method+arg', 'method+arg']

Yeah I know `_.each.call.*()` is crude - but I haven't found a good syntax to get rid of 
the .call yet. Feedback welcome.

## Chaining off of methods that return None

A major nuissance for using fluent interfaces are methods that return None. Now this is mostly 
a feature of python, where methods that don't have a return statement return None.
While this is way better than e.g. Ruby where that will just return the value of the last 
expression - which means objects constantly leak internals, it is very annoying if you want to 
chain off of one of these method calls. Fear not though, fluent has you covered. :) 
Fluent wrapped objects will behave more like SmallTalk objects, in that they pretend
that every method that returns None actually returned self - thus allowing chaining. So this just works:

>>> _([3,2,1]).sort().reverse().call(print)

Even though both sort() and reverse() return None

Of course, if you unwrap at any point with `.unwrap` or `._` you will get the true return value of `None`.

# Famous Last Words

This library tries to do a little of what underscore does for javascript. Just provide the missing glue to make the standard library nicer and easier to use - especially for short oneliners or short script. Have fun!

While I know that this is not something you want to use in big projects (see warning at the beginning) 
I envision this to be very usefull in quick python scripts and shell one liner filters, where python was previously just that little bit too hard to use, that 'overflowed the barrel' and prevented you from doing so.
"""

"""Future Ideas:

# TODO consider numeric type to do stuff like wrap(3).times(...)
    or wrap([1,2,3]).call(len).times(yank_me)

Rework _.each.call.foo(bar) so 'call' is no longer a used-up symbol on each.
Also _.each.call.method(...) has a somewhat different meaning as the .call method on callable
could _.each.method(_, ...) work when auto currying is enabled?

Rework fluent so explicit unwrapping is required to do anythign with wrapped objects. 
(Basically calling ._ at the end)
The idea here is that this would likely enable the library to be used in big / bigger 
projects as it looses it's virus like qualities.
* Maybe this is best done as a separate import?
* This would also be a chance to consider always using the iterator versions of 
  all the collection methods under their original name and automatically unpacking 
  / triggering the iteration on ._? Not sure that's a great idea, as getting the 
  iterator to abstract over it is a) great and b) triggering the iteration is also 
  hard see e.g. groupby.
* This would require carefull analysis where wrapped objects are handed out as arguments
  to called methods e.g. .tee(). Also requires __repr__ and __str__ implementations that
  make sense.

Roundable (for all numeric needs?)
    round, times, repeat, if_true, if_false, else_

if_true, etc. are pretty much like conditional versions of .tee() I guess.

.if_true(function_to_call).else_(other_function_to_call)
"""

# REFACT rename wrap -> fluent? perhaps as an alias?
__all__ = [
    'wrap', # generic wrapper factory that returns the appropriate subclass in this package according to what is wrapped
    '_', # _ is an alias for wrap
    'lib', # wrapper for python import machinery, access every importable package / function directly on this via attribute access
]

import typing
import re
import math
import types
import functools
import itertools
import operator
import collections.abc

def wrap(wrapped, *, previous=None, chain=None):
    """Factory method, wraps anything and returns the appropriate Wrapper subclass.
    
    This is the main entry point into the fluent wonderland. Wrap something and 
    everything you call off of that will stay wrapped in the apropriate wrappers.
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
        chain = previous.chain
    
    decider = wrapped
    if wrapped is None and chain is not None:
        decider = chain
    
    for clazz, wrapper in by_type:
        if isinstance(decider, clazz):
            return wrapper(wrapped, previous=previous, chain=chain)
    
    return Wrapper(wrapped, previous=previous, chain=chain)

# sadly _ is pretty much the only valid python identifier that is sombolic and easy to type. Unicode would also be a candidate, but hard to type $, § like in js cannot be used
_ = wrap

def wrapped(wrapped_function, additional_result_wrapper=None, self_index=0):
    """
    Using these decorators will take care of unwrapping and rewrapping the target object.
    Thus all following code is written as if the methods live on the wrapped object
    
    Also perfect to adapt free functions as instance methods.
    """
    @functools.wraps(wrapped_function)
    def wrapper(self, *args, **kwargs):
        result = wrapped_function(*args[0:self_index], self.chain, *args[self_index:], **kwargs)
        if callable(additional_result_wrapper):
            result = additional_result_wrapper(result)
        return wrap(result, previous=self)
    return wrapper

def unwrapped(wrapped_function):
    """Like wrapped(), but doesn't wrap the result.
    
    Use this to adapt free functions that should not return a wrapped value"""
    @functools.wraps(wrapped_function)
    def forwarder(self, *args, **kwargs):
        return wrapped_function(self.chain, *args, **kwargs)
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
        self.__chain = chain
    
    # Proxied methods
    
    __getattr__ = wrapped(getattr)
    __getitem__ = wrapped(operator.getitem)
    
    def __str__(self):
        return "fluent.wrap(%s)" % self.chain
    
    def __repr__(self):
        return "fluent.wrap(%r)" % self.chain
    
    # REFACT consider wether I want to support all other operators too or wether explicit 
    # unwrapping is actually a better thing
    __eq__ = unwrapped(operator.eq)
    
    # Breakouts
    
    @property
    def unwrap(self):
        return self.__wrapped
    _ = unwrap # alias
    
    @property
    def previous(self):
        return self.__previous
    
    @property
    def chain(self):
        "Like .unwrap but handles chaining off of methods / functions that return None like SmallTalk does"
        if self.unwrap is not None:
            return self.unwrap
        return self.__chain
    
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

# REFACT consider to use wrap as the placeholder to have less symbols? Probably not worth it...
virtual_root_module = object()
class Module(Wrapper):
    """Importer shortcut.
    
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
        if hasattr(self.chain, name):
            return wrap(getattr(self.chain, name))
        
        import importlib
        module = None
        if self.chain is virtual_root_module:
            module = importlib.import_module(name)
        else:
            module = importlib.import_module('.'.join((self.chain.__name__, name)))
        
        return wrap(module)

wrap.lib = lib = Module(virtual_root_module, previous=None, chain=None)

class Callable(Wrapper):
    
    def __call__(self, *args, **kwargs):
        """"Call through with a twist.
        
        If one of the args is `wrap` / `_`, then this acts as a shortcut to curry instead"""
        # REFACT consider to drop the auto curry - doesn't look like it is so super usefull
        # REFACT Consider how to expand this so every method in the library supports auto currying
        if wrap in args:
            return self.curry(*args, **kwargs)
        
        result = self.chain(*args, **kwargs)
        chain = None if self.previous is None else self.previous.chain
        return wrap(result, previous=self, chain=chain)
    
    # REFACT rename to partial for consistency with stdlib?
    # REFACT consider if there could be more utility in supporting placeholders for more usecases.
    # examples:
    #   Switching argument order?
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
                for subelement in _(element).iflatten(level=level-1):
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
        if hasattr(self.chain, '__next__'): # iterator
            first, second = itertools.tee(self.chain, 2)
            function(wrap(first, previous=self))
            return wrap(second, previous=self)
        else:
            return super().tee(function)

class Mapping(Iterable):
    
    def __getattr__(self, name):
        "Support JavaScript like dict item access via attribute access"
        if name in self.chain:
            return self[name]
        
        return super().__getattr__(self, name)
        
    @wrapped
    def star_call(self, function, *args, **kwargs):
        "Calls function(**self), but allows to add args and set defaults for kwargs."
        return function(*args, **dict(kwargs, **self))

class Set(Iterable): pass

# REFACT consider to inherit from Iterable? It's how Python works...
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
        return wrap(__op__).curry(wrap, *others)
    return wrapper

class Each(Wrapper):
    
    for name in dir(operator):
        if not name.startswith('__'):
            continue
        locals()[name] = make_operator(name)
    
    @wrapped
    def __getattr__(self, name):
        return operator.attrgetter(name)
    
    @wrapped
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
                return wrap(operator.methodcaller(self._method_name, *args, **kwargs))
        
        return MethodCallerConstructor()
    
each_marker = object()
wrap.each = Each(each_marker, previous=None, chain=None)

import unittest
from pyexpect import expect
import pytest

class FluentTest(unittest.TestCase): pass

class WrapperTest(FluentTest):
    
    def test_should_not_wrap_a_wrapper_again(self):
        wrapped = _(4)
        expect(type(_(wrapped).unwrap)) == int
    
    def test_should_provide_usefull_str_and_repr_output(self):
        expect(repr(_('foo'))) == "fluent.wrap('foo')"
        expect(str(_('foo'))) == "fluent.wrap(foo)"
    
    def test_should_wrap_callables(self):
        counter = [0]
        def foo(): counter[0] += 1
        expect(_(foo)).is_instance(Wrapper)
        _(foo)()
        expect(counter[0]) == 1
    
    def test_should_wrap_attribute_accesses(self):
        class Foo(): bar = 'baz'
        expect(_(Foo()).bar).is_instance(Wrapper)
    
    def test_should_wrap_item_accesses(self):
        expect(_(dict(foo='bar'))['foo']).is_instance(Wrapper)
    
    def test_should_error_when_accessing_missing_attribute(self):
        class Foo(): pass
        expect(lambda: _(Foo().missing)).to_raise(AttributeError)
    
    def test_should_explictly_unwrap(self):
        foo = 1
        expect(_(foo).unwrap).is_(foo)
    
    def test_should_wrap_according_to_returned_type(self):
        expect(_('foo')).is_instance(Text)
        expect(_([])).is_instance(Iterable)
        expect(_(iter([]))).is_instance(Iterable)
        expect(_({})).is_instance(Mapping)
        expect(_({1})).is_instance(Set)
        
        expect(_(lambda: None)).is_instance(Callable)
        class CallMe(object):
            def __call__(self): pass
        expect(_(CallMe())).is_instance(Callable)
        
        expect(_(object())).is_instance(Wrapper)
    
    def test_should_remember_call_chain(self):
        def foo(): return 'bar'
        expect(_(foo)().unwrap) == 'bar'
        expect(_(foo)().previous.unwrap) == foo
    
    def test_should_delegate_equality_test_to_wrapped_instance(self):
        # REFACT makes these tests much nicer - but probably has to go to make this library less virus like
        expect(_(1)) == 1
        expect(_('42')) == '42'
        callme = lambda: None
        expect(_(callme)) == callme
    
    def test_hasattr_getattr_setattr_delattr(self):
        expect(_((1,2)).hasattr('len'))
        expect(_('foo').getattr('__len__')()) == 3
        class Attr(object):
            def __init__(self): self.foo = 'bar'
        expect(_(Attr()).setattr('foo', 'baz').foo) == 'baz'
        
        expect(_(Attr()).delattr('foo').unwrap) == None
        expect(_(Attr()).delattr('foo').chain).isinstance(Attr)
        expect(_(Attr()).delattr('foo').vars()) == {}
    
    def test_isinstance_issubclass(self):
        expect(_('foo').isinstance(str)) == True
        expect(_('foo').isinstance(int)) == False
        expect(_(str).issubclass(object)) == True
        expect(_(str).issubclass(str)) == True
        expect(_(str).issubclass(int)) == False
    
    def test_dir_vars(self):
        expect(_(object()).dir()).contains('__class__', '__init__', '__eq__')
        class Foo(object): pass
        foo = Foo()
        foo.bar = 'baz'
        expect(_(foo).vars()) == {'bar': 'baz'}

class CallableTest(FluentTest):
    
    def test_call(self):
        expect(_(lambda: 3)()) == 3
        expect(_(lambda *x: x)(1,2,3)) == (1,2,3)
        expect(_(lambda x=3: x)()) == 3
        expect(_(lambda x=3: x)(x=4)) == 4
        expect(_(lambda x=3: x)(4)) == 4
    
    def test_star_call(self):
        expect(wrap([1,2,3]).star_call(str.format, '{} - {} : {}')) == '1 - 2 : 3'
    
    def test_should_call_callable_with_wrapped_as_first_argument(self):
        expect(_([1,2,3]).call(min)) == 1
        expect(_([1,2,3]).call(min)) == 1
        expect(_('foo').call(str.upper)) == 'FOO'
        expect(_('foo').call(str.upper)) == 'FOO'
    
    def test_tee_breakout_a_function_with_side_effects_and_disregard_return_value(self):
        side_effect = {}
        def observer(a_list): side_effect['tee'] = a_list.join('-')
        expect(_([1,2,3]).tee(observer)) == [1,2,3]
        expect(side_effect['tee']) == '1-2-3'
        
        def fnording(ignored): return 'fnord'
        expect(_([1,2,3]).tee(fnording)) == [1,2,3]
    
    def test_curry(self):
        expect(_(lambda x, y: x*y).curry(2, 3)()) == 6
        expect(_(lambda x=1, y=2: x*y).curry(x=3)()) == 6
    
    def test_auto_currying(self):
        expect(_(lambda x: x + 3)(_)(3)) == 6
        expect(_(lambda x, y: x + y)(_, 'foo')('bar')) == 'barfoo'
        expect(_(lambda x, y: x + y)('foo', _)('bar')) == 'foobar'
        
    def test_curry_should_support_placeholders_to_curry_later_positional_arguments(self):
        expect(_(operator.add).curry(_, 'foo')('bar')) == 'barfoo'
        expect(_(lambda x, y, z: x + y + z).curry(_, 'baz', _)('foo', 'bar')) == 'foobazbar'
        # expect(_(operator.add).curry(_2, _1)('foo', 'bar')) == 'barfoo'
    
    def test_compose_cast_wraps_chain(self):
        expect(_(lambda x: x*2).compose(lambda x: x+3)(5)) == 13
        expect(_(str.strip).compose(str.capitalize)('  fnord  ')) == 'Fnord'

class SmallTalkLikeBehaviour(FluentTest):
    
    def test_should_pretend_methods_that_return_None_returned_self(self):
        expect(_([3,2,1]).sort().unwrap) == None
        expect(_([3,2,1]).sort().previous.previous) == [1,2,3]
        expect(_([3,2,1]).sort().chain) == [1,2,3]
        expect(_([2,3,1]).sort().sort(reverse=True).unwrap) == None
        expect(_([2,3,1]).sort().sort(reverse=True).previous.previous.previous.previous) == [3,2,1]
        expect(_([2,3,1]).sort().sort(reverse=True).chain) == [3,2,1]
    
    def test_should_chain_off_of_previous_if_our_functions_return_none(self):
        class Attr(object):
            foo = 'bar'
        expect(_(Attr()).setattr('foo', 'baz').foo) == 'baz'
    
    # TODO check individually that the different forms of wrapping behave according to the SmallTalk contract
    # wrapped
    # unwrapped
    # wrapped_forward

class IterableTest(FluentTest):
    
    def test_should_call_callable_with_star_splat_of_self(self):
        expect(_([1,2,3]).star_call(lambda x, y, z: z-x-y)) == 0
    
    def test_join(self):
        expect(_(['1','2','3']).join(' ')) == '1 2 3'
        expect(_([1,2,3]).join(' ')) == '1 2 3'
    
    def test_any(self):
        expect(_((True, False)).any()) == True
        expect(_((False, False)).any()) == False
    
    def test_all(self):
        expect(_((True, False)).all()) == False
        expect(_((True, True)).all()) == True
    
    def test_len(self):
        expect(_((1,2,3)).len()) == 3
    
    def test_min_max_sum(self):
        expect(_([1,2]).min()) == 1
        expect(_([1,2]).max()) == 2
        expect(_((1,2,3)).sum()) == 6
    
    def test_map(self):
        expect(_([1,2,3]).imap(lambda x: x * x).call(list)) == [1, 4, 9]
        expect(_([1,2,3]).map(lambda x: x * x)) == (1, 4, 9)
    
    def test_starmap(self):
        expect(_([(1,2), (3,4)]).istarmap(lambda x, y: x+y).call(list)) == [3, 7]
        expect(_([(1,2), (3,4)]).starmap(lambda x, y: x+y)) == (3, 7)
    
    def test_filter(self):
        expect(_([1,2,3]).ifilter(lambda x: x > 1).call(list)) == [2,3]
        expect(_([1,2,3]).filter(lambda x: x > 1)) == (2,3)
    
    def test_zip(self):
        expect(_((1,2)).izip((3,4)).call(tuple)) == ((1, 3), (2, 4))
        expect(_((1,2)).izip((3,4), (5,6)).call(tuple)) == ((1, 3, 5), (2, 4, 6))
        
        expect(_((1,2)).zip((3,4))) == ((1, 3), (2, 4))
        expect(_((1,2)).zip((3,4), (5,6))) == ((1, 3, 5), (2, 4, 6))
    
    def test_reduce(self):
        # no iterator version of reduce as it's not a mapping
        expect(_((1,2)).reduce(operator.add)) == 3
    
    def test_grouped(self):
        expect(_((1,2,3,4,5,6)).igrouped(2).call(list)) == [(1,2), (3,4), (5,6)]
        expect(_((1,2,3,4,5,6)).grouped(2)) == ((1,2), (3,4), (5,6))
        expect(_((1,2,3,4,5)).grouped(2)) == ((1,2), (3,4))
    
    def test_group_by(self):
        actual = {}
        for key, values in _((1,1,2,2,3,3)).igroupby():
            actual[key] = tuple(values)
        
        expect(actual) == {
            1: (1,1),
            2: (2,2),
            3: (3,3)
        }
        
        actual = {}
        for key, values in _((1,1,2,2,3,3)).groupby():
            actual[key] = tuple(values)
        
        expect(actual) == {
            1: (1,1),
            2: (2,2),
            3: (3,3)
        }
    
    def test_tee_should_not_break_iterators(self):
        # This should work because the extend as well als the .call(list) 
        # should not exhaust the iterator created by .imap()
        recorder = []
        def record(generator): recorder.extend(generator)
        expect(_([1,2,3]).imap(lambda x: x*x).tee(record).call(list)) == [1,4,9]
        expect(recorder) == [1,4,9]
    
    def test_enumerate(self):
        expect(_(('foo', 'bar')).ienumerate().call(list)) == [(0, 'foo'), (1, 'bar')]
        expect(_(('foo', 'bar')).enumerate()) == ((0, 'foo'), (1, 'bar'))
    
    def test_reversed_sorted(self):
        expect(_([2,1,3]).ireversed().call(list)) == [3,1,2]
        expect(_([2,1,3]).reversed()) == (3,1,2)
        expect(_([2,1,3]).isorted().call(list)) == [1,2,3]
        expect(_([2,1,3]).sorted()) == (1,2,3)
        expect(_([2,1,3]).isorted(reverse=True).call(list)) == [3,2,1]
        expect(_([2,1,3]).sorted(reverse=True)) == (3,2,1)
    
    def test_flatten(self):
        expect(_([(1,2),[3,4],(5, [6,7])]).iflatten().call(list)) == \
            [1,2,3,4,5,6,7]
        expect(_([(1,2),[3,4],(5, [6,7])]).flatten()) == \
            (1,2,3,4,5,6,7)
        
        expect(_([(1,2),[3,4],(5, [6,7])]).flatten(level=1)) == \
            (1,2,3,4,5,[6,7])

class MappingTest(FluentTest):
    
    def test_should_call_callable_with_double_star_splat_as_keyword_arguments(self):
        def foo(*, foo): return foo
        expect(_(dict(foo='bar')).star_call(foo)) == 'bar'
        expect(_(dict(foo='baz')).star_call(foo, foo='bar')) == 'baz'
        expect(_(dict()).star_call(foo, foo='bar')) == 'bar'
    
    def test_should_support_attribute_access_to_mapping_items(self):
        expect(_(dict(foo='bar')).foo) == 'bar'

class StrTest(FluentTest):
    
    def test_search(self):
        expect(_('foo bar baz').search(r'b.r').span()) == (4,7)
    
    def test_match_fullmatch(self):
        expect(_('foo bar').match(r'foo\s').span()) == (0, 4)
        expect(_('foo bar').fullmatch(r'foo\sbar').span()) == (0, 7)
    
    def test_split(self):
        expect(_('foo\nbar\nbaz').split(r'\n')) == ['foo', 'bar', 'baz']
        expect(_('foo\nbar/baz').split(r'[\n/]')) == ['foo', 'bar', 'baz']
    
    def test_findall_finditer(self):
        expect(_("bazfoobar").findall('ba[rz]')) == ['baz', 'bar']
        expect(_("bazfoobar").finditer('ba[rz]').map(_.each.call.span())) == ((0,3), (6,9))
    
    def test_sub_subn(self):
        expect(_('bazfoobar').sub(r'ba.', 'foo')) == 'foofoofoo'
        expect(_('bazfoobar').sub(r'ba.', 'foo', 1)) == 'foofoobar'
        expect(_('bazfoobar').sub(r'ba.', 'foo', count=1)) == 'foofoobar'

class ImporterTest(FluentTest):
    
    def test_import_top_level_module(self):
        import sys
        expect(lib.sys) == sys
    
    def test_import_symbol_from_top_level_module(self):
        import sys
        expect(lib.sys.stdin) == sys.stdin
    
    def test_import_submodule_that_is_also_a_symbol_in_the_parent_module(self):
        import os
        expect(lib.os.name) == os.name
        expect(lib.os.path.join) == os.path.join
    
    def test_import_submodule_that_is_not_a_symbol_in_the_parent_module(self):
        import dbm
        expect(lambda: dbm.dumb).to_raise(AttributeError)
        
        def delayed_import():
            import dbm.dumb
            return dbm.dumb
        expect(lib.dbm.dumb) == delayed_import()
    
    def test_imported_objects_are_pre_wrapped(self):
        lib.os.path.join('/foo', 'bar', 'baz').findall(r'/(\w*)') == ['foo', 'bar', 'baz']

class EachTest(FluentTest):
    
    def test_should_produce_attrgetter_on_attribute_access(self):
        class Foo(object):
            bar = 'baz'
        expect(_([Foo(), Foo()]).map(_.each.bar)) == ('baz', 'baz')
    
    def test_should_produce_itemgetter_on_item_access(self):
        expect(_([['foo'], ['bar']]).map(_.each[0])) == ('foo', 'bar')
    
    def test_should_produce_callable_on_binary_operator(self):
        expect(_(['foo', 'bar']).map(_.each == 'foo')) == (True, False)
        expect(_([3, 5]).map(_.each + 3)) == (6, 8)
        expect(_([3, 5]).map(_.each < 4)) == (True, False)
    
    def test_should_produce_callable_on_unary_operator(self):
        expect(_([3, 5]).map(- _.each)) == (-3, -5)
        expect(_([3, 5]).map(~ _.each)) == (-4, -6)
    
    def test_should_produce_methodcaller_on_call_attribute(self):
        # problem: _.each.call is now not an attrgetter
        # _.each.method.call('foo') # like a method chaining
        # _.each_call.method('foo')
        # _.eachcall.method('foo')
        class Tested(object):
            def method(self, arg): return 'method+'+arg
        expect(_(Tested()).call(_.each.call.method('argument'))) == 'method+argument'
        expect(lambda: _.each.call('argument')).to_raise(AssertionError, '_.each.call.method_name')

class IntegrationTest(FluentTest):
    
    def test_extrac_and_decode_URIs(self):
        from xml.sax.saxutils import unescape
        line = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
            <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>'''

        actual = _(line).findall(r'value=\'(.*)\'').imap(unescape).call(list)
        expect(actual) == ['http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&fileformat=p2p&archiveformat=gz']
    
    def test_call_module_from_shell(self):
        from subprocess import check_output
        output = check_output(
            ['python', '-m', 'fluent', "lib.sys.stdin.read().split('\\n').imap(str.upper).imap(print).call(list)"],
            input=b'foo\nbar\nbaz')
        expect(output) == b'FOO\nBAR\nBAZ\n'

if __name__ == '__main__':
    import sys
    assert len(sys.argv) == 2, \
        "Usage: python -m fluent 'some code that can access fluent functions without having to import them'"
    
    exec(sys.argv[1], dict(wrap=wrap, _=_, lib=lib))
