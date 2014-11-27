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

from pyeemd import emd, eemd
from nose.tools import assert_equal, raises
from numpy import zeros, all, arange, sum
from numpy.testing import assert_allclose
from numpy.random import normal

@raises(TypeError)
def test_bogus_arguments1():
    x = normal(0, 1, 128)
    emd(x, S_number=4, noise_strength=1)

@raises(TypeError)
def test_bogus_arguments2():
    x = normal(0, 1, 128)
    emd(x, S_number=4, ensemble_size=100)

def test_emd_is_eemd():
    for i in range(16):
        x = normal(0, 1, 128)
        yield check_emd_is_eemd, x
    
def check_emd_is_eemd(x):
    emd_imfs = emd(x, S_number=4)
    eemd_imfs = eemd(x, S_number=4, ensemble_size=1, noise_strength=0)
    assert all(emd_imfs == eemd_imfs)

def test_empty():
    x = []
    imfs = emd(x, S_number=4)
    assert_equal(imfs.ndim, 2)
    assert_equal(imfs.size, 0)

def test_shorts():
    for n in range(1,4):
        yield check_short, n

def check_short(n):
    x = arange(n)
    imfs = emd(x, S_number=4, num_siftings=1000)
    assert_equal(imfs.ndim, 2)
    assert_equal(imfs.shape[0], 1)
    assert all(imfs[0,:] == x)

def test_identical_data():
    for i in range(8):
        yield check_identical_data

def check_identical_data():
    x = normal(0, 1, 64)
    imfs1 = emd(x, S_number=4, num_siftings=1000)
    imfs2 = emd(x, S_number=4, num_siftings=1000)
    assert_allclose(imfs1, imfs2)

def test_completeness():
    for i in range(8):
        yield check_completeness

def check_completeness():
    x = normal(0, 1, 64)
    imfs = emd(x, S_number=4, num_siftings=1000)
    imfsum = sum(imfs, axis=0)
    assert_allclose(x, imfsum)

def test_num_imfs_output_size():
    N = 64
    x = normal(0, 1, N)
    imfs = emd(x, num_imfs=3, S_number=4, num_siftings=100)
    assert imfs.shape[0] == 3

def test_num_imfs_just_residual():
    N = 64
    x = normal(0, 1, N)
    imfs = emd(x, num_imfs=1, num_siftings=10)
    assert all(imfs[-1,:] == x)
