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
Some utility functions for visualizing IMFs produced by the (E)EMD
methods.
"""

from pylab import plot, figure, title
from pyeemd import emd_find_extrema, emd_evaluate_spline

def plot_imfs(imfs, new_figs=True, plot_splines=True):
    """
    Plot utility method for plotting IMFs and their envelope splines with
    ``pylab``.

    Parameters
    ----------
    imfs : ndarray
        The IMFs as returned by :func:`pyeemd.emd`,
        :func:`pyeemd.eemd`, or :func:`pyeemd.ceemdan`.

    new_figs : bool, optional
        Whether to plot the IMFs in separate figures.

    plot_splines : bool, optional
        Whether to plot the envelope spline curves as well.
    """
    for i in range(imfs.shape[0]):
        label = "IMF #%d" % (i+1) if (i+1) < imfs.shape[0] else "Residual"
        print "Plotting", label
        if new_figs:
            figure()
        imf = imfs[i, :]
        if new_figs:
            title(label)
        plot(imf, label=label)
        if plot_splines:
            maxx, maxy, minx, miny = emd_find_extrema(imf)
            maxs = emd_evaluate_spline(maxx, maxy)
            mins = emd_evaluate_spline(minx, miny)
            means = (maxs+mins)/2
            plot(maxs, "g--")
            plot(mins, "r--")
            plot(minx, miny, "rv")
            plot(maxx, maxy, "g^")
            plot(means, "b:")

