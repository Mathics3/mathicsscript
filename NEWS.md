2.1.2
-----

* Packaging changes. Make sure egg/wheel/tarball has settings.m and GNU Readline inputrc files package
* Bump minimum Mathics-Scanner version. There was a small subtle bug in infix Function operators in that

2.1.1
-----

Administrative changes but necessary to get this working properly:

* Bump min version of mathicsscanner. There was a bug in mathicsscanner that prevented
the GNU Readline inputrc files from getting created properly.
* Include settings.m in distribution. There was a typo in setup.py for location of this file.

2.1.0
-----

* Allow command-line flag `-c` as an alias for `--execute` (along with `-e` to be compatible with wolframscript
* Better compliance on Windows which are GNU readline-starved
* Better unicode detection
* Accept newer mathics-scanner and Mathics3 versions

2.0.1
-----

* Fix `mathicsscript -f FILE` argument. See PR #26

2.0.0
-----

* All escape sequence for unicode and letter names added for GNU Readline
* Use Mathics Scanner package
* Support XDG-style configuration files

1.1.2
-----

* Fix ``Settings`$ShowFullForm`` now that we use Mathics supports Booleans better
* Show mathicsscript version on startup
* Add ``Settings`MathicsScriptVersion``
* Add all of the WL escape sequences
* Add conversions from WL Unicode to standard Unicode
* Shell escapes `!` and `!!` added

Incompatible changes:

* `-e` `--execute` is better suited for embedded use. It adds `--quiet` and shows just evaluation output as text

1.1.1
-----

* We require Mathics3 1.1.1 for features added in that to support unicode and user-formatting
* Start to support Unicode as a CLI option: `--unicode/--no-unicode`. The setting name is ``Settings`$UseUnicode``.
* Add a lot of Unicode symbols and the WL esc sequences. For example letters with dots under them. These are the "Formal" parmaters/letters.
* Handle Unicode versus WL character code mismatches, , in particular Unicode directed and undirected edges.
* Support for ``PyMathics`Graph`` (to be released on PyPI soon).
* Some XDG compatibility
* Toleratte MS/Windows pyreadline which doesn't handle `remove_history_item`
* Show pygments styles when an invalid one is given
* Use "inkpot" for dark backgrounds and "colorful" for  light backgrounds.
* Add ``Settings`PygementsStylesAvailable``
* Add settings.m to holds `mathicsscript`-specific definitions `Settings` and their default values. Settings include
  - ``Settings`$ShowFullFormInput``
  - ``Settings`$PygmentsStyle``
  - ``Settings`$PygmentsShowTokens``
  - ``Settings`$UseUnicode`` (also mentioned above)

A lot of code for handling graph formatting is here but will eventually be moved to a backend formattting module which hasn't been written yet.


1.1.0
-----

Now that Mathic3 1.1.0 is released depend on that.

Some interal prepartion work was done to support changing settings inside the REPL.
Not ready for release yet.

1.1.0 rc1
---------

Split off from plain `mathics` script.

* GNU Readline terminal interaction. This includes
   - saving command history between sessions.
   - variable completion, even for symbol names like `\\[Sigma]`
   - limited ESC keyboard input; for example *esc* ``p`` *esc* is π
* Syntax highlighting using `pygments`.
* Automatic detection of light or dark terminal background color.
