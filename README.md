libeemd – a C library for performing the ensemble empirical mode decomposition
==============================================================================

`libeemd` is a C library for performing the ensemble empirical mode
decomposition (EEMD), its complete variant (CEEMDAN) or the regular empirical
mode decomposition (EMD). It includes a Python interface called `pyeemd`. The
details of what `libeemd` actually computes are available as a separate
[article][], which you should read if you are unsure about what EMD, EEMD and
CEEMDAN are.

[article]: TO_BE_RELEASED

Introduction
------------

Acquiring libeemd
-----------------

The easiest way to get up-to-date versions of libeemd is to use [Bitbucket][],
which is a site built for distributing software using the amazing version
control system [Git][]. By using libeemd's [Bitbucket site][webpage] you can see
recent changes made to the program, report and track bugs found in the program,
access user-generated documentation and even create your own versions of
libeemd.

[bitbucket]: https://bitbucket.org
[git]: http://git-scm.com

Program license
---------------

libeemd is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

libeemd is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
libeemd.  If not, see <http://www.gnu.org/licenses/>.

[author]: mailto:perttu.luukko@iki.fi
[webpage]: https://bitbucket.org/luukko/libeemd

Installation
------------

### Dependencies

To compile `libeemd` you need:

* A fairly recent C compiler (something that understands C99)
* GNU [Scientific Library (GSL)][GSL]

If you want to use the easy route and use the `Makefile` distributed with
`libeemd`, you should have:

* GNU [Make][]
* GNU [Compiler Collection (GCC)][GCC]

[Make]: http://www.gnu.org/software/make/
[GCC]: http://gcc.gnu.org/
[GSL]: http://www.gnu.org/software/gsl/

### Compilation

If you have Make and GCC installed, you can simply run

	make

in the top-level directory of `libeemd` (the one with the `Makefile`). This
command compiles `libeemd` into a static library `libeemd.a`, a dynamic library
`libeemd.so`, and copies the header file `eemd.h` to the top-level directory.
You can then copy these files to wherever you need them. Note that to use the
Python interface `pyeemd` you don't need to move these files anywhere.

Using the C interface
------------

To use `libeemd` in your program include `eemd.h` in your header file and link
your program against `libeemd.a` or `libeemd.so` and [GSL][]. The routines
exported by `libeemd` are documented in the header file `eemd.h`.

To see a short example of `libeemd` in action, please see the `examples`
subdirectory.

`pyeemd`, the Python interface to `libeemd`
-------------------------

The Python interface to `libeemd` is contained in the subdirectory `pyeemd`. It
has its own documentation so head there if you want to know more about it.
You can also head straight to [Read the
Docs](http://pyeemd.readthedocs.org/en/latest/).
