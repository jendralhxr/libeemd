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

import os
import random
import subprocess
import random
import numpy as np
from tempfile import NamedTemporaryFile
from pyeemd import emd, emd_find_extrema, emd_evaluate_spline
from nose.tools import assert_equal
from nose.plugins.skip import SkipTest
from nose.plugins.attrib import attr

def check_arrays_equal(actual, expected, decimals=14):
    np.testing.assert_almost_equal(actual, expected, decimal=decimals, verbose=True)


def ensure_reference_code_exists(filenames):
    cwd = os.path.dirname(__file__)
    if not cwd:
        cwd = os.getcwd()
    for filename in filenames:
        if not os.path.exists(os.path.join(cwd, filename)):
            raise SkipTest("To run this test you need the file '%s' from the reference EEMD implementation available at <http://rcada.ncu.edu.tw/Matlab%%20runcode.zip>. Place it at the directory '%s'." % (filename, cwd))

def find_matlab():
    whichcmd = "which matlab"
    try:
        matlabcmd = subprocess.check_output(whichcmd, shell=True, stderr=subprocess.PIPE).rstrip("\n")
    except subprocess.CalledProcessError:
        raise SkipTest("Matlab not found in PATH (tried `%s`). Skipping test." % whichcmd)
    return matlabcmd


def execute_matlab(scriptfile):
    matlabcmd = find_matlab()
    cwd = os.path.dirname(__file__)
    if not cwd:
        cwd = os.getcwd()
    cmdline = [matlabcmd, "-nosplash", "-nodisplay", "-r", "addpath('%s'); run('%s'); quit" % (cwd, scriptfile)]
    p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, cwd=cwd)
    out, err = p.communicate()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmdline)


def get_reference_spline(xs, ys, spline_xs):
    with NamedTemporaryFile(suffix=".csv") as outfileobj:
        matlab_script = "x = %s\ny = %s\nxx = %s\nspliney = spline(x,y,xx)\ndlmwrite('%s', spliney, 'precision', 16)\n" % (list(xs), list(ys), list(spline_xs), outfileobj.name)
        with NamedTemporaryFile(suffix=".m") as scriptfileobj:
            # Write Matlab script to temporary file
            scriptfileobj.file.write(matlab_script)
            scriptfileobj.file.flush()
            # Execute Matlab
            execute_matlab(scriptfileobj.name)
        # Read back data
        spline_ys = np.genfromtxt(outfileobj.name, delimiter=',')
        return spline_ys


def check_spline(xs, ys):
    spline_xs = range(0, int(max(xs))+1)
    spline_ys = emd_evaluate_spline(xs, ys)
    ref_spline_ys = get_reference_spline(xs, ys, spline_xs)
    try:
        check_arrays_equal(spline_ys, ref_spline_ys, decimals=12)
    except AssertionError:
        from pylab import plot, show, title, figure, legend
        figure()
        plot(ref_spline_ys, 'ro', label="Reference")
        plot(spline_ys, 'bx', ms=10, label="Result")
        legend(loc="upper left")
        title("Spline comparison")
        show()
        print "xs:", list(xs)
        print "ys:", list(ys)
        print "spline_ys:", list(spline_ys)
        print "ref_spline_ys:", list(ref_spline_ys)
        absdiff = abs(spline_ys - ref_spline_ys)
        print "absolute difference", list(absdiff)
        print "maximal difference", max(absdiff)
        raise


@attr("needsmatlab")
def test_splines():
    for N in [2, 3, 4, 10, 50]:
        for i in range(5):
            dists = np.random.choice(np.arange(2, 20, 0.5), size=N)
            dists[0] = 0
            xs = np.cumsum(dists)
            xs[-1] = np.modf(xs[-1])[1]
            ys = np.random.uniform(-10, 10, N)
            yield check_spline, xs, ys


def get_reference_extrema(ys):
    ensure_reference_code_exists(["extrema.m"])
    maxx_fileobj = NamedTemporaryFile(suffix="_maxx.csv")
    maxy_fileobj = NamedTemporaryFile(suffix="_maxy.csv")
    minx_fileobj = NamedTemporaryFile(suffix="_minx.csv")
    miny_fileobj = NamedTemporaryFile(suffix="_miny.csv")
    matlab_script = """
    data = %s
    [spmax, spmin, flag] = extrema(data)
    dlmwrite('%s', spmax(:,1)-1, 'precision', 16)
    dlmwrite('%s', spmax(:,2), 'precision', 16)
    dlmwrite('%s', spmin(:,1)-1, 'precision', 16)
    dlmwrite('%s', spmin(:,2), 'precision', 16)
    """ % (list(ys), maxx_fileobj.name, maxy_fileobj.name,
           minx_fileobj.name, miny_fileobj.name)
    # Write Matlab script to temporary file
    scriptfileobj = NamedTemporaryFile(suffix=".m")
    scriptfileobj.file.write(matlab_script)
    scriptfileobj.file.flush()
    # Execute Matlab
    execute_matlab(scriptfileobj.name)
    # Read back data
    maxx = np.genfromtxt(maxx_fileobj.name, delimiter=',')
    maxy = np.genfromtxt(maxy_fileobj.name, delimiter=',')
    minx = np.genfromtxt(minx_fileobj.name, delimiter=',')
    miny = np.genfromtxt(miny_fileobj.name, delimiter=',')
    return maxx, maxy, minx, miny


def check_extrema(ys):
    maxx, maxy, minx, miny = emd_find_extrema(ys)
    ref_maxx, ref_maxy, ref_minx, ref_miny = get_reference_extrema(ys)
    assert(all(maxx == ref_maxx))
    check_arrays_equal(maxy, ref_maxy)
    assert(all(minx == ref_minx))
    check_arrays_equal(miny, ref_miny)


@attr("needsmatlab")
def test_extrema():
    for N in [2, 3, 4, 10, 50]:
        for i in range(5):
            jumps = np.random.normal(0, 1, size=N)
            ys = np.cumsum(jumps)
            yield check_extrema, ys


def get_reference_imfs(ys):
    ensure_reference_code_exists(["extrema.m", "eemd.m"])
    imfs_fileobj = NamedTemporaryFile(suffix="_imfs.csv")
    matlab_script = """
    data = %s
    eemdout = transpose(eemd(data, 0, 1))
    imfs = eemdout(2:end,:)
    dlmwrite('%s', imfs, 'precision', 16)
    """ % (list(ys), imfs_fileobj.name)
    # Write Matlab script to temporary file
    scriptfileobj = NamedTemporaryFile(suffix=".m")
    scriptfileobj.file.write(matlab_script)
    scriptfileobj.file.flush()
    # Execute Matlab
    execute_matlab(scriptfileobj.name)
    # Read back data
    imfs = np.genfromtxt(imfs_fileobj.name, delimiter=',')
    return imfs


def check_imfs(ys):
    imfs = emd(ys, num_siftings=10)
    ref_imfs = get_reference_imfs(ys)
    assert_equal(imfs.shape, ref_imfs.shape)
    exceptions = []
    # Note! The reference code handles flat regions in the data differently. This is
    # a rare event, except for the last IMF where it can change the result
    # drastically. The last IMF quite often has a unimodal shape, so if the top
    # or bottom is flat, the reference code interprets this as two equal
    # extrema, and because of the extrapolation to the ends the whole upper of
    # lower envelope is then flat. This seems like incorrect logic, so we do
    # not handle flat regions this way, and thus we don't check the last IMF or
    # the residual for being equal with the reference code.
    for n in xrange(imfs.shape[0]-2):
        imf = imfs[n]
        ref_imf = ref_imfs[n]
        try:
            check_arrays_equal(imf, ref_imf, decimals=13)
        except AssertionError as e:
            titlestr = "IMF #%d" % (n+1) if (n != imfs.shape[0]-1) else "Residual"
            exceptions.append((e, titlestr))
            from pylab import plot, show, title, figure, legend
            figure()
            title(titlestr)
            plot(imf, 'b:', label="Result")
            plot(ref_imf, 'r:', label="Reference")
            plot(imf-ref_imf, 'g-', label="Difference")
            legend()
            show()
            absdiff = abs(imf-ref_imf)
            mask = (ref_imf != 0)
            reldiff = absdiff[mask]/abs(ref_imf[mask])
            print "maximal absolute difference for %s: %.3e" % (titlestr, absdiff.max())
            print "maximal relative difference for %s: %.3e" %(titlestr, reldiff.max())
    if len(exceptions) != 0:
        for e, titlestr in exceptions:
            print titlestr, "didn't match with reference:"
            print e
        raise AssertionError("IMFs didn't match with reference for input data:\n%s" % list(ys))


@attr("needsmatlab")
def test_imfs():
    for N in [ 2**n+1 for n in range(2,6) ]:
        for rep in range(10):
            jumps = np.random.normal(0, 1, size=N)
            ys = np.cumsum(jumps)
            yield check_imfs, ys
