import requests
import xml.etree.ElementTree as ET
import re

from ..models import MetroWarning, Coordinates

def parse_metrowarnings(request_response: requests.Response) -> list[MetroWarning]:

    warnings_root = ET.fromstring(request_response.text)

    lines_document = warnings_root.find('{http://www.opengis.net/kml/2.2}Document')
    if lines_document is None:
        raise ValueError("Invalid KML: Missing Document element")

    metro_warnings = []

    for placemark in lines_document.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        # Line ID is SimpleData name=Line
        placemark_id = placemark.get("id")
        placemark_coordinates = placemark.find('{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates')

        placemark_extended_data = placemark.find('{http://www.opengis.net/kml/2.2}ExtendedData/{http://www.opengis.net/kml/2.2}Data[@name="details"]/{http://www.opengis.net/kml/2.2}value')

        # Get message and details from CDATA
        message = ""
        details = ""
        if placemark_extended_data is not None and placemark_extended_data.text is not None:
            cdata_content = placemark_extended_data.text
            td_matches = re.findall(r"<td>(.*?)</td>", cdata_content, re.DOTALL)
            if len(td_matches) >= 2:
                # Remove HTML tags from message
                message = re.sub(r"<.*?>", "", td_matches[0].strip())
                details = td_matches[1].strip()

        metro_warnings.append(MetroWarning(
            message=message,
            details=details,
            station=placemark_id if placemark_id is not None else "",
            coordinates=Coordinates(
                lat=float(placemark_coordinates.text.split(',')[1]) if placemark_coordinates is not None else 0.0,
                lon=float(placemark_coordinates.text.split(',')[0]) if placemark_coordinates is not None else 0.0,
            ),
        ))

    return metro_warnings


