|CI status| |Pypi Installs| |Latest Version| |Supported Python Versions|

|Packaging status|

mathicsscript is a command-line interface to `Mathics <https://mathics.org>`_.

|screenshot|

See the `screenshot directory <https://github.com/Mathics3/mathicsscript/tree/master/screenshots>`_ for a description and another example.


Features
--------

* GNU Readline terminal interaction. This includes
   - saving command history between sessions.
   - variable completion, even for symbol names like `\\[Sigma]`
   - limited ESC keyboard input; for example *esc* ``p`` *esc* is π
* Syntax highlighting using `pygments <https://pygments.org>`_.
* Automatic detection of light or dark `terminal background color <https://pypi.org/project/term-background/>`_.
* Entering and displaying Unicode symbols such as used for Pi or Rule arrows
* Provision for running in non-interactive batch mode which an be used inside POSIX shells

Installing
----------

To install, run
::

    $ make install

To install from git sources so that you run from the git source tree:


::

    $ make develop


Running
-------

Once install run using ``mathicsscript``:

::

   $ mathicsscript
   Mathicscript: 2.1.2, Mathics 2.1.1.dev0
   on CPython 3.7.10 (default, Feb 27 2021, 08:15:51)
   using SymPy 1.7.1, mpmath 1.2.1, numpy 1.20.1

   Copyright (C) 2011-2021 The Mathics Team.
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
are too onerous and you want even simpler, lighter-weight terminal interaction _without_
and of the features mentioend above, use ``mathics`` which is distributed as part of
the core Mathic3 package.


.. |screenshot| image:: https://mathics.org/images/mathicsscript1.gif
.. |Latest Version| image:: https://badge.fury.io/py/mathicsscript.svg
		 :target: https://badge.fury.io/py/mathicsscript
.. |Pypi Installs| image:: https://pepy.tech/badge/mathicsscript
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/mathicsscript.svg
.. |CI status| image:: https://github.com/Mathics3/mathicsscript/workflows/mathicsscript%20(ubuntu)/badge.svg
		       :target: https://github.com/Mathics3/mathicsscript/actions
.. |Packaging status| image:: https://repology.org/badge/vertical-allrepos/mathicsscript.svg
			    :target: https://repology.org/project/mathicsscript/versions
