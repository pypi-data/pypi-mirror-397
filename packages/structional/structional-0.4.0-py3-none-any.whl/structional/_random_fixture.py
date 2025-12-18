import os

import pytest

from ._random import PRNGKey


@pytest.fixture
def prngkey_fixture() -> PRNGKey:
    """Designed for use as a fixture in tests: generates a random PRNGKey.

    **Do not** use this in any other context; the random seed generation gives
    deliberate non-determinism.

    When writing a test, you should consider whether you want it to be deterministic (to
    specifically check a particular edge case), or random (to increase coverage of your
    system). If writing a random test then use of this class is best practice, as pytest
    will display the randomly generated seed, allowing for test failures to be debugged
    reproducibly.

    The seed used by this fixture will be set to the value of the
    `STRUCTIONAL_PRNGKEY_SEED` environment variable if that is available, else a random
    number will be used.

    !!! Example

        ```python
        # tests/conftest.py
        from structional import prngkey_fixture as prngkey

        # tests/some_test.py
        def test_foo(prngkey: PRNGKey):
            ...
        ```
    """
    seed = os.environ.get("STRUCTIONAL_PRNGKEY_SEED")
    if seed is None:
        import random

        seed = random.randint(0, 2**30)
    else:
        seed = int(seed)
    return PRNGKey(seed)
