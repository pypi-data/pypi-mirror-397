from .api import Transport
from .parsing import parse_trainstatuses, parse_metrostations, parse_metrolines, parse_metrowarnings
from .models import TrainStatus, MetroLine, MetroStation, MetroWarning

class TWMetro:
    def __init__(self, token: str, *, base_url: str = "https://app-metrortiapi-prod-001.azurewebsites.net/api/geo", timeout: int = 20):
        self.base_url = base_url
        self.timeout = timeout
        self.token = token
        self.transport: Transport = Transport(base_url=base_url, timeout=timeout, token=token)

    def get_trainstatuses(self) -> list[TrainStatus]:
        train_statuses = self.transport.get("trainstatuses.kml")
        parsed_train_statuses = parse_trainstatuses(train_statuses)
        return parsed_train_statuses

    def get_metrolines(self) -> list[MetroLine]:
        metro_lines = self.transport.get("metrolines.kml")
        parsed_metro_lines = parse_metrolines(metro_lines)
        return parsed_metro_lines

    def get_metrostations(self) -> list[MetroStation]:
        metro_stations = self.transport.get("metrostations.kml")
        parsed_metro_stations = parse_metrostations(metro_stations)
        return parsed_metro_stations

    def get_warnings(self) -> list[MetroWarning]:
        metro_warnings = self.transport.get("warning.kml")
        parsed_metro_warnings = parse_metrowarnings(metro_warnings)
        return parsed_metro_warnings