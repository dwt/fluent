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
def wrap(wrapped, *, previous=None):
    """Factory method, wraps anything and returns the appropriate :class:`.Wrapper` subclass.
    
    This is the main entry point into the fluent wonderland. Wrap something and 
    everything you call off of that will stay wrapped in the appropriate wrappers.
    
    It is usually imported in one of the following ways:
    
        >>> import fluentpy as _
        >>> import fluentpy as _f
        >>> from fluentpy import wrap
    
    ``wrap`` is the original name of the function, though I rarely recommend to use it by this name.
    """
    if isinstance(wrapped, Wrapper):
        return wrapped
    
    by_type = (
        (types.ModuleType, ModuleWrapper),
        (typing.Text, TextWrapper),
        (typing.Mapping, MappingWrapper),
        (typing.AbstractSet, SetWrapper),
        (typing.Iterable, IterableWrapper),
        (typing.Callable, CallableWrapper),
    )
    
    for clazz, wrapper in by_type:
        if isinstance(wrapped, clazz):
            return wrapper(wrapped, previous=previous)
    
    return Wrapper(wrapped, previous=previous)

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
        result = wrapped_function(*args[:self_index], self.unwrap, *args[self_index:], **kwargs)
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
    """Wrap the returned obect in a tuple to force execution of iterators.
    
    Especially useful to de-iterate methods / function
    """
    @functools.wraps(wrapped_function)
    def wrapper(self, *args, **kwargs):
        return wrap(tuple(wrapped_function(self, *args, **kwargs)), previous=self)
    return wrapper

@protected
class Wrapper(object):
    """Universal wrapper.
    
    This class ensures that all function calls and attribute accesses 
    (apart from such special CPython runtime accesses like ``object.__getattribute__``, 
    which cannot be intercepted) will be wrapped with the wrapper again. This ensures 
    that the fluent interface will persist and everything that is returned is itself 
    able to be chained from again.
    
    All returned objects will be wrapped by this class or one of its sub classes, which 
    add functionality depending on the type of the wrapped object. I.e. iterables will 
    gain the collection interface, mappings will gain the mapping interface, strings 
    will gain the string interface, etc.
    
    If you want to access the actual wrapped object, you will have to unwrap it explicitly
    using ``.unwrap`` or ``._``
    
    Please note: Since most of the methods on these objects are actual standard library methods that are 
    simply wrapped to rebind their (usually first) parameter to the object they where called on.
    So for example: ``repr(something)`` becomes ``_(something).repr()``.
    This means that the (unchanged) documentation (often) still shows the original signature 
    and refers to the original arguments. A little bit of common sense might therefore be required.
    """
    
    # Would love to restrict slots, but would also need to do that on all subclasses
    # and it prevents me from adjusting doc strings where i want to.
    # __slots__ = ['__wrapped', '__previous']
    
    def __init__(self, wrapped, *, previous):
        # assert wrapped is None and previous is None, 'Cannot chain off of None'
        if wrapped is None:
            assert previous is not None, 'Cannot chain off of None'
        
        self.__wrapped = wrapped
        self.__previous = previous
    
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
    # Maybe this works if all internal classes define # __slots__?
    # def __setattr__(self, name, value):
    #     if not _wrapper_is_sealed:
    #         return super().__setattr__(name, value)
    #     else:
    #         setattr(self.unwrap(), name, value)
    
    # Breakouts
    
    @property
    def unwrap(self):
        """Returns the underlying wrapped value of this wrapper instance.
        
        All other functions return wrappers themselves unless explicitly stated.
        
        Alias: ``_``
        """
        return self.__wrapped
    _ = unwrap # alias
    
    # REFACT consider rename / alias .prev so there is less reason to use .self
    @property
    def previous(self):
        """Returns the previous wrapper in the chain of wrappers.
        
        This allows you to walk the chain of wrappers that where created in your expression. 
        Mainly used internally but might be useful for introspection.
        """
        return self.__previous
    
    @property
    def self(self):
        """Returns the previous wrapped object. This is especially usefull for APIs that return None.
        
        For example ``_([1,3,2]).sort().self.print()`` will print the sorted list, even though
        ``sort()`` did return ``None``.
        
        This is simpler than using .previous as there are often multiple wrappers involved where you might expect only one.
        E.g. ``_([2,1]).sort().self._ == [1,2]`` but ``_([2,1]).sort().previous._`` will return the function ``list.sort()``
        as the attrget and call are two steps of the call chain.
        
        This eases chaining using APIs that where not designed with chaining in mind. 
        (Inspired by SmallTalk's default behaviour)
        """
        # This behavior is always triggered, not just in the `None` return case to avoid
        # code that behaves differently for methods that _sometimes_ return `None`.
        
        # Depending on wether the previous method was a transplanted method
        # we need to go back one level or two
        if isinstance(self.previous, CallableWrapper):
            return self.previous.previous
        else:
            return self.previous
    
    @property
    def proxy(self):
        """Allow access to shadowed attributes.
        
        Breakout that allows access to attributes of the wrapped object that are shadowed by 
        methods on the various wrapper classes. Wrapped of course.
        
            >>> class UnfortunateNames(object):
            >>>     def previous(self, *args):
            >>>         return args
        
        This raises TypeError, because Wrapper.previous() shadows UnfortunateNames.previous():
        
            >>> _(UnfortunateNames()).previous('foo')) 
        
        This works as expected:
        
            >>> _(UnfortunateNames()).proxy.previous('foo')._) == ('foo',)
        """
        class Proxy(object):
            def __init__(self, proxied):
                self.__proxied = proxied
            def __getattr__(self, name):
                return wrap(getattr(self.__proxied.unwrap, name), previous=self.__proxied)
        return Proxy(self)
    
    # Utilities
    
    @wrapped
    def call(self, function, *args, **kwargs):
        """Call function with self as its first argument.
        
        >>> _('foo').call(list)._ == list('foo')
        >>> _('fnord').call(textwrap.indent, prefix='  ')._ == textwrap.indent('fnord', prefix='  ')
        
        Call is mostly usefull to insert normal functions that express some algorithm into the call chain. For example like this:
        
        >>> seen = set()
        >>> def havent_seen(number):
        ...     if number in seen:
        ...         return False
        ...     seen.add(number)
        ...     return True
        >>> (
        ...     _([1,3,1,3,4,5,4])
        ...     .dropwhile(havent_seen)
        ...     .print()
        ... )
        
        Less obvious, it can also be used as a decorator, however the result can be confusing, so maybe not as recomended:
        
        >>> numbers = _(range(5))
        >>> @numbers.call
        ... def items(numbers):
        ...     for it in numbers:
        ...         yield it
        ...         yield it
        >>> items.call(list).print()
        
        Note the difference from ``.__call__()``. This applies ``function(self, …)`` instead of ``self(…)``.
        """
        return function(self, *args, **kwargs)
    
    def to(self, function, *args, **kwargs):
        """Like .call() but returns an unwrapped result.
        
        This makes ``.to()`` really convenient to terminate a call chain by converting to a type that perhaps itself con."""
        return function(self.unwrap, *args, **kwargs)
    
    setattr = wrapped(setattr)
    getattr = wrapped(getattr)
    hasattr = wrapped(hasattr)
    delattr = wrapped(delattr)
    
    isinstance = wrapped(isinstance)
    # REFACT wrong class, needs to be on a typing.Type specific subclass
    issubclass = wrapped(issubclass)
    
    dir = wrapped(dir)
    vars = wrapped(vars)
    print = wrapped(print)
    pprint = wrapped(pprint.pprint)
    help = wrapped(help)
    type = wrapped(type)
    str = wrapped(str)
    repr = wrapped(repr)

# REFACT consider to use wrap as the placeholder to have less symbols? Probably not worth it...
virtual_root_module = "virtual root module"

@protected
class ModuleWrapper(Wrapper):
    """The :class:`.Wrapper` for modules transforms attribute accesses into pre-wrapped imports of sub-modules."""
    
    # __slots__ = ['__name__', '__qualname__']
    
    def __getattr__(self, name):
        if hasattr(self.unwrap, name):
            return wrap(getattr(self.unwrap, name))
        
        module = None
        if self.unwrap is virtual_root_module:
            module = importlib.import_module(name)
        else:
            module = importlib.import_module('.'.join((self.unwrap.__name__, name)))
        
        return wrap(module)
    
    # REFACT consider to deprecate and remove this function since its behaviour is so unpredictable
    @wrapped
    @functools.wraps(importlib.reload)
    def reload(self):
        importlib.reload(self)
        return self

lib = ModuleWrapper(virtual_root_module, previous=None)
lib.__name__ = 'lib'
lib.__qualname__ = 'fluentpy.lib'  # Not really neccessary, but sphinx autoapi explodes without it
lib.__doc__ = """\
Imports as expressions. Already pre-wrapped.

All attribute accesses to instances of this class are converted to
an import statement, but as an expression that returns the wrapped imported object.

Example:

>>> lib.sys.stdin.read().map(print)

Is equivalent to

>>> import sys
>>> wrap(sys).stdin.read().map(print)

But of course without creating the intermediate symbol 'stdin' in the current namespace.

All objects returned from lib are pre-wrapped, so you can chain off of them immediately.
"""
public(lib)

@protected
class CallableWrapper(Wrapper):
    """The :class:`.Wrapper` for callables adds higher order methods."""
    
    # __slots__ = []
    
    @wrapped
    def __call__(self, *args, **kwargs):
        """Call through to the wrapped function."""
        return self(*args, **kwargs)
    
    @wrapped
    def curry(self, *default_args, **default_kwargs):
        """Like functools.partial, but with a twist.
        
        If you use ``wrap`` or ``_`` as a positional argument, upon the actual call, 
        arguments will be left-filled for those placeholders.
        
        >>> _(operator.add).curry(_, 'foo')('bar')._ == 'barfoo'
        
        If you use wrap._$NUMBER (with $NUMBER < 10) you can take full control 
        over the ordering of the arguments.
        
        >>> _(a_function).curry(_._0, _._0, _.7)
        
        This will repeat the first argument twice, then take the 8th and ignore all in between.
        
        You can also mix numbered with generic placeholders, but since it can be hard to read, 
        I would not advise it.
        
        There is also ``_._args`` which is the placeholder for the ``*args`` variable argument list specifier.
        (Note that it is only supported in the last position of the positional argument list.)
        
        >>> _(lambda x, y=3: x).curry(_._args)(1, 2)._ == (1, 2)
        >>> _(lambda x, y=3: x).curry(x=_._args)(1, 2)._ == (1, 2)
        """
        # REFACT consider, would it be easier to actually generate a wrapper function that has an argspec
        # according to the given spec?
        # Note to self: _.kwargs wouldn't make sense, as that s already the default behaviour of python
        
        placeholders = tuple(_wrap_alternatives)
        reordering_placeholders = tuple(_reordering_placeholders)
        splat_args_placeholder = wrap._args
        all_placeholders = placeholders + reordering_placeholders + (splat_args_placeholder,)
        
        def merge_arguments(actual_args, actual_kwargs):
            """Processing positional arguments first, then keyword arguments to keep this as 
            compatible as possible with the way Python works
            """
            # This works because dict() is sorted in python3.6+
            merged_default_kwargs = dict(default_kwargs, **actual_kwargs)
            
            def assert_has_enough_args(required_number):
                assert len(actual_args) > required_number, \
                    'Not enough arguments given to curried function. Need at least %i, got %i: <%r>' \
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
            used_arg_indexes = set()
            for arg_index, arg_default in enumerate(default_args):
                if arg_default in all_placeholders:
                    placeholder_index += 1
                if arg_default in placeholders:
                    assert_has_enough_args(placeholder_index)
                    merged_args.append(actual_args[placeholder_index])
                    used_arg_indexes.add(placeholder_index)
                elif arg_default in reordering_placeholders:
                    assert_has_enough_args(arg_default.unwrap)
                    merged_args.append(actual_args[arg_default.unwrap])
                    used_arg_indexes.add(arg_default.unwrap)
                elif arg_default is splat_args_placeholder:
                    assert_is_last_positional_placeholder(arg_index)
                    merged_args.append(actual_args[placeholder_index:])
                    used_arg_indexes.update(range(placeholder_index, len(actual_args)))
                else: # real argument
                    merged_args.append(arg_default)
            
            merged_kwargs = dict()
            for kwarg_index, (kwarg_name, kwarg_default) in enumerate(merged_default_kwargs.items()):
                if kwarg_default in all_placeholders:
                    placeholder_index += 1
                if kwarg_default in placeholders:
                    assert_has_enough_args(placeholder_index)
                    merged_kwargs[kwarg_name] = actual_args[placeholder_index]
                    used_arg_indexes.add(placeholder_index)
                elif kwarg_default in reordering_placeholders:
                    assert_has_enough_args(kwarg_default.unwrap)
                    merged_kwargs[kwarg_name] = actual_args[kwarg_default.unwrap]
                    used_arg_indexes.add(kwarg_default.unwrap)
                elif kwarg_default is splat_args_placeholder:
                    assert_is_last_keyword_placeholder(kwarg_index)
                    merged_kwargs[kwarg_name] = actual_args[placeholder_index:]
                    used_arg_indexes.update(range(placeholder_index, len(actual_args)))
                else: # real argument
                    merged_kwargs[kwarg_name] = kwarg_default
            
            last_used_argument = max(used_arg_indexes, default=-1)
            merged_args.extend(actual_args[last_used_argument+1:])
            
            # FIXME consider that it might actually be a feature to be able to drop extra arguments
            # Look into ways to make that explicit, something that hoovers up all extra arguments?
            
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
        # REFACT consider if rename is wise to clarify the difference between IterableWrapper.star_call and CallableWrapper.star_call
        # Maybe the same name is good, as they pretty much do the same thing, just with inverted arguments?
        return self(*args, **kwargs)

@protected
class IterableWrapper(Wrapper):
    """The :class:`.Wrapper` for iterables adds iterator methods to any iterable.
    
    Most iterators in Python 3 return an iterator by default, which is very interesting 
    if you want to build efficient processing pipelines, but not so hot for quick and 
    dirty scripts where you have to wrap the result in a list() or tuple() all the time 
    to actually get at the results (e.g. to print them) or to actually trigger the 
    computation pipeline.
    
    Thus all iterators on this class are by default immediate, i.e. they don't return the 
    iterator but instead consume it immediately and return a tuple. Of course if needed, 
    there is also an i{map,zip,enumerate,...} version for your enjoyment that returns the 
    iterator.
    
    Iterating over wrapped iterators yields unwrapped elements by design. This is neccessary to make 
    ``fluentpy`` interoperable with the standard library. This means you will have to rewrap 
    occasionally in handwritten iterator methods or when iterating over a wrapped iterator 
    
    Where methods return infinite iterators, the non i-prefixed method name is skipped.
    See ``icycle`` for an an example.
    """
    
    # __slots__ = []
    
    # __iter__ is not wrapped, and implicitly unwrap. If this is unwanted, use one of the explicit iterators
    # This is neccesary becasue otherwise all iterations would implicitly wrap the iterated elements, making it
    # impossible to use this library in a halfway sensible way with explicit wrapping and unwrapping.
    # iter is unwrapped, so it behaves the same as any other explicit iteration
    iter = __iter__ = unwrapped(iter)
    
    @wrapped
    def star_call(self, function, *args, **kwargs):
        "Calls ``function(*self)``, but allows to prepend args and add kwargs."
        return function(*args, *self, **kwargs)
    
    # This looks like it should be the same as 
    # starcall = wrapped(lambda function, wrapped, *args, **kwargs: function(*wrapped, *args, **kwargs))
    # but it's not. Why?
    
    @wrapped
    def get(self, target_index, default=_absent_default_argument):
        """Like ```dict.get()`` but for IterableWrappers and able to deal with generators"""
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
        """Like str.join, but the other way around. Bohoo!
        
        Also calls str on all elements of the collection before handing 
        it off to str.join as a convenience.
        """
        return with_what.join(map(str, self))
    
    ## Converters ........................................
    
    freeze = wrapped(tuple)
    
    ## Reductors .........................................
    
    @wrapped
    def len(self):
        """Just like len(), but also works for iterators.
        
        Beware, that it has to consume the iterator to compute its length"""
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
        """call ``a_function`` on each elment in self purely for the side effect, then yield the input element."""
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
    flatten = tupleize(iflatten)
    
    @wrapped
    def ireshape(self, *spec):
        """Creates structure from linearity.
        
        Allows you to turn ``(1,2,3,4)`` into ``((1,2),(3,4))``.
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
        
        Correctly consuming an itertools.groupby is surprisingly hard, thus this non tuple returning version that does it correctly.
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
class MappingWrapper(IterableWrapper):
    """The :class:`.Wrapper` for mappings allows indexing into mappings via attribute access.
    
    Indexing into dicts like objects. As JavaScript can.
    
    >>> _({ 'foo': 'bar: }).foo == 'bar
    """
    
    # __slots__ = []
    
    def __getattr__(self, name):
        """Support JavaScript like dict item access via attribute access"""
        if name in self.unwrap:
            return self[name]
        
        return super().__getattr__(name)
    
    # REFACT consider rename to splat_call to differentiate that it does something else tha
    # CallableWrapper.star_call
    @wrapped
    def star_call(self, function, *args, **kwargs):
        "Calls ``function(**self)``, but allows to add args and set defaults for kwargs."
        return function(*args, **dict(kwargs, **self))

@protected
class SetWrapper(IterableWrapper):
    """The :class:`.Wrapper` for sets is mostly like :class:`.IterableWrapper`.
    
    Mostly like IterableWrapper
    """

    freeze = wrapped(frozenset)

@protected
class TextWrapper(IterableWrapper):
    """The :class:`.Wrapper` for str adds regex convenience methods.
    
    Supports most of the regex methods as if they where native str methods
    """
    
    # __slots__ = []
    
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

def _make_operator(operator_name):
    __op__ = getattr(operator, operator_name)
    @functools.wraps(__op__)
    def wrapper(self, *others):
        def operation(placeholder):
            return __op__(placeholder, *others)
        return self._EachWrapper__operation.compose(operation)._  # auto unwraps
    return wrapper

reverse_operator_names = [
    '__radd__', '__rsub__', '__rmul__', '__rmatmul__', '__rtruediv__', 
    '__rfloordiv__', '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__', 
    '__rrshift__', '__rand__', '__rxor__', '__ror_',
]

def _make_reverse_operator(operator_name):
    def wrapper(self, other):
        def operation(placeholder):
            return getattr(placeholder, operator_name)(other)
        return self._EachWrapper__operation.compose(operation)._  # auto unwraps
    wrapper.__name__ = operator_name
    return wrapper


# REFACT consider to inherit from Callable to simplify methods. On the other hand, I want as few methods on this as possible, perhaps even inheriting from Wrapper is a bad idea already.
@protected
class EachWrapper(object):
    """The :class:`.Wrapper` for expressions (see documentation for :data:`.each`).
    """
    
    # __slots__ = ['__operation', '__name']
    
    def __init__(self, operation, name):
        self.__operation = operation
        self.__name = name
    
    @property
    def unwrap(self):
        return self.__operation._
    _ = unwrap # alias
    
    def __repr__(self):
        return f'fluentpy.wrap({self.__name})'
    __str__ = __repr__ # alias
    
    # Operator support
    
    for name in dir(operator):
        if not name.startswith('__') or name == '__doc__':
            continue
        locals()[name] = _make_operator(name)
    del name # prevent promotion to class variable
    
    # REFACT is there a way to get a reliable list of these operations from the stdlib somewhere?
    # These are currently scraped from the documentation
    for name in reverse_operator_names:
        locals()[name] = _make_reverse_operator(name)
    del name
    
    # there is no operator form for x in iterator, such an api is only the wrong way around on iterator which inverts the reading direction
    def in_(self, haystack):
        """Implements a method version of the ``in`` operator. 
        
        So ``_.each.in_('bar')`` is roughly equivalent to ``lambda each: each in 'bar'``
        """
        return EachWrapper(self.__operation.compose(haystack.__contains__), name=f'{self.__name} in {haystack!r}')
    
    def not_in(self, haystack):
        """Implements a method version of the ``not in`` operator. 
        
        So ``_.each.not_in('bar')`` is roughly equivalent to ``lambda each: each not in 'bar'``
        """
        def not_contains(needle):
            """The equivalent of  operator.__not_contains__ if it would exist."""
            return needle not in haystack
        return EachWrapper(self.__operation.compose(not_contains), name=f'{self.__name} not in {haystack!r}')
    
    # Generic operation support
    # These need to be below the operators above as we need to override operator.__getattr__ and operator.__getitem__
    
    def __getattr__(self, name):
        """Helper to generate something like operator.attrgetter from attribute accesses.
    
        ``_.each.some_attribute`` is roughly equivalent to ``lambda each: getattr(each, 'some_attribute')``
        """
        def operation(obj):
            return _(obj).__getattr__(name)._
        
        return EachWrapper(self.__operation.compose(operation), name=f'{self.__name}.{name}')
    
    def __getitem__(self, index):
        """Helper to generate something like operator.itemgetter from the getitem syntax.
    
        ``_.each[3]`` is roughly equivalent to ``lambda each: each[3]``
        """
        def operation(obj):
            return _(obj)[index]._
        return EachWrapper(self.__operation.compose(operation), name=f'{self.__name}[{index!r}]')
    
    def __call__(self, *args, **kwargs):
        """Helper to generate something like operator.methodcaller from calls.
    
        ``_.each.method('with_arguments')`` is roughly equivalent to ``lambda each: each.method('with_arguments)``
        """
        def operation(obj):
            return _(obj)(*args, **kwargs)._
        return EachWrapper(self.__operation.compose(operation), name=f'{self.__name}(*{args!r}, **{kwargs!r})')
    
def identity(each): return each
each = EachWrapper(_(identity), name='each')
each.__name__ = 'each'
each.__doc__ = """\
Create functions from expressions.

Use ``each.foo._`` to create attrgetters, ``each['foo']._`` to create itemgetters,
``each.foo()._`` to create methodcallers or ``each == 'foo'`` (with pretty much any operator) to create callable operators.

Many operations can be chained, to extract a deeper object by iterating a container. E.g.:

>>> each.foo.bar('baz')['quoox']._

creates a callable that will first get the attribute ``foo``, then call the method ``bar('baz')`` on the result
and finally applies gets the item 'quoox' from the result. For this reason, all callables need to be unwrapped before they
are used, as the actual application would just continue to build up the chain on the original callable otherwise.

Apply an operator like  ``each < 3`` to generate a callable that applies that operator. Different to all other cases,
applying any binary operator auto terminates the expression generator, so no unwrapping is neccessary.

Note: The generated functions never wrap their arguments or return values.
"""
public(each)


_reordering_placeholders = []
# add reordering placeholders to wrap to make it easy to reorder arguments in curry
# arbitrary limit, can be increased as neccessary
for index in range(NUMBER_OF_NAMED_ARGUMENT_PLACEHOLDERS):
    name = f'_{index}'
    placeholder = wrap(index)
    placeholder.__doc__ = f'Placeholder for :meth:`.CallableWrapper.curry` to access argument at index {index}.'
    _reordering_placeholders.append(placeholder)
    locals()[name] = public(placeholder, name)
del index, name, placeholder

_args = public(wrap('*'), '_args')
