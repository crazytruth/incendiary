.. image:: https://github.com/crazytruth/incendiary/raw/master/artwork/incendiary.jpg

**********
Incendiary
**********

|Build Status| |Documentation Status| |Codecov|

|PyPI pyversions| |PyPI version| |PyPI license| |Black|

.. |Build Status| image:: https://github.com/crazytruth/incendiary/workflows/Python%20Tests/badge.svg
    :target: https://github.com/crazytruth/incendiary/actions?query=workflow%3A%22Python+Tests%22

.. |Documentation Status| image:: https://readthedocs.org/projects/incendiary/badge/?version=latest
    :target: http://incendiary.readthedocs.io/?badge=latest

.. |Codecov| image:: https://codecov.io/gh/crazytruth/incendiary/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/crazytruth/incendiary

.. |PyPI version| image:: https://img.shields.io/pypi/v/incendiary-framework
    :target: https://pypi.org/project/insanic-incendiary/

.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/insanic-framework
    :target: https://pypi.org/project/insanic-incendiary/

.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |PyPI license| image:: https://img.shields.io/github/license/crazytruth/incendiary?style=flat-square
    :target: https://pypi.org/project/insanic-incendiary/

.. end-badges


A Tracing extension for `Insanic`_ that integrates AWS X-Ray.


Why?
=====

Tracing is needed in any micro service architecture, and this plugin
traces requests received and traces any requests with `Insanic`_'s
interservice's communications and sends it's traced information
to `AWS X-Ray`_.

You might be asking why this package is called incendiary.
In the military there, rifles and machine guns are usually loaded
with tracer rounds every 3-4 rounds which help adjust for aim.
And tracer rounds usually have a mild "incendiary" effect to help
with *visibility*.

Tracing is a distributed system also samples(every X request) to
help with overall *visibility* of the system.


Features
========

- Tracing with AWS X-ray.
- Creates a segment when Insanic receives a request.
- End the segment before return the response.
- Sampling configuration
- Starts and ends subsegments for interservice requests with Insanic.
- Capture other parts of your code.


Installation
============

Prerequisites for using:

-   python >= 3.6
-   Local running instance of AWS X-Ray Daemon. (Running
    instructions can be found `here <https://docs.aws.amazon.com/xray/latest/devguide/xray-daemon-local.html>`_)
-   AWS Credentials (if you want to actually send data to AWS-Ray)



To install:

.. code-block::

    pip install insanic-incendiary

Basic Usage
===========

Basic usage is actually quite simple. You should be able to get it
running without any extra configurations.

To Initialize
-------------

.. code-block:: python

    # app.py

    ...

    from insanic import Insanic
    from incendiary import Incendiary

    app = Insanic("my_app", version="0.1.0")
    Incendiary.init_app(app)

Now if you run, you should be able to start tracing.


To Capture
----------

.. code-block:: python

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

These functions will be its own subsegments in X-Ray.

.. warning::

    You should try and avoid capturing in a production environment,
    because capturing has a performance impact.

For more information please refer to Incendiary's `Documentation`_.

Release History
===============

View release `history <CHANGELOG.rst>`_


Contributing
=============

For guidance on setting up a development environment and how to make a contribution to Incendiary,
see the `CONTRIBUTING.rst <CONTRIBUTING.rst>`_ guidelines.


Meta
====

Distributed under the MIT license. See `LICENSE <LICENSE>`_ for more information.

Thanks to all the people at my prior company that worked with me to make this possible.

Links
=====

- Documentation: https://incendiary.readthedocs.io/en/latest/
- Releases: https://pypi.org/project/insanic-incendiary/
- Code: https://www.github.com/crazytruth/incendiary/
- Issue Tracker: https://www.github.com/crazytruth/incendiary/issues
- Insanic Documentation: http://insanic.readthedocs.io/
- Insanic Repository: https://www.github.com/crazytruth/insanic/
- AWS X-Ray: https://docs.aws.amazon.com/xray/index.html
- aws-xray-sdk: https://docs.aws.amazon.com/xray-sdk-for-python/latest/reference/index.html



.. _Insanic: https://github.com/crazytruth/insanic
.. _Documentation: https://incendiary.readthedocs.io/en/latest/
.. _AWS X-Ray: https://docs.aws.amazon.com/xray/index.html
