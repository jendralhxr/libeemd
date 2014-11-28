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
from pylab import plot, show, title, figure
import numpy as np
from numpy import pi

# An example signal with a lower frequency sinusoid modulated by an
# intermittent higher-frequency sinusoid
x = np.linspace(0, 2*pi, num=500)
signal = np.sin(4*x)
intermittent = 0.1*np.sin(80*x)
y = signal * (1 + np.select([signal > 0.7], [intermittent]))

figure()
title("Original signal")
plot(x, y)

# Decompose with EEMD
imfs = eemd(y, num_siftings=10)

# Plot high-frequency IMFs (1-3) and the rest separately. This illustrates how EEMD can extract the intermittent signal.

highfreq_sum = np.sum([ imfs[i] for i in range(0,3) ], axis=0)
lowfreq_sum = np.sum([ imfs[i] for i in range(3, imfs.shape[0]) ], axis=0)

figure()
title("Sum of IMFs 1 to 3")
plot(x, highfreq_sum)

figure()
title("Sum of rest of IMFs")
plot(x, lowfreq_sum)

show()
