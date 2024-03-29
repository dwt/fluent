# The fluent Library

```{eval-rst}
.. toctree::
   :caption: For more information see:

   Narrative Documentation <Readme>
   API Documentation <fluentpy/fluentpy>
   Integration.md
   Live Example Code to play with <https://mybinder.org/v2/gh/dwt/fluent/HEAD?labpath=%2Fexamples%2Faoc2018%2Ffluentpy.ipynb>
   Todo.md
   Hacking.md
   Changelog.md
```

## Project Matters

- Project Homepage: <https://github.com/dwt/fluent/>
- Bugs: <https://github.com/dwt/fluent/issues>
- Documentation: <https://fluentpy.readthedocs.io/en/latest/>
- Build Server: <https://circleci.com/gh/dwt/fluent>

```{image} https://readthedocs.org/projects/fluentpy/badge/?version=latest
:alt: Documentation Status
:target: https://fluentpy.readthedocs.io/en/latest/?badge=latest
```

## What problem does fluentpy solve

This library is a syntactic sugar library for Python. It allows you to write more things as expressions, which traditionally require statements in Python. The goal is to allow writing beautiful fluent code with the standard library or your classes, as defined at <https://en.wikipedia.org/wiki/Fluent_interface>.

## Quick Start

Fluent is a powerful library, that allows you to use existing libraries through a fluent interface. This is especially useful since most of the Python standard library was written in a way that makes it hard to be used in this style.

This makes `fluentpy` really usefull to write small Python shell filters, to do something that Python is good at, for example finding stuff with regexes:

```
$ python3 -m fluentpy "lib.sys.stdin.read().findall(r'(foo|bar)*').print()"
```

Or whatever other function from the standard lib or any library you would like to use. The Idea here is that while this is perfectly possible without fluent, it is just that little bit easier, to make it actually become fun and practical.

In this context you have basically three extra symbols `wrap` or `_`, `lib` and `each`

`wrap` is the factory for the object specific wrapper types. Every wrapped object has the fluent behaviour, i.e. every accessed property is also wrapped, while also gaining some type dependent special methods like regex methods on str like `.findall()` `.map()`, `.join()`, etc. on list, etc.

`lib` is a wrapper that allows to use any symbol that is anywhere in the standard library (or accessible via an import) by attribute access. For Example:

```python
import sys
sys.stdin.read()
```

becomes

```python
lib.sys.stdin.read()
```

`each` you probably best think as a convenience lambda generator. It is meant to be a little bit more compact to write down operations you want to execute on every element in a collection.

```python
print(map(lambda x: x * 2, range(1,10)))
```

becomes

```python
wrap(range(1, 10)).map(each * 2).print()
```

Here `each * 2` is the same as `lambda x: x * 2`. `each['foo']` becomes `lambda each: each['foo']`, `each.bar` becomes `lambda each: each.bar`. `each.call.foo('bar')` becomes `lambda each: each.foo('bar')` (Sorry about the `.call.` there, but I haven't found a way to get rid of it, pull requests welcome).

I suggest you use `.dir()` and `.help()` on the objects of this library to quickly get to know what they do.

## Usage in short scripts or bigger projects

Just import fluent under the name you would like to use it. For short scripts I prefer `_` but for projects where gettext is used, I prefer `_f`.

```python
import fluent as _
_(range(10)).map(_.each * 3)
```

`each` and `lib` are available as symbols on `_`, or you can import them  directly from fluent

```python
from fluent import wrap as _, lib, each
_(range(10)).map(each * 3)
```

## Further information

Read up on the {doc}`Narrative Documentation <Readme>`, browse the {doc}`API Documentation <fluentpy/fluentpy>` or take a look at some [Live Example Code](https://mybinder.org/v2/gh/dwt/fluent/HEAD?labpath=%2Fexamples%2Faoc2018%2Ffluentpy.ipynb).

And most important of all: Have phun!
