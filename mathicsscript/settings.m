(**********************************************************************)
(*                                                                    *)
(*                     Settings for mathicsscript                     *)
(*                                                                    *)
(*                                                                    *)
(*                                                                    *)
(**********************************************************************)


Settings`$ShowFullFormInput::usage = "If this Boolean variable is set True, mathicsscript shows the input in FullForm before evaluation.

Note this is for input entered, not the output of the evaluated result.
"

Settings`$ShowFullFormInput = False
Settings`$PygmentsStyle::usage = "This variable sets the Pygments style used to colorize output. The value should be a string.

The default value changes background depending on whether the terminal has a light or dark background. You can also set the color style used on the command with the ``--style`` option, or look at the variable ```Settings`PygmentsStylesAvailable```. Or it can be set in the settings.m file."

Settings`$PygmentsShowTokens::usage = "Setting this variable True will show Pygments tokenization of the output."

Settings`$PygmentsShowTokens = False

Settings`$UseUnicode::usage = "This Boolean variable sets whether Unicode is used in terminal input and output."
Settings`$UseUnicode = True

Settings`MathicsScriptVersion::usage = "This string is the version of MathicsScript we are running."
