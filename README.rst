|CI status| |PyPI Installs| |Latest Version| |Supported Python Versions|

|Packaging status|

mathicsscript is a command-line interface to `Mathics3 <https://mathics.org>`_.

|screenshot|

See the `screenshot directory <https://github.com/Mathics3/mathicsscript/tree/master/screenshots>`_ for a description and another example.


Features
--------

* `prompt_toolkit <https://python-prompt-toolkit.readthedocs.io/en/stable>`_ and GNU Readline terminal interaction. This includes:
   - saving command history between sessions.
   - variable completion, even for symbol names like ``\\[Sigma]``
   - limited ESC keyboard input; for example *esc* ``p`` *esc* is π
* Syntax highlighting using `mathics-pygments <https://pypi.org/project/mathics-pygments/>`_ which includes dynamically created variables and functions.
* Automatic detection of light or dark `terminal background color <https://pypi.org/project/term-background/>`_.
* Optional Graphics rendering via `matplotlib <https://matplotlib.org/>`_ for 2D graphics, and `Asymptote <https://asymptote.sourceforge.io>`_ for 3D and 2D graphics.
* Entering and displaying Unicode symbols such as used for Pi or Rule arrows
* Provision for running in non-interactive batch mode which an be used inside POSIX shells

Installing
----------

To install with the full dependencies, run:
::

    $ make install[full]

To install from git sources so that you run from the git source tree:


::

    $ make develop


Running
-------

Once install run using ``mathicsscript``:

::

   $ mathicsscript
   Mathicscript: 7.0.0, Mathics 7.0.0
   on CPython 3.11.9 (main, May  6 2024, 12:58:03) [GCC 13.2.0]
   Using:
   SymPy 1.12.1, mpmath 1.3.0, numpy 1.26.4
   cython 3.0.10, matplotlib 3.8.4,
   Asymptote version 2.87

   Copyright (C) 2011-2024 The Mathics Team.
   This program comes with ABSOLUTELY NO WARRANTY.
   This is free software, and you are welcome to redistribute it
   under certain conditions.
   See the documentation for the full license.

   Quit by evaluating Quit[] or by pressing CONTROL-D.

   In[1]:=


For batch use:
::

   $ mathicsscript -c "N[Pi, 30]"
   3.14159265358979323846264338328

To read from a file

In file ``/tmp/test.m``:

::

   sum=2+2
   integral=Integrate[1,x]
   Print["Results: ",{sum,integral}]

Feeding this into ``mathicsscript``:

::

    $ mathicsscript --no-prompt </tmp/test.m
    4
    x
    Results: {4, x}
    None


For a full list of options, type ``mathicsscript --help``.


Asymptote key bindings
----------------------

In asymptote graphs keyboard bindings are (copied from the asymptote
doc under `8.29 three
<https://asymptote.sourceforge.io/doc/three.html#index-keyboard-bindings_003a>`_::

    h: home
    f: toggle fitscreen
    x: spin about the X axis
    y: spin about the Y axis
    z: spin about the Z axis
    s: stop spinning
    m: rendering mode (solid/patch/mesh)
    e: export
    c: show camera parameters
    p: play animation
    r: reverse animation
    : step animation
    +: expand
    =: expand
    >: expand
    -: shrink
    _: shrink
    <: shrink
    q: exit
    Ctrl-q: exit


Why not IPython via Jupyter?
----------------------------

There will always be a need for simple terminal-like
interaction. Although there is IPython support via Jupyter all of this
is pretty heavy-weight. To code to this protocol, a developer needs to
write a kernel, and use a wire protocol. This adds complexity not
only for the person developing this package, but also for the user who
needs to load the extra layers that aren't used. And when something
goes wrong, it is harder to track down problems.

At the other end of the spectrum, if the dependencies of this package
are too onerous and you want even simpler, lighter-weight terminal interaction *without*
any of the features mentioned above, use ``mathics`` which is distributed as part of
the core Mathic3 package.


.. |screenshot| image:: https://mathics.org/images/mathicsscript1.gif
.. |Latest Version| image:: https://badge.fury.io/py/mathicsscript.svg
		 :target: https://badge.fury.io/py/mathicsscript
.. |PyPI Installs| image:: https://pepy.tech/badge/mathicsscript
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/mathicsscript.svg
.. |CI status| image:: https://github.com/Mathics3/mathicsscript/workflows/mathicsscript%20(ubuntu)/badge.svg
		       :target: https://github.com/Mathics3/mathicsscript/actions
.. |Packaging status| image:: https://repology.org/badge/vertical-allrepos/mathicsscript.svg
			    :target: https://repology.org/project/mathicsscript/versions
