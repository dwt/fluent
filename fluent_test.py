import unittest
from pyexpect import expect
import pytest

from fluent import *
from fluent import Wrapper, Text, Iterable, Mapping, Set, Callable
import operator

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
    
    def test_hasattr_getattr_setattr_delattr(self):
        expect(_((1,2)).hasattr('len')._).is_false()
        expect(_('foo').getattr('__len__')()._) == 3
        class Attr(object):
            def __init__(self): self.foo = 'bar'
        expect(_(Attr()).setattr('foo', 'baz').__.foo._) == 'baz'
        
        expect(_(Attr()).delattr('foo').unwrap) == None
        expect(_(Attr()).delattr('foo').__.unwrap).isinstance(Attr)
        expect(_(Attr()).delattr('foo').__.vars()._) == {}
    
    def test_isinstance_issubclass(self):
        expect(_('foo').isinstance(str)._) == True
        expect(_('foo').isinstance(int)._) == False
        expect(_(str).issubclass(object)._) == True
        expect(_(str).issubclass(str)._) == True
        expect(_(str).issubclass(int)._) == False
    
    def test_dir_vars(self):
        expect(_(object()).dir()._).contains('__class__', '__init__', '__eq__')
        class Foo(object): pass
        foo = Foo()
        foo.bar = 'baz'
        expect(_(foo).vars()._) == {'bar': 'baz'}

class CallableTest(FluentTest):
    
    def test_call(self):
        expect(_(lambda: 3)()._) == 3
        expect(_(lambda *x: x)(1,2,3)._) == (1,2,3)
        expect(_(lambda x=3: x)()._) == 3
        expect(_(lambda x=3: x)(x=4)._) == 4
        expect(_(lambda x=3: x)(4)._) == 4
    
    def test_star_call(self):
        expect(wrap([1,2,3]).star_call(str.format, '{} - {} : {}')._) == '1 - 2 : 3'
    
    def test_should_call_callable_with_wrapped_as_first_argument(self):
        expect(_([1,2,3]).call(min)._) == 1
        expect(_([1,2,3]).call(min)._) == 1
        expect(_('foo').call(str.upper)._) == 'FOO'
        expect(_('foo').call(str.upper)._) == 'FOO'
    
    def test_tee_breakout_a_function_with_side_effects_and_disregard_return_value(self):
        side_effect = {}
        def observer(a_list): side_effect['tee'] = a_list.join('-')._
        expect(_([1,2,3]).tee(observer)._) == [1,2,3]
        expect(side_effect['tee']) == '1-2-3'
        
        def fnording(ignored): return 'fnord'
        expect(_([1,2,3]).tee(fnording)._) == [1,2,3]
    
    def test_curry(self):
        expect(_(lambda x, y: x*y).curry(2, 3)()._) == 6
        expect(_(lambda x=1, y=2: x*y).curry(x=3)()._) == 6
    
    def test_auto_currying(self):
        expect(_(lambda x: x + 3)(_)(3)._) == 6
        expect(_(lambda x, y: x + y)(_, 'foo')('bar')._) == 'barfoo'
        expect(_(lambda x, y: x + y)('foo', _)('bar')._) == 'foobar'
        
    def test_curry_should_support_placeholders_to_curry_later_positional_arguments(self):
        expect(_(operator.add).curry(_, 'foo')('bar')._) == 'barfoo'
        expect(_(lambda x, y, z: x + y + z).curry(_, 'baz', _)('foo', 'bar')._) == 'foobazbar'
    
    def test_compose_cast_wraps_chain(self):
        expect(_(lambda x: x*2).compose(lambda x: x+3)(5)._) == 13
        expect(_(str.strip).compose(str.capitalize)('  fnord  ')._) == 'Fnord'

class SmallTalkLikeBehaviour(FluentTest):
    
    def test_should_pretend_methods_that_return_None_returned_self(self):
        expect(_([3,2,1]).sort().unwrap) == None
        expect(_([3,2,1]).sort()._) == None
        expect(_([3,2,1]).sort().previous.previous._) == [1,2,3]
        expect(_([3,2,1]).sort().__.unwrap) == [1,2,3]
        
        expect(_([2,3,1]).sort().__.sort(reverse=True).unwrap) == None
        expect(_([2,3,1]).sort().__.sort(reverse=True).previous.previous.previous.previous.previous._) == [3,2,1]
        expect(_([2,3,1]).sort().__.sort(reverse=True).__._) == [3,2,1]
        
        class Attr(object):
            foo = 'bar'
        expect(_(Attr()).setattr('foo', 'baz').__.foo._) == 'baz'

class IterableTest(FluentTest):
    
    def test_should_call_callable_with_star_splat_of_self(self):
        expect(_([1,2,3]).star_call(lambda x, y, z: z-x-y)._) == 0
    
    def test_join(self):
        expect(_(['1','2','3']).join(' ')._) == '1 2 3'
        expect(_([1,2,3]).join(' ')._) == '1 2 3'
    
    def test_any(self):
        expect(_((True, False)).any()._) == True
        expect(_((False, False)).any()._) == False
    
    def test_all(self):
        expect(_((True, False)).all()._) == False
        expect(_((True, True)).all()._) == True
    
    def test_len(self):
        expect(_((1,2,3)).len()._) == 3
    
    def test_min_max_sum(self):
        expect(_([1,2]).min()._) == 1
        expect(_([1,2]).max()._) == 2
        expect(_((1,2,3)).sum()._) == 6
    
    def test_map(self):
        expect(_([1,2,3]).imap(lambda x: x * x).call(list)._) == [1, 4, 9]
        expect(_([1,2,3]).map(lambda x: x * x)._) == (1, 4, 9)
    
    def test_starmap(self):
        expect(_([(1,2), (3,4)]).istarmap(lambda x, y: x+y).call(list)._) == [3, 7]
        expect(_([(1,2), (3,4)]).starmap(lambda x, y: x+y)._) == (3, 7)
    
    def test_filter(self):
        expect(_([1,2,3]).ifilter(lambda x: x > 1).call(list)._) == [2,3]
        expect(_([1,2,3]).filter(lambda x: x > 1)._) == (2,3)
    
    def test_zip(self):
        expect(_((1,2)).izip((3,4)).call(tuple)._) == ((1, 3), (2, 4))
        expect(_((1,2)).izip((3,4), (5,6)).call(tuple)._) == ((1, 3, 5), (2, 4, 6))
        
        expect(_((1,2)).zip((3,4))._) == ((1, 3), (2, 4))
        expect(_((1,2)).zip((3,4), (5,6))._) == ((1, 3, 5), (2, 4, 6))
    
    def test_reduce(self):
        # no iterator version of reduce as it's not a mapping
        expect(_((1,2)).reduce(operator.add)._) == 3
    
    def test_grouped(self):
        expect(_((1,2,3,4,5,6)).igrouped(2).call(list)._) == [(1,2), (3,4), (5,6)]
        expect(_((1,2,3,4,5,6)).grouped(2)._) == ((1,2), (3,4), (5,6))
        expect(_((1,2,3,4,5)).grouped(2)._) == ((1,2), (3,4))
    
    def test_group_by(self):
        actual = {}
        for key, values in _((1,1,2,2,3,3)).igroupby()._:
            actual[key] = tuple(values)
        
        expect(actual) == {
            1: (1,1),
            2: (2,2),
            3: (3,3)
        }
        
        actual = {}
        for key, values in _((1,1,2,2,3,3)).groupby()._:
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
        expect(_([1,2,3]).imap(lambda x: x*x).tee(record).call(list)._) == [1,4,9]
        expect(recorder) == [1,4,9]
    
    def test_enumerate(self):
        expect(_(('foo', 'bar')).ienumerate().call(list)._) == [(0, 'foo'), (1, 'bar')]
        expect(_(('foo', 'bar')).enumerate()._) == ((0, 'foo'), (1, 'bar'))
    
    def test_reversed_sorted(self):
        expect(_([2,1,3]).ireversed().call(list)._) == [3,1,2]
        expect(_([2,1,3]).reversed()._) == (3,1,2)
        expect(_([2,1,3]).isorted().call(list)._) == [1,2,3]
        expect(_([2,1,3]).sorted()._) == (1,2,3)
        expect(_([2,1,3]).isorted(reverse=True).call(list)._) == [3,2,1]
        expect(_([2,1,3]).sorted(reverse=True)._) == (3,2,1)
    
    def test_flatten(self):
        expect(_([(1,2),[3,4],(5, [6,7])]).iflatten().call(list)._) == \
            [1,2,3,4,5,6,7]
        expect(_([(1,2),[3,4],(5, [6,7])]).flatten()._) == \
            (1,2,3,4,5,6,7)
        
        expect(_([(1,2),[3,4],(5, [6,7])]).flatten(level=1)._) == \
            (1,2,3,4,5,[6,7])

class MappingTest(FluentTest):
    
    def test_should_call_callable_with_double_star_splat_as_keyword_arguments(self):
        def foo(*, foo): return foo
        expect(_(dict(foo='bar')).star_call(foo)._) == 'bar'
        expect(_(dict(foo='baz')).star_call(foo, foo='bar')._) == 'baz'
        expect(_(dict()).star_call(foo, foo='bar')._) == 'bar'
    
    def test_should_support_attribute_access_to_mapping_items(self):
        expect(_(dict(foo='bar')).foo._) == 'bar'

class StrTest(FluentTest):
    
    def test_search(self):
        expect(_('foo bar baz').search(r'b.r').span()._) == (4,7)
    
    def test_match_fullmatch(self):
        expect(_('foo bar').match(r'foo\s').span()._) == (0, 4)
        expect(_('foo bar').fullmatch(r'foo\sbar').span()._) == (0, 7)
    
    def test_split(self):
        expect(_('foo\nbar\nbaz').split(r'\n')._) == ['foo', 'bar', 'baz']
        expect(_('foo\nbar/baz').split(r'[\n/]')._) == ['foo', 'bar', 'baz']
    
    def test_findall_finditer(self):
        expect(_("bazfoobar").findall('ba[rz]')._) == ['baz', 'bar']
        expect(_("bazfoobar").finditer('ba[rz]').map(_.each.call.span())._) == ((0,3), (6,9))
    
    def test_sub_subn(self):
        expect(_('bazfoobar').sub(r'ba.', 'foo')._) == 'foofoofoo'
        expect(_('bazfoobar').sub(r'ba.', 'foo', 1)._) == 'foofoobar'
        expect(_('bazfoobar').sub(r'ba.', 'foo', count=1)._) == 'foofoobar'

class ImporterTest(FluentTest):
    
    def test_import_top_level_module(self):
        import sys
        expect(lib.sys._) == sys
    
    def test_import_symbol_from_top_level_module(self):
        import sys
        expect(lib.sys.stdin._) == sys.stdin
    
    def test_import_submodule_that_is_also_a_symbol_in_the_parent_module(self):
        import os
        expect(lib.os.name._) == os.name
        expect(lib.os.path.join._) == os.path.join
    
    def test_import_submodule_that_is_not_a_symbol_in_the_parent_module(self):
        import dbm
        expect(lambda: dbm.dumb).to_raise(AttributeError)
        
        def delayed_import():
            import dbm.dumb
            return dbm.dumb
        expect(lib.dbm.dumb._) == delayed_import()
    
    def test_imported_objects_are_pre_wrapped(self):
        lib.os.path.join('/foo', 'bar', 'baz').findall(r'/(\w*)')._ == ['foo', 'bar', 'baz']

class EachTest(FluentTest):
    
    def test_should_produce_attrgetter_on_attribute_access(self):
        class Foo(object):
            bar = 'baz'
        expect(_([Foo(), Foo()]).map(_.each.bar)._) == ('baz', 'baz')
    
    def test_should_produce_itemgetter_on_item_access(self):
        expect(_([['foo'], ['bar']]).map(_.each[0])._) == ('foo', 'bar')
    
    def test_should_produce_callable_on_binary_operator(self):
        expect(_(['foo', 'bar']).map(_.each == 'foo')._) == (True, False)
        expect(_([3, 5]).map(_.each + 3)._) == (6, 8)
        expect(_([3, 5]).map(_.each < 4)._) == (True, False)
    
    def test_should_produce_callable_on_unary_operator(self):
        expect(_([3, 5]).map(- _.each)._) == (-3, -5)
        expect(_([3, 5]).map(~ _.each)._) == (-4, -6)
    
    def test_should_produce_methodcaller_on_call_attribute(self):
        # problem: _.each.call is now not an attrgetter
        # _.each.method.call('foo') # like a method chaining
        # _.each_call.method('foo')
        # _.eachcall.method('foo')
        class Tested(object):
            def method(self, arg): return 'method+'+arg
        expect(_(Tested()).call(_.each.call.method('argument'))._) == 'method+argument'
        expect(lambda: _.each.call('argument')).to_raise(AssertionError, '_.each.call.method_name')

class IntegrationTest(FluentTest):
    
    def test_extrac_and_decode_URIs(self):
        from fluent import _
        
        from xml.sax.saxutils import unescape
        line = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
            <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>'''

        actual = _(line).findall(r'value=\'(.*)\'').map(unescape)._
        expect(actual) == ('http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&fileformat=p2p&archiveformat=gz',)
    
    def test_call_module_from_shell(self):
        from subprocess import check_output
        output = check_output(
            ['python', '-m', 'fluent', "lib.sys.stdin.read().split('\\n').imap(str.upper).imap(print).call(list)"],
            input=b'foo\nbar\nbaz')
        expect(output) == b'FOO\nBAR\nBAZ\n'
    
    def test_use_imported_module_as_wrap_function(self):
        import fluent as _f
        expect(_f('foo').upper()._) == 'FOO'
