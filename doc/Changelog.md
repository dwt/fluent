# Changelog

## Development version

### Breaking changes

`Iterable.iter()` now returns unwrapped instances. This was changed for uniformity, as all other ways to iterate through a wrapped `Iterable` returned unwrapped instances.

### Notable Changes

`Callable.curry()` now supports converting positional arguments to keyword arguments.

`Iterable.each()` to apply a function to every element just for the side effect while chaining off of the original value.

`Each.in_(haystack)` and `Each.not_in(haystack)` support to mimik `lambda each: each in haystack`.

New top level variable `call` (or `_.call`) that gives direct access to `_.each.call` to make it easier to generate methodcaller objects.