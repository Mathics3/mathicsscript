from mathics.builtin import builtins
from mathics.builtin.base import Predefined
from mathics.builtin.assignment import Set
from mathics.core.definitions import Definitions
from mathics.core.expression import (Expression, Symbol)
from mathics.core.expression import (Expression, Symbol)

# FullFormInput = Definition("Global`$FullFormInput", defaultvalues=[True],
#                            ownvalues=[True], builtin=True)

FullFormInput = Symbol("Global`$FullFormInput")
true = Symbol("System`True")
xx = Set(FullFormInput, true, expression=False)
definitions = Definitions(add_builtin=True)
from trepan.api import debug; debug()
xx.apply(FullFormInput, true, definitions)
print(xx)


# class FullFormInput(Predefined):
#     """
#     <dl>
#     <dt>'$FullFormInput'
#         <dd>
#     </dl>

#     Example:
#     <pre>
#     In[1] = $FullFormInput
#     Out[1] = False
#     </pre>

#     >> Head[$FullFormInteger] == Boolean
#      = True
#     """

#     name = "$FullFormInput"

#     def evaluate(self, evaluation) -> Expression:
#         return True

# instance = FullFormInput()
# builtins['$FullFormInput'] = instance
# definitions.get_attributes(').clear()
