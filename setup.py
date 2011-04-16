#!/usr/bin/env python

import os

from distutils.core import setup
from distutils.sysconfig import get_python_lib

import src.pycamps.__version__
import src.pycamps.__prog__

pkgs_path = get_python_lib()
app_name = 'pycamps'

setup(name=__prog__,
    version=__version__,
    description='Python Developer Camps',
    author='Clint Savage',
    author_email='herlo1@gmail.com',
    url='https://github.com/herlo/PyCamps',
    packages=['pycamps', 'pycamps.config', 'pycamps.contrib', 'pycamps.contrib.hooks'],
    package_dir={'pycamps': 'src/pycamps'},
    scripts=['pc',],
    package_data={'pycamps.config': ['settings.py.sample']},
)
