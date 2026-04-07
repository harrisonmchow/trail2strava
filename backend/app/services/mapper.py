ACTIVITY_TYPE_MAP: dict[str, str] = {
    "hike": "Hike",
    "hiking": "Hike",
    "walk": "Walk",
    "walking": "Walk",
    "run": "Run",
    "running": "Run",
    "trail run": "TrailRun",
    "trail running": "TrailRun",
    "bike": "Ride",
    "biking": "Ride",
    "cycling": "Ride",
    "road cycling": "Ride",
    "mountain bike": "MountainBikeRide",
    "mountain biking": "MountainBikeRide",
    "gravel biking": "GravelRide",
    "e-bike": "EBikeRide",
    "e-mountain biking": "EMountainBikeRide",
    "kayaking": "Kayaking",
    "canoeing": "Canoeing",
    "paddle boarding": "StandUpPaddling",
    "stand up paddling": "StandUpPaddling",
    "cross-country skiing": "NordicSki",
    "snowshoeing": "Snowshoe",
    "skiing": "AlpineSki",
    "backcountry skiing": "BackcountrySki",
    "rock climbing": "RockClimbing",
    "horseback riding": "Ride",
    "wheelchair": "Wheelchair",
}

DEFAULT_SPORT_TYPE = "Hike"


def map_activity_type(alltrails_type: str) -> str:
    normalized = alltrails_type.strip().lower()
    return ACTIVITY_TYPE_MAP.get(normalized, DEFAULT_SPORT_TYPE)
