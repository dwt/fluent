import functools, io, itertools, os, operator, sys

import unittest
from unittest.mock import patch

from pyexpect import expect
import fluentpy as _


class FluentTest(unittest.TestCase): pass

class WrapperTest(FluentTest):
    
    def test_should_not_wrap_a_wrapper_again(self):
        wrapped = _(4)
        expect(type(_(wrapped).unwrap)) == int
    
    def test_should_provide_usefull_str_and_repr_output(self):
        expect(repr(_('foo'))) == "fluentpy.wrap('foo')"
        expect(str(_('foo'))) == "fluentpy.wrap(foo)"
    
    def test_should_wrap_callables(self):
        counter = [0]
        def foo(): counter[0] += 1
        expect(_(foo)).is_instance(_.Wrapper)
        _(foo)()
        expect(counter[0]) == 1
    
    def test_should_wrap_attribute_accesses(self):
        class Foo(): bar = 'baz'
        expect(_(Foo()).bar).is_instance(_.Wrapper)
    
    def test_should_wrap_item_accesses(self):
        expect(_(dict(foo='bar'))['foo']).is_instance(_.Wrapper)
    
    def test_should_error_when_accessing_missing_attribute(self):
        class Foo(): pass
        expect(lambda: _(Foo().missing)).to_raise(AttributeError)
    
    def test_should_explictly_unwrap(self):
        foo = 1
        expect(_(foo).unwrap).is_(foo)
    
    def test_should_wrap_according_to_returned_type(self):
        expect(_('foo')).is_instance(_.TextWrapper)
        expect(_([])).is_instance(_.IterableWrapper)
        expect(_(iter([]))).is_instance(_.IterableWrapper)
        expect(_({})).is_instance(_.MappingWrapper)
        expect(_({1})).is_instance(_.SetWrapper)
        
        expect(_(lambda: None)).is_instance(_.CallableWrapper)
        class CallMe(object):
            def __call__(self): pass
        expect(_(CallMe())).is_instance(_.CallableWrapper)
        
        expect(_(object())).is_instance(_.Wrapper)
    
    def test_should_remember_call_chain(self):
        def foo(): return 'bar'
        expect(_(foo)().unwrap) == 'bar'
        expect(_(foo)().previous.unwrap) == foo
    
    def test_should_help_call_free_methods(self):
        expect(_([1,2,3]).call(itertools.combinations, r=2).to(tuple)) == ((1,2), (1,3), (2,3))
    
    def test_should_easily_convert_to_different_type(self):
        expect(_([1,2,3]).to(tuple)).is_instance_of(tuple)
    
    def test_hasattr_getattr_setattr_delattr(self):
        expect(_((1,2)).hasattr('len')._).is_false()
        expect(_('foo').getattr('__len__')()._) == 3
        class Attr(object):
            def __init__(self): self.foo = 'bar'
        expect(_(Attr()).setattr('foo', 'baz').self.foo._) == 'baz'
        
        expect(_(Attr()).delattr('foo').unwrap) == None
        expect(_(Attr()).delattr('foo').self.unwrap).isinstance(Attr)
        expect(_(Attr()).delattr('foo').self.vars()._) == {}
    
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
    
    def test_print(self):
        out = io.StringIO()
        _([1,2,3]).print(file=out)
        expect(out.getvalue()) == '[1, 2, 3]\n'
    
    def test_pprint(self):
        out = io.StringIO()
        _([1,2,3]).pprint(stream=out)
        expect(out.getvalue()) == '[1, 2, 3]\n'
    
    def test_str_and_repr_work(self):
        expect(str(_((1,2)))) == 'fluentpy.wrap((1, 2))'
        expect(repr(_((1,2)))) == 'fluentpy.wrap((1, 2))'
    
    def test_simple_forwards(self):
        expect(_(3).type()._) == int
        expect(_('3').type()._) == str
    
    def _test_creating_new_attributes_should_create_attribute_on_wrapped_object(self):
        wrapped = _(object())
        wrapped.foo = 'bar'
        expect(wrapped._.foo) == 'bar'

class CallableWrapperTest(FluentTest):
    
    def test_call(self):
        expect(_(lambda: 3)()._) == 3
        expect(_(lambda *x: x)(1,2,3)._) == (1,2,3)
        expect(_(lambda x=3: x)()._) == 3
        expect(_(lambda x=3: x)(x=4)._) == 4
        expect(_(lambda x=3: x)(4)._) == 4
    
    def test_curry(self):
        expect(_(lambda x, y: x*y).curry(2, 3)()._) == 6
        expect(_(lambda x=1, y=2: x*y).curry(x=3)()._) == 6
    
    def test_curry_supports_positional_arguments(self):
        expect(_(operator.add).curry(_, 'foo')('bar')._) == 'barfoo'
        expect(_(lambda x, y, z: x + y + z).curry(_, 'baz', _)('foo', 'bar')._) == 'foobazbar'
    
    def test_curry_supports_uncurried_positional_arguments(self):
        expect(_(lambda x, y, z: x + y + z).curry(_, 'bar')('foo', 'baz')._) == 'foobarbaz'
    
    def test_curry_can_transform_keyword_into_positional_arguments(self):
        curried = _(lambda x, y: (x, y)).curry(x=_, y=1)
        expect(curried(x=0)._) == (0, 1)
        expect(curried(0)._) == (0, 1)
    
    def test_curry_supports_positional_placeholders_and_keyword_placeholders_together(self):
        expect(_(lambda x, y: (x,y)).curry(_, y=_)._(1, 2)) == (1,2)
    
    def _test_curry_positional_placeholder_can_be_overridden_by_keyword_argument(self):
        """For this to work, I would need to actually parse the argspec of the curried function,
        and would need the code to implement the full Python argument merging semantic. 
        Not fun, nor neccessary I believe."""
        curried = _(lambda x, y: (x, y)).curry(_, y=1)
        expect(curried(x=0)._) == (0, 1)
    
    def test_curry_allows_reordering_arguments(self):
        expect(_(lambda x, y: x + y).curry(_._1, _._0)('foo', 'bar')._) == 'barfoo'
        expect(_(lambda x, y, z: x + y + z).curry(_._1, 'baz', _._0)('foo', 'bar')._) == 'barbazfoo'
    
    def test_curry_raises_if_number_of_arguments_missmatch(self):
        expect(lambda: _(lambda x, y: x + y).curry(_, _)('foo')).to_raise(AssertionError, 'Not enough arguments')
        expect(lambda: _(lambda x, y: x + y).curry(_._1)('foo')).to_raise(AssertionError, 'Not enough arguments')
        
        seen = set()
        expect(lambda: _(seen).add.curry(_._1)((True, 1))).to_raise(AssertionError,
            r'Not enough arguments.*Need at least 2, got 1'
        )
    
    def test_curry_can_handle_variable_argument_lists(self):
        add = _(lambda *args: args)
        expect(add.curry(1, _._args)(2, 3)._) == (1,(2,3))
        expect(add.curry(1, _._args)()._) == (1, tuple())
        expect(add.curry(1, 2, _._args)(3)._) == (1,2,(3,))
        expect(add.curry(_, _._args)(1, 2, 3)._) == (1,(2,3))
        # This one is slightly fishy - there's a good argument that the result should be (2,(3))
        # But the code currently says otherwise, and I don't want to break existing code.
        expect(add.curry(_._1, _._args)(1, 2, 3)._) == (2,(2,3))
        expect(_(lambda x: x).curry(_._args)(1,2,3)._) == (1,2,3)
        expect(_(lambda x: x).curry(x=_._args)(1,2,3)._) == (1,2,3)
        
        # varargs need to be last
        error_message = 'Variable arguments placeholder <_args> needs to be last'
        expect(lambda: add.curry(_._args, _)('foo', 'bar')).to_raise(
            AssertionError, error_message
        )
        
        expect(lambda: _(lambda x,y: (x,y)).curry(_._args, y=_)(1,2,3)).to_raise(
            AssertionError, error_message
        )
        expect(lambda: _(lambda x,y: (x,y)).curry(x=_._args, y=_)(1,2,3)).to_raise(
            AssertionError, error_message
        )
    
    def test_curry_can_be_applied_multiple_times(self):
        add = _(lambda *args: functools.reduce(operator.add, args))
        expect(add.curry(_, 'bar', _).curry('foo', _)('baz')._) == 'foobarbaz'
        expect(add.curry(_._1, 'baz', _._0).curry('foo', _)('bar')._) == 'barbazfoo'
    
    def test_curry_raises_if_handed_too_many_arguments(self):
        curried = _(lambda x: x).curry(3)._ # this should now be a funnction that takes _no_ arguments!
        expect(lambda: curried(2)).to_raise(TypeError, r'<lambda>\(\) takes 1 positional argument but 2 were given')
        expect(lambda: curried(x=2)).to_raise(TypeError, r"<lambda>\(\) got multiple values for argument 'x'")
        
        # a function of 3 arguments of which the first two are ignored
        curried = _(lambda x: x).curry(_._2)._ 
        expect(curried(1,2,3)) == 3
        expect(lambda: curried(1,2,3,4)).to_raise(TypeError, r'<lambda>\(\) takes 1 positional argument but 2 were given')
    
    
    def test_curry_raises_if_handed_too_little_arguments(self):
        curried = _(lambda x, y: x+y).curry(x=3)._ # this should now be a functino that takes _one_ argument
        expect(lambda: curried()).to_raise(TypeError, r"<lambda>\(\) missing 1 required positional argument: 'y'")
    
    def test_should_star_apply_arguments(self):
        expect(_(lambda a, b: b).star_call((1,2))._) == 2
    
    def test_compose_cast_wraps_chain(self):
        expect(_(lambda x: x*2).compose(lambda x: x+3)(5)._) == 13
        expect(_(str.strip).compose(str.capitalize)('  fnord  ')._) == 'Fnord'

class IterableWrapperTest(FluentTest):
    
    def test_iter(self):
        # Iter implicitly unwraps, because all other iterators behave this way, and there would otherwise be no way to explicitly get an iterator by chaining.
        iterator = _([1,2,3]).iter()
        expect(next(iterator)) == 1
        expect(next(iterator)) == 2
        expect(next(iterator)) == 3
        expect(lambda: next(iterator)).to_raise(StopIteration)
    
    def test_should_call_callable_with_star_splat_of_self(self):
        expect(_([1,2,3]).star_call(lambda x, y, z: z-x-y)._) == 0
    
    def test_join(self):
        expect(_(['1','2','3']).join(' ')._) == '1 2 3'
        expect(_([1,2,3]).join(' ')._) == '1 2 3'
        
        expect(_([1,2]).join()._) == '12'
    
    def test_any(self):
        expect(_((True, False)).any()._) == True
        expect(_((False, False)).any()._) == False
    
    def test_all(self):
        expect(_((True, False)).all()._) == False
        expect(_((True, True)).all()._) == True
    
    def test_len(self):
        expect(_((1,2,3)).len()._) == 3
        # len needs to deal with iterators correctly
        expect(_((1,2,3)).ifilter(_.each==1).len()._) == 1
    
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
        
        expect(
            _(((1, 2), (1, 4))).reduce(
                lambda acc, each: acc.setdefault(each[0], []).append(each[1]) or acc,
                dict()
            )._
        ) == { 1: [2, 4] }
    
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
        
        actual = _((1,1,2,2,3,3)).groupby()._
        
        expect(actual) == (
            (1, (1,1)),
            (2, (2,2)),
            (3, (3,3)),
        )
    
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
        
        # can flatten lists of strings
        expect(_([('D', 'L'), ('B', 'G')]).flatten()._) == ('D', 'L', 'B', 'G')
        expect(_([(b'D', b'L'), (b'B', b'G')]).flatten()._) == (b'D', b'L', b'B', b'G')
    
    def test_reshape(self):
        # This can be considered the inverse of flatten
        expect(_((1,2,3,4)).reshape()._) == (1,2,3,4)
        expect(_((1,2,3,4)).reshape(2)._) == ((1,2),(3,4))
        expect(_((1,2,3,4)).reshape(2,2)._) == (((1,2),(3,4)),)
        expect(_((1,2,3,4)).reshape(1,2)._) == (((1,),(2,)),((3,),(4,)))
        expect(_((1,2,3,4)).reshape(1,1,2)._) == ((((1,),),((2,),)),(((3,),),((4,),)))
        expect(_(range(4)).reshape(2)._) == ((0,1),(2,3))
        expect(_(range(12)).reshape(4)._) == (
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (8, 9, 10, 11),
        )
        expect(_(range(12)).reshape(4,3)._) == ((
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (8, 9, 10, 11),
        ),)
        
        expect(_((1,2,3)).reshape(2)._) == ((1,2), (3,))
    
    def test_star_call(self):
        expect(_([1,2,3]).star_call(str.format, '{} - {} : {}')._) == '1 - 2 : 3'
    
    def test_should_call_callable_with_wrapped_as_first_argument(self):
        expect(_([1,2,3]).call(min)._) == 1
        expect(_([1,2,3]).call(min)._) == 1
        expect(_('foo').call(str.upper)._) == 'FOO'
        expect(_('foo').call(str.upper)._) == 'FOO'
    
    def test_get_with_default(self):
        expect(_([1]).get(0, 2)._) == 1
        expect(_([]).get(0, 2)._) == 2
        expect(_([1]).get(0)._) == 1
        expect(lambda: _([]).get(0)).to_raise(IndexError)
    
    def test_get_with_default_should_support_iterators(self):
        expect(_(i for i in range(10)).get(0, 'fnord')._) == 0
        expect(_(i for i in range(10)).get(11, 'fnord')._) == 'fnord'
    
    def test_each_should_allow_to_call_functions_on_iterators_purely_for_their_side_effect(self):
        from unittest.mock import Mock
        call_counter = Mock()
        
        expect(next(iter(_(['a', 'b']).ieach(call_counter)))) == 'a'
        expect(call_counter.call_count) == 1
        
        expect(_(['a', 'b']).ieach(call_counter).to(tuple)) == ('a', 'b')
        expect(call_counter.call_count) == 3
        expect(_(['a', 'b']).each(call_counter)._) == ('a', 'b')
        expect(call_counter.call_count) == 5
    
    # Tests for other itertools methods
        
    def test_islice(self):
        expect(_([1,2,1]).slice(1)._) == (1,)
        expect(_([1,2,1]).slice(1,2)._) == (2,)
        expect(_([1,2,1]).slice(None, None,2)._) == (1,1)
        
        expect(_([1,2,1]).islice(1).to(tuple)) == (1,)
        expect(_([1,2,1]).islice(1,2).to(tuple)) == (2,)
        expect(_([1,2,1]).islice(None, None,2).to(tuple)) == (1,1)
        
        expect(_([1,2,1]).icycle().slice(1)._) == (1,)
        expect(_([1,2,1]).icycle().slice(1,2)._) == (2,)
        expect(_([1,2]).icycle().slice(None, 8,2)._) == (1,1,1,1)
    
    def test_itertools_moved_collection_methods(self):
        import typing
        iterators = _(iter([1,2,3])).itee(10)._
        expect(iterators).has_length(10)
        for iterator in iterators:
            expect(isinstance(iterator, typing.Iterator)).is_true()
        
        expect(_([1,2,3]).accumulate()._) == (1,3,6)
        
        expect(_([1,2,1]).dropwhile(_.each < 2)._) == (2,1)
        expect(_([1,2,1]).filterfalse(_.each < 2)._) == (2,)
        
        expect(_([1,2]).permutations()._) == ((1,2), (2,1))
        expect(_([1,2]).permutations(r=2)._) == ((1,2), (2,1))
        expect(_([1,2]).permutations(2)._) == ((1,2), (2,1))
        
        expect(_([1,2,3]).combinations(r=2)._) == ((1,2),(1,3),(2,3))
        expect(_([1,2]).combinations_with_replacement(r=2)._) == (
            (1,1), (1,2), (2,2),
        )
        
        expect(_([1,2]).product([3,4])._) == ((1,3), (1,4), (2,3), (2,4))
        expect(_([1,2]).product(repeat=2)._) == ((1,1), (1,2), (2,1), (2,2))

class MappingWrapperTest(FluentTest):
    
    def test_should_call_callable_with_double_star_splat_as_keyword_arguments(self):
        def foo(*, foo): return foo
        expect(_(dict(foo='bar')).star_call(foo)._) == 'bar'
        expect(_(dict(foo='baz')).star_call(foo, foo='bar')._) == 'baz'
        expect(_(dict()).star_call(foo, foo='bar')._) == 'bar'
    
    def test_should_support_attribute_access_to_mapping_items(self):
        expect(_(dict(foo='bar')).foo._) == 'bar'
        expect(_(dict(foo='bar')).keys().to(list)) == ['foo']
        expect(lambda: _(dict(foo='bar')).baz).to_raise(AttributeError, "has no attribute 'baz'")

class SetWrapperTest(FluentTest):
    
    def test_should_freeze(self):
        frozen = _({'foo', 'bar', 'baz'}).freeze()._
        expect(frozen).contains('foo', 'bar', 'baz')
        expect(frozen).isinstance(frozenset)

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
        expect(_("bazfoobar").finditer('ba[rz]').map(_.each.span())._) == ((0,3), (6,9))
    
    def test_sub_subn(self):
        expect(_('bazfoobar').sub(r'ba.', 'foo')._) == 'foofoofoo'
        expect(_('bazfoobar').sub(r'ba.', 'foo', 1)._) == 'foofoobar'
        expect(_('bazfoobar').sub(r'ba.', 'foo', count=1)._) == 'foofoobar'

class ImporterTest(FluentTest):
    
    def test_import_top_level_module(self):
        expect(_.lib.sys._) == sys
    
    def test_import_symbol_from_top_level_module(self):
        expect(_.lib.sys.stdin._) == sys.stdin
    
    def test_import_submodule_that_is_also_a_symbol_in_the_parent_module(self):
        expect(_.lib.os.name._) == os.name
        expect(_.lib.os.path.join._) == os.path.join
    
    def test_import_submodule_that_is_not_a_symbol_in_the_parent_module(self):
        import dbm
        expect(lambda: dbm.dumb).to_raise(AttributeError)
        
        def delayed_import():
            import dbm.dumb
            return dbm.dumb
        expect(_.lib.dbm.dumb._) == delayed_import()
    
    def test_imported_objects_are_pre_wrapped(self):
        _.lib.os.path.join('/foo', 'bar', 'baz').findall(r'/(\w*)')._ == ['foo', 'bar', 'baz']
    
    def test_should_allow_reloading_modules(self):
        sensed = {}
        def sensor(*args, **kwargs):
            sensed['args'] = args
            sensed['kwargs'] = kwargs
        
        with patch('importlib.reload', sensor):
            _.lib.os.path.reload()
            expect(sensed['args']) == (_.lib.os.path._, )

class AutoChainingEachWrapper(FluentTest):
    
    def test_should_produce_attrgetter_on_attribute_access(self):
        class Foo(object):
            bar = 'baz'
        attrgetter = _.each.bar._
        expect(attrgetter(Foo())) == 'baz'
    
    def test_should_produce_itemgetter_on_item_access(self):
        itemgetter = _.each[0]._
        expect(itemgetter(['foo'])) == 'foo'
    
    def test_should_produce_methodcaller_on_call_attribute(self):
        class Tested(object):
            def method(self, arg): return 'method+'+arg
        
        methodcaller = _.each.method('argument')._
        expect(methodcaller(Tested())) == 'method+argument'
    
    def test_should_behave_as_if_each_was_wrapped(self):
        expect(_.each.first._(dict(first='foo'))) == 'foo'
    
    def test_should_produce_callable_on_binary_operator(self):
        operation = _.each == 'foo'
        expect(operation('foo')).is_true()
        
        operation = _.each + 3
        expect(operation(3)) == 6
        
        operation = _.each < 4
        expect(operation(3)).is_true()
    
    def test_should_produce_callable_on_unary_operator(self):
        operation = - _.each
        expect(operation(3)) == -3
        operation = ~ _.each
        expect(operation(3)) == -4
    
    def test_in(self):
        expect(_.each.in_([1,2])._(3)).is_false()
        expect(_.each.in_([1,2])._(1)).is_true()
        
        expect(_.each.not_in([1,2])._(3)).is_true()
        expect(_.each.not_in([1,2])._(1)).is_false()
    
    def test_should_auto_chain_operations(self):
        operation = _.each['foo'][0].bar().baz._
        
        class Foo:
            def bar(self):
                return self
            baz = 'fnord'
        data = dict(foo=[Foo()])
        expect(operation(data)) == 'fnord'
        
        operation = _.each.split()._
        expect(operation('f o o')) == ['f', 'o', 'o']
    
    def test_should_auto_terminate_chains_when_using_operators(self):
        operation = _.each['foo'] % 3
        data = dict(foo=5)
        expect(operation(data)) == 2
    
    def test_should_have_sensible_repr_and_str_output(self):
        expect(repr(_.each)) == "fluentpy.wrap(each)"
        expect(repr(_.each['foo'])) == "fluentpy.wrap(each['foo'])"
        expect(repr(_.each.foo)) == "fluentpy.wrap(each.foo)"
        expect(repr(_.each.foo('bar', baz='quoox'))) == "fluentpy.wrap(each.foo(*('bar',), **{'baz': 'quoox'}))"
        
        expect(repr(_.each.foo['bar'])) == "fluentpy.wrap(each.foo['bar'])"
        
        expect(repr(_.each.in_([1,2]))) == "fluentpy.wrap(each in [1, 2])"
        expect(repr(_.each.not_in([1,2]))) == "fluentpy.wrap(each not in [1, 2])"
    
class WrapperLeakTest(FluentTest):
    
    def test_wrapped_objects_will_wrap_every_action_to_them(self):
        expect(_('foo').upper()).is_instance(_.Wrapper)
        expect(_([1,2,3])[1]).is_instance(_.Wrapper)
        expect(_(lambda: 'foo')()).is_instance(_.Wrapper)
        expect(_(dict(foo='bar')).foo).is_instance(_.Wrapper)
    
    def _test_function_expressions_return_unwrapped_objects(self):
        class Foo(object):
            bar = 'baz'
        expect(_.each.bar(Foo())).is_('baz')
        expect((_.each + 3)(4)).is_(7)
        expect(_.each['foo'](dict(foo='bar'))).is_('bar')

class AccessShadowedAttributesOnWrappedObjects(FluentTest):
    
    def test_use_getitem_to_bypass_overrides(self):
        class UnfortunateNames(object):
            def previous(self, *args):
                return args
        
        def producer(*args):
            return UnfortunateNames()
        
        expect(_(producer)().previous('foo')).is_instance(_.Wrapper)
        expect(_(UnfortunateNames()).proxy.previous('foo')._) == ('foo',)
    
    def test_chain_is_not_broken_by_proxy_usage(self):
        class UnfortunateNames(object):
            def previous(self, *args):
                return args
        
        expect(_(UnfortunateNames()).proxy.previous('foo').previous.previous._).is_instance(UnfortunateNames)
    
    def test_smalltalk_like_behaviour_is_not_broken_by_proxy(self):
        class UnfortunateNames(object):
            def previous(self, *args):
                self.args = args
        
        expect(_(UnfortunateNames()).proxy.previous('foo').self.args._) == ('foo',)

class SmallTalkLikeBehaviour(FluentTest):
    
    def test_should_ease_chaining_off_methods_that_return_none(self):
        expect(_([3,2,1]).sort()._) == None
        expect(_([3,2,1]).sort().unwrap) == None
        expect(_([3,2,1]).sort().previous.previous._) == [1,2,3]
        expect(_([3,2,1]).sort().self._) == [1,2,3]
        
        expect(_([2,3,1]).sort().self.sort(reverse=True)._) == None
        expect(_([2,3,1]).sort().self.sort(reverse=True).previous.previous._) == [3,2,1] # sorted, because in place
        expect(_([2,3,1]).sort().self.sort(reverse=True).self._) == [3,2,1]
        
        class Attr(object):
            foo = 'bar'
        expect(_(Attr()).setattr('foo', 'baz').self.foo._) == 'baz'
    
    def test_should_behave_consistently_in_face_of_methods_returning_none_intermittently(self):
        # The problem with the implicit 'self' behaviour, the code changed behaviour 
        # if a method returned 'zero' depending on the input
        
        class SometimesNone(object):
            def maybe_none(self, should_return_none):
                if should_return_none:
                    return None
                return 'fnord'
        
        expect(_(SometimesNone()).maybe_none(True).self._).isinstance(SometimesNone)
        expect(_(SometimesNone()).maybe_none(False).self._).isinstance(SometimesNone)

class IntegrationTest(FluentTest):
    
    def test_extrac_and_decode_URIs(self):
        from xml.sax.saxutils import unescape
        line = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
            <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>'''
        
        actual = _(line).findall(r'value=\'(.*)\'').map(unescape)._
        expect(actual) == ('http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&fileformat=p2p&archiveformat=gz',)
    
    def test_call_module_from_shell(self):
        from subprocess import check_output
        output = check_output(
            ['python', '-m', 'fluentpy', "lib.sys.stdin.read().split('\\n').imap(each.upper()._).map(print)"],
            input=b'foo\nbar\nbaz')
        expect(output) == b'FOO\nBAR\nBAZ\n'
    
    def test_can_import_public_symbols(self):
        from fluentpy import lib,  each, _ as _f, Wrapper
        expect(lib.sys._) == sys
        expect(_f(3)).is_instance(Wrapper)
        expect((each + 3)(4)) == 7
    
    def test_can_get_symbols_via_star_import(self):
        nested_locals = {}
        exec('from fluentpy import *; locals()', {}, nested_locals)
        # need _._ here so we don't get the executable module wrapper that we get from `import fluentpy as _`
        expect(nested_locals).has_subdict( _=_._, wrap=_._, lib=_.lib, each=_.each, _1=_._1, _9=_._9)
        # only symbols from __all__ get imported
        expect(nested_locals.keys()).not_contains('Wrapper')
    
    def test_can_access_original_module(self):
        import types
        expect(_.module).instanceof(types.ModuleType)

class DocumentationTest(FluentTest):
    
    def test_wrap_has_usefull_docstring(self):
        expect(_.__doc__).matches(r'_\(_\)\.dir\(\)\.print\(\)')
        expect(_.__doc__).matches(r'https://github.com/dwt/fluent')
    
    def test_classes_have_usefull_docstrings(self):
        expect(_.Wrapper.__doc__).matches(r'Universal wrapper')
        expect(_.CallableWrapper.__doc__).matches(r'subclass that wraps callables')
        expect(_.IterableWrapper.__doc__).matches(r'subclass that wraps iterables')
        expect(_.MappingWrapper.__doc__).matches(r'subclass that wraps mappings')
        expect(_.TextWrapper.__doc__).matches(r'regex methods')
        
        expect(_.SetWrapper.__doc__).matches(r'Mostly like IterableWrapper')
    
    def test_special_proxies_have_usefull_docstrings(self):
        expect(_.lib.__doc__).matches('Imports as expressions')
        expect(_.each.__doc__).matches('functions from expressions')
    
    def test_help_method_outputs_correct_docstrings(self):
        with patch.object(sys, 'stdout', io.StringIO()):
            help(_)
            expect(sys.stdout.getvalue()).matches('Help on function fluentpy.wrap')
        
        with patch.object(sys, 'stdout', io.StringIO()):
            _(list).help()
            expect(sys.stdout.getvalue()).matches('Help on class list in module builtins')
    
    def test_lib_has_usefull_repr(self):
        expect(repr(_.lib)).matches('virtual root module')

