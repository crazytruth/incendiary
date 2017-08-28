from setuptools import setup, find_packages

import incendiary

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='incendiary',
    version=incendiary.__version__,
    description='opentracing implementation in python',
    long_description=readme(),
    classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    ],
    keywords='opentracing zipkin',
    url='https://github.com/MyMusicTaste/incendiary',
    author='crazytruth',
    author_email='kwangjinkim@gmail.com',
    license='BSD',
    install_requires=[
        'basictracer',
        'thriftpy'
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    tests_require=['mock',],
)
