#!/usr/bin/env python

import os

from distutils.core import setup
from distutils.sysconfig import get_python_lib

pkgs_path = get_python_lib()
app_name = 'pycamps'

setup(name=app_name,
    version='0.1',
    description='Python Developer Camps',
    author='Clint Savage',
    author_email='herlo1@gmail.com',
    url='https://github.com/herlo/PyCamps',
    packages=['pycamps',],
    package_dir={'pycamps': 'src/pycamps'},
    scripts=['pycamps',],
    package_data={'pycamps': ['settings.py.sample']},
)
