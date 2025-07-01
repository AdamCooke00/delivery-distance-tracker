"""
Geocoding service for address resolution using Nominatim API.

This module provides functionality to convert addresses into geographic coordinates
using the OpenStreetMap Nominatim service with error handling and rate limiting.
"""

import asyncio
import time
from typing import Dict, Optional, Any, List, Tuple

import httpx
from pydantic import BaseModel, Field

from app.utils.logging import get_logger

logger = get_logger(__name__)


class GeocodingError(Exception):
    """Base exception for geocoding-related errors."""

    pass


class GeocodingResult(BaseModel):
    """Model for geocoding result data."""

    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    display_name: str = Field(..., description="Formatted address name")
    place_id: Optional[int] = Field(None, description="Nominatim place ID")
    importance: Optional[float] = Field(None, description="Result importance score")
    category: Optional[str] = Field(None, description="Place category")
    place_type: Optional[str] = Field(None, description="Place type")
    address: Optional[Dict[str, str]] = Field(
        None, description="Detailed address components"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            float: lambda v: round(v, 7)  # Limit precision for coordinates
        }


class GeocodingService:
    """
    Service for geocoding addresses using Nominatim API.

    Features:
    - Async HTTP client for API requests
    - Rate limiting and retry logic
    - Comprehensive error handling
    - Request logging and monitoring
    """

    def __init__(
        self,
        base_url: str = "https://nominatim.openstreetmap.org",
        timeout: int = 10,
        max_retries: int = 3,
        rate_limit_delay: float = 1.0,  # 1 second between requests
    ):
        """
        Initialize geocoding service.

        Args:
            base_url: Nominatim API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            rate_limit_delay: Minimum delay between requests in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay

        self._last_request_time = 0.0

        # HTTP client configuration
        self._client = None
        self._headers = {
            "User-Agent": "DeliveryDistanceTracker/1.0 (https://github.com/AdamCooke00/delivery-distance-tracker)",
            "Accept": "application/json",
            "Accept-Language": "en",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers=self._headers,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def close(self):
        """Close HTTP client connections."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            await asyncio.sleep(sleep_time)

        self._last_request_time = time.time()

    async def _make_request(self, address: str) -> Dict[str, Any]:
        """
        Make HTTP request to Nominatim API.

        Args:
            address: Address to geocode

        Returns:
            API response data

        Raises:
            GeocodingError: If request fails or returns invalid data
        """
        await self._rate_limit()

        params = {
            "q": address,
            "format": "jsonv2",
            "limit": 1,
            "addressdetails": 1,
            "accept-language": "en",
        }

        url = f"{self.base_url}/search"
        client = await self._get_client()

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(
                    f"Making geocoding request (attempt {attempt + 1}): {address}"
                )

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        return data[0]
                    else:
                        raise GeocodingError(f"No results found for address: {address}")

                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = 2**attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    continue

                else:
                    error_msg = f"API error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise GeocodingError(error_msg)

            except httpx.TimeoutException:
                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    logger.warning(f"Request timeout, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise GeocodingError(
                        f"Request timeout after {self.max_retries} retries"
                    )

            except httpx.RequestError as e:
                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    logger.warning(f"Request error: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise GeocodingError(
                        f"Request failed after {self.max_retries} retries: {e}"
                    )

        raise GeocodingError(
            f"Failed to geocode address after {self.max_retries} retries"
        )

    async def geocode_address(self, address: str) -> GeocodingResult:
        """
        Geocode an address to coordinates.

        Args:
            address: Address string to geocode

        Returns:
            GeocodingResult with coordinates and metadata

        Raises:
            GeocodingError: If geocoding fails
        """
        start_time = time.time()

        try:
            # Make API request
            response_data = await self._make_request(address)

            # Parse response
            result = GeocodingResult(
                latitude=float(response_data["lat"]),
                longitude=float(response_data["lon"]),
                display_name=response_data.get("display_name", ""),
                place_id=response_data.get("place_id"),
                importance=response_data.get("importance"),
                category=response_data.get("category"),
                place_type=response_data.get("type"),
                address=response_data.get("address", {}),
            )

            elapsed_time = time.time() - start_time
            logger.info(f"Geocoded address in {elapsed_time:.2f}s: {address}")

            return result

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"Geocoding failed after {elapsed_time:.2f}s for address '{address}': {e}"
            )
            raise

    async def geocode_addresses(
        self, addresses: List[str]
    ) -> Dict[str, Optional[GeocodingResult]]:
        """
        Geocode multiple addresses concurrently.

        Args:
            addresses: List of address strings to geocode

        Returns:
            Dictionary mapping addresses to geocoding results
        """
        if not addresses:
            return {}

        logger.info(f"Geocoding {len(addresses)} addresses")

        async def geocode_single(addr: str) -> Tuple[str, Optional[GeocodingResult]]:
            try:
                result = await self.geocode_address(addr)
                return addr, result
            except GeocodingError as e:
                logger.warning(f"Failed to geocode address '{addr}': {e}")
                return addr, None

        # Execute geocoding requests concurrently
        tasks = [geocode_single(addr) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        geocoded_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Geocoding task failed: {result}")
                continue

            address, geocoding_result = result
            geocoded_results[address] = geocoding_result

        success_count = sum(
            1 for result in geocoded_results.values() if result is not None
        )
        logger.info(f"Successfully geocoded {success_count}/{len(addresses)} addresses")

        return geocoded_results
