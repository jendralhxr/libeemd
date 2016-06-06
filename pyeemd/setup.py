#!/usr/bin/env python2

# Copyright 2013 Perttu Luukko

# This file is part of libeemd.
# 
# libeemd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# libeemd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with libeemd.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(name='pyeemd',
      version='1.3.1',
      description='Ensemble Empirical Mode Decomposition with Python',
      author='Perttu Luukko',
      author_email='perttu.luukko@iki.fi',
      url='https://bitbucket.org/luukko/libeemd',
      install_requires=['numpy', 'matplotlib'],
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose']
      )
