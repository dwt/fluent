#!/usr/bin/env python3
# encoding: utf8

"""
Usage:

>>> from fluent_interface import *
>>> import sys
>>> str(sys.stdin).split().map().join()(print)

>>> from fluent import _ # as something if it colides

then start everything with:

>>> _(something)…

to get the right wrapper.

should also have 
    _.lib.$something that could be imported
    _.list, -.str, _.tuple, _.dict, … all the wrappers
    _.wrapper for the generic wrapping logic

This library tries to do a little of what underscore does for javascript. Just provide the missing glue to make the standard library nicer to use.

Consider what to do for __ functions as they cannot easily be wrapped. Implement them all on the wraper?
"""

from __future__ import print_function

import typing
import re
import types
import functools
import itertools
import operator

__all__ = [
    'wrap',
    'lib', # wrapper for python stdlib, access every stdlib package directly on this without need to import it
]


__list, __str = (list, str)

def wrap(wrapped, *, previous=None):
    """Factory method, wraps anything and returns the appropriate Wrapper subclass.
    
    This is the main entry point into the fluent wonderland. Wrap something and 
    everything you call off of that will stay wrapped in the apropriate wrappers.
    """
    if wrapped is None: wrapped = previous
        
    # ordered in python3
    by_type = (
        (typing.Text, Text),
        (typing.Mapping, Mapping),
        (typing.AbstractSet, Set),
        (typing.Iterable, Iterable),
        (typing.Callable, Callable),
    )
    for clazz, wrapper in by_type:
        if isinstance(wrapped, clazz):
            return wrapper(wrapped, previous=previous)
    
    return Wrapper(wrapped, previous=previous)

def apply(function, *args, **kwargs):
    return function(*args, **kwargs)

def wrapping(wrapped_function):
    @functools.wraps(wrapped_function)
    def wrapper(self, *args, **kwargs):
        return wrap(wrapped_function(self.unwrap, *args, **kwargs), previous=self)
    return wrapper

def forward(operation):
    @functools.wraps(operation)
    def forwarder(self, *args, **kwargs):
        return operation(self.unwrap, *args, **kwargs)
    return forwarder

def wrapping_forward(operation):
    @functools.wraps(operation)
    @wrapping
    def forwarder(self, *args, **kwargs):
        return operation(self, *args, **kwargs)
    return forwarder

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
    
    c) Operators like ==, +, *, will just proxy to the wrapped object and 
       return an unwrapped object. If you want to chain from these, use the
       chainable alternatives (.eq, .mul, .add, …)
    """
    
    def __init__(self, wrapped, previous):
        assert wrapped is not None, 'Cannot chain off of None'
        self.__wrapped = wrapped
        self.__previous = previous
    
    # Proxied methods
    
    __call__ = wrapping_forward(apply)
    __getattr__ = wrapping_forward(getattr)
    
    __str__ = forward(str)
    __repr__ = forward(repr)
    
    __eq__ = forward(operator.eq)
    
    # Breakouts
    
    @property
    def unwrap(self):
        return self.__wrapped
    
    @property
    def previous(self):
        return self.__previous
    
    # Chainable versions of operators
    
    @wrapping
    def call(self, function, *args, **kwargs):
        "Call function with self as first argument"
        # Different from __call__! Calls function(self, …) instead of self(…)
        return function(self, *args, **kwargs)
    
    # REFACT eq - keep or toss?
    eq = wrapping_forward(operator.eq)
    
    @wrapping_forward
    def tee(self, function):
        function(wrap(self))
        return self
    
    # isinstance, issubclass?

class Callable(Wrapper):
    
    # REFACT rename to partial for consistency with stdlib?
    @wrapping
    def curry(self, *args, **kwargs):
        """"Like functools.partial, but with a twist.
        
        If you use wrap (best imported as _) as a positional argument,
        upon the actual call, arguments will be left-filled for those placeholders.
        For example:
        
        >>> from fluent import wrap as _
        >>> _(operator.add).curry(_, 'foo')('bar') == 'barfoo'
        """
        # would be so nice to just use functools.partial(self, *args, **kwargs)
        # but they don't support placeholders
        placeholder = wrap
        def merge_args(curried_args, fargs):
            new_args = list(curried_args)
            if placeholder in curried_args:
                assert curried_args.count(placeholder) == len(fargs), \
                    'Need the right ammount of arguments for the placeholders'
                index = 0
                for arg in fargs:
                    index = new_args.index(placeholder, index)
                    new_args[index] = arg
            return new_args
        @functools.wraps(self)
        def wrapper(*fargs, **fkeywords):
            # TODO do I want the curried arguments to overwrite the 
            # direct ones or should they define defaults?
            # Currently they define defaults. This feels similar to how python handles
            #  keyword arguments in function definitions, but i wonder if the other 
            # way around would be more usefull here?
            new_kwargs = dict(kwargs, **fkeywords)
            new_args = merge_args(args, fargs)
            return self(*new_args, **new_kwargs)
        return wrapper
    
    @wrapping
    def compose(self, outer):
        return lambda *args, **kwargs: outer(self(*args, **kwargs))
    # REFACT consider aliasses wrap = chain = cast = compose
    
    
class Iterable(Wrapper):
    
    __iter__ = forward(iter)
    
    @wrapping
    def star_call(self, function, *args, **kwargs):
        "Call function with *self as first argument"
        return function(*args, *self, **kwargs)
    
    # This looks like it should be the same as 
    # starcall = wrapping_forward(lambda function, wrapped, *args, **kwargs: function(*wrapped, *args, **kwargs))
    # but it's not. Why?
    
    @wrapping_forward
    def join(wrapped, with_what):
        "Like str.join, but the other way around. Bohoo!"
        return with_what.join(map(str, wrapped))
    
    @wrapping_forward
    def map(self, iterator):
        return map(iterator, self)
    
    @wrapping_forward
    def filter(self, iterator):
        return filter(iterator, self)
    
    @wrapping_forward
    def zip(self, *args):
        return zip(self, *args)
    
    @wrapping_forward
    def tee(self, function):
        if not isinstance(self, typing.Collection): # probably a consuming iterator
            first, second = itertools.tee(self, 2)
            function(wrap(first))
            return second
        else: # can't call super from here, as self is not the real self
            function(wrap(self))
            return self
    
    # any, all, enumerate, len, max, min, reverse, setattr?, sum,, vars, dir
    # grouped, flatten

class Mapping(Iterable):
    
    # REFACT rename: kwargs_call?
    @wrapping
    def splat_call(self, function, *args, **kwargs):
        "Calls function(*self), but allows to override kwargs"
        return function(*args, **dict(self, **kwargs))
    
    # consider key_map, value_map, item_map?
# Do I want something more abstract that also encompasses frozenset?
class Set(Iterable): pass

class Text(Wrapper): pass

# Roundable (for all numeric needs?)
    # round
"""comment
# list.format = lambda self, format_string: str(format_string.format(*self))
#
#
# str.findall = lambda self, pattern: list(re.findall(pattern, self))
#  # REFACT can this be generalized to a mixin?
# # str.apply = lambda self, function: function(*self)
# # str.map = lambda self, iterator: list(map(iterator, self))
# # str.split = lambda self, *args, **kwargs: list(__str.split(self, *args, **kwargs))
# # str.split = list.cast(__str.split)
# # str.split = str.split.cast(list)
# # str.split = str.split.chain(list)
# # str.split = func.compose(str.split, list)
# str.split = func.wrap(str.split, list)
# str.upper = lambda self: str(__str.upper(self))
# str.prepend = lambda self, other: str(other + self)
# str.format = lambda self, format_string: str(format_string.format(self))

# REFACT accept regex as first argument and route to re.split then instead

# REFACT add auto-enhancer object (proxy that auto wraps method / function returns in a suitable subclass)
# REFACT add imp auto importer, that pre-wraps everything he imports. End effect should be that python is seamlessly usable like this.
# REFACT add python -m fluent 'code…' support which auto injects module importer and 
# TODO stuff to implement: zip, len, a way to get at the underlaying value
# TODO add flatten to listlikes
# TODO add sort, groupby, grouped
# TODO add convenience keyword arguments to map etc.
# map(attr='attrname') as shortcut for map(attrgetter('attrname'))
# map(item='itemname') as shortcut for map(itemgetter('itemname'))
# TODO consider starcall for Iterable and Mapping
# TODO consider numeric type to do stuff like wrap(3).times(...)
    or wrap([1,2,3]).call(len).times(yank_me)
"""

import unittest
from pyexpect import expect
import pytest

class FluentTest(unittest.TestCase):
    pass

class WrapperTest(FluentTest):
    
    def test_should_wrap_callables(self):
        counter = [0]
        def foo():
            counter[0] += 1
        expect(wrap(foo)()).is_instance(Wrapper)
        expect(counter[0]) == 1
    
    def test_should_wrap_attribute_accesses(self):
        class Foo(): bar = 'baz'
        expect(wrap(Foo()).bar).is_instance(Wrapper)
    
    def test_should_error_when_accessing_missing_attribute(self):
        class Foo(): pass
        expect(lambda: wrap(Foo().missing)).to_raise(AttributeError)
    
    def test_should_explictly_unwrap(self):
        foo = 1
        expect(wrap(foo).unwrap).is_(foo)
    
    def test_should_wrap_according_to_returned_type(self):
        expect(wrap('foo')).is_instance(Text)
        expect(wrap([])).is_instance(Iterable)
        expect(wrap({})).is_instance(Mapping)
        expect(wrap({1})).is_instance(Set)
        
        expect(wrap(lambda: None)).is_instance(Callable)
        class CallMe(object):
            def __call__(self): pass
        expect(wrap(CallMe())).is_instance(Callable)
        
        expect(wrap(object())).is_instance(Wrapper)
    
    def test_should_remember_call_chain(self):
        def foo(): return 'bar'
        expect(wrap(foo)().unwrap) == 'bar'
        expect(wrap(foo)().previous.unwrap) == foo
    
    def test_should_delegate_equality_test_to_wrapped_instance(self):
        # import sys; sys.stdout = sys.__stdout__; from pdb import set_trace; set_trace()
        expect(wrap(1)) == 1
        expect(wrap('42')) == '42'
        callme = lambda: None
        expect(wrap(callme)) == callme

class CallableTest(FluentTest):
    
    def test_should_call_callable_with_wrapped_as_first_argument(self):
        expect(wrap([1,2,3]).call(min)) == 1
        expect(wrap([1,2,3]).call(min)) == 1
        expect(wrap('foo').call(str.upper)) == 'FOO'
        expect(wrap('foo').call(str.upper)) == 'FOO'
    
    def test_tee_breakout_a_function_with_side_effects_and_disregard_return_value(self):
        side_effect = {}
        def tee(a_list): side_effect['tee'] = a_list.join('-')
        expect(wrap([1,2,3]).tee(tee)) == [1,2,3]
        expect(side_effect['tee']) == '1-2-3'
        
        def fnording(ignored): return 'fnord'
        expect(wrap([1,2,3]).tee(fnording)) == [1,2,3]
    
    def test_curry(self):
        expect(wrap(lambda x, y: x*y).curry(2, 3)()) == 6
        expect(wrap(lambda x=1, y=2: x*y).curry(x=3)()) == 6
    
    def test_curry_should_support_placeholders_to_curry_later_positional_arguments(self):
        _ = wrap
        expect(wrap(operator.add).curry(_, 'foo')('bar')) == 'barfoo'
    
    def test_compose_cast_wraps_chain(self):
        expect(wrap(lambda x: x*2).compose(lambda x: x+3)(5)) == 13
        expect(wrap(str.strip).compose(str.capitalize)('  fnord  ')) == 'Fnord'

class IterableTest(FluentTest):
    
    def test_should_call_callable_with_star_splat_of_self(self):
        expect(wrap([1,2,3]).star_call(lambda x, y, z: z-x-y)) == 0
    
    def test_join(self):
        expect(wrap(['1','2','3']).join(' ')) == '1 2 3'
        expect(wrap([1,2,3]).join(' ')) == '1 2 3'
    
    def test_map(self):
        expect(wrap([1,2,3]).map(lambda x: x * x).call(list)) == [1, 4, 9]
    
    def test_filter(self):
        expect(wrap([1,2,3]).filter(lambda x: x > 1).call(list)) == [2,3]
    
    def test_zip(self):
        expect(wrap((1,2)).zip((3,4)).call(tuple)) == ((1, 3), (2, 4))
        expect(wrap((1,2)).zip((3,4), (5,6)).call(tuple)) == ((1, 3, 5), (2, 4, 6))
    
    def test_tee_should_not_break_iterators(self):
        recorder = []
        def record(generator): recorder.extend(generator)
        expect(wrap([1,2,3]).map(lambda x: x*x).tee(record).call(list)) == [1,4,9]
        expect(recorder) == [1,4,9]
    
class MappingTest(FluentTest):
    
    def test_should_call_callable_with_double_star_splat_as_keyword_arguments(self):
        def foo(*, foo): return foo
        expect(wrap(dict(foo='bar')).splat_call(foo)) == 'bar'
        expect(wrap(dict(foo='baz')).splat_call(foo, foo='bar')) == 'bar'
    
class StrTest(FluentTest):
    
    def _test_findall(self):
        expect(str("bazfoobar").findall('ba[rz]')) == ['baz', 'bar']
    
    def _test_split(self):
        expect(str('foo\nbar\nbaz').split('\n')) == ['foo', 'bar', 'baz']
        # supports chaining
        expect(str('foo\nbar\nbaz').split('\n').map(str.upper)) == ['FOO', 'BAR', 'BAZ']
        
    def _test_prepend(self):
        expect(str('foo').prepend('Fnord: ')) == 'Fnord: foo'
    
    def _test_format(self):
        expect(str('foo').format('bar {} baz')) == 'bar foo baz'

class IntegrationTest(FluentTest):
    
    def test_format(self):
        expect(wrap([1,2,3]).star_call(str.format, '{} - {} : {}')) == '1 - 2 : 3'
    
    def _test_extrac_and_decode_URIs(self):
        from xml.sax.saxutils import unescape
        line = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
            <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>'''

        actual = str(line).findall(r'value=\'(.*)\'').map(unescape)
        expect(actual) == ['http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&fileformat=p2p&archiveformat=gz']

        
"""
Wie möchte ich denn das es sich bedient? Wie Smalltalk dass alles per default 'self' zurück gibt?
Alles generator basiert? Nur wenn man das nicht explizit auspacken muss für ausgabe. 
Evtl. trigger der ganzen chain mittels .unwrap?
"""
    
def _test():
    from xml.sax.saxutils import unescape
    
    """
    rico:~ dwt$ curl -sL 'https://www.iblocklist.com/lists.php' | egrep -A1 'star_[345]' | python -c "from __future__ import print_function; import sys, re; from from xml.sax.saxutils import unescape; print(map(unescape, re.findall(r'value=\'(.*)\'', sys.stdin.read())))"
    
    # CHECK wenn man das commando eh an -m fluent übergibt kann man auch das global objekt überschreiben und im getattr darin die imports dynamisch auflösen
    python -m fluent "str(sys.stdin).split('\n').map(xml.sax.unescape).map(print)"
    python -m fluent "[print(line) for line in [xml.sax.unescape(line) for line in sys.stdin.split('\n')]]
    """


    line = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>'''

    str(line).findall(r'value=\'(.*)\'').map(unescape).map(print)
    str(line).findall(r'value=\'(.*)\'').map(unescape).join('\n').call(print)
    str(line).findall(r'value=\'(.*)\'').map(unescape).join('\n')(print)
    str(line).findall(r'value=\'(.*)\'').map(unescape).apply(print)
    str('lalala').upper().call(print)
    str('fnord').upper()(print)
    str('fnord').upper().prepend('Formatted: ')(print)
    str('fnord').upper().format('Formatted: {}')(print)
    list(['foo', 'bar', 'baz']).map(str.upper).tee(print).join(' ')(print)
    str('foo,bar,baz').split(',').map(print)
    # def to_curry(one, two, three):
    #     print(one, two, three)
    # functools.partial(to_curry, 1, 2, 3)()

    lines = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='gyisgnzbhppbvsphucsw' readonly='readonly' onClick="select_text('gyisgnzbhppbvsphucsw');" value='http://list.iblocklist.com/?list=gyisgnzbhppbvsphucsw&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='uwnukjqktoggdknzrhgh' readonly='readonly' onClick="select_text('uwnukjqktoggdknzrhgh');" value='http://list.iblocklist.com/?list=uwnukjqktoggdknzrhgh&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='imlmncgrkbnacgcwfjvh' readonly='readonly' onClick="select_text('imlmncgrkbnacgcwfjvh');" value='http://list.iblocklist.com/?list=imlmncgrkbnacgcwfjvh&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='plkehquoahljmyxjixpu' readonly='readonly' onClick="select_text('plkehquoahljmyxjixpu');" value='http://list.iblocklist.com/?list=plkehquoahljmyxjixpu&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='gihxqmhyunbxhbmgqrla' readonly='readonly' onClick="select_text('gihxqmhyunbxhbmgqrla');" value='http://list.iblocklist.com/?list=gihxqmhyunbxhbmgqrla&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='dgxtneitpuvgqqcpfulq' readonly='readonly' onClick="select_text('dgxtneitpuvgqqcpfulq');" value='http://list.iblocklist.com/?list=dgxtneitpuvgqqcpfulq&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='llvtlsjyoyiczbkjsxpf' readonly='readonly' onClick="select_text('llvtlsjyoyiczbkjsxpf');" value='http://list.iblocklist.com/?list=llvtlsjyoyiczbkjsxpf&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='xoebmbyexwuiogmbyprb' readonly='readonly' onClick="select_text('xoebmbyexwuiogmbyprb');" value='http://list.iblocklist.com/?list=xoebmbyexwuiogmbyprb&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='cwworuawihqvocglcoss' readonly='readonly' onClick="select_text('cwworuawihqvocglcoss');" value='http://list.iblocklist.com/?list=cwworuawihqvocglcoss&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='xshktygkujudfnjfioro' readonly='readonly' onClick="select_text('xshktygkujudfnjfioro');" value='http://list.iblocklist.com/?list=xshktygkujudfnjfioro&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='mcvxsnihddgutbjfbghy' readonly='readonly' onClick="select_text('mcvxsnihddgutbjfbghy');" value='http://list.iblocklist.com/?list=mcvxsnihddgutbjfbghy&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='usrcshglbiilevmyfhse' readonly='readonly' onClick="select_text('usrcshglbiilevmyfhse');" value='http://list.iblocklist.com/?list=usrcshglbiilevmyfhse&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='xpbqleszmajjesnzddhv' readonly='readonly' onClick="select_text('xpbqleszmajjesnzddhv');" value='http://list.iblocklist.com/?list=xpbqleszmajjesnzddhv&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ficutxiwawokxlcyoeye' readonly='readonly' onClick="select_text('ficutxiwawokxlcyoeye');" value='http://list.iblocklist.com/?list=ficutxiwawokxlcyoeye&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ghlzqtqxnzctvvajwwag' readonly='readonly' onClick="select_text('ghlzqtqxnzctvvajwwag');" value='http://list.iblocklist.com/?list=ghlzqtqxnzctvvajwwag&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='bcoepfyewziejvcqyhqo' readonly='readonly' onClick="select_text('bcoepfyewziejvcqyhqo');" value='http://list.iblocklist.com/?list=bcoepfyewziejvcqyhqo&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='cslpybexmxyuacbyuvib' readonly='readonly' onClick="select_text('cslpybexmxyuacbyuvib');" value='http://list.iblocklist.com/?list=cslpybexmxyuacbyuvib&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='pwqnlynprfgtjbgqoizj' readonly='readonly' onClick="select_text('pwqnlynprfgtjbgqoizj');" value='http://list.iblocklist.com/?list=pwqnlynprfgtjbgqoizj&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='jhaoawihmfxgnvmaqffp' readonly='readonly' onClick="select_text('jhaoawihmfxgnvmaqffp');" value='http://list.iblocklist.com/?list=jhaoawihmfxgnvmaqffp&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='zbdlwrqkabxbcppvrnos' readonly='readonly' onClick="select_text('zbdlwrqkabxbcppvrnos');" value='http://list.iblocklist.com/?list=zbdlwrqkabxbcppvrnos&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    '''

    # str(lines).findall(r'value=\'(.*)\'').map(unescape).apply(print)

    blocklists = [u'http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=gyisgnzbhppbvsphucsw&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=uwnukjqktoggdknzrhgh&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=imlmncgrkbnacgcwfjvh&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=plkehquoahljmyxjixpu&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=gihxqmhyunbxhbmgqrla&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=dgxtneitpuvgqqcpfulq&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=llvtlsjyoyiczbkjsxpf&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=xoebmbyexwuiogmbyprb&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=cwworuawihqvocglcoss&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=xshktygkujudfnjfioro&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=mcvxsnihddgutbjfbghy&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=usrcshglbiilevmyfhse&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=xpbqleszmajjesnzddhv&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=ficutxiwawokxlcyoeye&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=ghlzqtqxnzctvvajwwag&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=bcoepfyewziejvcqyhqo&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=cslpybexmxyuacbyuvib&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=pwqnlynprfgtjbgqoizj&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=jhaoawihmfxgnvmaqffp&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=zbdlwrqkabxbcppvrnos&amp;fileformat=p2p&amp;archiveformat=gz']

if __name__ == '__main__':
    unittest.main()
    # test()
