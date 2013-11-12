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

#pylint: disable=C0111,C0103

from pyeemd import emd_evaluate_spline
from nose.tools import assert_equal, raises
from numpy import array

@raises(ValueError)
def test_bogus1():
    emd_evaluate_spline(x="foo", y="bar")

@raises(TypeError)
def test_missing():
    emd_evaluate_spline(x=range(3))

@raises(ValueError)
def test_too_short():
    emd_evaluate_spline(x=[0], y=[1])

@raises(ValueError)
def test_invalid_shape():
    x = array(range(4))
    x = x.reshape((2,2))
    emd_evaluate_spline(x=x, y=x)

@raises(ValueError)
def test_not_equal_size():
    emd_evaluate_spline(x=range(3), y=range(4))

@raises(ValueError)
def test_invalid_x_firstnotzero():
    emd_evaluate_spline(x=range(1,4), y=range(3))

@raises(ValueError)
def test_invalid_x_lastnotinteger():
    emd_evaluate_spline(x=[0, 1, 2.3], y=range(3))

@raises(ValueError)
def test_invalid_x_notsorted():
    emd_evaluate_spline(x=[0, 2, 1], y=range(3))
