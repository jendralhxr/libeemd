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

import os
import subprocess
from shutil import copy2
from distutils.core import setup, Extension, Command
from distutils.command.build_ext import build_ext


class CustomBuildExt(build_ext):
    """
    A hackish wrapper around standard build_ext to ensure libeemd.so is built
    using the Makefile (no need to re-invent the wheel for compiling the C
    code).
    """
    def build_extension(self, ext):
        if ext.name == "eemd":
            subprocess.check_call(['make', 'libeemd.so'], cwd="..")
            destdir = os.path.join(self.build_lib, "pyeemd")
            try:
                os.makedirs(destdir)
            except OSError:
                pass
            copy2('../libeemd.so', destdir)
        else:
            build_ext(self, ext)

class DummySDist(Command):
    """
    Creating a source distribution package with `python setup.py sdist` is not
    supported.  pyeemd is currently not supposed to be distributed as source on
    its own, only as a part of libeemd. You can still make a binary package
    with `python setup.py bdist`.
    """
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        raise NotImplementedError(self.__doc__)


libeemd = Extension('eemd', ['../src/eemd.c', '../src/eemd.h', '../Makefile'])

setup(name='pyeemd',
      version='1.0a1',
      description='Ensemble Empirical Mode Decomposition with Python',
      author='Perttu Luukko',
      author_email='perttu.luukko@iki.fi',
      url='https://bitbucket.org/luukko/libeemd',
      packages=['pyeemd', 'pyeemd.tests'],
      ext_modules=[libeemd],
      cmdclass={'build_ext': CustomBuildExt, 'sdist': DummySDist}
      )
