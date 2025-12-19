from dataclasses import dataclass

from . import coordinates

@dataclass(frozen=True)
class TrainStatus:
    runningNumber: int
    coordinates: coordinates.Coordinates
    lastSeen: str
