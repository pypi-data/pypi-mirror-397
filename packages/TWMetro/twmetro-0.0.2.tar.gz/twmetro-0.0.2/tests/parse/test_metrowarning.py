import pytest
from TWMetro.parsing import parse_metrowarnings

def test_metro_station_parsing():
    # Load ExamplePayload
    with open("tests/parse/ExamplePayloads/warning.kml", "r", encoding="utf-8") as f:
        kml_content = f.read()

    assert kml_content, "KML content should not be empty"

    # Mock requests.Response
    class MockResponse:
        def __init__(self, text):
            self.text = text
    mock_response = MockResponse(kml_content)
    # Parse the KML content
    train_statuses = parse_metrowarnings(mock_response)
    assert len(train_statuses) != 0, "Parsed metro warnings should not be empty"
    for warning in train_statuses:
        assert warning.message, "Warning message should not be empty"
        assert warning.details, "Warning details should not be empty"
        assert warning.station, "Warning station should not be empty"
        assert warning.coordinates, "Warning coordinates should not be empty"