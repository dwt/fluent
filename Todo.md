consider numeric type to do stuff like wrap(3).times(...)
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

consider to make chain/previous/unwrap functions for similarity with the other stuff

solve this inconsistency

>>> from fluent import *
>>> _([None]).pop()
fluent.wrap([])
>>> _([None]).pop().chain
[]
>>> _([None]).pop()
fluent.wrap([])
>>> _([1]).pop()
fluent.wrap(1)
