import pytest
from TWMetro.parsing import parse_metrostations

def test_metro_station_parsing():
    # Load ExamplePayload
    with open("tests/parse/ExamplePayloads/metrostations.kml", "r", encoding="utf-8") as f:
        kml_content = f.read()

    assert kml_content, "KML content should not be empty"

    # Mock requests.Response
    class MockResponse:
        def __init__(self, text):
            self.text = text
    mock_response = MockResponse(kml_content)
    # Parse the KML content
    train_statuses = parse_metrostations(mock_response)
    assert len(train_statuses) != 0, "Parsed metro stations should not be empty"
    for station in train_statuses:
        assert station.name, "Metro station name should not be empty"
        assert station.coordinates, "Metro station coordinates should not be empty"
        assert station.station_id, "Metro station station_id should not be empty"