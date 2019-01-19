============
``fluentpy``
============

.. automodule:: fluentpy

   .. contents::
      :local:

.. currentmodule:: fluentpy


Functions
=========

- :py:func:`wrap`:
  Factory method, wraps anything and returns the appropriate Wrapper subclass.


.. autofunction:: wrap


Classes
=======

- :py:class:`Wrapper`:
  Universal wrapper.

- :py:class:`Module`:
  Imports as expressions. Already pre-wrapped.

- :py:class:`Callable`:
  Higher order methods for callables.

- :py:class:`Iterable`:
  Add iterator methods to any iterable.

- :py:class:`Mapping`:
  Index into dicts like objects. As JavaScript can.

- :py:class:`Set`:
  Mostly like Iterable

- :py:class:`Text`:
  Supports most of the regex methods as if they where native str methods


.. autoclass:: Wrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Wrapper
      :parts: 1

.. autoclass:: Module
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Module
      :parts: 1

.. autoclass:: Callable
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Callable
      :parts: 1

.. autoclass:: Iterable
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Iterable
      :parts: 1

.. autoclass:: Mapping
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Mapping
      :parts: 1

.. autoclass:: Set
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Set
      :parts: 1

.. autoclass:: Text
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Text
      :parts: 1

.. autoclass:: Each
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Each
      :parts: 1

Variables
=========

- :py:data:`lib`
- :py:data:`each`
- :py:data:`call`

.. autodata:: lib
   :annotation:

.. autodata:: each
   :annotation:

.. autodata:: call
   :annotation:
