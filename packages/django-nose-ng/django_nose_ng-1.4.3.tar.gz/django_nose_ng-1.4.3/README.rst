==============
django-nose-ng
==============

.. image:: https://img.shields.io/pypi/v/django-nose-ng.svg
    :alt: The PyPI package
    :target: https://pypi.python.org/pypi/django-nose-ng

.. image:: https://github.com/kkszysiu/django-nose-ng/workflows/Test/badge.svg
    :target: https://github.com/kkszysiu/django-nose-ng/actions
    :alt: GitHub Actions

.. image:: https://codecov.io/gh/kkszysiu/django-nose-ng/branch/master/graph/badge.svg
    :alt: Coverage
    :target: https://codecov.io/gh/kkszysiu/django-nose-ng

.. Omit badges from docs

**django-nose-ng** provides all the goodness of `nose-ng`_ in your Django tests, like:

* Testing just your apps by default, not all the standard ones that happen to
  be in ``INSTALLED_APPS``
* Running the tests in one or more specific modules (or apps, or classes, or
  folders, or just running a specific test)
* Obviating the need to import all your tests into ``tests/__init__.py``.
  This not only saves busy-work but also eliminates the possibility of
  accidentally shadowing test classes.
* Taking advantage of all the useful `nose plugins`_

.. _nose-ng: https://github.com/kkszysiu/nose-ng
.. _nose plugins: http://nose-plugins.jottit.com/

It also provides:

* Fixture bundling, an optional feature which speeds up your fixture-based
  tests by a factor of 4
* Reuse of previously created test DBs, cutting 10 seconds off startup time
* Hygienic TransactionTestCases, which can save you a DB flush per test
* Support for various databases. Tested with MySQL, PostgreSQL, and SQLite.
  Others should work as well.

django-nose-ng requires nose-ng 1.4.3 or later. It supports:

* Django 4.2 (LTS) with Python 3.11 or 3.12
* Django 5.0 with Python 3.11, 3.12, or 3.13
* Django 5.1 with Python 3.11, 3.12, 3.13, or 3.14


Note to users
-------------

This is a fork of the original `django-nose`_ project, updated to work with
modern Python (3.11+) and Django (4.2+) versions. It uses `nose-ng`_ instead
of the unmaintained ``nose`` package.

.. _django-nose: https://github.com/jazzband/django-nose

Installation
------------

You can get django-nose-ng from PyPI with... :

.. code-block:: shell

    $ pip install django-nose-ng

Or using uv:

.. code-block:: shell

    $ uv add django-nose-ng

The development version can be installed with... :

.. code-block:: shell

    $ pip install -e git+https://github.com/kkszysiu/django-nose-ng.git#egg=django-nose-ng

Since django-nose-ng extends Django's built-in test command, you should add it to
your ``INSTALLED_APPS`` in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'django_nose',
        ...
    ]

Then set ``TEST_RUNNER`` in ``settings.py``:

.. code-block:: python

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

Development
-----------
:Code:   https://github.com/kkszysiu/django-nose-ng
:Issues: https://github.com/kkszysiu/django-nose-ng/issues?state=open
