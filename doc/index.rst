.. fluent documentation master file, created by
   sphinx-quickstart on Tue May 16 10:43:09 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The fluent Library
==================

.. toctree::
   :numbered:
   :caption: For more information see:
   
   Narrative Documentation <Readme>
   API Documentation <fluentpy/fluentpy>
   Example Code <https://github.com/dwt/fluent/tree/master/examples>


Project Matters
---------------

- Project Homepage: https://github.com/dwt/fluent/
- Bugs: https://github.com/dwt/fluent/issues
- Documentation: https://fluentpy.readthedocs.io/en/latest/ 
- Build Server: TODO

.. image:: https://readthedocs.org/projects/fluentpy/badge/?version=latest
    :target: https://fluentpy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


What problem does fluent solve
------------------------------

The fluent library is a syntactic sugar library for python. It allows you to write more things as expressions, which traditionally require statements in python. The goal is to allow writing beautiful fluent code with the standard library or your classes, as defined at https://en.wikipedia.org/wiki/Fluent_interface

Quick Start
-----------

Fluent is a powerful library, that allows you to use existing libraries through a fluent interface. This is especially useful since most of the python standard library was written in a way that makes it hard to be used in this style.

This makes Fluent really usefull to write small python shell filters, to do something that Python is good at, for example finding stuff with regexes::

    $ python3 -m fluent "lib.sys.stdin.read().findall(r'(foo|bar)*').print()"

Or whatever other function from the standard lib or any library you would like to use. The Idea here is that while this is perfectly possible without fluent, it is just that little bit easier, to make it actually become fun and practical.

In this context you have basically three extra symbols ``wrap`` or ``_``, ``lib`` and ``each``

``wrap`` is the factory for the object specific wrapper types. Every wrapped object has the fluent behaviour, i.e. every accessed property is also wrapped, while also gaining some type dependent special methods like regex methods on str like ``.findall()`` ``.map()``, ``.join()``, etc. on list, etc.

``lib`` is a wrapper that allows to use any symbol that is anywhere in the standard library by attribute access. For Example:

    >>> import sys
    >>> sys.stdin.read()

becomes

    >>> lib.sys.stdin.read()

``each`` you probably best think as a convenience lambda generator. It is meant to be a little bit more compact to write down operations you want to execute on every element in a collection.

    >>> numbers = range(1,10)
    >>> print(map(lambda x: x * 2, numbers))

becomes

    >>> wrap(range(1,10)).map(each * 2).print()

Here ``each * 2`` is the same as ``lambda x: x * 2``. ``each['foo']`` becomes ``lambda each: each['foo']``, ``each.bar`` becomes ``lambda each: each.bar``. ``each.call.foo('bar')`` becomes ``lambda each: each.foo('bar')`` (Sorry about the ``.call.`` there, but I haven't found a way to get rid of it, pull requests welcome).

I suggest you use ``.dir()`` and ``.help()`` on the objects of this library to quickly get to know what they do.
 
Usage in short scripts or bigger projects
-----------------------------------------

Just import fluent under the name you would like to use it. For short scripts I prefer ``_`` but for projects where gettext is used, I prefer ``_f``

    >>> import fluent as _
    >>> _(range(10)).map(_.each * 3)

``each`` and ``lib`` are available as symbols on ``_``, or you can import them  directly from fluent

    >>> from fluent import wrap as _, lib, each
    >>> _(range(10)).map(each * 3)

Further information
-------------------

Read up on the :doc:`Narrative Documentation <Readme>`, browse the :doc:`API Documentation <fluentpy/fluentpy>` or take a look at some `Example Code <https://github.com/dwt/fluent/tree/master/examples>`_

And most important of all: Have phun!
