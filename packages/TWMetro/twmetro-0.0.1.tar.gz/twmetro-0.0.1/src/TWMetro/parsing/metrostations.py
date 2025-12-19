import requests
import xml.etree.ElementTree as ET

from ..models import MetroStation
from ..models import Coordinates

def parse_metrostations(request_response: requests.Response) -> list[MetroStation]:

    stations_root = ET.fromstring(request_response.text)

    stations_document = stations_root.find('{http://www.opengis.net/kml/2.2}Document')
    if stations_document is None:
        raise ValueError("Invalid KML: Missing Document element")

    metro_stations = []

    for placemark in stations_document.findall('{http://www.opengis.net/kml/2.2}Placemark'):
        placemark_id = placemark.get('id')
        placemark_coordinates = placemark.find('{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')
        placemark_rotation = placemark.find('{http://www.opengis.net/kml/2.2}Rotation')
        placemark_extended_data = placemark.find('{http://www.opengis.net/kml/2.2}ExtendedData/{http://www.opengis.net/kml/2.2}Data[@name="details"]/{http://www.opengis.net/kml/2.2}value')

        # Parse name from CDATA
        parsed_name     = ""
        if placemark_extended_data is not None and placemark_extended_data.text is not None:
            cdata_content = placemark_extended_data.text
            # Extract the "Station" information from the HTML table
            try:
                name_start = cdata_content.index('<th>Station</th>') + len('<th>Station</th>')
                name_start = cdata_content.index('<td>', name_start) + len('<td>')
                name_end = cdata_content.index('</td>', name_start)
                parsed_name = cdata_content[name_start:name_end]
            except ValueError:
                parsed_name = ""

        metro_stations.append(MetroStation(
            station_id=placemark_id if placemark_id is not None else "",
            name=parsed_name,
            coordinates=Coordinates(
                lat=float(placemark_coordinates.text.split(',')[1]) if placemark_coordinates is not None else 0.0,
                lon=float(placemark_coordinates.text.split(',')[0]) if placemark_coordinates is not None else 0.0,
            ),
        ))

    return metro_stations


