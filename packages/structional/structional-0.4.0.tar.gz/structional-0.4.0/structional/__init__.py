# ruff: noqa: I001
import importlib.util
import warnings
from typing import TYPE_CHECKING

if (
    TYPE_CHECKING
    or importlib.util.find_spec("cr") is None
    or importlib.util.find_spec("cr.struct") is None
):
    from ._better_abstract import (
        AbstractClassVar as AbstractClassVar,
        AbstractVar as AbstractVar,
    )
    from ._struct import (
        is_abstract_struct as is_abstract_struct,
        replace as replace,
        Struct as Struct,
    )
else:
    # Cradle-internal shim to make it easy to switch over. This shouldn't affect anyone
    # else.
    warnings.warn(
        "Found importable `cr.struct`. For this reason then `structional` will import "
        "from there instead, instead of using its own definitions. This is to ensure "
        "maximal compatibility: there will be only one definition of `Struct` etc. "
        "Please switch from `cr.struct` to `structional` as at some point this shim "
        "will be removed and this will become an error."
    )
    from cr.struct import (
        AbstractClassVar as AbstractClassVar,
        AbstractVar as AbstractVar,
        is_abstract_struct as is_abstract_struct,
        replace as replace,
        Struct as Struct,
    )

# Has to come after the `Struct` imports above so that `tree` can import them.
from . import tree as tree

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


del importlib, warnings, TYPE_CHECKING
