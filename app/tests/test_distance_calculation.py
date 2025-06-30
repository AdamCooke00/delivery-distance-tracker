"""
Test cases for distance calculation functionality.

This module tests the Haversine formula implementation and related
distance calculation utilities with known coordinate pairs.
"""

import pytest
import math
from app.utils.distance import (
    calculate_distance,
    haversine_distance,
    calculate_distance_from_coordinates,
    convert_distance_unit,
    get_distance_bounds,
    calculate_bearing,
    is_coordinate_in_bounds,
    EARTH_RADIUS_KM,
    EARTH_RADIUS_MILES,
)


class TestDistanceCalculation:
    """Test distance calculation functionality."""

    def test_distance_calculation_known_locations(self):
        """Test distance calculation between known locations"""
        # Test cases with known distances (approximate)
        test_cases = [
            {
                "name": "NYC to Los Angeles",
                "coords": ((40.7128, -74.0060), (34.0522, -118.2437)),
                "expected_km": 3944,
                "tolerance_km": 50,  # 50km tolerance
            },
            {
                "name": "London to Paris",
                "coords": ((51.5074, -0.1278), (48.8566, 2.3522)),
                "expected_km": 344,
                "tolerance_km": 20,
            },
            {
                "name": "Berlin to Munich",
                "coords": ((52.5200, 13.4050), (48.1351, 11.5820)),
                "expected_km": 504,
                "tolerance_km": 25,
            },
            {
                "name": "Tokyo to Osaka",
                "coords": ((35.6762, 139.6503), (34.6937, 135.5023)),
                "expected_km": 400,
                "tolerance_km": 25,
            },
            {
                "name": "Sydney to Melbourne",
                "coords": ((33.8688, 151.2093), (37.8136, 144.9631)),
                "expected_km": 713,
                "tolerance_km": 30,
            },
        ]

        for test_case in test_cases:
            (lat1, lng1), (lat2, lng2) = test_case["coords"]

            # Test km calculation
            distance_km = calculate_distance(lat1, lng1, lat2, lng2, "km")
            expected_km = test_case["expected_km"]
            tolerance_km = test_case["tolerance_km"]

            assert (
                abs(distance_km - expected_km) <= tolerance_km
            ), f"{test_case['name']}: Expected ~{expected_km}km, got {distance_km}km"

            # Test miles calculation
            distance_miles = calculate_distance(lat1, lng1, lat2, lng2, "miles")
            expected_miles = expected_km * 0.621371
            tolerance_miles = tolerance_km * 0.621371

            assert (
                abs(distance_miles - expected_miles) <= tolerance_miles
            ), f"{test_case['name']}: Expected ~{expected_miles:.1f}mi, got {distance_miles}mi"

            print(
                f"✅ {test_case['name']}: {distance_km:.1f}km / {distance_miles:.1f}mi"
            )

        print("✅ Distance calculation for known locations accurate")

    def test_distance_calculation_same_location(self):
        """Test distance calculation for same location"""
        test_coordinates = [
            (40.7128, -74.0060),  # New York
            (0.0, 0.0),  # Equator, Prime Meridian
            (90.0, 0.0),  # North Pole
            (-90.0, 0.0),  # South Pole
        ]

        for lat, lng in test_coordinates:
            distance_km = calculate_distance(lat, lng, lat, lng, "km")
            distance_miles = calculate_distance(lat, lng, lat, lng, "miles")

            assert distance_km == 0.0, f"Same location should be 0km: {distance_km}"
            assert (
                distance_miles == 0.0
            ), f"Same location should be 0mi: {distance_miles}"

        print("✅ Same location distance calculation works")

    def test_distance_calculation_invalid_coordinates(self):
        """Test distance calculation with invalid coordinates"""
        invalid_test_cases = [
            (91.0, 0.0, 0.0, 0.0),  # Invalid latitude > 90
            (-91.0, 0.0, 0.0, 0.0),  # Invalid latitude < -90
            (0.0, 181.0, 0.0, 0.0),  # Invalid longitude > 180
            (0.0, -181.0, 0.0, 0.0),  # Invalid longitude < -180
            (0.0, 0.0, 91.0, 0.0),  # Invalid second latitude
            (0.0, 0.0, 0.0, 181.0),  # Invalid second longitude
        ]

        for lat1, lng1, lat2, lng2 in invalid_test_cases:
            with pytest.raises(ValueError):
                calculate_distance(lat1, lng1, lat2, lng2)

        print("✅ Invalid coordinate validation works")

    def test_haversine_formula_accuracy(self):
        """Test Haversine formula implementation accuracy"""
        # Test with specific coordinates where distance is well-known
        test_cases = [
            {
                "name": "Equator quarter circle",
                "coords": (0.0, 0.0, 0.0, 90.0),
                "expected_km": math.pi
                * EARTH_RADIUS_KM
                / 2,  # Quarter of Earth's circumference
                "tolerance_percent": 0.1,
            },
            {
                "name": "Meridian quarter circle",
                "coords": (0.0, 0.0, 90.0, 0.0),
                "expected_km": math.pi * EARTH_RADIUS_KM / 2,
                "tolerance_percent": 0.1,
            },
            {
                "name": "Antipodal points",
                "coords": (0.0, 0.0, 0.0, 180.0),
                "expected_km": math.pi * EARTH_RADIUS_KM,  # Half Earth's circumference
                "tolerance_percent": 0.1,
            },
        ]

        for test_case in test_cases:
            lat1, lng1, lat2, lng2 = test_case["coords"]
            distance = haversine_distance(lat1, lng1, lat2, lng2)
            expected = test_case["expected_km"]
            tolerance = expected * test_case["tolerance_percent"] / 100

            assert (
                abs(distance - expected) <= tolerance
            ), f"{test_case['name']}: Expected {expected:.1f}km, got {distance:.1f}km"

            print(
                f"✅ {test_case['name']}: {distance:.1f}km (expected ~{expected:.1f}km)"
            )

        print("✅ Haversine formula accuracy validated")

    def test_distance_calculation_edge_cases(self):
        """Test distance calculation edge cases"""
        edge_cases = [
            {
                "name": "Across date line",
                "coords": (0.0, 179.0, 0.0, -179.0),
                "expected_km": 222.39,  # Approximately 2 degrees at equator
                "tolerance_km": 10,
            },
            {
                "name": "Near North Pole",
                "coords": (89.0, 0.0, 89.0, 180.0),
                "expected_km": 222.39,  # Same latitude difference
                "tolerance_km": 50,  # Larger tolerance near poles
            },
            {
                "name": "Near South Pole",
                "coords": (-89.0, 0.0, -89.0, 90.0),
                "expected_km": 157.08,  # Smaller circle near pole
                "tolerance_km": 50,
            },
        ]

        for test_case in edge_cases:
            lat1, lng1, lat2, lng2 = test_case["coords"]
            distance = calculate_distance(lat1, lng1, lat2, lng2)
            expected = test_case["expected_km"]
            tolerance = test_case["tolerance_km"]

            assert (
                abs(distance - expected) <= tolerance
            ), f"{test_case['name']}: Expected ~{expected}km, got {distance}km"

            print(f"✅ {test_case['name']}: {distance:.1f}km")

        print("✅ Edge case distance calculations work")


class TestDistanceUtilities:
    """Test distance utility functions."""

    def test_coordinate_tuple_distance(self):
        """Test distance calculation from coordinate tuples"""
        coord1 = (40.7128, -74.0060)  # NYC
        coord2 = (34.0522, -118.2437)  # LA

        distance = calculate_distance_from_coordinates(coord1, coord2)
        expected_distance = calculate_distance(
            coord1[0], coord1[1], coord2[0], coord2[1]
        )

        assert distance == expected_distance

        # Test invalid tuples
        with pytest.raises(ValueError):
            calculate_distance_from_coordinates((40.7128,), coord2)  # Wrong length

        with pytest.raises(ValueError):
            calculate_distance_from_coordinates("invalid", coord2)  # Wrong type

        print("✅ Coordinate tuple distance calculation works")

    def test_distance_unit_conversion(self):
        """Test distance unit conversion"""
        test_distance = 100.0

        # Test km to miles
        km_to_miles = convert_distance_unit(test_distance, "km", "miles")
        expected_miles = test_distance * 0.621371
        assert abs(km_to_miles - expected_miles) < 0.001

        # Test miles to km
        miles_to_km = convert_distance_unit(test_distance, "miles", "km")
        expected_km = test_distance * 1.609344
        assert abs(miles_to_km - expected_km) < 0.001

        # Test same unit conversions
        assert convert_distance_unit(test_distance, "km", "kilometers") == test_distance
        assert convert_distance_unit(test_distance, "miles", "mi") == test_distance

        # Test invalid units
        with pytest.raises(ValueError):
            convert_distance_unit(test_distance, "invalid", "km")

        print("✅ Distance unit conversion works")

    def test_distance_bounds_calculation(self):
        """Test bounding box calculation for distance queries"""
        center_lat, center_lng = 40.7128, -74.0060  # NYC
        radius_km = 10.0

        min_lat, max_lat, min_lng, max_lng = get_distance_bounds(
            center_lat, center_lng, radius_km, "km"
        )

        # Verify bounds are around center
        assert min_lat < center_lat < max_lat
        assert min_lng < center_lng < max_lng

        # Verify bounds are reasonable (rough approximation)
        lat_diff = max_lat - min_lat
        lng_diff = max_lng - min_lng

        # At NYC latitude, 1 degree latitude ≈ 111km, 1 degree longitude ≈ 85km
        expected_lat_diff = (radius_km * 2) / 111.0
        expected_lng_diff = (radius_km * 2) / 85.0

        assert abs(lat_diff - expected_lat_diff) < 0.05  # 5% tolerance
        assert abs(lng_diff - expected_lng_diff) < 0.05

        # Test with miles
        min_lat_mi, max_lat_mi, min_lng_mi, max_lng_mi = get_distance_bounds(
            center_lat, center_lng, radius_km * 0.621371, "miles"
        )

        # Should be approximately the same
        assert abs(min_lat - min_lat_mi) < 0.001
        assert abs(max_lat - max_lat_mi) < 0.001

        print("✅ Distance bounds calculation works")

    def test_bearing_calculation(self):
        """Test bearing calculation between points"""
        # Test cardinal directions
        center_lat, center_lng = 40.0, -74.0

        # North
        north_bearing = calculate_bearing(
            center_lat, center_lng, center_lat + 1, center_lng
        )
        assert abs(north_bearing - 0.0) < 5.0  # Should be ~0° (North)

        # East
        east_bearing = calculate_bearing(
            center_lat, center_lng, center_lat, center_lng + 1
        )
        assert abs(east_bearing - 90.0) < 5.0  # Should be ~90° (East)

        # South
        south_bearing = calculate_bearing(
            center_lat, center_lng, center_lat - 1, center_lng
        )
        assert abs(south_bearing - 180.0) < 5.0  # Should be ~180° (South)

        # West
        west_bearing = calculate_bearing(
            center_lat, center_lng, center_lat, center_lng - 1
        )
        assert abs(west_bearing - 270.0) < 5.0  # Should be ~270° (West)

        # Test bearing range
        all_bearings = [north_bearing, east_bearing, south_bearing, west_bearing]
        for bearing in all_bearings:
            assert 0 <= bearing <= 360

        print("✅ Bearing calculation works")

    def test_coordinate_bounds_checking(self):
        """Test coordinate bounds checking"""
        # Define a bounding box around NYC
        bounds = (40.5, 41.0, -74.5, -73.5)  # (min_lat, max_lat, min_lng, max_lng)

        # Test coordinates inside bounds
        inside_coords = [(40.7, -74.0), (40.6, -74.2), (40.9, -73.8)]

        for lat, lng in inside_coords:
            assert is_coordinate_in_bounds(lat, lng, bounds)

        # Test coordinates outside bounds
        outside_coords = [
            (40.3, -74.0),  # South of bounds
            (41.2, -74.0),  # North of bounds
            (40.7, -75.0),  # West of bounds
            (40.7, -73.0),  # East of bounds
        ]

        for lat, lng in outside_coords:
            assert not is_coordinate_in_bounds(lat, lng, bounds)

        # Test invalid coordinates
        assert not is_coordinate_in_bounds(91.0, -74.0, bounds)  # Invalid lat
        assert not is_coordinate_in_bounds(40.7, 181.0, bounds)  # Invalid lng

        print("✅ Coordinate bounds checking works")


class TestDistanceFormulas:
    """Test mathematical accuracy of distance formulas."""

    def test_earth_radius_constants(self):
        """Test Earth radius constants are reasonable"""
        # Earth's radius should be approximately 6371 km
        assert 6300 < EARTH_RADIUS_KM < 6400

        # Miles conversion should be approximately correct
        expected_miles = EARTH_RADIUS_KM * 0.621371
        assert abs(EARTH_RADIUS_MILES - expected_miles) < 10

        print("✅ Earth radius constants are accurate")

    def test_distance_precision(self):
        """Test distance calculation precision"""
        # Test very close points (should handle small distances)
        lat1, lng1 = 40.7128, -74.0060
        lat2, lng2 = 40.7129, -74.0061  # Very close to first point

        distance = calculate_distance(lat1, lng1, lat2, lng2)

        # Should be a small but non-zero distance
        assert 0 < distance < 1.0  # Less than 1km

        # Test precision with identical coordinates
        distance_same = calculate_distance(lat1, lng1, lat1, lng1)
        assert distance_same == 0.0

        print("✅ Distance precision handling works")

    def test_distance_rounding(self):
        """Test distance result rounding"""
        # Distance should be rounded to 3 decimal places
        lat1, lng1 = 40.0, -74.0
        lat2, lng2 = 41.0, -75.0

        distance = haversine_distance(lat1, lng1, lat2, lng2)

        # Check decimal places
        decimal_places = len(str(distance).split(".")[-1])
        assert decimal_places <= 3, f"Too many decimal places: {distance}"

        print("✅ Distance rounding works correctly")
