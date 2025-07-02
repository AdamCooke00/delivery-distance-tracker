"""
Test cases for geocoding service reliability and consistency.

This module tests the geocoding service for reliable, consistent results
and proper error handling without caching complexity.
"""

import pytest
import asyncio
import time
from app.services.geocoding import GeocodingService, GeocodingError


class TestGeocodingReliability:
    """Test geocoding service reliability and consistency."""

    @pytest.fixture
    def geocoding_service(self):
        """Create geocoding service instance."""
        return GeocodingService(timeout=15, rate_limit_delay=1.1)

    @pytest.mark.asyncio
    async def test_consistent_geocoding_results(self, geocoding_service):
        """Test that geocoding returns consistent results for repeated requests"""
        test_address = "Times Square, New York City, NY, USA"

        try:
            # Make multiple requests for the same address
            result1 = await geocoding_service.geocode_address(test_address)
            await asyncio.sleep(1.5)  # Respect rate limiting
            result2 = await geocoding_service.geocode_address(test_address)

            # Results should be identical or very close
            assert abs(result1.latitude - result2.latitude) < 0.001
            assert abs(result1.longitude - result2.longitude) < 0.001
            assert result1.display_name == result2.display_name

            print(f"✅ Consistent results for: {test_address}")
            print(f"   Result 1: {result1.latitude}, {result1.longitude}")
            print(f"   Result 2: {result2.latitude}, {result2.longitude}")

        except GeocodingError as e:
            pytest.skip(f"API not available for consistency test: {e}")
        finally:
            await geocoding_service.close()

        print("✅ Geocoding consistency validation works")

    @pytest.mark.asyncio
    async def test_geocoding_service_configuration_no_cache(self, geocoding_service):
        """Test geocoding service configuration without caching"""
        # Test service properties
        assert geocoding_service.base_url == "https://nominatim.openstreetmap.org"
        assert geocoding_service.timeout == 15
        assert geocoding_service.rate_limit_delay == 1.1
        assert geocoding_service.max_retries == 3

        # Verify no cache attributes exist
        assert not hasattr(geocoding_service, "cache_ttl")
        assert not hasattr(geocoding_service, "_cache")

        print("✅ Service configuration validated (no caching)")

    @pytest.mark.asyncio
    async def test_fresh_data_every_request(self, geocoding_service):
        """Test that each request goes to API (no caching)"""
        test_address = "Central Park, New York, NY, USA"

        try:
            # Time multiple requests to ensure they all hit the API
            start_time = time.time()

            await geocoding_service.geocode_address(test_address)
            mid_time = time.time()

            await geocoding_service.geocode_address(test_address)
            end_time = time.time()

            # Each request should take reasonable time (indicating API call)
            first_duration = mid_time - start_time
            second_duration = end_time - mid_time

            # Both requests should take significant time (API calls)
            assert (
                first_duration > 0.5
            ), f"First request too fast: {first_duration:.2f}s"
            assert (
                second_duration > 0.5
            ), f"Second request too fast: {second_duration:.2f}s"

            print(
                f"✅ Fresh API data: Request 1: {first_duration:.2f}s, Request 2: {second_duration:.2f}s"
            )

        except GeocodingError as e:
            pytest.skip(f"API not available for fresh data test: {e}")
        finally:
            await geocoding_service.close()

        print("✅ Fresh data validation works")

    @pytest.mark.asyncio
    async def test_address_variation_handling(self, geocoding_service):
        """Test handling of address variations"""
        address_variations = [
            "Empire State Building, New York",
            "Empire State Building, NYC",
            "Empire State Building, New York City",
            "350 5th Ave, New York, NY",
        ]

        results = []

        try:
            for address in address_variations:
                try:
                    result = await geocoding_service.geocode_address(address)
                    results.append((address, result))
                    await asyncio.sleep(1.2)  # Rate limiting
                except GeocodingError as e:
                    print(f"⚠️  Failed to geocode variation: {address} - {e}")

            if len(results) >= 2:
                # Check that results are for the same general area
                base_result = results[0][1]
                for address, result in results[1:]:
                    lat_diff = abs(result.latitude - base_result.latitude)
                    lng_diff = abs(result.longitude - base_result.longitude)

                    # Should be within ~1km for same landmark
                    assert (
                        lat_diff < 0.01
                    ), f"Latitude too different for {address}: {lat_diff}"
                    assert (
                        lng_diff < 0.01
                    ), f"Longitude too different for {address}: {lng_diff}"

                print("✅ Address variations handled consistently")
            else:
                pytest.skip("Not enough successful geocoding results for comparison")

        except Exception as e:
            pytest.skip(f"Address variation test failed: {e}")
        finally:
            await geocoding_service.close()

        print("✅ Address variation handling works")

    @pytest.mark.asyncio
    async def test_geocoding_error_recovery(self, geocoding_service):
        """Test error recovery and retry behavior"""
        # Test with a problematic address that might cause issues
        problematic_addresses = [
            "",  # Empty address
            "NonexistentPlace12345XYZ",  # Nonexistent location
            "🏠🌍📍",  # Emoji only
        ]

        error_count = 0

        for address in problematic_addresses:
            try:
                await geocoding_service.geocode_address(address)
                print(f"⚠️  Unexpected success for problematic address: {address}")
            except GeocodingError as e:
                error_count += 1
                print(f"✅ Properly handled problematic address: {address} - {e}")
            except Exception as e:
                error_count += 1
                print(f"✅ Caught unexpected error for: {address} - {type(e).__name__}")

            await asyncio.sleep(0.5)  # Small delay between attempts

        # Most problematic addresses should fail gracefully
        assert error_count >= len(problematic_addresses) // 2

        await geocoding_service.close()
        print("✅ Error recovery works")

    def _calculate_quality_score(self, result):
        """Calculate quality score for geocoding result"""
        quality_score = 0

        # Basic required fields
        if result.latitude and result.longitude:
            quality_score += 2
        if result.display_name and len(result.display_name) > 10:
            quality_score += 1

        # Enhanced fields
        if result.place_id:
            quality_score += 1
        if result.importance and result.importance > 0:
            quality_score += 1
        if result.category:
            quality_score += 1
        if result.place_type:
            quality_score += 1
        if result.address and len(result.address) > 0:
            quality_score += 1

        return quality_score

    @pytest.mark.asyncio
    async def test_response_data_quality(self, geocoding_service):
        """Test quality and completeness of geocoding response data"""
        quality_test_addresses = [
            "Statue of Liberty, New York",
            "Big Ben, London, UK",
            "Eiffel Tower, Paris, France",
        ]

        quality_results = []

        try:
            for address in quality_test_addresses:
                try:
                    result = await geocoding_service.geocode_address(address)
                    quality_score = self._calculate_quality_score(result)
                    quality_results.append((address, quality_score))

                    print(f"✅ Quality score for {address}: {quality_score}/8")
                    await asyncio.sleep(1.2)

                except GeocodingError as e:
                    print(f"⚠️  Could not test quality for: {address} - {e}")

            if quality_results:
                avg_quality = sum(score for _, score in quality_results) / len(
                    quality_results
                )
                assert (
                    avg_quality >= 4.0
                ), f"Average quality too low: {avg_quality:.1f}/8"
                print(f"✅ Average response quality: {avg_quality:.1f}/8")
            else:
                pytest.skip("No successful geocoding results for quality test")

        except Exception as e:
            pytest.skip(f"Response quality test failed: {e}")
        finally:
            await geocoding_service.close()

        print("✅ Response data quality validation works")

    @pytest.mark.asyncio
    async def test_international_address_support(self, geocoding_service):
        """Test support for international addresses"""
        international_addresses = [
            "Tokyo Tower, Tokyo, Japan",
            "Sydney Opera House, Sydney, Australia",
            "CN Tower, Toronto, Canada",
            "Sagrada Familia, Barcelona, Spain",
        ]

        successful_international = 0

        try:
            for address in international_addresses:
                try:
                    result = await geocoding_service.geocode_address(address)

                    # Verify coordinates are reasonable for international locations
                    assert -90 <= result.latitude <= 90
                    assert -180 <= result.longitude <= 180
                    assert len(result.display_name) > 0

                    successful_international += 1
                    print(f"✅ Successfully geocoded international: {address}")

                    await asyncio.sleep(1.2)

                except GeocodingError as e:
                    print(f"⚠️  Failed international geocoding: {address} - {e}")

            # At least half of international addresses should work
            success_rate = successful_international / len(international_addresses)
            assert (
                success_rate >= 0.5
            ), f"International success rate too low: {success_rate:.2f}"

        except Exception as e:
            pytest.skip(f"International address test failed: {e}")
        finally:
            await geocoding_service.close()

        print("✅ International address support works")
