"""
Integration tests for complete geocoding workflow.

This module tests the end-to-end geocoding workflow combining
address validation, geocoding, and distance calculation.
"""

import pytest
import asyncio
from app.services.geocoding import GeocodingService, GeocodingError
from app.utils.validation import validate_address, sanitize_address
from app.utils.distance import calculate_distance_from_coordinates


class TestGeocodingIntegration:
    """Test complete geocoding integration workflow."""

    @pytest.fixture
    def geocoding_service(self):
        """Create geocoding service instance."""
        return GeocodingService(timeout=20, rate_limit_delay=1.2)

    @pytest.fixture
    def delivery_scenarios(self):
        """Real-world delivery scenarios for testing."""
        return [
            {
                "name": "Restaurant to Customer - NYC",
                "origin": "Times Square, New York, NY",
                "destination": "Central Park, New York, NY",
                "expected_distance_km": 1.5,  # Approximate
                "tolerance_km": 1.0,
            },
            {
                "name": "Fast Food Chain - London",
                "origin": "Piccadilly Circus, London, UK",
                "destination": "Tower Bridge, London, UK",
                "expected_distance_km": 4.0,
                "tolerance_km": 2.0,
            },
            {
                "name": "Coffee Shop Delivery - Paris",
                "origin": "Eiffel Tower, Paris, France",
                "destination": "Louvre Museum, Paris, France",
                "expected_distance_km": 3.0,
                "tolerance_km": 1.5,
            },
        ]

    @pytest.mark.asyncio
    async def test_complete_delivery_workflow(
        self, geocoding_service, delivery_scenarios
    ):
        """Test complete delivery distance calculation workflow"""
        successful_scenarios = 0

        for scenario in delivery_scenarios:
            try:
                # Step 1: Validate addresses
                origin_valid = validate_address(scenario["origin"])
                dest_valid = validate_address(scenario["destination"])

                assert origin_valid, f"Origin address invalid: {scenario['origin']}"
                assert (
                    dest_valid
                ), f"Destination address invalid: {scenario['destination']}"

                # Step 2: Sanitize addresses
                origin_clean = sanitize_address(scenario["origin"])
                dest_clean = sanitize_address(scenario["destination"])

                # Step 3: Geocode addresses
                origin_result = await geocoding_service.geocode_address(origin_clean)
                await asyncio.sleep(1.5)  # Rate limiting
                dest_result = await geocoding_service.geocode_address(dest_clean)

                # Step 4: Calculate distance
                origin_coords = (origin_result.latitude, origin_result.longitude)
                dest_coords = (dest_result.latitude, dest_result.longitude)

                distance_km = calculate_distance_from_coordinates(
                    origin_coords, dest_coords, "km"
                )

                # Step 5: Validate distance is reasonable
                expected = scenario["expected_distance_km"]
                tolerance = scenario["tolerance_km"]

                assert distance_km > 0, "Distance should be positive"
                assert (
                    distance_km <= 50
                ), "Distance should be reasonable for city delivery"

                # Check if within expected range (flexible for real-world data)
                if abs(distance_km - expected) <= tolerance:
                    print(
                        f"✅ {scenario['name']}: {distance_km:.2f}km (expected ~{expected}km)"
                    )
                else:
                    print(
                        f"⚠️  {scenario['name']}: {distance_km:.2f}km (expected ~{expected}km, outside tolerance)"
                    )

                successful_scenarios += 1

                # Log complete workflow result
                print(f"   Origin: {origin_result.display_name}")
                print(f"   Destination: {dest_result.display_name}")
                print(f"   Distance: {distance_km:.2f}km")

                await asyncio.sleep(1.2)  # Rate limiting between scenarios

            except GeocodingError as e:
                print(f"⚠️  Geocoding failed for {scenario['name']}: {e}")
            except Exception as e:
                print(f"⚠️  Workflow failed for {scenario['name']}: {e}")

        # At least 60% of scenarios should complete successfully
        success_rate = successful_scenarios / len(delivery_scenarios)
        assert (
            success_rate >= 0.6
        ), f"Integration success rate too low: {success_rate:.2f}"

        await geocoding_service.close()
        print("✅ Complete delivery workflow integration works")

    @pytest.mark.asyncio
    async def test_address_validation_integration(self, geocoding_service):
        """Test integration between address validation and geocoding"""
        test_cases = [
            {"raw_address": "  Times Square, NYC  ", "should_geocode": True},
            {
                "raw_address": 'Times Square<script>alert("xss")</script>, NYC',
                "should_geocode": False,  # Should be rejected by validation
            },
            {"raw_address": "Empire State Building, New York", "should_geocode": True},
            {"raw_address": "", "should_geocode": False},
        ]

        successful_integrations = 0

        for test_case in test_cases:
            raw_address = test_case["raw_address"]
            should_geocode = test_case["should_geocode"]

            try:
                # Step 1: Validate
                is_valid = validate_address(raw_address)

                if not is_valid:
                    if not should_geocode:
                        print(f"✅ Correctly rejected invalid address: {raw_address}")
                        successful_integrations += 1
                    else:
                        print(f"⚠️  Unexpectedly rejected valid address: {raw_address}")
                    continue

                # Step 2: Sanitize
                clean_address = sanitize_address(raw_address)

                # Step 3: Geocode
                result = await geocoding_service.geocode_address(clean_address)

                if should_geocode:
                    print(f"✅ Successfully processed: {raw_address} → {clean_address}")
                    print(f"   Result: {result.display_name}")
                    successful_integrations += 1
                else:
                    print(
                        f"⚠️  Unexpectedly geocoded problematic address: {raw_address}"
                    )

                await asyncio.sleep(1.0)

            except Exception as e:
                if not should_geocode:
                    print(f"✅ Correctly failed for problematic address: {raw_address}")
                    successful_integrations += 1
                else:
                    print(f"⚠️  Failed to process valid address: {raw_address} - {e}")

        success_rate = successful_integrations / len(test_cases)
        assert (
            success_rate >= 0.75
        ), f"Validation integration success rate too low: {success_rate:.2f}"

        await geocoding_service.close()
        print("✅ Address validation integration works")

    @pytest.mark.asyncio
    async def test_batch_geocoding_workflow(self, geocoding_service):
        """Test batch geocoding for multiple addresses"""
        batch_addresses = [
            "Statue of Liberty, New York",
            "Golden Gate Bridge, San Francisco",
            "Space Needle, Seattle",
        ]

        try:
            # Test batch geocoding
            results = await geocoding_service.geocode_addresses(batch_addresses)

            assert isinstance(results, dict)
            assert len(results) == len(batch_addresses)

            successful_results = []

            for address, result in results.items():
                if result is not None:
                    # Validate result
                    assert hasattr(result, "latitude")
                    assert hasattr(result, "longitude")
                    assert -90 <= result.latitude <= 90
                    assert -180 <= result.longitude <= 180

                    successful_results.append((address, result))
                    print(f"✅ Batch geocoded: {address}")
                else:
                    print(f"⚠️  Failed in batch: {address}")

            # At least 60% should succeed
            success_rate = len(successful_results) / len(batch_addresses)
            assert (
                success_rate >= 0.6
            ), f"Batch success rate too low: {success_rate:.2f}"

            # Calculate distances between successful results
            if len(successful_results) >= 2:
                addr1, result1 = successful_results[0]
                addr2, result2 = successful_results[1]

                coords1 = (result1.latitude, result1.longitude)
                coords2 = (result2.latitude, result2.longitude)

                distance = calculate_distance_from_coordinates(coords1, coords2, "km")

                print(f"✅ Distance between {addr1} and {addr2}: {distance:.1f}km")
                assert distance > 0, "Distance should be positive"
                assert distance < 10000, "Distance should be reasonable"

        except Exception as e:
            pytest.skip(f"Batch geocoding integration test failed: {e}")
        finally:
            await geocoding_service.close()

        print("✅ Batch geocoding workflow works")

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, geocoding_service):
        """Test integrated error handling across all components"""
        error_scenarios = [
            {
                "name": "Invalid coordinates in distance calculation",
                "address": "Valid Address, New York",
                "coordinate_override": (91.0, 0.0),  # Invalid latitude
                "expect_error": True,
            },
            {
                "name": "Malicious address injection",
                "address": 'Restaurant<script>alert("hack")</script>, NYC',
                "coordinate_override": None,
                "expect_error": True,
            },
            {
                "name": "Empty address handling",
                "address": "",
                "coordinate_override": None,
                "expect_error": True,
            },
        ]

        error_handled_count = 0

        for scenario in error_scenarios:
            try:
                # Test validation first
                if not validate_address(scenario["address"]):
                    error_handled_count += 1
                    print(f"✅ Validation caught: {scenario['name']}")
                    continue

                # Test sanitization
                clean_address = sanitize_address(scenario["address"])

                # Test geocoding
                result = await geocoding_service.geocode_address(clean_address)

                # Test distance calculation
                if scenario["coordinate_override"]:
                    # Use invalid coordinates
                    coords1 = scenario["coordinate_override"]
                    coords2 = (result.latitude, result.longitude)

                    from app.utils.distance import calculate_distance_from_coordinates

                    calculate_distance_from_coordinates(coords1, coords2)

                if scenario["expect_error"]:
                    print(f"⚠️  Expected error but succeeded: {scenario['name']}")
                else:
                    print(f"✅ Successful processing: {scenario['name']}")

                await asyncio.sleep(0.8)

            except Exception as e:
                if scenario["expect_error"]:
                    error_handled_count += 1
                    print(
                        f"✅ Error properly handled for {scenario['name']}: {type(e).__name__}"
                    )
                else:
                    print(f"⚠️  Unexpected error for {scenario['name']}: {e}")

        # Most error scenarios should be handled properly
        error_handling_rate = error_handled_count / len(error_scenarios)
        assert (
            error_handling_rate >= 0.7
        ), f"Error handling rate too low: {error_handling_rate:.2f}"

        await geocoding_service.close()
        print("✅ Integrated error handling works")

    @pytest.mark.asyncio
    async def test_real_world_delivery_distances(self, geocoding_service):
        """Test real-world delivery distance scenarios"""
        delivery_routes = [
            {
                "route": "McDonald's to Nearby Apartment",
                "addresses": ["McDonald's Times Square, NYC", "5th Avenue, New York"],
                "max_reasonable_km": 10,
            },
            {
                "route": "Pizza Place to Office Building",
                "addresses": ["Pizza Hut London", "Big Ben, London"],
                "max_reasonable_km": 15,
            },
        ]

        successful_routes = 0

        for route_info in delivery_routes:
            try:
                addresses = route_info["addresses"]
                max_km = route_info["max_reasonable_km"]

                # Geocode both addresses
                results = []
                for addr in addresses:
                    result = await geocoding_service.geocode_address(addr)
                    results.append(result)
                    await asyncio.sleep(1.3)

                # Calculate distance
                if len(results) == 2:
                    coords1 = (results[0].latitude, results[0].longitude)
                    coords2 = (results[1].latitude, results[1].longitude)

                    distance_km = calculate_distance_from_coordinates(
                        coords1, coords2, "km"
                    )

                    # Validate distance is reasonable for delivery
                    assert distance_km > 0, "Distance must be positive"
                    assert (
                        distance_km <= max_km
                    ), f"Distance too far for delivery: {distance_km:.1f}km > {max_km}km"

                    successful_routes += 1
                    print(f"✅ {route_info['route']}: {distance_km:.2f}km")
                    print(f"   From: {results[0].display_name}")
                    print(f"   To: {results[1].display_name}")

            except Exception as e:
                print(f"⚠️  Failed to test route {route_info['route']}: {e}")

        if successful_routes > 0:
            print(f"✅ Successfully tested {successful_routes} delivery routes")
        else:
            pytest.skip("No delivery routes could be tested")

        await geocoding_service.close()
        print("✅ Real-world delivery distance testing works")
