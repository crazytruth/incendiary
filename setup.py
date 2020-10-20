import os
import re

from setuptools import setup, find_packages

here = os.path.dirname(__file__)


def read(fname):
    """
    Read given file's content.
    :param str fname: file name
    :returns: file contents
    :rtype: str
    """
    return open(os.path.join(here, fname)).read()


def get_meta(meta):
    search_string = f'__{meta}__ = "(.*?)"'

    with open("incendiary/__init__.py", encoding="utf8") as f:
        return re.search(search_string, f.read()).group(1)


setup(
    name="insanic-incendiary",
    version=get_meta("version"),
    description="tracing for insanic",
    long_description=read("README.rst"),
    author=get_meta("author"),
    author_email=get_meta("email"),
    url="https://github.com/crazytruth/incendiary",
    packages=find_packages(exclude=["docs", "tests*"]),
    include_package_data=True,
    install_requires=["insanic-framework>=0.9.0,<=0.10.0", "aws-xray-sdk"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
    ],
    keywords="opentracing zipkin msa microservice xray tracing",
    license="MIT",
)
