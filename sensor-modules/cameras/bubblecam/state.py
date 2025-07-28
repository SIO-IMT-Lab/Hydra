from enum import Enum


class State(Enum):
    """Operational states for the glider."""

    LOW_POWER = 1
    QUIESCENT = 2
    STORM = 3
    WAVEBREAK = 4
