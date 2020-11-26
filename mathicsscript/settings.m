(**********************************************************************)
(*                                                                    *)
(*                     Settings for mathicsscript                     *)
(*                                                                    *)
(*                                                                    *)
(*                                                                    *)
(**********************************************************************)


Settings`$ShowFullFormInput::usage = "If this variable is set nonzero, mathicsscript shows the input in FullForm before evaluation.

Note this is for input entered, not the output of the evaluated result.
"

Settings`$ShowFullFormInput = 0
Settings`$PygmentsStyle::usage = "This sets the Pygments style used to colorize output. The value should be a string.

The default value changes background depending on whether the terminal has a light or dark background. You can also set the color style used on the command with the ``--style`` option, or look at the variable ```Settings`PygmentsStylesAvailable```. Or it can be set in the settings.m file."

Settings`$PygmentsShowTokens::usage = "Setting this 1 will show Pygments tokenization of the output."
