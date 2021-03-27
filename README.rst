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

Installing
----------

To install, run
::

    $ make install

To install from git sources so that you run from the git source tree:


::

    $ make develop


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
