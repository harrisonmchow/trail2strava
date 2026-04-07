from __future__ import annotations

import json
import re

from playwright.async_api import async_playwright, Response

from app.models.alltrails import AllTrailsActivity, AllTrailsPhoto

ALLTRAILS_URL_PATTERN = re.compile(
    r"^https?://(www\.)?alltrails\.com/explore/(recording|map|trail)/[\w._~:/?#\[\]@!$&'()*+,;=%.-]+$"
)


def validate_alltrails_url(url: str) -> bool:
    return bool(ALLTRAILS_URL_PATTERN.match(url))


def _parse_distance(text: str) -> float:
    """Parse distance string like '5.2 mi' or '12.15 km' to meters."""
    text = text.strip().lower().replace(",", "")
    match = re.search(r"([\d.]+)\s*(mi|km|m\b)", text)
    if not match:
        return 0.0
    value = float(match.group(1))
    unit = match.group(2)
    if unit == "mi":
        return value * 1609.34
    elif unit == "km":
        return value * 1000
    return value


def _parse_elevation(text: str) -> float:
    """Parse elevation string like '1,200 ft' or '689 m' to meters."""
    text = text.strip().lower().replace(",", "")
    match = re.search(r"([\d.]+)\s*(ft|m\b)", text)
    if not match:
        return 0.0
    value = float(match.group(1))
    unit = match.group(2)
    if unit == "ft":
        return value * 0.3048
    return value


def _parse_duration(text: str) -> int:
    """Parse duration like '3:26:08' or '2h 30m' to seconds."""
    text = text.strip()

    # Try colon format first: "3:26:08" or "26:08"
    colon_match = re.match(r"^(\d+):(\d{2}):(\d{2})$", text)
    if colon_match:
        return (
            int(colon_match.group(1)) * 3600
            + int(colon_match.group(2)) * 60
            + int(colon_match.group(3))
        )
    colon_match = re.match(r"^(\d+):(\d{2})$", text)
    if colon_match:
        return int(colon_match.group(1)) * 60 + int(colon_match.group(2))

    # Try h/m/s format: "2h 30m"
    text_lower = text.lower()
    hours = minutes = seconds = 0
    h_match = re.search(r"(\d+)\s*h", text_lower)
    m_match = re.search(r"(\d+)\s*m", text_lower)
    s_match = re.search(r"(\d+)\s*s", text_lower)
    if h_match or m_match or s_match:
        hours = int(h_match.group(1)) if h_match else 0
        minutes = int(m_match.group(1)) if m_match else 0
        seconds = int(s_match.group(1)) if s_match else 0
        return hours * 3600 + minutes * 60 + seconds

    return 0


async def scrape_alltrails(url: str) -> AllTrailsActivity:
    if not validate_alltrails_url(url):
        raise ValueError("Invalid AllTrails URL")

    coordinates: list[tuple[float, float, float | None]] = []
    captured_responses: dict[str, object] = {}
    photos: list[AllTrailsPhoto] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()

        # Capture ALL network responses for GPS/track data
        async def handle_response(response: Response):
            try:
                resp_url = response.url
                content_type = response.headers.get("content-type", "")
                # Capture JSON API responses
                if "json" in content_type:
                    body = await response.text()
                    try:
                        data = json.loads(body)
                        captured_responses[resp_url] = data
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass

        page.on("response", handle_response)

        await page.goto(url, wait_until="networkidle", timeout=45000)

        # Wait extra for dynamic content to load
        await page.wait_for_timeout(3000)

        # Dismiss cookie/consent banners
        try:
            for selector in [
                "button:has-text('Accept')",
                "button:has-text('Got it')",
                "button:has-text('OK')",
                "[data-testid='close-button']",
            ]:
                btn = page.locator(selector)
                if await btn.count() > 0:
                    await btn.first.click()
                    await page.wait_for_timeout(300)
                    break
        except Exception:
            pass

        # ===== EXTRACT METADATA FROM OG TAGS =====
        og_data = await page.evaluate("""
            () => {
                const getMeta = (prop) => {
                    const el = document.querySelector(`meta[property="${prop}"]`) ||
                               document.querySelector(`meta[name="${prop}"]`);
                    return el ? el.getAttribute('content') : null;
                };
                return {
                    title: getMeta('og:title'),
                    image: getMeta('og:image'),
                    lat: getMeta('place:location:latitude'),
                    lon: getMeta('place:location:longitude'),
                };
            }
        """)

        # ===== EXTRACT TITLE =====
        title = ""
        try:
            # Try H1 first (most reliable)
            h1 = page.locator("h1").first
            title = (await h1.text_content() or "").strip()
        except Exception:
            pass
        if not title:
            title = og_data.get("title") or "AllTrails Activity"

        # ===== EXTRACT STATS FROM DATA SECTIONS =====
        stats_data = await page.evaluate(
            r"""
            () => {
                const result = {
                    stats: [],
                    dateType: null,
                };

                // Strategy 1: Find data sections by class pattern (AllTrails uses CSS modules)
                // The stats section contains labeled data values
                const allElements = document.querySelectorAll('div, span, p');
                const statLabels = ['distance', 'elev. gain', 'elevation gain', 'elevation',
                                    'moving time', 'avg. pace', 'avg pace', 'average pace',
                                    'calories', 'total time', 'est. steps', 'elapsed time'];

                for (const el of allElements) {
                    const text = (el.textContent || '').trim().toLowerCase();
                    if (statLabels.some(label => text === label)) {
                        // Found a label - get the sibling/parent value
                        const parent = el.parentElement;
                        if (parent) {
                            const children = Array.from(parent.children);
                            const texts = children.map(c => c.textContent.trim()).filter(t => t && t.toLowerCase() !== text);
                            if (texts.length > 0) {
                                result.stats.push({
                                    label: text,
                                    value: texts[0]
                                });
                            }
                        }
                    }
                }

                // Strategy 2: Look for the date + activity type line (e.g., "April 2, 2026 • Snowshoeing")
                const bodyText = document.body.innerText;
                const dateTypeMatch = bodyText.match(
                    /(\w+ \d{1,2},? \d{4})\s*[•·]\s*(\w[\w\s]*?)(?:\n|$)/
                );
                if (dateTypeMatch) {
                    result.dateType = {
                        date: dateTypeMatch[1].trim(),
                        type: dateTypeMatch[2].trim()
                    };
                }

                // Strategy 3: Extract all text blocks that look like stat values
                // Look for sections with numeric values near stat-like labels
                const sections = document.querySelectorAll('[class*="statsSection"], [class*="dataSection"], [class*="stat"]');
                for (const section of sections) {
                    const sectionText = section.textContent.trim();
                    if (sectionText) {
                        result.stats.push({
                            label: '_raw_section',
                            value: sectionText
                        });
                    }
                }

                return result;
            }
        """
        )

        # Parse extracted stats
        distance_meters = 0.0
        elevation_meters = 0.0
        duration_seconds = 0
        moving_time_seconds = 0
        avg_pace = ""
        calories = 0
        activity_type = "Hike"
        date = ""

        for stat in stats_data.get("stats", []):
            label = stat["label"].lower()
            value = stat["value"]

            if "distance" in label:
                distance_meters = _parse_distance(value)
            elif "elev" in label or "elevation" in label:
                elevation_meters = _parse_elevation(value)
            elif "moving time" in label:
                moving_time_seconds = _parse_duration(value)
            elif "total time" in label or "elapsed" in label:
                duration_seconds = _parse_duration(value)
            elif "pace" in label:
                avg_pace = value
            elif "calories" in label or "cal" in label:
                cal_match = re.search(r"([\d,]+)", value.replace(",", ""))
                if cal_match:
                    calories = int(cal_match.group(1))

        # Use moving time as duration if total time wasn't found
        if duration_seconds == 0 and moving_time_seconds > 0:
            duration_seconds = moving_time_seconds

        # Extract date and activity type from the combined line
        date_type = stats_data.get("dateType")
        if date_type:
            if date_type.get("date"):
                date = date_type["date"]
            if date_type.get("type"):
                activity_type = date_type["type"]

        # If stats weren't found via labels, try a broader extraction
        if distance_meters == 0 and elevation_meters == 0:
            fallback_stats = await page.evaluate(
                r"""
                () => {
                    const text = document.body.innerText;
                    const result = {};

                    // Distance: look for patterns like "12.15 km" or "5.2 mi"
                    const distMatch = text.match(/([\d.]+)\s*(km|mi)\b/i);
                    if (distMatch) result.distance = distMatch[0];

                    // Elevation: look for patterns like "689 m" near elevation context or "1,200 ft"
                    const elevMatch = text.match(/([\d,]+)\s*(m|ft)\s*$/im) ||
                                      text.match(/elev[\.\w]*\s*(?:gain)?\s*([\d,]+)\s*(m|ft)/i);
                    if (elevMatch) result.elevation = elevMatch[0];

                    // Duration: look for HH:MM:SS pattern
                    const timeMatch = text.match(/\b(\d{1,2}:\d{2}:\d{2})\b/);
                    if (timeMatch) result.duration = timeMatch[1];

                    return result;
                }
            """
            )
            if fallback_stats.get("distance"):
                distance_meters = _parse_distance(fallback_stats["distance"])
            if fallback_stats.get("elevation"):
                elevation_meters = _parse_elevation(fallback_stats["elevation"])
            if fallback_stats.get("duration") and duration_seconds == 0:
                duration_seconds = _parse_duration(fallback_stats["duration"])

        # ===== EXTRACT PHOTOS =====
        photo_urls = await page.evaluate("""
            () => {
                const photos = [];
                // AllTrails photo carousel/gallery images
                const imgElements = document.querySelectorAll('img');
                for (const img of imgElements) {
                    const src = img.src || img.getAttribute('data-src') || '';
                    // AllTrails photo URLs typically contain 'photos' or 'images' and are from their CDN
                    if ((src.includes('alltrails') || src.includes('cloudfront')) &&
                        (src.includes('photos') || src.includes('images') || src.includes('Pictures')) &&
                        !src.includes('avatar') && !src.includes('icon') && !src.includes('logo') &&
                        !src.includes('share_image')) {
                        const alt = img.alt || '';
                        if (!photos.some(p => p.url === src)) {
                            photos.push({ url: src, caption: alt || null });
                        }
                    }
                }

                // Also check background images in photo containers
                const photoContainers = document.querySelectorAll(
                    '[class*="photo"], [class*="gallery"], [class*="carousel"], [class*="image"]'
                );
                for (const container of photoContainers) {
                    const style = window.getComputedStyle(container);
                    const bgImage = style.backgroundImage;
                    if (bgImage && bgImage !== 'none') {
                        const urlMatch = bgImage.match(/url\(["']?([^"')]+)["']?\)/);
                        if (urlMatch && (urlMatch[1].includes('photos') || urlMatch[1].includes('Pictures'))) {
                            if (!photos.some(p => p.url === urlMatch[1])) {
                                photos.push({ url: urlMatch[1], caption: null });
                            }
                        }
                    }
                }

                return photos;
            }
        """)
        photos = [AllTrailsPhoto(**p) for p in photo_urls]

        # ===== EXTRACT GPS COORDINATES =====

        # Method 1: Check captured network responses for track/geo data
        for resp_url, data in captured_responses.items():
            coords = _extract_coordinates(data)
            if coords and len(coords) > 5:
                coordinates = coords
                break

        # Method 2: Try to get the map ID and fetch track data via API
        if not coordinates:
            map_id = await page.evaluate("""
                () => {
                    // Look for map ID in page links, scripts, or data attributes
                    const html = document.documentElement.innerHTML;

                    // Pattern: /maps/DIGITS/ in API calls or links
                    const mapMatch = html.match(/\\/maps\\/(\\d{5,})/);
                    if (mapMatch) return mapMatch[1];

                    // Pattern in og:image URL
                    const ogImage = document.querySelector('meta[property="og:image"]');
                    if (ogImage) {
                        const imgMatch = ogImage.content.match(/maps\\/(\\d+)/);
                        if (imgMatch) return imgMatch[1];
                    }

                    return null;
                }
            """)

            if map_id:
                # Try fetching track data via AllTrails API
                for api_path in [
                    f"/api/alltrails/v3/maps/{map_id}/recordings",
                    f"/api/alltrails/maps/{map_id}",
                ]:
                    try:
                        api_resp = await page.evaluate(
                            """
                            async (path) => {
                                try {
                                    const resp = await fetch(path, {
                                        credentials: 'include',
                                        headers: { 'Accept': 'application/json' }
                                    });
                                    if (resp.ok) {
                                        return await resp.json();
                                    }
                                } catch(e) {}
                                return null;
                            }
                        """,
                            api_path,
                        )
                        if api_resp:
                            coords = _extract_coordinates(api_resp)
                            if coords and len(coords) > 5:
                                coordinates = coords
                                break
                    except Exception:
                        pass

        # Method 3: Try extracting coordinates from Mapbox map instance
        if not coordinates:
            try:
                map_coords = await page.evaluate("""
                    () => {
                        // Try accessing Mapbox GL sources directly
                        const canvases = document.querySelectorAll('.mapboxgl-canvas');
                        for (const canvas of canvases) {
                            // Walk up to find the map container
                            let container = canvas.closest('.mapboxgl-map');
                            if (!container) continue;

                            // Try to find the map instance via internal properties
                            const mapKeys = Object.keys(container).filter(k => k.startsWith('_'));
                            for (const key of mapKeys) {
                                const val = container[key];
                                if (val && typeof val.getStyle === 'function') {
                                    const style = val.getStyle();
                                    if (style && style.sources) {
                                        for (const [name, source] of Object.entries(style.sources)) {
                                            if (source.data && source.data.type === 'FeatureCollection') {
                                                for (const feature of source.data.features || []) {
                                                    if (feature.geometry && feature.geometry.coordinates) {
                                                        return feature.geometry.coordinates;
                                                    }
                                                }
                                            }
                                            if (source.data && source.data.geometry) {
                                                return source.data.geometry.coordinates;
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Alternative: check window for any map instances
                        if (window.mapboxgl && window.mapboxgl.Map) {
                            // Map instances aren't globally accessible typically
                        }

                        return null;
                    }
                """)
                if map_coords and isinstance(map_coords, list) and len(map_coords) > 5:
                    coordinates = [
                        (c[1], c[0], c[2] if len(c) > 2 else None)
                        for c in map_coords
                        if isinstance(c, list) and len(c) >= 2
                    ]
            except Exception:
                pass

        # Method 4: Look for encoded polyline or coordinate data in page scripts
        if not coordinates:
            try:
                script_coords = await page.evaluate("""
                    () => {
                        const scripts = document.querySelectorAll('script');
                        for (const script of scripts) {
                            const text = script.textContent || '';
                            // Look for coordinate arrays in script tags
                            const coordMatch = text.match(/"coordinates"\s*:\s*(\[\[[\d\s,.[\]-]+\]\])/);
                            if (coordMatch) {
                                try {
                                    return JSON.parse(coordMatch[1]);
                                } catch(e) {}
                            }
                            // Look for lat/lng arrays
                            const latlngMatch = text.match(/"lat"\s*:\s*([\d.-]+).*?"lng"\s*:\s*([\d.-]+)/g);
                            if (latlngMatch && latlngMatch.length > 5) {
                                const coords = [];
                                for (const m of latlngMatch) {
                                    const lat = m.match(/"lat"\s*:\s*([\d.-]+)/);
                                    const lng = m.match(/"lng"\s*:\s*([\d.-]+)/);
                                    if (lat && lng) {
                                        coords.push([parseFloat(lng[1]), parseFloat(lat[1])]);
                                    }
                                }
                                if (coords.length > 5) return coords;
                            }
                        }
                        return null;
                    }
                """)
                if script_coords and len(script_coords) > 5:
                    coordinates = [
                        (c[1], c[0], c[2] if len(c) > 2 else None)
                        for c in script_coords
                        if isinstance(c, list) and len(c) >= 2
                    ]
            except Exception:
                pass

        await browser.close()

    return AllTrailsActivity(
        url=url,
        title=title or "AllTrails Activity",
        activity_type=activity_type,
        distance_meters=distance_meters,
        elevation_gain_meters=elevation_meters,
        duration_seconds=duration_seconds,
        moving_time_seconds=moving_time_seconds,
        avg_pace=avg_pace,
        calories=calories,
        date=date,
        has_gps_data=len(coordinates) > 0,
        coordinates=coordinates,
        photos=photos,
    )


def _extract_coordinates(
    data: dict | list,
) -> list[tuple[float, float, float | None]]:
    """Recursively search for coordinate arrays in API response data."""
    if isinstance(data, list):
        # Check if it looks like a coordinate array [[lon, lat, ele], ...]
        if (
            len(data) > 2
            and isinstance(data[0], (list, tuple))
            and len(data[0]) >= 2
            and all(isinstance(x, (int, float)) for x in data[0][:2])
        ):
            return [
                (c[1], c[0], c[2] if len(c) > 2 else None)
                for c in data
                if isinstance(c, (list, tuple)) and len(c) >= 2
            ]
        for item in data:
            if isinstance(item, (dict, list)):
                result = _extract_coordinates(item)
                if result and len(result) > 5:
                    return result

    elif isinstance(data, dict):
        # Check common GeoJSON and track data keys
        for key in [
            "coordinates",
            "geometry",
            "features",
            "track",
            "path",
            "points",
            "latlngs",
            "trackPoints",
            "geoJSON",
            "geojson",
            "line",
            "route",
        ]:
            if key in data:
                result = _extract_coordinates(data[key])
                if result and len(result) > 5:
                    return result
        # Recurse into all dict values
        for value in data.values():
            if isinstance(value, (dict, list)):
                result = _extract_coordinates(value)
                if result and len(result) > 5:
                    return result

    return []
