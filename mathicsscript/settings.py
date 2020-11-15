from mathics.builtin import builtins
from mathics.builtin.base import Builtin
from mathics.builtin.assignment import Set
from mathics.core.definitions import Definitions
from mathics.core.expression import Expression, Symbol

from mathicsscript.version import __version__

pymathics_version_data = {
    "author": "The Mathics Team",
    "version": __version__,
    "requires": [],
}


class ShowFullFormInput(Builtin):
    """
    <dl>
      <dt>$ShowFullFormInput'
      <dd> If True, show the FullForm parse of terminal input
    </dl>
    """

    name = "$ShowFullFormInput"
    attributes = ("Unprotected",)

    def apply(self, lhs, rhs, evaluation):
        "lhs_ = rhs_"

        self.assign(lhs, rhs, evaluation)
        return rhs

    def evaluate(self, evaluation) -> Symbol:
        return self.value


# definitions.get_attributes(').clear()
