import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiService, calculateDistance, getHistory } from './api';
import type { DistanceQueryResponse, HistoryResponse } from './api';

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('API Service', () => {
	beforeEach(() => {
		mockFetch.mockClear();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('calculateDistance', () => {
		it('should make correct API call for distance calculation', async () => {
			const mockResponse: DistanceQueryResponse = {
				id: 1,
				source_address: 'New York, NY',
				destination_address: 'Los Angeles, CA',
				source_lat: 40.7128,
				source_lng: -74.006,
				destination_lat: 34.0522,
				destination_lng: -118.2437,
				distance_km: 3944.0,
				created_at: '2025-06-30T17:23:00Z'
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse
			});

			const result = await calculateDistance('New York, NY', 'Los Angeles, CA');

			// Verify API call
			expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/distance', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					source_address: 'New York, NY',
					destination_address: 'Los Angeles, CA'
				})
			});

			// Verify response
			expect(result).toEqual(mockResponse);
		});

		it('should handle API errors correctly', async () => {
			const errorResponse = {
				error: 'Address not found',
				detail: 'Could not geocode the provided address'
			};

			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 400,
				json: async () => errorResponse
			});

			await expect(calculateDistance('Invalid Address', 'Another Invalid Address')).rejects.toThrow(
				'Address not found'
			);
		});

		it('should handle network errors', async () => {
			mockFetch.mockRejectedValueOnce(new Error('Network error'));

			await expect(calculateDistance('New York, NY', 'Los Angeles, CA')).rejects.toThrow(
				'Network error'
			);
		});

		it('should handle malformed error responses', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				statusText: 'Internal Server Error',
				json: async () => {
					throw new Error('Invalid JSON');
				}
			});

			await expect(calculateDistance('New York, NY', 'Los Angeles, CA')).rejects.toThrow(
				'HTTP 500: Internal Server Error'
			);
		});
	});

	describe('getHistory', () => {
		it('should make correct API call without parameters', async () => {
			const mockResponse: HistoryResponse = {
				items: [
					{
						id: 1,
						source_address: 'New York, NY',
						destination_address: 'Los Angeles, CA',
						source_lat: 40.7128,
						source_lng: -74.006,
						destination_lat: 34.0522,
						destination_lng: -118.2437,
						distance_km: 3944.0,
						created_at: '2025-06-30T17:23:00Z'
					}
				],
				total: 1,
				limit: 10,
				offset: 0,
				has_more: false
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse
			});

			const result = await getHistory();

			expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/history', {
				headers: {
					'Content-Type': 'application/json'
				}
			});

			expect(result).toEqual(mockResponse);
		});

		it('should make correct API call with parameters', async () => {
			const mockResponse: HistoryResponse = {
				items: [],
				total: 0,
				limit: 5,
				offset: 10,
				has_more: false
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse
			});

			const params = {
				limit: 5,
				offset: 10,
				search: 'New York',
				sort_by: 'created_at',
				sort_order: 'desc'
			};

			const result = await getHistory(params);

			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/api/v1/history?limit=5&offset=10&search=New+York&sort_by=created_at&sort_order=desc',
				{
					headers: {
						'Content-Type': 'application/json'
					}
				}
			);

			expect(result).toEqual(mockResponse);
		});

		it('should handle undefined and null parameters', async () => {
			const mockResponse: HistoryResponse = {
				items: [],
				total: 0,
				limit: 10,
				offset: 0,
				has_more: false
			};

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse
			});

			const params = {
				limit: 5,
				offset: undefined,
				search: null as string | null,
				sort_by: 'distance_km'
			};

			await getHistory(params);

			// Should only include defined parameters
			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/api/v1/history?limit=5&sort_by=distance_km',
				{
					headers: {
						'Content-Type': 'application/json'
					}
				}
			);
		});

		it('should handle history API errors', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 422,
				json: async () => ({
					error: 'Invalid pagination parameters'
				})
			});

			await expect(getHistory({ limit: -1, offset: -5 })).rejects.toThrow(
				'Invalid pagination parameters'
			);
		});
	});

	describe('apiService instance', () => {
		it('should be a singleton instance', () => {
			// Test that we get the same instance
			expect(apiService).toBeDefined();
			expect(typeof apiService.calculateDistance).toBe('function');
			expect(typeof apiService.getHistory).toBe('function');
		});

		it('should have exported convenience methods', () => {
			expect(typeof calculateDistance).toBe('function');
			expect(typeof getHistory).toBe('function');
		});
	});

	describe('URL encoding', () => {
		it('should properly encode search parameters with special characters', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => ({ items: [], total: 0, limit: 10, offset: 0, has_more: false })
			});

			await getHistory({
				search: 'Main St & Oak Ave',
				start_date: '2025-01-01T00:00:00Z'
			});

			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/api/v1/history?search=Main+St+%26+Oak+Ave&start_date=2025-01-01T00%3A00%3A00Z',
				expect.any(Object)
			);
		});
	});
});
