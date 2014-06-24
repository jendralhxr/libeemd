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

from pyeemd import ceemdan
from pyeemd.utils import plot_imfs
from pylab import plot, show, title
from numpy import loadtxt

ecg = loadtxt("ecg.csv", delimiter=',')
title("Original signal")
plot(ecg)
imfs = ceemdan(ecg, S_number=4)
plot_imfs(imfs, plot_splines=False)
show()
