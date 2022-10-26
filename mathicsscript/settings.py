# -*- coding: utf-8 -*-

from mathics.core.definitions import Definitions
from mathics.settings import default_pymathics_modules

# Initialize definitions
extension_modules = default_pymathics_modules


definitions = Definitions(add_builtin=True, extension_modules=extension_modules)
pass
