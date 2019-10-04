#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://incendiary.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

version = '0.1.3.dev2'

test_requires = [
    "coverage",
    'pytest',
    "pytest-cov",
    'pytest-redis',
    'pytest-sanic',
    'pytest-cov',
    'pytest-sugar',
    "pytest-xdist",
    "pytest-flake8",
    'boto3==1.9.99',
    'requests',
    'aioresponses'
]

xray_requirements = [
    'aws-xray-sdk==2.4.2'
]

opentracing_requirements = [
    'basictracer', 'thriftpy',
]

docs_requirements = ['sphinx', 'sphinx_rtd_theme']

cli_requirements = ["Click>=6.0"]

setup(
    name='incendiary',
    version=version,
    description='tracing for insanic',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author_email='david@mymusictaste.com',
    url='https://github.com/MyMusicTaste/incendiary',
    author='Kwang Jin Kim',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    install_requires=[
        'insanic>=0.8.1',
    ],
    tests_require=test_requires,
    extras_require={
        "xray": xray_requirements,
        "opentracing": opentracing_requirements,
        "docs": docs_requirements,
        "cli": cli_requirements,
        "development": test_requires +
                       xray_requirements +
                       opentracing_requirements +
                       docs_requirements +
                       cli_requirements,
        "release": ["zest.releaser[recommended]", "flake8"],
    },
    classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
    ],
    keywords='opentracing zipkin msa microservice xray',
    license='MIT',
)
