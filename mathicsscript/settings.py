# -*- coding: utf-8 -*-

from mathics.core.definitions import Definitions
from mathics.core.load_builtin import import_and_load_builtins
from mathics.settings import default_pymathics_modules

# Initialize definitions
extension_modules = default_pymathics_modules


# from mathics.timing import TimeitContextManager
# with TimeitContextManager("import_and_load_builtins()"):
#     import_and_load_builtins()

import_and_load_builtins()

definitions = Definitions(add_builtin=True, extension_modules=extension_modules)
pass
