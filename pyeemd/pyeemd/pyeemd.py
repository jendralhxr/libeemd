#!/usr/bin/env python2
# vim: set fileencoding=utf-8 ts=4 sw=4 lw=79

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

"""
pyeemd: A Python module for performing the (Ensemble) Empirical Mode
Decomposition on various kinds of data.

This Python module exposes the methods defined in libeemd.so via a simple
ctypes interface. Note that libeemd.so must be present in the same directory as
this file.
"""

import os
import ctypes
import numpy
from numpy.ctypeslib import ndpointer

# Load libeemd.so
_LIBDIR = os.path.dirname(os.path.realpath(__file__))
_LIBFILE = os.path.join(_LIBDIR, "libeemd.so")
_libeemd = ctypes.CDLL(_LIBFILE)
# Call signature for eemd()
_libeemd.eemd.restype = None
_libeemd.eemd.argtypes = [ndpointer(float, flags=('C', 'A')),
                          ctypes.c_size_t,
                          ndpointer(float, flags=('C', 'A', 'W')),
                          ctypes.c_uint,
                          ctypes.c_double,
                          ctypes.c_uint,
                          ctypes.c_uint]
# Call signature for emd_find_extrema()
_libeemd.emd_find_extrema.restype = ctypes.c_bool
_libeemd.emd_find_extrema.argtypes = [ndpointer(float, flags=('C', 'A')),
                                      ctypes.c_size_t,
                                      ndpointer(float, flags=('C', 'A', 'W')),
                                      ndpointer(float, flags=('C', 'A', 'W')),
                                      ctypes.POINTER(ctypes.c_size_t),
                                      ndpointer(float, flags=('C', 'A', 'W')),
                                      ndpointer(float, flags=('C', 'A', 'W')),
                                      ctypes.POINTER(ctypes.c_size_t)]
# Call signature for emd_num_imfs()
_libeemd.emd_num_imfs.restype = ctypes.c_size_t
_libeemd.emd_num_imfs.argtypes = [ctypes.c_size_t]

# Call signature for emd_evaluate_spline()
_libeemd.emd_evaluate_spline.restype = None
_libeemd.emd_evaluate_spline.argtypes = [ndpointer(float, flags=('C', 'A')),
                                         ndpointer(float, flags=('C', 'A')),
                                         ctypes.c_size_t,
                                         ndpointer(float, flags=('C', 'A', 'W')),
                                         ndpointer(float, flags=('C', 'A', 'W'))]


def eemd(inp, ensemble_size=250, noise_strength=0.2, S_number=0,
         num_siftings=0):
    """
    Decompose input data array inp to Intrinsic Mode Functions (IMFs) with the
    Ensemble Empirical Mode Decomposition algorithm. The size of the ensemble
    and the relative magnitude of the added noise are given by parameters
    ensemble_size and noise_strength, respectively.  The stopping criterion for
    the decomposition is given by either a S-number or an absolute number of
    siftings. In the case that both are positive numbers, the sifting ends when
    either of the conditions is fulfilled.

    Returns a MxN array with M = emd_num_imfs(N). The rows of the array are
    the IMFs, with the last row being the final residual.

    For more information please see:
    Z. Wu and N. Huang, Ensemble Empirical Mode Decomposition: A Noise-Assisted
    Data Analysis Method, Advances in Adaptive Data Analysis, Vol. 1, No. 1
    (2009) 1–41
    """
    # Perform some checks on input arguments first
    if (ensemble_size < 1):
        raise ValueError("ensemble_size passed to eemd must be >= 1")
    if (S_number < 0):
        raise ValueError("S_number passed to eemd must be non-negative")
    if (num_siftings < 0):
        raise ValueError("num_siftings passed to eemd must be non-negative")
    if (S_number == 0 and num_siftings == 0):
        raise ValueError("One of S_number or num_siftings must be positive")
    if (noise_strength < 0):
        raise ValueError("noise_strength passed to eemd must be non-negative")
    # Initialize numpy arrays
    inp = numpy.require(inp, float, ('C', 'A'))
    if (inp.ndim != 1):
        raise ValueError("input data passed to eemd must be a 1D array")
    N = inp.size
    M = emd_num_imfs(N)
    outbuffer = numpy.zeros(M*N, dtype=float, order='C')
    # Call C routine
    _libeemd.eemd(inp, N, outbuffer, ensemble_size, noise_strength, S_number,
                  num_siftings)
    # Reshape outbuffer to a proper 2D array and return
    outbuffer = numpy.reshape(outbuffer, (M, N))
    return outbuffer


def emd(inp, S_number=0, num_siftings=0):
    """
    A convenience function for performing EMD (not EEMD). This simply calls
    function eemd with ensemble_size=1 and noise_strength=0.
    """
    return eemd(inp, ensemble_size=1, noise_strength=0, S_number=S_number,
                num_siftings=num_siftings)


def emd_find_extrema(x):
    """
    Find the local minima and maxima from input data x, including the
    artificial extrema added to the ends of the data.

    Returns a list [all_extrema_good, maxx, maxy, minx, miny],
    where the boolean value all_extrema_good specifies if the extrema
    fulfill the requirements of and IMF, i.e., the local minima are negative
    and the local maxima are positive. The rest are the x and y coordinates of
    the maxima and minima, respectively.

    """
    x = numpy.require(x, float, ('C', 'A'))
    if (x.ndim != 1):
        raise ValueError("input data passed to eemd must be a 1D array")
    N = x.size
    maxx = numpy.empty(N, dtype=float, order='C')
    maxy = numpy.empty(N, dtype=float, order='C')
    num_max = ctypes.c_size_t()
    minx = numpy.empty(N, dtype=float, order='C')
    miny = numpy.empty(N, dtype=float, order='C')
    num_min = ctypes.c_size_t()
    all_extrema_good = _libeemd.emd_find_extrema(x, N, maxx, maxy,
                                                 ctypes.byref(num_max), minx,
                                                 miny, ctypes.byref(num_min))
    maxx.resize(num_max.value)
    maxy.resize(num_max.value)
    minx.resize(num_min.value)
    miny.resize(num_min.value)
    return [all_extrema_good, maxx, maxy, minx, miny]


def emd_num_imfs(N):
    """
    Return number of IMFs that will be extracted from input data of
    length N, including the final residual.
    """
    N = int(N)
    if (N < 0):  # Negative values will overflow silently otherwise
        raise ValueError("Negative value passed for N in emd_num_imfs")
    return _libeemd.emd_num_imfs(N)

def emd_evaluate_spline(x, y):
    x = numpy.require(x, float, ('C', 'A'))
    y = numpy.require(y, float, ('C', 'A'))
    if (x.ndim != 1):
        raise ValueError("input data passed to emd_evaluate_spline must be a 1D array")
    if (x.shape != y.shape):
        raise ValueError("the shapes of x and y passed to emd_evaluate_spline must match")
    if not (x.size >= 2):
        raise ValueError("the size of the array x passed to emd_evaluate_spline must be at least two")
    if not all(numpy.diff(x) >= 0):
        raise ValueError("the input array x passed to emd_evaluate_spline is not sorted")
    if not (x[0] == 0 and numpy.modf(x[-1])[0] == 0):
        raise ValueError("the input array x passed to emd_evaluate_spline needs to start at zero and end at an integer")
    N = x.size
    output_N = int(x[-1])+1
    spline_y = numpy.empty(output_N, dtype=float, order='C')
    ws_size = 5*N-10 if N>=2 else 0
    spline_workspace = numpy.empty(ws_size, dtype=float, order='C')
    _libeemd.emd_evaluate_spline(x, y, N, spline_y, spline_workspace)
    return spline_y