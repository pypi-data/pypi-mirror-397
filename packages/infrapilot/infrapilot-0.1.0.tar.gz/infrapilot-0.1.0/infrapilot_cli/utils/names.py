from __future__ import annotations

import random
import secrets
from typing import Sequence

ADJECTIVES: Sequence[str] = (
    "brave",
    "curious",
    "eager",
    "fuzzy",
    "gentle",
    "lively",
    "mellow",
    "nifty",
    "plucky",
    "quirky",
    "rusty",
    "sunny",
    "swift",
    "tidy",
    "witty",
    "rotten",
    "furry",
    "careful",
    "fluffy",
    "jazzy",
    "beneficial",
    "calculating",
    "mysterious",
    "silky",
    "tangible",
    "meek",
    "ripe",
    "illegal",
    "royal",
    "incandescent",
    "sweet",
    "adjoining",
    "soggy",
    "average",
    "dynamic",
    "blue",
    "long-term",
    "fluttering",
    "smart",
    "longing",
    "complete",
    "powerful",
    "remarkable",
    "amused",
    "bloody",
    "glamorous",
    "depressed",
    "unwieldy",
    "melodic",
    "financial",
    "small",
    "plastic",
    "pointless",
    "nasty",
    "quaint",
    "ill",
    "handsomely",
    "telling",
    "eight",
    "medical",
    "bad",
    "lovely",
    "gleaming",
    "pale",
    "mushy",
)

NOUNS: Sequence[str] = (
    "otter",
    "falcon",
    "panther",
    "sprout",
    "lagoon",
    "nebula",
    "citadel",
    "ember",
    "aurora",
    "prairie",
    "pioneer",
    "voyager",
    "anchor",
    "harbor",
    "summit",
)


def generate_fun_name(seed: str | None = None) -> str:
    """
    Produce a fun docker-style name like ``sunny-otter``.

    When ``seed`` is provided the output is deterministic which keeps names in sync
    across CLI + backend responses.
    """

    rng = random.Random(seed) if seed else random.Random(secrets.randbits(32))
    adjective = rng.choice(ADJECTIVES)
    noun = rng.choice(NOUNS)
    return f"{adjective}-{noun}"


__all__ = ["generate_fun_name"]
