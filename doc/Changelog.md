# Changelog

## Development version

## Version 2.1

- `Wrapper.self` will now always go back in the chain to the base of the last call, instead of onyl when the last callable returned `None`. This should fix the possible behaviour change when methods sometimes return None and sometimes a usefull value.

- Fixed inconsistencies on how `CallableWrapper.curry()` deals with too many arguments. In Python this leads to a `TypeError` - and now it does here too.

- Fixed bug that `_._args` behaved differently than documented. The documentation stated that `_(lambda x, y=3: x).curry(_._args)(1, 2)._ == (1, 2)` but it did instead return `tuple(1)`

- Add `__rmul__` and friends support on `_._each`to allow expressions like `4 % _._each` to work.

## Version 2.0

### Breaking changes

- `IterableWrapper.iter()` now returns unwrapped instances. This was changed for uniformity, as all other ways to iterate through a wrapped `IterableWrapper` returned unwrapped instances.

- Removed `Wrapper.tee()` and `Itertools.tee()` as `_(something).tee(a_function)` is easily replicable by `_(something).call(a_function).previous` and `IterableWrapper.tee()` prevented me from providing `itertools.tee`.

- `Wrapper.type()` returns a wrapped type for consistency.

- `Wrapper.{tuplify,listify,dictify,setify}` have been removed, use `Wrapper.call(a_type)` for a wrapped or `Wrapper.to(a_type)` for an unwrapped result instead.

- `_.each` now supports auto chaining of operations. That means you can type `_.each.foo['bar'].baz('quoox')._` to generate a function that applies all of these operations in order. This also means that all functions generated from `_.each` need to be unwrapped (`._`) before usage!

- `_.each.call` is removed, as `_.each.method('arg')` now works as expected, so `_.each.call` is not neccessary any more.

### Notable Changes

- `CallableWrapper.curry()` now supports converting positional arguments to keyword arguments.

- `IterableWrapper.each()` to apply a function to every element just for the side effect while chaining off of the original value.

- `EachWrapper.in_(haystack)` and `EachWrapper.not_in(haystack)` support to mimik `lambda each: each in haystack`.

- All the top level classes have been renamed to have a common -`Wrapper` suffix for consistency and debuggability.

- Added new method `.to(a_type, *args, **kwargs)` that calls `a_type(self, **args, **kwars)` but returns an unwrapped result, to more smothely terminate call chains in common scenarios.
