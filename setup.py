#!/usr/bin/env python

from distutils.core import setup

setup(name='simlib',
      version='0.1',
      description='Common functions for ICESat-2 2020 Assimilation working group',
      author='The team',
      author_email='email@address.com',
      url='https://github.com/ICESAT-2HackWeek/Assimilation',
      packages=['simlib'],
      install_requires=['requests']
     )