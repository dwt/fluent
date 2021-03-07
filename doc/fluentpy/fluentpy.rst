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
  Factory method, wraps anything and returns the appropriate :class:`.Wrapper` subclass.


.. autofunction:: wrap


Classes
=======

- :py:class:`Wrapper`:
  Universal wrapper.

- :py:class:`ModuleWrapper`:
  The :class:`.Wrapper` for modules transforms attribute accesses into pre-wrapped imports of sub-modules.

- :py:class:`CallableWrapper`:
  The :class:`.Wrapper` for callables adds higher order methods.

- :py:class:`IterableWrapper`:
  The :class:`.Wrapper` for iterables adds iterator methods to any iterable.

- :py:class:`MappingWrapper`:
  The :class:`.Wrapper` for mappings allows indexing into mappings via attribute access.

- :py:class:`SetWrapper`:
  The :class:`.Wrapper` for sets is mostly like :class:`.IterableWrapper`.

- :py:class:`TextWrapper`:
  The :class:`.Wrapper` for str adds regex convenience methods.

- :py:class:`EachWrapper`:
  The :class:`.Wrapper` for expressions (see documentation for :data:`.each`).


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
- :py:data:`_0`
- :py:data:`_1`
- :py:data:`_2`
- :py:data:`_3`
- :py:data:`_4`
- :py:data:`_5`
- :py:data:`_6`
- :py:data:`_7`
- :py:data:`_8`
- :py:data:`_9`
- :py:data:`_args`

.. autodata:: lib
   :annotation:

   .. code-block:: text

      fluentpy.wrap('virtual root module')

.. autodata:: each
   :annotation:

   .. code-block:: text

      fluentpy.wrap(each)

.. autodata:: _0
   :annotation:

   .. code-block:: text

      fluentpy.wrap(0)

.. autodata:: _1
   :annotation:

   .. code-block:: text

      fluentpy.wrap(1)

.. autodata:: _2
   :annotation:

   .. code-block:: text

      fluentpy.wrap(2)

.. autodata:: _3
   :annotation:

   .. code-block:: text

      fluentpy.wrap(3)

.. autodata:: _4
   :annotation:

   .. code-block:: text

      fluentpy.wrap(4)

.. autodata:: _5
   :annotation:

   .. code-block:: text

      fluentpy.wrap(5)

.. autodata:: _6
   :annotation:

   .. code-block:: text

      fluentpy.wrap(6)

.. autodata:: _7
   :annotation:

   .. code-block:: text

      fluentpy.wrap(7)

.. autodata:: _8
   :annotation:

   .. code-block:: text

      fluentpy.wrap(8)

.. autodata:: _9
   :annotation:

   .. code-block:: text

      fluentpy.wrap(9)

.. autodata:: _args
   :annotation:

   .. code-block:: text

      fluentpy.wrap('*')
