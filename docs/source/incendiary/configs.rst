Configurations
==============

Incendiary provides some extra configurations to change the behavior of
Incendiary.

Important Configs
-----------------

:code:`INCENDIARY_XRAY_ENABLED`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


To turn tracing on or off.  Note however, that even if this
is :code:`False`, but receives a request with tracing
sampled headers, the request is still sampled.
It is recommended, even if you don't need tracing,
you should still install and initialize Incendiary so the
request can at least be traced.

:code:`INCENDIARY_XRAY_CONTEXT_MISSING_STRATEGY`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the behavior of :code:`aws_xray_sdk` when a segment
is not found. Values can be :code:`LOG_ERROR`, which just
logs the missing error, or can be :code:`RUNTIME_ERROR`, which
like it says, raises an exception.

:code:`INCENDIARY_XRAY_PATCH_MODULES`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:code:`aws_xray_sdk` comes with several modules that can be
patched with X-Ray. Reference their :code:`aws_xray_sdk`'s
`documentation <https://docs.aws.amazon.com/xray-sdk-for-python/latest/reference/thirdparty.html>`_
for supported libraries.

:code:`INCENDIARY_XRAY_DEFAULT_SAMPLING_FIXED_TARGET`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default sampling fixed target time period in seconds
for local sampling rules. This value means that
the first request during this period is
sampled. For example, if the value is set to 5 minutes(60 * 5).
The first request in a 5 minute time period is always sampled.

:code:`INCENDIARY_XRAY_DEFAULT_SAMPLING_RATE`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the default sampling rate for local sampling rules.
This value represents the percentage of all requests
to be sampled. For example, a value of :code:`0.01` means that
1% of all requests are sampled.


See Also
--------

- Refer to :doc:`Config Reference <api_xray_configs>` for all available configurations.
