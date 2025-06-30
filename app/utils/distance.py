"""
Distance calculation utilities using the Haversine formula.

This module provides functions to calculate distances between geographic coordinates
with support for different units and comprehensive coordinate validation.
"""

import math
from typing import Tuple

from app.utils.validation import validate_coordinates
from app.utils.logging import get_logger

logger = get_logger(__name__)


# Earth's radius in kilometers
EARTH_RADIUS_KM = 6371.0

# Earth's radius in miles
EARTH_RADIUS_MILES = 3958.8


def haversine_distance(
    lat1: float, lng1: float, lat2: float, lng2: float, unit: str = "km"
) -> float:
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.

    The Haversine formula determines the great-circle distance between two points on a sphere
    given their latitude and longitude coordinates.

    Args:
        lat1: Latitude of first point in decimal degrees
        lng1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lng2: Longitude of second point in decimal degrees
        unit: Distance unit ('km' for kilometers, 'miles' for miles)

    Returns:
        Distance between the two points in the specified unit

    Raises:
        ValueError: If coordinates are invalid or unit is unsupported
    """
    # Validate coordinates
    if not validate_coordinates(lat1, lng1):
        raise ValueError(f"Invalid coordinates for point 1: ({lat1}, {lng1})")

    if not validate_coordinates(lat2, lng2):
        raise ValueError(f"Invalid coordinates for point 2: ({lat2}, {lng2})")

    # Validate unit
    unit = unit.lower()
    if unit not in ["km", "kilometers", "miles", "mi"]:
        raise ValueError(f"Unsupported unit: {unit}. Use 'km' or 'miles'")

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)

    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad

    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))

    # Calculate distance based on unit
    if unit in ["km", "kilometers"]:
        distance = EARTH_RADIUS_KM * c
    else:  # miles
        distance = EARTH_RADIUS_MILES * c

    return round(distance, 3)  # Round to 3 decimal places


def calculate_distance(
    lat1: float, lng1: float, lat2: float, lng2: float, unit: str = "km"
) -> float:
    """
    Calculate distance between two geographic points.

    This is a wrapper around haversine_distance with additional validation and logging.

    Args:
        lat1: Latitude of first point in decimal degrees
        lng1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lng2: Longitude of second point in decimal degrees
        unit: Distance unit ('km' for kilometers, 'miles' for miles)

    Returns:
        Distance between the two points in the specified unit

    Raises:
        ValueError: If coordinates are invalid
    """
    try:
        # Handle same location case
        if lat1 == lat2 and lng1 == lng2:
            logger.debug("Same location detected, returning 0 distance")
            return 0.0

        # Calculate distance
        distance = haversine_distance(lat1, lng1, lat2, lng2, unit)

        logger.debug(
            f"Calculated distance: {distance} {unit} between "
            f"({lat1}, {lng1}) and ({lat2}, {lng2})"
        )

        return distance

    except Exception as e:
        logger.error(f"Distance calculation failed: {e}")
        raise


def calculate_distance_from_coordinates(
    coord1: Tuple[float, float], coord2: Tuple[float, float], unit: str = "km"
) -> float:
    """
    Calculate distance between two coordinate tuples.

    Args:
        coord1: First coordinate as (latitude, longitude) tuple
        coord2: Second coordinate as (latitude, longitude) tuple
        unit: Distance unit ('km' for kilometers, 'miles' for miles)

    Returns:
        Distance between the two points in the specified unit

    Raises:
        ValueError: If coordinates are invalid
    """
    if not isinstance(coord1, (tuple, list)) or len(coord1) != 2:
        raise ValueError("coord1 must be a tuple/list of (latitude, longitude)")

    if not isinstance(coord2, (tuple, list)) or len(coord2) != 2:
        raise ValueError("coord2 must be a tuple/list of (latitude, longitude)")

    lat1, lng1 = coord1
    lat2, lng2 = coord2

    return calculate_distance(lat1, lng1, lat2, lng2, unit)


def convert_distance_unit(distance: float, from_unit: str, to_unit: str) -> float:
    """
    Convert distance from one unit to another.

    Args:
        distance: Distance value to convert
        from_unit: Source unit ('km', 'kilometers', 'miles', 'mi')
        to_unit: Target unit ('km', 'kilometers', 'miles', 'mi')

    Returns:
        Converted distance value

    Raises:
        ValueError: If units are invalid or conversion is not supported
    """
    # Normalize unit names
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    # Define unit groups
    km_units = ["km", "kilometers"]
    mile_units = ["miles", "mi"]

    # Validate units
    valid_units = km_units + mile_units
    if from_unit not in valid_units:
        raise ValueError(f"Invalid source unit: {from_unit}")
    if to_unit not in valid_units:
        raise ValueError(f"Invalid target unit: {to_unit}")

    # No conversion needed if same unit type
    if (from_unit in km_units and to_unit in km_units) or (
        from_unit in mile_units and to_unit in mile_units
    ):
        return distance

    # Convert between km and miles
    if from_unit in km_units and to_unit in mile_units:
        # km to miles
        return round(distance * 0.621371, 3)
    elif from_unit in mile_units and to_unit in km_units:
        # miles to km
        return round(distance * 1.609344, 3)

    # Should never reach here
    raise ValueError(f"Unsupported conversion: {from_unit} to {to_unit}")


def get_distance_bounds(
    center_lat: float, center_lng: float, radius: float, unit: str = "km"
) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box coordinates for a given radius around a center point.

    This is useful for database queries to find points within a certain distance.

    Args:
        center_lat: Center latitude in decimal degrees
        center_lng: Center longitude in decimal degrees
        radius: Radius in the specified unit
        unit: Distance unit ('km' for kilometers, 'miles' for miles)

    Returns:
        Tuple of (min_lat, max_lat, min_lng, max_lng) bounding box coordinates

    Raises:
        ValueError: If coordinates or radius are invalid
    """
    if not validate_coordinates(center_lat, center_lng):
        raise ValueError(f"Invalid center coordinates: ({center_lat}, {center_lng})")

    if radius <= 0:
        raise ValueError("Radius must be positive")

    # Convert radius to kilometers if needed
    if unit.lower() in ["miles", "mi"]:
        radius_km = radius * 1.609344
    else:
        radius_km = radius

    # Calculate angular distance in radians
    angular_distance = radius_km / EARTH_RADIUS_KM

    # Convert center coordinates to radians
    center_lat_rad = math.radians(center_lat)
    center_lng_rad = math.radians(center_lng)

    # Calculate latitude bounds
    min_lat_rad = center_lat_rad - angular_distance
    max_lat_rad = center_lat_rad + angular_distance

    # Calculate longitude bounds (accounting for longitude compression at higher latitudes)
    if min_lat_rad > -math.pi / 2 and max_lat_rad < math.pi / 2:
        # Normal case - not near poles
        delta_lng = math.asin(math.sin(angular_distance) / math.cos(center_lat_rad))
        min_lng_rad = center_lng_rad - delta_lng
        max_lng_rad = center_lng_rad + delta_lng
    else:
        # Near poles - use full longitude range
        min_lng_rad = -math.pi
        max_lng_rad = math.pi

    # Convert back to degrees
    min_lat = math.degrees(max(min_lat_rad, -math.pi / 2))
    max_lat = math.degrees(min(max_lat_rad, math.pi / 2))
    min_lng = math.degrees(min_lng_rad)
    max_lng = math.degrees(max_lng_rad)

    # Handle longitude wraparound
    if min_lng < -180:
        min_lng += 360
    if max_lng > 180:
        max_lng -= 360

    return min_lat, max_lat, min_lng, max_lng


def calculate_bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the initial bearing (forward azimuth) from point 1 to point 2.

    Args:
        lat1: Latitude of first point in decimal degrees
        lng1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lng2: Longitude of second point in decimal degrees

    Returns:
        Initial bearing in degrees (0-360, where 0 is North)

    Raises:
        ValueError: If coordinates are invalid
    """
    if not validate_coordinates(lat1, lng1):
        raise ValueError(f"Invalid coordinates for point 1: ({lat1}, {lng1})")

    if not validate_coordinates(lat2, lng2):
        raise ValueError(f"Invalid coordinates for point 2: ({lat2}, {lng2})")

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlng_rad = math.radians(lng2 - lng1)

    # Calculate bearing
    y = math.sin(dlng_rad) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(
        lat2_rad
    ) * math.cos(dlng_rad)

    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)

    # Normalize to 0-360 degrees
    bearing_deg = (bearing_deg + 360) % 360

    return round(bearing_deg, 1)


def is_coordinate_in_bounds(
    lat: float, lng: float, bounds: Tuple[float, float, float, float]
) -> bool:
    """
    Check if a coordinate is within the given bounding box.

    Args:
        lat: Latitude to check
        lng: Longitude to check
        bounds: Bounding box as (min_lat, max_lat, min_lng, max_lng)

    Returns:
        True if coordinate is within bounds, False otherwise
    """
    if not validate_coordinates(lat, lng):
        return False

    min_lat, max_lat, min_lng, max_lng = bounds

    # Check latitude bounds
    if lat < min_lat or lat > max_lat:
        return False

    # Check longitude bounds (handle wraparound)
    if min_lng <= max_lng:
        # Normal case
        return min_lng <= lng <= max_lng
    else:
        # Wraparound case (crosses 180/-180 boundary)
        return lng >= min_lng or lng <= max_lng
