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

Settings`$PygmentsStyle = "inkpot"
Settings`$PygmentsStyle::usage = "This variable sets the Pygments style used to colorize output. The value should be a string.

The default value changes background depending on whether the terminal has a light or dark background. You can also set the color style used on the command with the ``--style`` option, or look at the variable ```Settings`PygmentsStylesAvailable```. Or it can be set in the settings.m file."

Settings`$PygmentsShowTokens = False
Settings`$PygmentsShowTokens::usage = "Setting this variable True will show Pygments tokenization of the output."

Settings`$UseUnicode = True
Settings`$UseUnicode::usage = "This Boolean variable sets whether Unicode is used in terminal input and output."

Settings`$UseAsymptote = True
Settings`$UseAsymptote::usage = "This Boolean variable sets whether 3D Graphics should render using Asymptote."

Settings`$UseMatplotlib = True
Settings`$UseMatplotlib::usage = "This Boolean variable sets whether 2D Graphics should render using Matplotlib."

Settings`MathicsScriptVersion::usage = "This string is the version of MathicsScript we are running."

System`$Notebooks = False
System`$Notebooks::usage = "Set True if the Mathics is being used with a notebook-based front end."

Settings`$GroupAutocomplete = True
Settings`$GroupAutocomplete::usage = "This Boolean variable sets whether mathicsscript should automatically close braces."
