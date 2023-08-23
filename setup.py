#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dataclass_rest',
    description='An utility for writing simple clients for REST like APIs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.4',
    url='https://github.com/reagento/dataclass-rest',
    author='A. Tikhonov',
    author_email='17@itishka.org',
    license='Apache2',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ],
    packages=['dataclass_rest', 'dataclass_rest.http'],
    install_requires=[
        'dataclasses;python_version<"3.7"',
        'adaptix',
        'typing_extensions;python_version<"3.8"',
    ],
    package_data={
        'dataclass_rest': ['py.typed'],
    },
    python_requires=">=3.6",
)
