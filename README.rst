mathicsscript is a command-line interface to Mathics.

|screenshot|

See the `screenshot directory <https://github.com/Mathics3/mathicsscript/tree/master/screenshots>`_ for a description and another example.


Features
--------

* GNU Readline terminal interaction. This includes
   - saving command history between sessions.
   - variable completion, even for symbol names like `\\[Sigma]`
   - limited ESC keyboard input; for example *esc* ``p`` *esc* is π
* Syntax highlighting using `pygments`.
* Automatic detection of light or dark terminal background color.


Installing
----------

To install, run
::

    $ make install

To install from git shources so that you run from the git source tree:


::

    $ make develop


Why not IPython via Jupyter?
----------------------------

There will always be a need for simple terminal-like
interaction. Although there is IPython support via Jupyter all of this
is pretty heavy-weight. To code to this a developer needs to code
write a kernel, and use a wire protocol and this adds complexity not
only for the person developing this package, but also for the user who
needs to load the extra layers that aren't used. And when something
goes wrong, it is harder to track down problems.


.. |screenshot| image:: https://github.com/Mathics3/mathicsscript/blob/master/screenshots/mathicsscript1.gif
