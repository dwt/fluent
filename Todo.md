# Before next release

…

# Bunch of Ideas

Consider if Callable.__call__() and Callable.cury() should not auto unwrap their arguments? This behaviour seems quite different to the rest of the library.

Docs
    Check all methods have a docstring
    Check all the methods from itertools are forwarded where sensible
    Consider using http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html for more readable docstrings
    Use doctest to keep the code examples healthy
    When wrapping methods with documentation, prepend the argument mapping to that documentation to make it easier to read.
    consider to add the curried arg spec to the help / repr() output of a curried function.

Consider .forget() method that 'forgets' the history of the chain, so python can reclaim the memory of all those intermediate results without one having to terminate the chain. Not sure what this would give us? Maybe better on wrap as a keyword only argumnet like (forget_history=True)

Set build server with different python versions on one of the public build server plattforms

Curry: consider supporting turning keyword argumnents into positional arguments (the other way around already works)

Consider Number wrapper that allows calling stuff like itertools.count, construct ranges, stuff like that
consider numeric type to do stuff like wrap(3).times(...)
    or wrap([1,2,3]).call(len).times(yank_me)

Consider bool wrapper, that allows creating operator versions of if_(), else_(), elsif_(), not_(), ...

add Callable.vectorize() similar to how it works in numpy - not sure this is actually sensible? Interesting experiment
    # vectorize is much like curry
    # possible to reuse placeholders
    # if wanted, could integrate vectorization in curry
    # own method might be cleaner?
    # could save signature transformation and execute it in call
    # or just wrap a specialized wrapped callable?
    # signature transformation specification?
    # should allow to describe as much of the broadcasting rules of numpy
    # ideally compatible to the point where a vectorization can meaningfully work with np.vectorize
    # 
    # _.map()? 
    # def vectorize(self, *args, **kwargs):
    #     pass

Consider replacing all placeholders by actually unique objects

Allow setting new attributes on wrapped objects through the wrapper -> test_creating_new_attributes_should_create_attribute_on_wrapped_object
This needs solving that the objects themselves need to create attributes while the module is parsed, but they need to be 'closed' after the module has finished parsing.

add .unwrapped (or something similar) to have .unwrap as a higher order function
    this should allow using .curry() in contexts where the result cannot be 

allow [{'foo': 'bar'},{'foo':'baz'}].map(each.foo)

find a way to allow something like map(_.each.foo, _.each.bar) or .map(.each['foo', 'bar'])
Rework _.each.call.foo(bar) so 'call' is no longer a used-up symbol on each.
Also _.each.call.method(...) has a somewhat different meaning as the .call method on callable
could _.each.method(_, ...) work when auto currying is enabled?

Roundable (for all numeric needs?)
    round, times, repeat, if_true, if_false, else_
if_true, etc. are pretty much like conditional versions of .tee() I guess.
.if_true(function_to_call).else_(other_function_to_call)
allow to make ranges by _(1).range(10)
support _.if()

example why list comprehension is really bad (Found in zope unit tests)

def u7(x):
    stuff = [i + j for toplevel, in x for i, j in toplevel]
    assert stuff == [3, 7]

add itertools and collections methods where it makes sense

Would be really nice to allow inputting the chain into a list comprehension in a readable way

consider what it takes to allow reloading fluentpy itself. This is not so super easy, as the executable module caches all the old values on the function (functools.wraps does that). So afterwards all manner of instance checks don't work anymore. Therefore, just defining __getattr__ on the instance method doesn't quite work

consider typing all the methods for better autocompletion?
