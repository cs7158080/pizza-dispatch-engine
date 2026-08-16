"""Unit test comparing `.env.example` with the settings classes.

The configuration surface is written twice: the field lists in `pizza.config` and the
committed example. This test keeps the two from drifting apart.
"""

import re
from pathlib import Path

from pizza.config import ClientSettings, ServiceSettings

_EXAMPLE = Path(__file__).parents[2] / ".env.example"
_PREFIXED = re.compile(r"PIZZA_[A-Z_]+")


def test_env_example_matches_the_settings_classes() -> None:
    """Scenario: the example documents every declared variable, and nothing more.

    Why it matters: the comparison runs in both directions because each direction is
    a different failure. A field renamed only in `config.py` leaves a reviewer copying
    an example that no longer works; a documented variable nothing reads sends them to
    set something with no effect. Comment lines count as documentation, which is how
    the two URLs Compose assembles are covered without a settable line.
    """
    documented = set(_PREFIXED.findall(_EXAMPLE.read_text(encoding="utf-8")))
    declared = {
        f"PIZZA_{name.upper()}"
        for model in (ServiceSettings, ClientSettings)
        for name in model.model_fields
    }

    assert documented == declared
