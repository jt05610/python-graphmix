========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |github-actions| |codecov|
    * - package
      - |version| |wheel| |supported-versions| |supported-implementations| |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-graphmix/badge/?style=flat
    :target: https://readthedocs.org/projects/python-graphmix/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/jt05610/python-graphmix/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/jt05610/python-graphmix/actions

.. |codecov| image:: https://codecov.io/gh/jt05610/python-graphmix/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://app.codecov.io/github/jt05610/python-graphmix

.. |version| image:: https://img.shields.io/pypi/v/graphmix.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/graphmix

.. |wheel| image:: https://img.shields.io/pypi/wheel/graphmix.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/graphmix

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/graphmix.svg
    :alt: Supported versions
    :target: https://pypi.org/project/graphmix

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/graphmix.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/graphmix

.. |commits-since| image:: https://img.shields.io/github/commits-since/jt05610/python-graphmix/v0.0.2.svg
    :alt: Commits since latest release
    :target: https://github.com/jt05610/python-graphmix/compare/v0.0.2...main



.. end-badges

Intelligent experiment planning and optimization powered by graph algorithms.

* Free software: MIT license

Installation
============

::

    pip install graphmix

You can also install the in-development version with::

    pip install https://github.com/jt05610/python-graphmix/archive/main.zip


Documentation
=============


https://python-graphmix.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
