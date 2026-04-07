from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from datetime import datetime

from app.models.alltrails import AllTrailsActivity

GPX_NS = {
    "": "http://www.topografix.com/GPX/1/1",
    "gpx10": "http://www.topografix.com/GPX/1/0",
}


def parse_gpx(gpx_content: str, source_url: str = "") -> AllTrailsActivity:
    """Parse a GPX file and extract activity data."""
    root = ET.fromstring(gpx_content)

    # Determine namespace
    ns = ""
    tag = root.tag
    if "{" in tag:
        ns = tag.split("}")[0] + "}"

    def find(el: ET.Element, path: str) -> ET.Element | None:
        # Try with namespace
        result = el.find(f"{ns}{path}")
        if result is None:
            # Try without namespace
            result = el.find(path)
        return result

    def findall(el: ET.Element, path: str) -> list[ET.Element]:
        result = el.findall(f"{ns}{path}")
        if not result:
            result = el.findall(path)
        return result

    # Extract track name
    title = ""
    metadata = find(root, "metadata")
    if metadata is not None:
        name_el = find(metadata, "name")
        if name_el is not None and name_el.text:
            title = name_el.text.strip()

    # Try track name
    if not title:
        for trk in findall(root, "trk"):
            name_el = find(trk, "name")
            if name_el is not None and name_el.text:
                title = name_el.text.strip()
                break

    if not title:
        title = "AllTrails Activity"

    # Extract all track points
    coordinates: list[tuple[float, float, float | None]] = []
    timestamps: list[datetime] = []

    for trk in findall(root, "trk"):
        for trkseg in findall(trk, "trkseg"):
            for trkpt in findall(trkseg, "trkpt"):
                lat = float(trkpt.get("lat", 0))
                lon = float(trkpt.get("lon", 0))

                ele_el = find(trkpt, "ele")
                ele = float(ele_el.text) if ele_el is not None and ele_el.text else None

                time_el = find(trkpt, "time")
                if time_el is not None and time_el.text:
                    try:
                        ts = datetime.fromisoformat(
                            time_el.text.replace("Z", "+00:00")
                        )
                        timestamps.append(ts)
                    except ValueError:
                        pass

                coordinates.append((lat, lon, ele))

    # Calculate stats from coordinates
    distance_meters = _calculate_distance(coordinates)
    elevation_gain = _calculate_elevation_gain(coordinates)

    # Calculate duration from timestamps
    duration_seconds = 0
    date = ""
    if timestamps:
        date = timestamps[0].isoformat()
        duration_seconds = int(
            (timestamps[-1] - timestamps[0]).total_seconds()
        )

    # Try to detect activity type from title or GPX metadata
    activity_type = _detect_activity_type(title, gpx_content)

    return AllTrailsActivity(
        url=source_url,
        title=title,
        activity_type=activity_type,
        distance_meters=distance_meters,
        elevation_gain_meters=elevation_gain,
        duration_seconds=duration_seconds,
        moving_time_seconds=duration_seconds,
        date=date,
        has_gps_data=len(coordinates) > 0,
        coordinates=coordinates,
    )


def _calculate_distance(
    coords: list[tuple[float, float, float | None]],
) -> float:
    """Calculate total distance in meters using the Haversine formula."""
    total = 0.0
    for i in range(1, len(coords)):
        lat1, lon1 = math.radians(coords[i - 1][0]), math.radians(coords[i - 1][1])
        lat2, lon2 = math.radians(coords[i][0]), math.radians(coords[i][1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        total += 6371000 * c  # Earth radius in meters

    return total


def _calculate_elevation_gain(
    coords: list[tuple[float, float, float | None]],
) -> float:
    """Calculate total elevation gain in meters."""
    gain = 0.0
    for i in range(1, len(coords)):
        ele_prev = coords[i - 1][2]
        ele_curr = coords[i][2]
        if ele_prev is not None and ele_curr is not None:
            diff = ele_curr - ele_prev
            if diff > 0:
                gain += diff
    return gain


def _detect_activity_type(title: str, gpx_content: str) -> str:
    """Try to detect activity type from title and GPX metadata."""
    text = (title + " " + gpx_content[:500]).lower()

    if "snowshoe" in text:
        return "Snowshoeing"
    if "trail run" in text:
        return "Trail Run"
    if "run" in text and "trail" not in text:
        return "Run"
    if "mountain bik" in text or "mtb" in text:
        return "Mountain Bike"
    if "bik" in text or "cycl" in text:
        return "Bike"
    if "walk" in text:
        return "Walk"
    if "kayak" in text:
        return "Kayaking"
    if "ski" in text:
        return "Skiing"

    return "Hike"
