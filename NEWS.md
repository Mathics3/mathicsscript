5.0.0
--------

* Adjust for Mathics3 core 5.0.0 API
* Fixed autobrace and rewritten with Condition from prompt_toolkit.filter
* Add $GroupAutoComplete setting (default True) to disable completing closer group symbol. Feature provided by DUO Labs and Alessandro Piras.
* Remove bindings for the right brackets
* For prompt-toolkit and GNU Readline users, we allow a user input binding file in CONFIGDIR/inputrc (e.g. ~/.config/mathicsscript/inputrc).
  You can set the location this file via environment variable MATHICS_INPUTRC
* Handle version-getting timeout better
* Python 3.6 tolerance
* Create code of conduct
* Some code linting

4.0.0
-----

* Handle images via PNG and matplotlib
* Packaging: include matplotlib in full install
* Customize Asymptote configuration and add a psviewer that removes eps trash
* Bump minimum Mathics core version to 4.0.0
* Bug fix: Check if `self` has `session` attribute in `asy.__del__`

3.3.1
-----

* Packaging issues: getting setttings.m file into distribution and other missing files
* More pervasive handling of import errors

3.3.0
-----

* 3D Graphics is now handled if Asymptote is installed.
* ``Settings`$UseMatplotlib`` and ``Settings`$UseAsymptote`` were added. The can disable the use of matplotlib and Asymptote when those are available.

3.2.1
-----

Fix packaging issues and be more tolerant matplotlib errors.

3.2.0
-----

* Many 2D plots and graphs can now be viewed via a matplotlib shell! PR #40.
* In prompt-toolkit:
   - Better word-boundary detection for `NamedCharacters`, `Symbols`
   - Include grouping start symbols "(", "{", "[" in detection

3.1.0
-----

Word completion detection was improved slightly. Previously, a grouping opener like "[", "(", or "{" would prevent word completion.

ASCII to unicode conversion was disabled since it was flaky and turned `===` into
garbage upon seeing `==`. Issue #38

In prompt-readline by default, inserting a "[", "(", or "{" will automatically insert the corresponding closing "]", ")", and "}".
Use f3 to toggle this behavoir.

The packaging of 3.0.0 omitted some Readline inputrc files, and a JSON operator table. Issue #37
A few other Python packaging problems were fixe.

We've separated prompt_readline functions into its own module separate from the common prompt readline functions


3.0.0
-----

The primary readline interface has been redone using the excellent [prompt-toolkit](https://pypi.org/project/prompt-toolkit/).
This is pure Python code so it should be available everywhere.
We still include GNU-Readline for those situations where prompt-toolkit doesn't work. Select the readline style now with the
`--choice` option which can be one of `GNU`, `Prompt`, or `None`.

Prompt toolkit allows us to color input as it is getting typed. It also has nicer completion facilities, and sports a bottom modeline status bar.

There is still a bit of cleanup work to do to support GNU readline inputrc files better, or to handle completion better, but this will come later.

Independent of prompt-toolkit, there better pygments colorization using [mathics-pygments](https://pypi.org/project/prompt-toolkit/). Expect that to improve over time too.


2.2.0
-----

* There are now system setting and user settings. User settings take precedence over system settings.
* String output is now shown in quotes to make it more distinguishable from symbol and unexpanded
  expressssion output. This does not follow how `wolframscript` works. Option `strict-wl-output` wil
  disable this.
* Syntax and Highlighting is now done via the Python
  [mathics-pygments](https://pypi.org/project/mathics-pygments/)
  package.  I think you'll find colorization more complete and
  useful. Expect more improvements as mathics-pygments improves.
* Flag `--initfile` is now `--run` to have better conformance with `wolframscript`. In the future we hope
  to support support conformance with `wolfram` if the` mathicsscript` (or code underneath) is called
  using the name `mathics3`.

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
