==================
backports.unittest
==================

|pypi_vers| |pypi_stat| |pypi_pyvr|

A backport of Python 3.14.x `unittest`_ and `unittest.mock`_ to older versions
of Python, under the `backports`_ namespace.

Usage
=====

::

    from backports import unittest

    def hello(greetee='world'):
        return 'Hello {greetee}!'.format(greetee=greetee)


    class HelloTest(unittest.TestCase)
        def test_greeting(self):
            # assertStartsWith() added in Python 3.14
            self.assertStartsWith(hello(), 'Hello')


Installation
============

Use ::

    pip install backports.unittest

or ::

    uv pip install backports.unittest


Compatibility
=============

Python 3.10 - 3.14 are tested, using backports of the CPython's own test suite.


Related work
============

- `unittest2`_ backports `unittest`_ from Python 2.7 to Python 2.4+
- `backports.test.support`_ backports `test.support`_ from Python 3.6 to Python 2.7+


.. _backports: https://pypi.org/project/backports/
.. _backports.test.support: https://pypi.org/project/backports.test.support/
.. _test.support: https://docs.python.org/3/library/test.html#module-test.support
.. _unittest: https://docs.python.org/3/library/unittest.html
.. _unittest.mock: https://docs.python.org/3/library/unittest.mock.html
.. _unittest2: https://pypi.org/project/unittest2/

.. |pypi_vers| image:: https://img.shields.io/pypi/v/backports.unittest
               :target: https://pypi.org/project/backports.unittest
.. |pypi_stat| image:: https://img.shields.io/pypi/status/backports.unittest
               :target: https://pypi.org/project/backports.unittest
.. |pypi_pyvr| image:: https://img.shields.io/pypi/pyversions/backports.unittest
               :target: https://pypi.org/project/backports.unittest
