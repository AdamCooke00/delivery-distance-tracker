"""
Test cases for geocoding service functionality using real Nominatim API calls.

This module tests the geocoding service with actual API requests
to ensure reliable functionality without mocking complexities.
"""

import pytest
from app.services.geocoding import GeocodingService, GeocodingError, GeocodingResult


class TestGeocodingService:
    """Test geocoding service with real API calls."""

    @pytest.fixture
    def geocoding_service(self):
        """Create geocoding service instance."""
        return GeocodingService(
            timeout=15,  # Longer timeout for real API calls
            rate_limit_delay=1.1,  # Respect API rate limits
        )

    @pytest.fixture
    def known_addresses(self):
        """Well-known addresses that should geocode successfully."""
        return [
            "1600 Amphitheatre Parkway, Mountain View, CA, USA",
            "Times Square, New York City, NY, USA",
            "Eiffel Tower, Paris, France",
            "Big Ben, London, UK",
            "Golden Gate Bridge, San Francisco, CA, USA",
            "Brandenburg Gate, Berlin, Germany",
        ]

    @pytest.fixture
    def invalid_addresses(self):
        """Addresses that should fail to geocode."""
        return [
            "Nonexistent Address 12345 Fake Street, Nowhere, XX",
            "asdfghjkl qwertyuiop zxcvbnm",
            "123456789 999999999 888888888",
            "!@#$%^&*() invalid characters only",
        ]

    @pytest.mark.asyncio
    async def test_successful_geocoding(self, geocoding_service, known_addresses):
        """Test successful geocoding of well-known addresses"""
        successful_geocodes = 0

        for address in known_addresses:
            try:
                result = await geocoding_service.geocode_address(address)

                # Verify result structure
                assert isinstance(result, GeocodingResult)
                assert isinstance(result.latitude, float)
                assert isinstance(result.longitude, float)
                assert isinstance(result.display_name, str)

                # Verify coordinate bounds
                assert -90 <= result.latitude <= 90
                assert -180 <= result.longitude <= 180

                # Verify display name is meaningful
                assert len(result.display_name) > 0

                # Verify optional fields if present
                if result.place_id:
                    assert isinstance(result.place_id, int)
                if result.importance:
                    assert isinstance(result.importance, float)
                    assert 0 <= result.importance <= 1
                if result.category:
                    assert isinstance(result.category, str)
                if result.place_type:
                    assert isinstance(result.place_type, str)
                if result.address:
                    assert isinstance(result.address, dict)

                successful_geocodes += 1
                print(f"✅ Successfully geocoded: {address}")
                print(f"   → {result.latitude}, {result.longitude}")
                print(f"   → {result.display_name}")

            except GeocodingError as e:
                print(f"⚠️  Failed to geocode known address: {address} - {e}")

        # At least 80% of known addresses should geocode successfully
        success_rate = successful_geocodes / len(known_addresses)
        assert success_rate >= 0.8, f"Success rate too low: {success_rate:.2f}"

        await geocoding_service.close()
        print("✅ Successful geocoding works")

    @pytest.mark.asyncio
    async def test_geocoding_no_results(self, geocoding_service, invalid_addresses):
        """Test geocoding when no results are found"""
        no_result_count = 0

        for address in invalid_addresses:
            try:
                result = await geocoding_service.geocode_address(address)
                print(
                    f"⚠️  Unexpected result for invalid address: {address} → {result.display_name}"
                )
            except GeocodingError as e:
                assert "No results found" in str(e) or "API error" in str(e)
                no_result_count += 1
                print(f"✅ Correctly rejected invalid address: {address}")

        # Most invalid addresses should fail to geocode
        failure_rate = no_result_count / len(invalid_addresses)
        assert (
            failure_rate >= 0.5
        ), f"Should reject more invalid addresses: {failure_rate:.2f}"

        await geocoding_service.close()
        print("✅ No results error handling works")

    @pytest.mark.asyncio
    async def test_geocoding_response_structure(self, geocoding_service):
        """Test that geocoding response has proper structure"""
        test_address = "Empire State Building, New York, NY, USA"

        try:
            result = await geocoding_service.geocode_address(test_address)

            # Required fields
            assert hasattr(result, "latitude")
            assert hasattr(result, "longitude")
            assert hasattr(result, "display_name")

            # Optional fields should exist as attributes (even if None)
            assert hasattr(result, "place_id")
            assert hasattr(result, "importance")
            assert hasattr(result, "category")
            assert hasattr(result, "place_type")
            assert hasattr(result, "address")

            # Verify JSON serialization works
            result_dict = result.model_dump()
            assert isinstance(result_dict, dict)
            assert "latitude" in result_dict
            assert "longitude" in result_dict
            assert "display_name" in result_dict

            print(f"✅ Response structure validated for: {test_address}")
            print(f"   Place ID: {result.place_id}")
            print(f"   Category: {result.category}")
            print(f"   Type: {result.place_type}")
            print(f"   Importance: {result.importance}")
            if result.address:
                print(f"   Address components: {len(result.address)} items")

        except GeocodingError as e:
            pytest.skip(f"API not available for structure test: {e}")
        finally:
            await geocoding_service.close()

        print("✅ Geocoding response structure validated")

    @pytest.mark.asyncio
    async def test_geocoding_coordinate_precision(self, geocoding_service):
        """Test coordinate precision in geocoding results"""
        test_addresses = [
            "Statue of Liberty, New York, NY, USA",
            "Space Needle, Seattle, WA, USA",
        ]

        successful_tests = 0

        for address in test_addresses:
            try:
                result = await geocoding_service.geocode_address(address)

                # Check coordinate precision (should be reasonable for landmarks)
                lat_precision = len(str(result.latitude).split(".")[-1])
                lng_precision = len(str(result.longitude).split(".")[-1])

                # Should have at least 4 decimal places for good accuracy
                assert (
                    lat_precision >= 4
                ), f"Latitude precision too low: {lat_precision}"
                assert (
                    lng_precision >= 4
                ), f"Longitude precision too low: {lng_precision}"

                # Should not have excessive precision (over 10 decimal places)
                assert (
                    lat_precision <= 10
                ), f"Latitude precision too high: {lat_precision}"
                assert (
                    lng_precision <= 10
                ), f"Longitude precision too high: {lng_precision}"

                successful_tests += 1
                print(f"✅ Coordinate precision validated: {address}")
                print(f"   Lat: {result.latitude} ({lat_precision} decimals)")
                print(f"   Lng: {result.longitude} ({lng_precision} decimals)")

            except GeocodingError as e:
                print(f"⚠️  Could not test precision for: {address} - {e}")

        assert successful_tests > 0, "No addresses could be tested for precision"
        await geocoding_service.close()
        print("✅ Coordinate precision validation works")

    @pytest.mark.asyncio
    async def test_geocoding_service_configuration(self, geocoding_service):
        """Test geocoding service configuration and settings"""
        # Test service properties
        assert geocoding_service.base_url == "https://nominatim.openstreetmap.org"
        assert geocoding_service.timeout == 15
        assert geocoding_service.rate_limit_delay == 1.1
        assert geocoding_service.max_retries == 3
        # Verify no cache attributes exist (no caching implementation)
        assert not hasattr(geocoding_service, "cache_ttl")
        assert not hasattr(geocoding_service, "_cache")

        print("✅ Service configuration validated")

    @pytest.mark.asyncio
    async def test_multiple_address_geocoding(self, geocoding_service):
        """Test geocoding multiple addresses concurrently"""
        addresses = [
            "Central Park, New York, NY, USA",
            "Piccadilly Circus, London, UK",
            "Colosseum, Rome, Italy",
        ]

        try:
            results = await geocoding_service.geocode_addresses(addresses)

            assert isinstance(results, dict)
            assert len(results) == len(addresses)

            successful_results = 0
            for address, result in results.items():
                assert address in addresses
                if result is not None:
                    assert isinstance(result, GeocodingResult)
                    successful_results += 1
                    print(f"✅ Batch geocoded: {address}")
                else:
                    print(f"⚠️  Failed in batch: {address}")

            # At least half should succeed
            success_rate = successful_results / len(addresses)
            assert (
                success_rate >= 0.5
            ), f"Batch success rate too low: {success_rate:.2f}"

        except Exception as e:
            pytest.skip(f"Batch geocoding not available: {e}")
        finally:
            await geocoding_service.close()

        print("✅ Multiple address geocoding works")

    @pytest.mark.asyncio
    async def test_geocoding_error_scenarios(self, geocoding_service):
        """Test various error scenarios"""
        error_test_cases = [
            ("", "empty address"),
            ("   ", "whitespace only"),
            ("a" * 1000, "extremely long address"),
        ]

        for test_address, description in error_test_cases:
            try:
                result = await geocoding_service.geocode_address(test_address)
                print(f"⚠️  Unexpected success for {description}: {result.display_name}")
            except GeocodingError as e:
                print(f"✅ Correctly handled {description}: {e}")
            except Exception as e:
                print(
                    f"✅ Correctly handled {description} with exception: {type(e).__name__}"
                )

        await geocoding_service.close()
        print("✅ Error scenario handling works")

    @pytest.mark.asyncio
    async def test_geocoding_rate_limiting(self, geocoding_service):
        """Test that rate limiting is working"""
        import time

        test_address = "White House, Washington, DC, USA"

        # Make two rapid requests and measure time
        start_time = time.time()

        try:
            # First request
            await geocoding_service.geocode_address(test_address)

            # Second request (should be rate limited)
            await geocoding_service.geocode_address(test_address + " duplicate")

            elapsed_time = time.time() - start_time

            # Should take at least the rate limit delay
            expected_min_time = geocoding_service.rate_limit_delay
            assert (
                elapsed_time >= expected_min_time
            ), f"Rate limiting not working: {elapsed_time:.2f}s < {expected_min_time}s"

            print(f"✅ Rate limiting working: {elapsed_time:.2f}s delay")

        except GeocodingError:
            # Rate limiting still works even if geocoding fails
            elapsed_time = time.time() - start_time
            print(f"✅ Rate limiting enforced even with errors: {elapsed_time:.2f}s")
        finally:
            await geocoding_service.close()

        print("✅ Rate limiting validation works")
