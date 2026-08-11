"""`.env.example` against the settings classes (10.3).

13.6's rule is that a fact written in two places will eventually disagree with itself, and
`.env.example` is a second place: the first is the field list in `pizza.config`. This test is
what keeps them from drifting.
"""

import re
from pathlib import Path

from pizza.config import ClientSettings, ServiceSettings

_EXAMPLE = Path(__file__).parents[2] / ".env.example"
_PREFIXED = re.compile(r"PIZZA_[A-Z_]+")


def test_env_example_matches_the_settings_classes() -> None:
    """Every variable the code reads appears in the example, and nothing else does.

    The comparison runs in both directions on purpose, because each direction is a different
    failure. A field renamed in ``config.py`` and not in the file leaves a reviewer copying an
    example that no longer works; a variable documented that nothing reads sends them to set
    something with no effect. Comment lines count as documentation, which is how the two URLs
    Compose assembles are covered without a settable line (10.3).
    """
    documented = set(_PREFIXED.findall(_EXAMPLE.read_text(encoding="utf-8")))
    declared = {
        f"PIZZA_{name.upper()}"
        for model in (ServiceSettings, ClientSettings)
        for name in model.model_fields
    }

    assert documented == declared
