.. _installing:

Installing pyeemd
=================

The `pyeemd` module comes with a regular Python distutils installation script,
so installing it should be quite straightforward. The only catch is that you
need to first compile ``libeemd.so``, since `pyeemd` is only a wrapper for that
library. Please see the ``README`` file distributed with `libeemd` on more
details on how to compile `libeemd`, but if you are unpatient and already have
the necessary dependencies installed (GCC, GSL), you can just run ``make`` in
the top-level directory of `libeemd` and you are done.

To install `pyeemd` please run::

    python2 setup.py install

In the top-level directory of `pyeemd` (the one with ``setup.py``).

If you want to specify an alternative installation prefix, you can do it as follows::

    python2 setup.py install --prefix=$HOME/usr
