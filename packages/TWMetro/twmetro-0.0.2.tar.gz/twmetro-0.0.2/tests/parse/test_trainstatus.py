import pytest
from TWMetro.parsing import parse_trainstatuses

def test_train_status_parsing():
    # Load ExamplePayload
    with open("tests/parse/ExamplePayloads/trainstatuses.kml", "r", encoding="utf-8") as f:
        kml_content = f.read()

    assert kml_content, "KML content should not be empty"

    # Mock requests.Response
    class MockResponse:
        def __init__(self, text):
            self.text = text
    mock_response = MockResponse(kml_content)
    # Parse the KML content
    train_statuses = parse_trainstatuses(mock_response)
    assert len(train_statuses) != 0, "Parsed train statuses should not be empty"
    for status in train_statuses:
        assert status.runningNumber, "Running number should not be empty"
        assert status.coordinates, "Coordinates should not be empty"
        assert status.lastSeen, "Last seen should not be empty"
