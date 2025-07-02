/**
 * API service for communicating with the backend
 * Provides methods for distance calculation and history retrieval
 */

import { REQUEST_TIMEOUTS, formatErrorMessage } from '../utils/units';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// API Response Types (matching backend schemas)
interface DistanceQueryResponse {
	id: number;
	source_address: string;
	destination_address: string;
	source_lat: number | null;
	source_lng: number | null;
	destination_lat: number | null;
	destination_lng: number | null;
	distance_km: number | null;
}

interface HistoryItem {
	id: number;
	source_address: string;
	destination_address: string;
	source_lat: number | null;
	source_lng: number | null;
	destination_lat: number | null;
	destination_lng: number | null;
	distance_km: number | null;
}

interface HistoryResponse {
	items: HistoryItem[];
	total: number;
	limit: number;
	offset: number;
	has_more: boolean;
}

interface ApiError {
	error: string;
	detail?: string;
}

class ApiService {
	private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
		const url = `${API_BASE_URL}${endpoint}`;

		// Create AbortController for request timeout
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUTS.API_REQUEST);

		try {
			const response = await fetch(url, {
				headers: {
					'Content-Type': 'application/json',
					...options.headers
				},
				signal: controller.signal,
				...options
			});

			clearTimeout(timeoutId);

			if (!response.ok) {
				const errorData: ApiError = await response.json().catch(() => ({
					error: `HTTP ${response.status}: ${response.statusText}`
				}));
				throw new Error(errorData.error || errorData.detail || 'Unknown API error');
			}

			return response.json();
		} catch (error) {
			clearTimeout(timeoutId);

			if (error instanceof Error && error.name === 'AbortError') {
				throw new Error('Request timeout - please try again');
			}

			throw new Error(formatErrorMessage(error, 'API request failed'));
		}
	}

	// Distance calculation API
	async calculateDistance(
		sourceAddress: string,
		destinationAddress: string
	): Promise<DistanceQueryResponse> {
		return this.request<DistanceQueryResponse>('/distance', {
			method: 'POST',
			body: JSON.stringify({
				source_address: sourceAddress, // Backend expects snake_case
				destination_address: destinationAddress
			})
		});
	}

	// History API with optional parameters
	async getHistory(params?: {
		limit?: number;
		offset?: number;
		search?: string;
		sort_by?: string;
		sort_order?: string;
	}): Promise<HistoryResponse> {
		const searchParams = new URLSearchParams();

		if (params) {
			Object.entries(params).forEach(([key, value]) => {
				if (value !== undefined && value !== null) {
					searchParams.append(key, value.toString());
				}
			});
		}

		const query = searchParams.toString();
		const endpoint = `/history${query ? `?${query}` : ''}`;

		return this.request<HistoryResponse>(endpoint);
	}
}

// Export singleton instance
export const apiService = new ApiService();

// Export individual methods for convenience (bound to maintain 'this' context)
export const calculateDistance = apiService.calculateDistance.bind(apiService);
export const getHistory = apiService.getHistory.bind(apiService);

// Export types for use in components
export type { DistanceQueryResponse, HistoryItem, HistoryResponse };
