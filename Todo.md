# Before next release

undo flatten special case for str/bytes as that should be better handled by stop_at_type or level arguments
get documentation built and upload it
    check all methods have a docstring
check all the methods from itertools are forwarded where sensible

# Done

# Bunch of Ideas
Set build server with different python versions on one of the public build server plattforms

consider supporting turning keyword argumnents into positional arguments in curry

consider Number wrapper that allows calling stuff like itertools.count, construct ranges, stuff like that

consider bool wrapper, that allows creating operator versions of if_(), else_(), elsif_(), not_(), ...

add Callable.vectorize() similar to how it works in numpy

add Module.reload() to reload modules
replace all placeholders by actually unique objects

allow setting new attributes on wrapped objects through the wrapper -> test_creating_new_attributes_should_create_attribute_on_wrapped_object
This needs solving that the objects themselves need to create attributes while the module is parsed, but they need to be 'closed' after the module has finished parsing

add .unwrapped (or something similar) to have .unwrap as a higher order function
    this should allow using .curry() in contexts where the result cannot be 

find a way to allow something like map(_.each.foo, _.each.bar) or .map(.each['foo', 'bar'])

allow [{'foo': 'bar'},{'foo':'baz'}].map(each.foo)

replace all last remnants of fluent by fluentpy in the documentation
upload documentation to pythonhosted or readthedocs

consider numeric type to do stuff like wrap(3).times(...)
    or wrap([1,2,3]).call(len).times(yank_me)

Rework _.each.call.foo(bar) so 'call' is no longer a used-up symbol on each.
Also _.each.call.method(...) has a somewhat different meaning as the .call method on callable
could _.each.method(_, ...) work when auto currying is enabled?
Review whole library for symbols that can be removed.

Roundable (for all numeric needs?)
    round, times, repeat, if_true, if_false, else_

if_true, etc. are pretty much like conditional versions of .tee() I guess.

.if_true(function_to_call).else_(other_function_to_call)

consider to support something like this

    expect(_(operator.add).curry(_._2, _._1)('foo', 'bar')) == 'barfoo'

example why list comprehension is really bad (Found in zope unit tests)

def u7(x):
    stuff = [i + j for toplevel, in x for i, j in toplevel]
    assert stuff == [3, 7]

add itertools and collections methods where it makes sense

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

Would be really nice to allow inputting the chain into a list comprehension in a readable way

consider collection.join() to have a default argument of '' (empty string)

allow to make ranges by _(1).range(10)

_.lib.pprint.pprint('foo') bombs

_('foo').len() explodes

support _.if()

consider to add the curried arg spec to the help / repr() output of a curried function.

consider what it takes to allow reloading fluentpy itself. This is not so super easy, as the executable module caches all the old values on the function (functools.wraps does that). So afterwards all manner of instance checks don't work anymore. Therefore, just defining __getattr__ on the instance method doesn't quite work

consider typing all the methods for better autocomletionk?

# Make a release
* source and wheel distribution builds
* markdown readme is included as package description (maybe pypy already supports markdown?)
* dev dependencies auf pyexpect
* try release on TestPyPy
* use twine to upload
    * and gpg sign the release!
* werbung für pexpect und fluent auf reddit machen
* rename to fluentpy
* document how to make and upload a release
