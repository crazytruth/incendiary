=============================
incendiary
=============================

.. image:: https://badge.fury.io/py/incendiary.png
    :target: http://badge.fury.io/py/incendiary

.. image:: https://travis-ci.org/crazytruth/incendiary.png?branch=master
    :target: https://travis-ci.org/crazytruth/incendiary

Messaging integration for insanic

.. image:: docs/_static/incendiary.png

Why?
----

Incendiary is a tracing plugin for Insanic.


Features
--------

* Tracing with AWS X-ray
* Tracing with OpenTracing

Installation
============

Prerequisites:

* python >= 3.6


To install:

.. code-block::

    pip install incendiary

Usage
=====

For AWS X-Ray usage
-------------------

.. code-block:: bash

    pip install .[xray]

For OpenTracing usage
---------------------

.. code-block:: bash

    pip install .[opentracing]

NOTE: for your requirements.txt must place

.. code-block:: txt

    incendiary[xray] == 0.1.0

    # or

    incendiary[opentracing] == 0.1.0

Commands
========

Development
===========

.. code-block:: bash

    pip install .[development]
    # or
    pip install incendiary[development]

Testing
=======

.. code-block:: bash

    $ pip install .[development]
    $ pytest
    # with coverage
    $ pytest --cov=incendiary --cov-report term-missing:skip-covered

To view documentation
=====================

.. code-block:: bash

    $ git clone https://github.com/MyMusicTaste/incendiary.git
    $ cd incendiary
    $ pip install .[development]
    $ cd docs
    $ make html
    # files will be in /path/to/incendiary/docs/_build


Release History
===============

View release history `here <HISTORY.rst>`_

TODO
----


