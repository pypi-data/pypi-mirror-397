from dataclasses import dataclass

from . import coordinates

@dataclass(frozen=True)
class LineString:
    coordinates: list[coordinates.Coordinates]  # List of (longitude, latitude) tuples

@dataclass(frozen=True)
class MetroLine:
    name: str
    multiGeometry: list[LineString]