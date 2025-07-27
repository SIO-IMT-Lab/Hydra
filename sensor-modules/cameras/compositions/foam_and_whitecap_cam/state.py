from enum import Enum

# TODO(bobbytatum27): Header to explain Glider States (and who cares about them)
class State(Enum):
	LOW_POWER = 1
	QUIESCENT = 2
	STORM = 3
	WAVEBREAK = 4