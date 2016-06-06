
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

from pyeemd import emd_num_imfs
from nose.tools import assert_equal, raises

def test0():
    assert_equal(emd_num_imfs(0), 0)

def test5():
    assert_equal(emd_num_imfs(5), 2)

def test10():
    assert_equal(emd_num_imfs(10), 3)

def test16():
    assert_equal(emd_num_imfs(16), 4)

@raises(ValueError)
def test_bogus1():
    emd_num_imfs(-1)

@raises(OverflowError)
def test_bogus2():
    emd_num_imfs(float('inf'))

@raises(ValueError)
def test_bogus3():
    emd_num_imfs("Eat flaming death")

