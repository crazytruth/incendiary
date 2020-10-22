Incendiary
===========

Welcome to Incendiary's Documentation. Incendiary is an
extension for `Insanic`_ that provides tracing
functionality with AWS X-Ray. Since `Insanic`_ is a
framework for micro services, being able to trace and
get a transparent visualization of your system is very
important.

Basically, Incendiary wraps :code:`aws-xray-sdk` for use with
Insanic.


Background
----------

This package's was created to relieve the issue of
transparency when architecting a microservice system at my
former employer.  We needed a way to visualize how
each application reacts to a certain request, how
long each request was taking, and to debug any performance
inefficiencies.

But why **Incendiary**? Well, this is a tracing package,
and in the military there are tracer rounds.  Tracer ammunition
are usually loaded in automatic rifles and machine guns with
a tracer round for every 3-5 rounds. The purpose of these
tracer rounds help to *visualize* where the shooter is firing,
and adjust for aim. And finally, those tracer rounds have
a mild "incendiary" effect ergo, the name for this package.


Features
--------

- Tracing with AWS X-ray.
- Creates a segment when Insanic receives a request.
- End the segment before return the response.
- Sampling configuration
- Starts and ends subsegments for interservice requests with Insanic.
- Capture other parts of your code.


Good to Know
------------

Since this is a tracing implementation, I would be good to know
that basics of what is needed for tracing a micro service system.

Also, since Incendiary integrates AWS X-Ray, it would be
good to know how `AWS X-Ray`_ works.


What about OpenTracing?
-----------------------

Although I wanted to develop tracing with a vendor
neutral solution (i.e. `OpenTracing`_), at the point in time when
this project was in development, `OpenTracing`_ was not
mature enough, and there weren't any "good" visualization tools
available.

I do want Incendiary to be able to support `OpenTracing`_ in the
future, but the timeline is currently unknown. Unless you would like
to contribute!


.. _Insanic: https://github.com/crazytruth/insanic
.. _OpenTracing: https://opentracing.io/
.. _AWS X-Ray: https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html
