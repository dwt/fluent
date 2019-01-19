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

- :py:class:`ModuleWrapper`:
  Imports as expressions. Already pre-wrapped.

- :py:class:`CallableWrapper`:
  Higher order methods for callables.

- :py:class:`IterableWrapper`:
  Add iterator methods to any iterable.

- :py:class:`MappingWrapper`:
  Index into dicts like objects. As JavaScript can.

- :py:class:`SetWrapper`:
  Mostly like IterableWrapper

- :py:class:`TextWrapper`:
  Supports most of the regex methods as if they where native str methods

- :py:class:`EachWrapper`:
  Generate lambdas from expressions

.. autoclass:: Wrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: Wrapper
      :parts: 1

.. autoclass:: ModuleWrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: ModuleWrapper
      :parts: 1

.. autoclass:: CallableWrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: CallableWrapper
      :parts: 1

.. autoclass:: IterableWrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: IterableWrapper
      :parts: 1

.. autoclass:: MappingWrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: MappingWrapper
      :parts: 1

.. autoclass:: SetWrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: SetWrapper
      :parts: 1

.. autoclass:: TextWrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: TextWrapper
      :parts: 1

.. autoclass:: EachWrapper
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: EachWrapper
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
