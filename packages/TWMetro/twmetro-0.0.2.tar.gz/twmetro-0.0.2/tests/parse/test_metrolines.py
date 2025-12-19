import pytest
from TWMetro.parsing import parse_metrolines

def test_metro_line_parsing():
    # Load ExamplePayload
    with open("tests/parse/ExamplePayloads/metrolines.kml", "r", encoding="utf-8") as f:
        kml_content = f.read()

    assert kml_content, "KML content should not be empty"

    # Mock requests.Response
    class MockResponse:
        def __init__(self, text):
            self.text = text
    mock_response = MockResponse(kml_content)
    # Parse the KML content
    train_statuses = parse_metrolines(mock_response)
    assert len(train_statuses) != 0, "Parsed metro lines should not be empty"
    for line in train_statuses:
        assert line.name, "Metro line name should not be empty"
        assert line.multiGeometry, "Metro line multiGeometry should not be empty"
        for geom in line.multiGeometry:
            assert geom.coordinates, "Metro line geometry coordinates should not be empty"