=============================
incendiary
=============================

.. image:: https://badge.fury.io/py/incendiary.png
    :target: http://badge.fury.io/py/incendiary

.. image:: https://travis-ci.org/crazytruth/incendiary.png?branch=master
    :target: https://travis-ci.org/crazytruth/incendiary

Tracing plugin for insanic

.. image:: incendiary.jpg

Why?
----

Tracing is needed in any micro service architecture, and this plugin aims to
patch insanic's interservice's object so tracing information can be sent to xray.


The reason it is called incendiary is because of tracer ammunition.


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

    pip install incendiary[xray]

For OpenTracing usage
---------------------

.. code-block:: bash

    pip install incendiary[opentracing]

NOTE: for your requirements.txt must place

.. code-block:: txt

    incendiary[xray] == 0.1.0

    # or

    incendiary[opentracing] == 0.1.0


To initialize
=============

.. code-block:: py

    # app.py

    ...

    from incendiary import Incendiary

    app = Insanic(__name__)

    Incendiary.init_app(app)

To capture
==========

.. code-block:: py

    # in_some_module_you_want_to_capture.py

    from incendiary import Incendiary

    # if async function

    @Incendiary.capture_async(name="Name of subsegment")
    async def i_want_to_capture_async():
        pass

    # if sync function

    @Incendiary.capture(name="Name of subsegment")
    def i_want_to_capture():
        pass


- `name` can be `None`. If `None` will default to function name.


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


