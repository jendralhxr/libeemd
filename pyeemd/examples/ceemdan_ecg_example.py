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
from matplotlib.pyplot import plot, show, title
from numpy import loadtxt

# Load example ECG signal
# The data is from the MIT-BIH Normal Sinus Rhythm Database, record 16265, ECG1
# More data can be downloaded from http://www.physionet.org/cgi-bin/atm/ATM
ecg = loadtxt("ecg.csv", delimiter=',')

# Plot the original data using Matplotlib
title("Original signal")
plot(ecg)

# Calculate IMFs and the residual by CEEMDAN using a S-number of 4
imfs = ceemdan(ecg, S_number=4)

# Plot the results using the plot_imfs helper function from pyeemd.utils
plot_imfs(imfs, plot_splines=False)
show()
