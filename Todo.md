# Before next release
* look at https://toolz.readthedocs.io/en/latest/ as it seems to do similar thinigs to what I do
* travis and backport to pythons it's easy to backport
    * 3.5 would be possible if I can go without f-strings (possible) and without the ordered dict on curry (or maybe without overpowered curry)

* integrate introspection methods better CallableWrapper.signature(), ...
* would really like to have a helper that gives me the type structure of someting, to make it easier to reason about
    * i.e. {0: [[func1, func2], [func1,funce]]} -> dict[int, list[list[function]]]

* would be cool to have a way to get from _.each to _(_.each) to be able to chain from there. Not sure how that would / should be terminated though.
* Simplify curry, so it mostly only does what functools.partial does, and factor out the wild reordering stuff into it's own method `.adapt_signature` or something similar. This should also simplify / allow porting to python 3.5
* Ideally, curry will return a new wrapping function that knows what it wraps and still has most of the metadata
* consider to split curry into a straight functools.partial port and a more sophisticated curry / signature_adapter. Maybe foregoing too complicated signature adaption by just using a lambda for complicated adaptions. Not sure how to best express that fluently though

* consider if there is a way to make it easier to debug that you forgot to terminate an _.each expression before handing it of to one of the wrapped iteration methods

* consider to have something on _.each that allows to turn it into a Wrapper to chain off of (as this would allow to use .call() to call it as the argument of something)

# Bunch of Ideas

Consider allowing curry to take expressions as baked arguments that allow to transform arguments via _.each expressions?

get mybinder tutorial going so users can more easily explore fluentpy

    No problem. If you are curious about Spark, the high-level idea is that if you have a lot of data, you want to break your problem across multiple machines to speed up computation. I used Spark as an example as that's one of the most popular distributed computing frameworks. On a day to day basis, I actually use Apache Dask, which is basically the same thing as Spark.  Both Spark and Dask are lazy (like a generator). I looked at the source code of FluentPy, and it seems some parts of lazy (ie uses yield) and some parts are eager (ie uses return). If you are curious, take a look at this Dask syntax. It looks very similar to fluentpy: https://github.com/dask/dask-tutorial/blob/master/02_bag.ipynb In Dask, all the transformations (map/filter/reduce/etc) are lazy until you use .compute(), which triggers actual computation.  Also here's a neat tool: https://mybinder.org/    Mybinder gives you a Jupyter notebook to run in your browser for free--behind the scenes, it's just a container that clones a repo and installs the library. Hence, you can run the Dask tutorial by going to https://mybinder.org/v2/gh/dask/dask-tutorial/HEAD If you want, you can consider adding a tutorial notebook in your fluentpy repo, so then users can simply go to https://mybinder.org/v2/gh/dwt/fluent/HEAD to run the code all through the browser.   I think the fluent interface is a very cool thing that most Python programmers are not aware about, so when I show them for the first time, they are amazed! I remember when I first saw it in Java (and it was just a quick screenshot since I actually don't program in Java), I was thinking, wow this is amazing.  Hope that helps, Eugene

allow each._ or something similar to continue with a wrapped version of each

There should be a way to wrap and unwrap an object when chaining off of _.each

There should be a way to express negation when chaining off of _.each

can I have an `.assign(something)` method that treats self as an lvalue and assigns to it?

`python -m fluentpy` could invoke a repl with fluentpy premported?
Would it even make sense to have every object pre-wrapped? Not even sure how to do this.

Consider what a monkey patch to object would look like that added `._ ` as an accessor to get at a wrapped object.

Consider chainging Wrapper.to() to return the target type unwrapped, to have a shorter way to terminate chains for common usecases

Better Each:
    allow [{'foo': 'bar'},{'foo':'baz'}].map(each.foo)
    find a way to allow something like map(_.each.foo, _.each.bar) or .map(.each['foo', 'bar'])
    Rework _.each.call.foo(bar) so 'call' is no longer a used-up symbol on each.
    Also _.each.call.method(...) has a somewhat different meaning as the .call method on callable
    could _.each.method(_, ...) work when auto currying is enabled?
    Consider if auto chaining opens up the possibility to express all of fluent lazily, i.e. always build up expressions and then call them on unwrap? That way perhaps using iterators internally and returning tuples on .unwrap makes sense? (Could allow to get rid of the i- prefixed iterators)

Make the narrative documentation more compact

Support IterableWrapper.__getitem__

Consider to change return types of functions that are explicitly wrapped but always return None to return .previous

Enhance Wrapper.call() to allow to specify where 'self' is inserted into the arguments. Like wrapped() does.

Get on python-ideas and understand why there is no operator for x in y, x not in y, *x and **y

IterableWrapper.list(), IterableWrapper.tuple(), IterableWrapper.dict(), IterableWrapper.set() instead of the somewhat arbitrary tuplify(), dictify(), … Perhaps do Wrapper.to(a_typer) to convert to any type? Would be identical to Wrapper.call(a_type), but maybe clearer/shorter?

consider if it is possible to monkey-patch object to add a '_' property to start chaining off of it?

Docs
    Check all methods have a docstring
    Check all the methods from itertools are forwarded where sensible
    Consider using http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html for more readable docstrings
    Use doctest to keep the code examples healthy
    When wrapping methods with documentation, prepend the argument mapping to that documentation to make it easier to read.
    consider to add the curried arg spec to the help / repr() output of a curried function.
        Something like: This documentation comes from foo.bar.baz, when called from a wrapped object the wrapped object 
        is inserted as the $nth parameter
    Understand why @functools.wraps sometimes causes the first parameter to ber removed from the documentation

Consider .forget() method that 'forgets' the history of the chain, so python can reclaim the memory of all those intermediate results without one having to terminate the chain. Not sure what this would give us? Maybe better on wrap as a keyword only argumnet like (forget_history=True)

Set build server with different python versions on one of the public build server plattforms

Curry: consider supporting turning keyword argumnents into positional arguments (the other way around already works)

Consider Number wrapper that allows calling stuff like itertools.count, construct ranges, stuff like that
consider numeric type to do stuff like wrap(3).times(...)
    or wrap([1,2,3]).call(len).times(yank_me)

Consider bool wrapper, that allows creating operator versions of if_(), else_(), elsif_(), not_(), ...

add CallableWrapper.vectorize() similar to how it works in numpy - not sure this is actually sensible? Interesting experiment
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

consider what it takes to allow reloading wpy itself. This is not so super easy, as the executable module caches all the old values on the function (functools.wraps does that). So afterwards all manner of instance checks don't work anymore. Therefore, just defining __getattr__ on the instance method doesn't quite work

consider typing all the methods for better autocompletion?
