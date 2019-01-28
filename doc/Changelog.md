# Changelog

## Development version

## Version 2.0

### Breaking changes

`IterableWrapper.iter()` now returns unwrapped instances. This was changed for uniformity, as all other ways to iterate through a wrapped `IterableWrapper` returned unwrapped instances.

Removed `Wrapper.tee()` and `Itertools.tee()` as `_(something).tee(a_function)` is easily replicable by `_(something).call(a_function).previous` and `IterableWrapper.tee()` prevented me from providing `itertools.tee`.

`Wrapper.type()` returns a wrapped type for consistency.

`Wrapper.{tuplify,listify,dictify,setify}` have been removed, use `Wrapper.to(a_type)` instead.

`_.each` now supports auto chaining of operations. That means you can type `_.each.foo['bar'].baz('quoox')._` to generate a function that applies all of these operations in order. This also means that all functions generated from `_.each` need to be unwrapped (`._`) before usage!

### Notable Changes

`CallableWrapper.curry()` now supports converting positional arguments to keyword arguments.

`IterableWrapper.each()` to apply a function to every element just for the side effect while chaining off of the original value.

`EachWrapper.in_(haystack)` and `EachWrapper.not_in(haystack)` support to mimik `lambda each: each in haystack`.

New top level variable `call` (or `_.call`) that gives direct access to `_.each.call` to make it easier to generate methodcaller objects.

All the top level classes have been renamed to have a common -`Wrapper` suffix for consistency and debuggability.
