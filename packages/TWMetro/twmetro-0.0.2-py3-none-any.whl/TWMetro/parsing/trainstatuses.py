import requests
import xml.etree.ElementTree as ET

from ..models import TrainStatus
from ..models import Coordinates

def parse_trainstatuses(request_response: requests.Response) -> list[TrainStatus]:
    trainstatuses = request_response.text # XML response

    statuses_root = ET.fromstring(trainstatuses)

    status_document = statuses_root.find('{http://www.opengis.net/kml/2.2}Document')
    if status_document is None:
        raise ValueError("Invalid KML: Missing Document element")

    train_statuses = []

    for placemark in status_document.findall('{http://www.opengis.net/kml/2.2}Placemark'):
        placemark_id = placemark.get('id')
        placemark_coordinates = placemark.find('{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')
        placemark_extended_data = placemark.find('{http://www.opengis.net/kml/2.2}ExtendedData/{http://www.opengis.net/kml/2.2}Data[@name="details"]/{http://www.opengis.net/kml/2.2}value')

        # Parse last seen from CDATA
        parsed_last_seen     = ""
        if placemark_extended_data is not None and placemark_extended_data.text is not None:
            cdata_content = placemark_extended_data.text
            # Extract the "Last seen" information from the HTML table
            try:
                last_seen_start = cdata_content.index('data-title="Last seen">') + len('data-title="Last seen">')
                last_seen_end = cdata_content.index('</td>', last_seen_start)
                parsed_last_seen = cdata_content[last_seen_start:last_seen_end]
            except ValueError:
                parsed_last_seen = ""

        train_statuses.append(TrainStatus(
            runningNumber=int(placemark_id) if placemark_id is not None else 0,
            coordinates=Coordinates(
                lat=float(placemark_coordinates.text.split(',')[1]) if placemark_coordinates is not None else 0.0,
                lon=float(placemark_coordinates.text.split(',')[0]) if placemark_coordinates is not None else 0.0,
            ),
            lastSeen=parsed_last_seen,
        ))

    return train_statuses


