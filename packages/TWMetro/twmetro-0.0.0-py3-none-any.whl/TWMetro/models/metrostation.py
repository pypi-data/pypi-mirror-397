from dataclasses import dataclass

from . import coordinates

@dataclass(frozen=True)
class MetroStation:
    station_id:  str
    name: str
    coordinates: coordinates.Coordinates