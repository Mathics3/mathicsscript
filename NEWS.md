1.1.0 rc1
---------

Split off from plain `mathics` script.

* GNU Readline terminal interaction. This includes
   - saving command history between sessions.
   - variable completion, even for symbol names like `\\[Sigma]`
   - limited ESC keyboard input; for example *esc* ``p`` *esc* is π
* Syntax highlighting using `pygments`.
* Automatic detection of light or dark terminal background color.
