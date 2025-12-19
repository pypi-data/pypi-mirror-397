import requests
import xml.etree.ElementTree as ET

from ..models import MetroLine, LineString, Coordinates

LINE_MAPPING = {
    "Y": "Yellow Line",
    "G": "Green Line",
}

def parse_metrolines(request_response: requests.Response) -> list[MetroLine]:

    lines_root = ET.fromstring(request_response.text)

    lines_document = lines_root.find('{http://www.opengis.net/kml/2.2}Document')
    if lines_document is None:
        raise ValueError("Invalid KML: Missing Document element")

    metro_lines = []

    for placemark in lines_document.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        # Line ID is SimpleData name=Line
        placemark_id = placemark.find('{http://www.opengis.net/kml/2.2}ExtendedData/{http://www.opengis.net/kml/2.2}SchemaData/{http://www.opengis.net/kml/2.2}SimpleData[@name="Line"]')

        if placemark_id is None:
            continue

        parsed_geometry = []

        for line_string in placemark.findall('.//{http://www.opengis.net/kml/2.2}LineString'):
            coordinates = line_string.find('{http://www.opengis.net/kml/2.2}coordinates')
            if coordinates is not None and coordinates.text:
                coord_list = []
                for coord in coordinates.text.strip().split():
                    lon, lat, *rest = map(float, coord.split(','))
                    coord_list.append((lat, lon))
                line_string_obj = LineString(coordinates=[Coordinates(lat=lat, lon=lon) for lat, lon in coord_list])
                parsed_geometry.append(line_string_obj)

        metro_lines.append(MetroLine(
            name=LINE_MAPPING.get(placemark_id.text, placemark_id.text if placemark_id is not None else "Unknown Line"),
            multiGeometry=parsed_geometry
        ))

    return metro_lines


