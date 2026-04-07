from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


def generate_gpx(
    coordinates: list[tuple[float, float, float | None]],
    activity_name: str,
    start_time: datetime,
    duration_seconds: int,
) -> str:
    gpx = ET.Element(
        "gpx",
        {
            "version": "1.1",
            "creator": "AllTrailsToStrava",
            "xmlns": "http://www.topografix.com/GPX/1/1",
        },
    )

    metadata = ET.SubElement(gpx, "metadata")
    ET.SubElement(metadata, "name").text = activity_name
    ET.SubElement(metadata, "time").text = start_time.isoformat() + "Z"

    trk = ET.SubElement(gpx, "trk")
    ET.SubElement(trk, "name").text = activity_name
    trkseg = ET.SubElement(trk, "trkseg")

    num_points = len(coordinates)
    time_interval = duration_seconds / max(num_points - 1, 1)

    for i, coord in enumerate(coordinates):
        lat, lon = coord[0], coord[1]
        trkpt = ET.SubElement(
            trkseg, "trkpt", {"lat": str(lat), "lon": str(lon)}
        )
        if len(coord) > 2 and coord[2] is not None:
            ET.SubElement(trkpt, "ele").text = str(coord[2])
        point_time = start_time + timedelta(seconds=i * time_interval)
        ET.SubElement(trkpt, "time").text = point_time.isoformat() + "Z"

    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        gpx, encoding="unicode"
    )
