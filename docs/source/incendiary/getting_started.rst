Getting Started
================

Getting started with incendiary should be pretty straight
forward.

Prerequisites
-------------

-   Python version >= 3.6
-   AWS Account and Credentials
-   A local instance of AWS X-Ray Daemon.  Instructions can
    be found `here <https://docs.aws.amazon.com/xray/latest/devguide/xray-daemon-local.html>`_


Installing
----------

.. code-block::

    pip install insanic-incendiary


Initialization
--------------

.. code-block:: python

    from insanic import Insanic
    from insanic.conf import settings
    from incendiary import Incendiary

    __version__ = "0.1.0.dev0"

    settings.configure(ENVIRONMENT="development")
    app = Insanic('example',  version=__version__)

    Incendiary.init_app(app)

When you send a request to your application, your node on
AWS X-Ray's visualization will be :code:`example.development`.

See Also
--------

- :ref:`api-incendiary-xray-app`
