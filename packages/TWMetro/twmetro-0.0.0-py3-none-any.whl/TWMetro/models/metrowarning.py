from dataclasses import dataclass

from . import coordinates

@dataclass(frozen=True)
class MetroWarning:
    message: str
    details: str
    station: str
    coordinates: coordinates.Coordinates
