from typing import TYPE_CHECKING

from . import tree as tree
from ._better_abstract import (
    AbstractClassVar as AbstractClassVar,
    AbstractVar as AbstractVar,
)
from ._struct import (
    is_abstract_struct as is_abstract_struct,
    replace as replace,
    Struct as Struct,
)


# Defer imports of items that have optional dependencies.
if TYPE_CHECKING:
    from ._random import PRNGKey as PRNGKey
    from ._random_fixture import prngkey_fixture as prngkey_fixture
else:

    def __getattr__(item):
        if item == "PRNGKey":
            from ._random import PRNGKey

            return PRNGKey
        elif item == "prngkey_fixture":
            from ._random_fixture import prngkey_fixture as prngkey_fixture

            return prngkey_fixture
        else:
            raise AttributeError(f"module 'structional' has no attribute '{item}'")


del TYPE_CHECKING
