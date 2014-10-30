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

from pyeemd import eemd
from nose.tools import assert_equal, raises
from numpy import zeros, all, abs, allclose, linspace
from numpy.random import normal

@raises(ValueError)
def test_bogus1():
    x = eemd("I am a banana")

@raises(ValueError)
def test_bogus2():
    x = eemd(7)

@raises(ValueError)
def test_wrong_dims():
    x = zeros((2,2))
    eemd(x)

@raises(ValueError)
def test_invalid_arguments1():
    x = []
    eemd(x, S_number=4, ensemble_size=0)

@raises(ValueError)
def test_invalid_arguments2():
    x = []
    eemd(x, S_number=4, noise_strength=-2)

@raises(ValueError)
def test_invalid_arguments3():
    x = []
    eemd(x, S_number=0)

@raises(ValueError)
def test_invalid_arguments4():
    x = []
    eemd(x, num_siftings=-3)

@raises(ValueError)
def test_invalid_arguments5():
    x = []
    eemd(x)

@raises(ValueError)
def test_invalid_arguments6():
    x = []
    eemd(x, num_imfs="Lots")

@raises(ValueError)
def test_invalid_arguments7():
    x = []
    eemd(x, num_imfs=0)

@raises(ValueError)
def test_invalid_arguments8():
    x = []
    eemd(x, num_imfs=-5)

def test_zeros():
    x = zeros(64)
    imfs = eemd(x, S_number=4, ensemble_size=10)
    # the zero signal has zero standard deviation so no noise should be added
    assert all(imfs == 0)

def test_ones():
    N = 64
    x = [1]*N
    imfs = eemd(x, S_number=4, num_siftings=1000, ensemble_size=100)
    for n in range(imfs.shape[0]-1):
        imf = imfs[n,:]
        assert all(abs(imf) < 1e-9)
    assert allclose(imfs[-1,:], x)

def test_extract_residual():
    N = 100
    t = linspace(1, 10, num=N)
    x = t**2
    xn = x + normal(0, 0.5, N)
    imfs = eemd(xn, S_number=4, num_siftings=1000)
    # the residual should be approximately equal to the signal without the
    # added noise, at least away from the ends
    residual = imfs[-1,:]
    print abs(residual-x)[10:-10]
    assert allclose(residual[10:-10], x[10:-10], rtol=0.1, atol=1)

def test_rng_seed():
    N = 64
    x1 = normal(0, 1, N)
    x2 = normal(0, 1, N)
    imfs1 = eemd(x1, S_number=4, num_siftings=100, rng_seed=3141)
    imfs2 = eemd(x2, S_number=4, num_siftings=100, rng_seed=5926)
    assert not allclose(imfs1, imfs2)

def test_num_imfs():
    N = 64
    x = normal(0, 1, N)
    imfs1 = eemd(x, num_imfs=3, S_number=4, num_siftings=100)
    imfs2 = eemd(x, num_imfs=4, S_number=4, num_siftings=100)
    assert allclose(imfs1[:2,:], imfs2[:2,:])

def test_num_imfs_output_size():
    N = 64
    x = normal(0, 1, N)
    imfs = eemd(x, num_imfs=3, S_number=4, num_siftings=100)
    assert imfs.shape[0] == 3

@raises(ValueError)
def test_num_imfs_too_much():
    N = 8
    x = normal(0, 1, N)
    imfs = eemd(x, num_imfs=100, S_number=4, num_siftings=100)
