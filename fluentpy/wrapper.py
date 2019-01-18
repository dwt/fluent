import functools
import itertools
import math
import operator
import re
import importlib
import sys
import types
import typing
import pprint

__all__ = ['wrap', '_'] # + @public
__api__ = ['wrap'] # + @protected

NUMBER_OF_NAMED_ARGUMENT_PLACEHOLDERS = 10
# _wrapper_is_sealed = False
_absent_default_argument = object()

# TODO investigate if functools.singledispatch would be a good candidate to replace / enhance this function
def wrap(wrapped, *, previous=None, chain=None):
    """Factory method, wraps anything and returns the appropriate Wrapper subclass.
    
    This is the main entry point into the fluent wonderland. Wrap something and 
    everything you call off of that will stay wrapped in the apropriate wrappers.
    
    It is usually imported like this:
    
        >>> import fluentpy as _
        >>> import fluentpy as _f
        >>> from fluentpy import wrap
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
_wrap_alternatives = [wrap]

def public(something, optional_name=None):
    __all__.append(optional_name or something.__name__)
    return protected(something, optional_name=optional_name)

def protected(something, optional_name=None):
    __api__.append(optional_name or something.__name__)
    setattr(wrap, optional_name or something.__name__, something)
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
    
    Use this to adapt free functions that should not return a wrapped value
    """
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

# REFACT consider rename to tuplify for consistency? Maybe not because it haves a different return type?
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
    
    Please note: most of the methods are actual standard library methods that are 
    simply wrapped to rebind their (usually first) parameter to the object they where called on.
    So for example: `repr(something)` becomes `_(something).repr()`.
    This means that the (unchanged) documentation (often) still shows the original signature 
    and refers to the original arguments. A little bit of common sense might therefore be required.
    """
    
    __slots__ = ['__wrapped', '__previous', '__chain']
    
    def __init__(self, wrapped, *, previous, chain):
        assert wrapped is not None or chain is not None, 'Cannot chain off of None'
        self.__wrapped = wrapped
        self.__previous = previous
        self.__chain = chain # REFACT consider rename to __self?
    
    def __str__(self):
        return "fluentpy.wrap(%s)" % (self.unwrap,)
    
    def __repr__(self):
        return "fluentpy.wrap(%r)" % (self.unwrap,)
    
    # Proxied methods
    
    # for name in dir(operator):
    #     if not name.startswith('__') or name in ('__doc__',):
    #         continue
    #     locals()[name] = wrapped(getattr(operator, name))
    # del name # prevent promotion to class variable
    # Would this make __getitem__ and __getattr__ obsolete?

    __getitem__ = wrapped(operator.getitem)
    __getattr__ = wrapped(getattr)
    # TODO Would be nice if all write acccesses could be given through to the wrapped object. But this breaks many current assumptions of this library. :/
    # Maybe this works if all internal classes define __slots__?
    # def __setattr__(self, name, value):
    #     if not _wrapper_is_sealed:
    #         return super().__setattr__(name, value)
    #     else:
    #         setattr(self.unwrap(), name, value)
    
    # Breakouts
    
    @property
    def unwrap(self):
        """Returns the underlying wrapped value of this wrapper instance."""
        return self.__wrapped
    _ = unwrap # alias
    
    @property
    def previous(self):
        """Returns the previous wrapper in the chain of wrappers.
        
        This allows you to walk the chain of wrappers that where created in your expression. 
        Mainly used internally but might be usefull for introspection.
        """
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
    
    dir = wrapped(dir)
    vars = wrapped(vars)
    print = wrapped(print)
    pprint = wrapped(pprint.pprint)
    help = wrapped(help)
    type = unwrapped(type)
    str = wrapped(str)
    repr = wrapped(repr)

# REFACT consider to use wrap as the placeholder to have less symbols? Probably not worth it...
virtual_root_module = "virtual root module"

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
        
        module = None
        if self.unwrap is virtual_root_module:
            module = importlib.import_module(name)
        else:
            module = importlib.import_module('.'.join((self.unwrap.__name__, name)))
        
        return wrap(module)
    
    @wrapped
    @functools.wraps(importlib.reload)
    def reload(self):
        importlib.reload(self)
        return self

lib = Module(virtual_root_module, previous=None, chain=None)
lib.__name__ = 'lib'
public(lib)

@protected
class Callable(Wrapper):
    """Higher order methods for callables."""
    
    def __call__(self, *args, **kwargs):
        """"Call through to the wrapped function."""
        def unwrap_if_neccessary(something):
            if isinstance(something, Wrapper):
                return something.unwrap
            return something

        args = list(map(unwrap_if_neccessary, args))
        kwargs = {key: unwrap_if_neccessary(value) for key, value in kwargs.items()}

        result = self.unwrap(*args, **kwargs)
        chain = None if self.previous is None else self.previous
        return wrap(result, previous=self, chain=chain)
    
    @wrapped
    def curry(self, *default_args, **default_kwargs):
        """Like functools.partial, but with a twist.
        
        If you use `wrap` or `_` as a positional argument, upon the actual call, 
        arguments will be left-filled for those placeholders.
        
        >>> _(operator.add).curry(_, 'foo')('bar')._ == 'barfoo'
        
        If you use wrap._$NUMBER (with $NUMBER < 10) you can take full controll 
        over the ordering of the arguments.
        
        >>> _(a_function).curry(_._0, _._0, _.7)
        
        This will repeat the first argument twice, then take the 8th and ignore all in between.
        
        You can also mix numbered with generic placeholders, but since it can be hard to read, 
        I would not advise it.
        
        There is also `_._args` which is the placeholder for the `*args` variable argument list specifier.
        (Note that it is only supported in the last position of the positional argument list.)
        
        >>> _(operator.add).curry(_.args)('foo', 'bar)._ == 'foobar'
        """
        # REFACT consider, would it be easier to actually generate a wrapper function that has an argspec
        # according to the given spec?
        
        placeholders = tuple(_wrap_alternatives)
        reordering_placeholders = tuple(_reordering_placeholders)
        splat_args_placeholder = wrap._args
        all_placeholders = placeholders + reordering_placeholders + (splat_args_placeholder,)
        
        def merge_arguments(actual_args, actual_kwargs):
            """Processing positional arguments first, then keyword arguments to keep this as 
            compatible as possible with the way python works
            """
            # This works because dict() is sorted in python3.6+
            merged_default_kwargs = dict(default_kwargs, **actual_kwargs)
            
            def assert_has_enough_args(required_number):
                assert len(actual_args) > required_number, \
                    'Foo: Not enough arguments given to curried function. Need at least %i, got %i: <%r>' \
                        % (required_number + 1, len(actual_args), actual_args)
            
            def assert_is_last_positional_placeholder(arg_index):
                assert arg_index + 1 == len(default_args), \
                    'Variable arguments placeholder <_args> needs to be last'
                assert_is_last_keyword_placeholder(-1) # can have none
            
            def assert_is_last_keyword_placeholder(arg_index):
                relevant_kwarg_values = tuple(merged_default_kwargs.values())[arg_index+1:]
                assert all(each not in all_placeholders for each in relevant_kwarg_values), \
                    'Variable arguments placeholder <_args> needs to be last'
            
            merged_args = list()
            placeholder_index = -1
            for arg_index, arg_default in enumerate(default_args):
                if arg_default in all_placeholders:
                    placeholder_index += 1
                if arg_default in placeholders:
                    assert_has_enough_args(placeholder_index)
                    merged_args.append(actual_args[placeholder_index])
                elif arg_default in reordering_placeholders:
                    assert_has_enough_args(arg_default.unwrap)
                    merged_args.append(actual_args[arg_default.unwrap])
                elif arg_default is splat_args_placeholder:
                    assert_is_last_positional_placeholder(arg_index)
                    merged_args.extend(actual_args[placeholder_index:])
                else: # real argument
                    merged_args.append(arg_default)
            
            merged_kwargs = dict()
            for kwarg_index, (kwarg_name, kwarg_default) in enumerate(merged_default_kwargs.items()):
                if kwarg_default in all_placeholders:
                    placeholder_index += 1
                if kwarg_default in placeholders:
                    assert_has_enough_args(placeholder_index)
                    merged_kwargs[kwarg_name] = actual_args[placeholder_index]
                elif kwarg_default in reordering_placeholders:
                    assert_has_enough_args(kwarg_default.unwrap)
                    merged_kwargs[kwarg_name] = actual_args[kwarg_default.unwrap]
                elif kwarg_default is splat_args_placeholder:
                    assert_is_last_keyword_placeholder(kwarg_index)
                    merged_kwargs[kwarg_name] = actual_args[placeholder_index:]
                else: # real argument
                    merged_kwargs[kwarg_name] = kwarg_default
            
            
            return merged_args, merged_kwargs
        
        @functools.wraps(self)
        def wrapper(*actual_args, **actual_kwargs):
            merged_args, merged_kwargs = merge_arguments(actual_args, actual_kwargs)
            return self(*merged_args, **merged_kwargs)
        return wrapper
    
    @wrapped
    def compose(self, outer):
        """Compose two functions.
        
        >>>  inner_function.compose(outer_function) \\
        ...    == lambda *args, **kwargs: outer_function(inner_function(*args, **kwargs))
        """
        return lambda *args, **kwargs: outer(self(*args, **kwargs))
    # REFACT consider aliasses wrap = chain = cast = compose
    
    @wrapped
    def star_call(self, args, **kwargs):
        # REFACT consider if this might be better called map/ lift to use the functional concepts more directly
        # REFACT might be nice to check wether args is a sequence or a dict and ** it if dict
        # REFACT consider if rename is wise to clarify the difference between Iterable.star_call and Callable.star_call
        # Maybe the same name is good, as they pretty much do the same thing, just with inverted arguments?
        return self(*args, **kwargs)

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
    
    All iterators return unwrapped elements by design. Fluent is meant to facilitate 
    chaining, not sprad it's wrapper everywhere. This means you will have to rewrap 
    occasionally in handwritten iterator methods.
    
    Where methods return infinite iterators, the non i-prefixed method name is skipped.
    See `icycle` as an example.
    """
    
    # __iter__ is not wrapped, and implicitly unwrap. If this is unwanted, use one of the explicit iterators
    # This is neccesary becasue otherwise all iterations would implicitly wrap the iterated elements, making it
    # impossible to use this library in a halfway sensible way with explicit wrapping and unwrapping.
    # iter is unwrapped, so it behaves the same as any other explicit iteration
    iter = __iter__ = unwrapped(iter)
    
    @wrapped
    def star_call(self, function, *args, **kwargs):
        "Calls `function(*self)`, but allows to prepend args and add kwargs."
        return function(*args, *self, **kwargs)
    
    # This looks like it should be the same as 
    # starcall = wrapped(lambda function, wrapped, *args, **kwargs: function(*wrapped, *args, **kwargs))
    # but it's not. Why?
    
    @wrapped
    def get(self, target_index, default=_absent_default_argument):
        # Not sure this is the best way to support iterators - but there is no clear way in which we can retain the generator 
        if not isinstance(self, typing.Sized):
            # This is very suboptimal, as it consumes the generator till the asked for index. Still, I don't want this to crash on infinite iterators by just doing tuple(self)
            for index, element in enumerate(self):
                if index == target_index:
                    return element
            return default
        
        if default is not _absent_default_argument and target_index >= len(self):
            return default
        
        return self[target_index]
        
    @wrapped
    def join(self, with_what=''):
        """"Like str.join, but the other way around. Bohoo!
        
        Also calls str on all elements of the collection before handing 
        it off to str.join as a convenience.
        """
        return with_what.join(map(str, self))
    
    ## Converters ........................................
    
    # REFACT consider to deprecate these, as .call({set, list, dict, set}) does the job
    tuplify = wrapped(tuple)
    listify = wrapped(list)
    dictify = wrapped(dict)
    setify = wrapped(set)

    freeze = tuplify
    
    ## Reductors .........................................
    
    @wrapped
    def len(self):
        """Just like len(), but also works for iterators.
        
        Beware, that it has to consume the iterator to compute it's length"""
        # REFACT there are iterators that know their length, check and use that!
        if isinstance(self, typing.Iterator):
            length = 0
            for i in self:
                length += 1
            return length
        else:
            return len(self)
    
    max = wrapped(max)
    min = wrapped(min)
    sum = wrapped(sum)
    any = wrapped(any)
    all = wrapped(all)
    reduce = wrapped_forward(functools.reduce)
    
    ## Iterators .........................................
    
    @wrapped
    def ieach(self, a_function):
        """call `a_function` on each elment in self purely for the side effect, then yield the input element"""
        for element in self:
            a_function(element)
            yield element
    each = tupleize(ieach)
    
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
        """Cut self into tupels of length group_length
        s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ...
        """
        return zip(*[iter(self)]*group_length)
    grouped = tupleize(igrouped)
    
    izip = wrapped(zip)
    zip = tupleize(izip)
    
    @wrapped
    def iflatten(self, level=math.inf, stop_at_types=(str, bytes)):
        """Modeled after rubys array.flatten @see http://ruby-doc.org/core-1.9.3/Array.html#method-i-flatten
        
        Calling flatten on string likes would lead to infinity recursion, thus @arg stop_at_types.
        If you want to flatten those, use a combination of @arg level and @arg stop_at_types.
        """
        for element in self:
            if level > 0 and (isinstance(element, typing.Iterable) and not isinstance(element, stop_at_types)):
                yield from wrap(element).iflatten(level=level-1)
            else:
                yield element
        return
    flatten = tupleize(iflatten)
    
    @wrapped
    def ireshape(self, *spec):
        """Modeled to be the inverse of flatten, allowing to create structure from linearity.
        
        Allows you to turn `(1,2,3,4)` into `((1,2),(3,4))`.
        Very much inspired by numpy.reshape. @see https://docs.scipy.org/doc/numpy/reference/generated/numpy.reshape.html
        
        @argument spec integer of tuple of integers that give the spec for the dimensions of the returned structure. 
        The last dimension is inferred as needed. For example:
        
        >>> _([1,2,3,4]).reshape(2)._ == ((1,2),(3,4))
        
        Please note that 
        
        >>> _([1,2,3,4]).reshape(2,2)._ == (((1,2),(3,4)),)
        
        The extra tuple around this is due to the specification being, two tuples of two elements which is possible
        exactly once with the given iterable.
        
        This iterator will *not* ensure that the shape you give it will generate fully 'rectangular'.
        This means that the last element in the generated sequnce the number of elements can be different!
        This tradeoff is made, so it works with infinite sequences.
        """
        def chunkify(iterable, chunk_size):
            assert chunk_size >= 1
            collector = []
            for element in iterable:
                collector.append(element)
                if len(collector) == chunk_size:
                    yield tuple(collector)
                    collector = []
            if len(collector) != 0:
                yield tuple(collector)
        
        if 0 == len(spec):
            return self
        
        current_level, *other_levels = spec
        
        return wrap(chunkify(self, current_level)).ireshape(*other_levels).unwrap
    
    reshape = tupleize(ireshape)
    
    igroupby = wrapped(itertools.groupby)
    def groupby(self, *args, **kwargs):
        """See igroupby for most of the docs.
        
        Correctly consuming an itertoo.groupby is surprisingly hard, thus this non tuple returning version that does it correctly.
        """
        result = []
        for key, values in self.igroupby(*args, **kwargs):
            result.append((key, tuple(values)))
        return wrap(tuple(result), previous=self)
    
    # itertools method support ............................
    
    itee = wrapped(itertools.tee)
    
    islice = wrapped(itertools.islice)
    slice = tupleize(islice)
    
    icycle = wrapped(itertools.cycle)
    
    iaccumulate = wrapped(itertools.accumulate)
    accumulate = tupleize(iaccumulate)
    
    idropwhile = wrapped(itertools.dropwhile, self_index=1)
    dropwhile = tupleize(idropwhile)
    
    ifilterfalse = wrapped(itertools.filterfalse, self_index=1)
    filterfalse = tupleize(ifilterfalse)
    
    ipermutations = wrapped(itertools.permutations)
    permutations = tupleize(ipermutations)
    
    icombinations = wrapped(itertools.combinations)
    combinations = tupleize(icombinations)
    
    icombinations_with_replacement = wrapped(itertools.combinations_with_replacement)
    combinations_with_replacement = tupleize(icombinations_with_replacement)
    
    iproduct = wrapped(itertools.product)
    product = tupleize(iproduct)
    
    # TODO make all (applicable?) methods of itertools available here

@protected
class Mapping(Iterable):
    """Index into dicts like objects. As JavaScript can."""
    
    def __getattr__(self, name):
        """Support JavaScript like dict item access via attribute access"""
        if name in self.unwrap:
            return self[name]
        
        return super().__getattr__(name)
    
    # REFACT consider rename to splat_call to differentiate that it does something else tha
    # Callable.star_call
    @wrapped
    def star_call(self, function, *args, **kwargs):
        "Calls `function(**self)`, but allows to add args and set defaults for kwargs."
        return function(*args, **dict(kwargs, **self))

@protected
class Set(Iterable):
    """Mostly like Iterable"""

    freeze = wrapped(frozenset)

@protected
class Text(Iterable):
    """Supports most of the regex methods as if they where native str methods"""
    
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

def _make_operator(name):
    __op__ = getattr(operator, name)
    @functools.wraps(__op__)
    def wrapper(self, *others):
        # Can't easily use .curry() here, as that would return a wrapped object and I don't want the lambda builder methods to return wrapped objects - yet.
        # return wrap(__op__).curry(_, *others) #.unwrap
        # FIXME the order of the placeholder likely needs to depend on the operator. All the __r*__ operators need it reversed?
        return lambda placeholder: __op__(placeholder, *others)
    return wrapper

@protected
class Each(Wrapper):
    """Create functions from expressions.

    Use ``each.foo`` to create attrgetters, ``each['foo']`` to create itemgetters,
    ``each.call.foo()`` to create methodcallers or ``each == 'foo'`` (with pretty much any operator) to create callable operators.
    
    Note: All generated functions never wrap their arguments or return values.
    """
    
    # REFACT consider returning a wrapper that knows wether it is called immediately, or if it is called by one of the iterators
    # The problem is that the call operator needs to differentiate if it is called from within one map/ filter/ etc. or from 
    # a user that wants to map a call oeration or 
    for name in dir(operator):
        if not name.startswith('__') or name == '__doc__':
            continue
        locals()[name] = _make_operator(name)
    del name # prevent promotion to class variable
    
    # there is no operator form for x in iterator, such an api is only the wrong way around on iterator which inverts the reading direction
    def in_(self, haystack):
        """Implements a method version of the `in` operator. 
        
        So `_.each.in_('bar')` is roughly equivalent to `lambda each: each in 'bar'`
        """
        return haystack.__contains__
    
    def not_in(self, haystack):
        """Implements a method version of the `not in` operator. 
        
        So `_.each.not_in('bar')` is roughly equivalent to `lambda each: each not in 'bar'`
        """
        def not_contains(needle):
            """The equivalent of  operator.__not_contains__ if it would exist."""
            return needle not in haystack
        return not_contains
    
    def __getattr__(self, name):
        # Experimentally using this to allow attribute access for dictionaries just as all other wrapped dicts would allow
        return lambda obj: getattr(_(obj), name).unwrap
        # return operator.attrgetter(name)
    
    def __getitem__(self, index):
        return operator.itemgetter(index)
    
    @property
    def call(self):
        """Helper to generate operator.methodcaller objects from normal calls.
        
        `_.call.method('with_arguments')` is roughly equivalent to `lambda each: each.method('with_arguments)`
        """
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

each_marker = "lambda generator"
each = Each(each_marker, previous=None, chain=None)
each.__name__ = 'each'
public(each)

call = each.call
call.__name__ = 'call'
public(call)

_reordering_placeholders = []
# add reordering placeholders to wrap to make it easy to reorder arguments in curry
# arbitrary limit, can be increased as neccessary
for index in range(NUMBER_OF_NAMED_ARGUMENT_PLACEHOLDERS):
    locals()[f'_{index}'] = public(wrap(index), f'_{index}')
    _reordering_placeholders.append(locals()[f'_{index}'])
_args = public(wrap('*'), '_args')
