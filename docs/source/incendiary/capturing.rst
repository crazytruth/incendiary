Capturing Code
===============

Capturing allows developers to "capture" parts of their code
and have it represented in the trace.

Incendiary provides separate sync and async capture decorators
to facilitate this.

Usage
-----

.. code-block:: python

    # somewhere you would like to capture

    from incendiary import Incendiary

    # for synchronous functions
    @Incendiary.capture(name="help")
    def function_i_want_to_capture():
        return

    # for asynchronous functions

    @Incendiary.capture_async(name="aiohelp")
    async def async_function():
        return

    # for methods

    class SomeClass:

        @Incendiary.capture(name="help method")
        def method_i_want_to_capture(self):
            # do something
            return

        @Incendiary.capture_async(name="help async method")
        async def async_method(self):
            return


Note that the decorators are different for synchronous
and asynchronous functions and methods.

Also, if the :code:`name` is not provided, the function
name is used. For example, for the synchronous function above,
the name would resolve to :code:`function_i_want_to_capture`.

See Also
--------

- :ref:`api-incendiary-xray-mixins`
