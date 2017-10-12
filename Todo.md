ensure documented functions are listed in source order

Review documentation to ensure it is accessible and complete via `help()` and sphinx generated docs

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
