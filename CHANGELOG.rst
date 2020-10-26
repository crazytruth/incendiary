.. :changelog:

Change Log
==========

0.2.0 (2020-10-26)
------------------

- BREAKING: remove opentracing integration for maybe future release
- UPDATE: change License to MIT

.. note::

    Up until here, Incendiary has been an internal release only.


0.1.5 (2020-03-02)
------------------

- FIX: fix change wrong exception name AlreadyEndedSegment -> AlreadyEndedException
- CHORE: backward compatibility for 0.8.3> because request user and service is no longer awaitable


0.1.4 (2019-12-18)
------------------

- FIX: handles AlreadyEndedException problems when execute http_dispatch in ensure_future task


0.1.3 (2019-10-04)
------------------

- FIX: fixes dependency issue with insanic where task manager was being overwritten


0.1.2 (2019-08-30)
------------------

- UDPATE: error level for initializing increased to critical
- FIX: incendiary config overriding vault settings


0.1.1 (2019-08-27)
------------------

- UPDATE: updates behavior for capture to just log if incendiary is not initialized
- CHORE: image and documentations updates
- FIX: updates insanic requirements to 0.8.1


0.1.0 (2019-08-20)
------------------

- MAJOR: Initial possible working commit of incendiary
- BREAKING: changed tracing name to be the same as hostname
- UPDATE: Capture functionality
- UPDATE: Task factories/wrappers
- UPDATE: Sampling Class
- UPDATE: Interservice tracing
- UPDATE: include initialized plugin for insanic 0.8.0 required plugin enforcement
