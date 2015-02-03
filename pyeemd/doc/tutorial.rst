Tutorial
========

After installing `pyeemd` as described in :ref:`installing` you are all set to
using it with::

    import pyeemd

The three main decomposition routines implemented in `pyeemd` – EMD, EEMD and
CEEMDAN – are available as :func:`~pyeemd.emd`, :func:`~pyeemd.eemd` and
:func:`~pyeemd.ceemdan`, respectively. All these methods use similar
conventions so interchanging one for another is easy.

Input data to these routines can be any kind of Python sequence that
:mod:`numpy` can convert to an 1D array of floating point values. The output
data will be a 2D :mod:`numpy` array, where each row of the array represents a
single *intrinsic mode function* (IMF).

As an example, the `examples` subfolder of `pyeemd` contains a file
``ecg.csv``, which contains ECG (electrocardiogram) data from the `MIT-BIH
Normal Sinus Rhythm Database <http://www.physionet.org/cgi-bin/atm/ATM>`_. The
data is in CSV (comma separated value) format, which can be read into Python in
many ways, one of which is using :func:`numpy.loadtxt` using the appropriate
delimiter::

    from numpy import loadtxt

    ecg = loadtxt("ecg.csv", delimiter=',')

Now we have the data in a :mod:`numpy` array `ecg`. We can quickly plot what
the data looks like using :mod:`matplotlib.pyplot`.

.. _orig-data-figure:

.. figure:: /images/orig_data.png

    Original ECG signal as plotted by :mod:`matplotlib.pyplot`.

.. code:: python

    from matplotlib.pyplot import plot, show, title

    title("Original signal")
    plot(ecg)
    show()

The data stored in `ecg` can be decomposed with CEEMDAN using the routine
:func:`~pyeemd.ceemdan`. The only thing we need to decide is what to use as the
stopping criterion for the sifting iterations. In this example we use a
S-number of 4 and a maximum number of siftings of 50::

    from pyeemd import ceemdan

    imfs = ceemdan(ecg, S_number=4, num_siftings=50)

Now the rows of the 2D array `imfs` are the IMFs the original signal decomposes
to when applying CEEMDAN. We can plot these IMFs using :mod:`matplotlib.pyplot`
as before, but `pyeemd` also comes with an utility function
:func:`~utils.plot_imfs` for easily plotting the IMFs (using
:mod:`matplotlib.pyplot`) in separate figures.

.. _imf7-figure:

.. figure:: /images/imf7.png

    IMF 7 extracted from ECG data with :func:`~pyeemd.ceemdan` and plotted with
    :func:`~utils.plot_imfs`.

.. code:: python

    from pyeemd.utils import plot_imfs

    plot_imfs(imfs, plot_splines=False)
    show()

The ``plot_splines=False`` argument prevents the plotting of the envelope
curves of the IMFs, which would otherwise be shown.

This concludes our simple tutorial. For more in-depth information about the
methods available in `pyeemd` please head to the :ref:`api-doc`. You can also
look at example code at the :file:`examples` subdirectory of `pyeemd`. How you
choose to use or process the IMFs obtained by the decomposition routines is
beyond the scope of this document – and beyond the scope of `pyeemd` – but you
might be interested in the Hilbert transform routine offered by
:func:`scipy.fftpack.hilbert`.

