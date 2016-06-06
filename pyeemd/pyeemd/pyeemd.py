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
Decomposition on various kinds of data. This Python module exposes the methods
defined in ``libeemd.so`` via a simple ``ctypes`` interface.

.. important::
    If the library file ``libeemd.so`` is present in the same directory as
    ``pyeemd.py`` pyeemd will try to use it. Otherwise it resorts to
    ``ctypes.util.find_library`` for finding it. If you have trouble getting
    pyeemd to find the libeemd library, check out the documentation of
    ``ctypes.util.find_library`` to see what the utility actually does on your
    platform.
"""

import os
import warnings
import ctypes
from ctypes.util import find_library
import numpy
from numpy.ctypeslib import ndpointer

# Load libeemd.so

def _init():
    # First try 'libeemd.so' in current directory
    dirname = os.path.dirname(os.path.realpath(__file__))
    check_first_names = ["libeemd.so"]
    for libfile in [os.path.join(dirname, filename) for filename in check_first_names]:
        if os.path.exists(libfile):
            return ctypes.CDLL(libfile)
    # Then try find_library
    lib = find_library("eemd")
    if lib:
        return ctypes.CDLL(lib)
    else:
        raise RuntimeError("Cannot find libeemd C library. Tried directory '%s' and ctypes.util.find_library" % dirname)

_libeemd = _init()

def libeemd_error_handler(err):
    """
    Function for handling error codes reported by libeemd and converting
    them to exceptions if needed.
    """
    if err == 0:
        return
    if 1 <= err <= 7:
        raise ValueError("libeemd reported a call with incorrect parameters, but the error condition was not handled by pyeemd. The error code was %d. Please see eemd.h to see what the error was and file a bug report." % err)
    else:
        raise RuntimeError("libeemd reported a runtime error with error code %d. Please see eemd.h to see what the error was and file a bug report." % err)
    return

# Call signature for eemd()
_libeemd.eemd.restype = libeemd_error_handler
_libeemd.eemd.argtypes = [ndpointer(float, flags=('C', 'A')),
                          ctypes.c_size_t,
                          ndpointer(float, flags=('C', 'A', 'W')),
                          ctypes.c_size_t,
                          ctypes.c_uint,
                          ctypes.c_double,
                          ctypes.c_uint,
                          ctypes.c_uint,
                          ctypes.c_ulong]
# Call signature for ceemdan() (exactly the same as eemd)
_libeemd.ceemdan.restype = libeemd_error_handler
_libeemd.ceemdan.argtypes = [ndpointer(float, flags=('C', 'A')),
                          ctypes.c_size_t,
                          ndpointer(float, flags=('C', 'A', 'W')),
                          ctypes.c_size_t,
                          ctypes.c_uint,
                          ctypes.c_double,
                          ctypes.c_uint,
                          ctypes.c_uint,
                          ctypes.c_ulong]
# Call signature for emd_find_extrema()
_libeemd.emd_find_extrema.restype = None
_libeemd.emd_find_extrema.argtypes = [ndpointer(float, flags=('C', 'A')),
                                      ctypes.c_size_t,
                                      ndpointer(float, flags=('C', 'A', 'W')),
                                      ndpointer(float, flags=('C', 'A', 'W')),
                                      ctypes.POINTER(ctypes.c_size_t),
                                      ndpointer(float, flags=('C', 'A', 'W')),
                                      ndpointer(float, flags=('C', 'A', 'W')),
                                      ctypes.POINTER(ctypes.c_size_t),
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


def eemd(inp, num_imfs=None, ensemble_size=250, noise_strength=0.2, S_number=None,
         num_siftings=None, rng_seed=0):
    """
    Decompose input data array `inp` to Intrinsic Mode Functions (IMFs) with the
    Ensemble Empirical Mode Decomposition algorithm [1]_.

    The size of the ensemble and the relative magnitude of the added noise are
    given by parameters `ensemble_size` and `noise_strength`, respectively.  The
    stopping criterion for the decomposition is given by either a S-number or
    an absolute number of siftings. In the case that both are positive numbers,
    the sifting ends when either of the conditions is fulfilled. By default,
    `num_siftings=50` and `S_number=4`. If only `S_number` is set to a positive
    value, `num_siftings` defaults to 50. If only `num_siftings` is set to a
    positive value, `S_number` defaults to 0.

    Parameters
    ----------
    inp : array_like, shape (N,)
        The input signal to decompose. Has to be a one-dimensional array-like object.

    num_imfs : int, optional
        Number of IMFs to extract. If set to `None`, a default value given by
        `emd_num_imfs(N)` is used. Note that the residual is also counted in
        this number, so num_imfs=1 will simply give you the input signal plus
        noise.

    ensemble_size : int, optional
        Number of copies of the input signal to use as the ensemble.

    noise_strength : float, optional
        Standard deviation of the Gaussian random numbers used as additional
        noise. **This value is relative** to the standard deviation of the input
        signal.

    S_number : int, optional
        Use the S-number stopping criterion [2]_ for the EMD procedure with the given values of `S`.
        That is, iterate until the number of extrema and zero crossings in the
        signal differ at most by one, and stay the same for `S` consecutive
        iterations. Typical values are in the range `3 .. 8`. If `S_number` is
        zero, this stopping criterion is ignored.

    num_siftings : int, optional
        Use a maximum number of siftings as a stopping criterion. If
        `num_siftings` is zero, this stopping criterion is ignored.

    rng_seed : int, optional
        A seed for the random number generator. A value of zero denotes
        an implementation-defined default value.

    Notes
    ------
    At least one of `S_number` and `num_siftings` must be positive. If both are
    positive, the iteration stops when either of the criteria is fulfilled.

    Returns
    -------
    imfs : ndarray, shape (M, N)
        A `MxN` array with `M = num_imfs`. The rows of the array are the IMFs
        of the input signal, with the last row being the final residual.

    References
    ----------
    .. [1] Z. Wu and N. Huang, "Ensemble Empirical Mode Decomposition: A
       Noise-Assisted Data Analysis Method", Advances in Adaptive Data Analysis,
       Vol. 1 (2009) 1–41
    .. [2] N. E. Huang, Z. Shen and S. R. Long, "A new view of nonlinear water
       waves: The Hilbert spectrum", Annual Review of Fluid Mechanics, Vol. 31
       (1999) 417–457

    See also
    --------
    emd : The regular Empirical Mode Decomposition routine.
    emd_num_imfs : The number of IMFs returned for a given input length `N`
        unless a specific number is set by `num_imfs`.
    """
    # Set default values for S_number and num_siftings
    if (S_number is None and num_siftings is None):
        S_number = 4
        num_siftings = 50
    if (S_number is None and num_siftings is not None):
        S_number = 0
    if (S_number is not None and num_siftings is None):
        num_siftings = 50
    # Perform some checks on input arguments first
    if (num_imfs is not None and num_imfs < 1):
        raise ValueError("num_imfs passed to eemd must be >= 1")
    if (ensemble_size < 1):
        raise ValueError("ensemble_size passed to eemd must be >= 1")
    if (S_number < 0):
        raise ValueError("S_number passed to eemd must be non-negative")
    if (num_siftings < 0):
        raise ValueError("num_siftings passed to eemd must be non-negative")
    if (S_number == 0 and num_siftings == 0):
        raise ValueError("one of S_number or num_siftings must be positive")
    if (noise_strength < 0):
        raise ValueError("noise_strength passed to eemd must be non-negative")
    if (num_siftings == 0):
        warnings.warn("(E)EMD with only the S-number stopping criterion (i.e., num_siftings=0) might never finish if stuck in some obscure numerical corner case.", stacklevel=2)
    # Initialize numpy arrays
    inp = numpy.require(inp, float, ('C', 'A'))
    if (inp.ndim != 1):
        raise ValueError("input data passed to eemd must be a 1D array")
    N = inp.size
    M = (num_imfs if num_imfs is not None else emd_num_imfs(N))
    outbuffer = numpy.zeros(M*N, dtype=float, order='C')
    # Call C routine
    _libeemd.eemd(inp, N, outbuffer, M, ensemble_size, noise_strength,
            S_number, num_siftings, rng_seed)
    # Reshape outbuffer to a proper 2D array and return
    outbuffer = numpy.reshape(outbuffer, (M, N))
    return outbuffer

def ceemdan(inp, num_imfs=None, ensemble_size=250, noise_strength=0.2, S_number=None,
        num_siftings=None, rng_seed=0):
    """
    Decompose input data array `inp` to Intrinsic Mode Functions (IMFs) with the
    Complete Ensemble Empirical Mode Decomposition with Adaptive Noise (CEEMDAN)
    algorithm [1]_, a variant of EEMD. For description of the input parameters
    and output, please see documentation of :func:`~pyeemd.eemd`.


    References
    ----------
    .. [1] M. Torres et al, "A Complete Ensemble Empirical Mode Decomposition
       with Adaptive Noise" IEEE Int. Conf. on Acoust., Speech and Signal Proc.
       ICASSP-11, (2011) 4144–4147


    See also
    --------
    eemd : The regular Ensemble Empirical Mode Decomposition routine.
    emd_num_imfs : The number of IMFs returned for a given input length.
    """
    # Set default values for S_number and num_siftings
    if (S_number is None and num_siftings is None):
        S_number = 4
        num_siftings = 50
    if (S_number is None and num_siftings is not None):
        S_number = 0
    if (S_number is not None and num_siftings is None):
        num_siftings = 50
    # Perform some checks on input arguments first
    if (num_imfs is not None and num_imfs < 1):
        raise ValueError("num_imfs passed to ceemdan must be >= 1")
    if (ensemble_size < 1):
        raise ValueError("ensemble_size passed to ceemdan must be >= 1")
    if (S_number < 0):
        raise ValueError("S_number passed to ceemdan must be non-negative")
    if (num_siftings < 0):
        raise ValueError("num_siftings passed to ceemdan must be non-negative")
    if (S_number == 0 and num_siftings == 0):
        raise ValueError("one of S_number or num_siftings must be positive")
    if (noise_strength < 0):
        raise ValueError("noise_strength passed to ceemdan must be non-negative")
    if (num_siftings == 0):
        warnings.warn("CEEMDAN with only the S-number stopping criterion (i.e., num_siftings=0) might never finish if stuck in some obscure numerical corner case.", stacklevel=2)
    # Initialize numpy arrays
    inp = numpy.require(inp, float, ('C', 'A'))
    if (inp.ndim != 1):
        raise ValueError("input data passed to ceemdan must be a 1D array")
    N = inp.size
    M = (num_imfs if num_imfs is not None else emd_num_imfs(N))
    outbuffer = numpy.zeros(M*N, dtype=float, order='C')
    # Call C routine
    _libeemd.ceemdan(inp, N, outbuffer, M, ensemble_size, noise_strength, S_number,
                  num_siftings, rng_seed)
    # Reshape outbuffer to a proper 2D array and return
    outbuffer = numpy.reshape(outbuffer, (M, N))
    return outbuffer


def emd(inp, num_imfs=None, S_number=None, num_siftings=None):
    """
    A convenience function for performing EMD (not EEMD). This simply calls
    function :func:`~pyeemd.eemd` with ``ensemble_size=1`` and ``noise_strength=0``.
    """
    return eemd(inp, num_imfs, ensemble_size=1, noise_strength=0,
            S_number=S_number, num_siftings=num_siftings)


def emd_find_extrema(x):
    """
    Find the local minima and maxima from input data `x`. This includes the
    artificial extrema added to the ends of the data as specified in the
    original EEMD article [1]_.

    Parameters
    ----------
    x : array_like, shape (N,)
        The input data. Has to be a one-dimensional array_like object.

    Returns
    -------
    maxx : ndarray
        The x-coordinates of the local maxima.

    maxy : ndarray
        The y-coordinates of the local maxima.

    minx : ndarray
        The x-coordinates of the local minima.

    miny : ndarray
        The y-coordinates of the local minima.

    References
    ----------
    .. [1] Z. Wu and N. Huang, "Ensemble Empirical Mode Decomposition: A
       Noise-Assisted Data Analysis Method", Advances in Adaptive Data Analysis,
       Vol. 1 (2009) 1–41
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
    num_zc = ctypes.c_size_t()
    _libeemd.emd_find_extrema(x, N, maxx, maxy, ctypes.byref(num_max), minx,
            miny, ctypes.byref(num_min), ctypes.byref(num_zc))
    maxx.resize(num_max.value)
    maxy.resize(num_max.value)
    minx.resize(num_min.value)
    miny.resize(num_min.value)
    return [maxx, maxy, minx, miny]


def emd_num_imfs(N):
    """
    Return number of IMFs that will be extracted from input data of
    length `N`, including the final residual.
    """
    N = int(N)
    if (N < 0):  # Negative values will overflow silently otherwise
        raise ValueError("Negative value passed for N in emd_num_imfs")
    return _libeemd.emd_num_imfs(N)

def emd_evaluate_spline(x, y):
    """
    Evaluates a cubic spline with the given (x, y) points as knots.

    Parameters
    ----------
    x : array_like, shape (N,)
        The x coordinates of the knots. The array must be sorted, start from 0
        and end at an integer.

    y : array_like, shape (N,)
        The y coordinates of the knots.

    Returns
    -------
    spline_y : ndarray
        The cubic spline curve defined by the knots and the "not-a-knot" end
        conditions, evaluated at integer points from 0 to ``max(x)``.

    Notes
    -----
    As you can see from the definition, this method is tuned to work only in
    the case needed by EMD. This method is made available mainly for
    visualization and unit testing purposes. Better general purpose spline
    methods exist already in :mod:`scipy.interpolate`.

    See also
    --------
    emd_find_extrema : A method of finding the extrema for spline fitting.
    """

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
