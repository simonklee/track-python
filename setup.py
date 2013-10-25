# -*- coding: utf-8 -*-
r"""
track-python
---

A track python client.
"""

import sys

from setuptools import setup
try:
    import multiprocessing
except ImportError:
    pass

def run_setup(with_binary):
    features = {}

    setup(
        name='track-python',
        version='0.1.3',
        license='MIT',
        url='https://github.com/simonz05/track-python/',
        author='Simon Zimmermann',
        author_email='simon@insmo.com',
        description='A track Python client',
        long_description=__doc__,
        keywords="track",
        platforms='any',
        packages=['track'],
        features=features,
        install_requires=['requests'],
        test_suite="nose.collector",
        tests_require=['nose'],
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX",
            "Programming Language :: Python",
            "Topic :: Software Development",
            "Topic :: Software Development :: Libraries",
        ],
    )

def echo(msg=''):
    sys.stdout.write(msg + '\n')

run_setup(True)
