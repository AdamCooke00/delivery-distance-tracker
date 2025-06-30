/**
 * Unit conversion utilities and constants
 * Provides standardized unit conversion functions with named constants
 */

// Conversion constants
export const CONVERSION_FACTORS = {
	KM_TO_MILES: 0.621371,
	MILES_TO_KM: 1.609344
} as const;

// Request timeout constants
export const REQUEST_TIMEOUTS = {
	API_REQUEST: 10000, // 10 seconds
	GEOCODING_REQUEST: 15000 // 15 seconds for geocoding (can be slower)
} as const;

/**
 * Convert kilometers to miles with specified precision
 * @param km - Distance in kilometers
 * @param precision - Number of decimal places (default: 2)
 * @returns Distance in miles rounded to specified precision
 */
export function kmToMiles(km: number, precision: number = 2): number {
	const miles = km * CONVERSION_FACTORS.KM_TO_MILES;
	return parseFloat(miles.toFixed(precision));
}

/**
 * Convert miles to kilometers with specified precision
 * @param miles - Distance in miles
 * @param precision - Number of decimal places (default: 2)
 * @returns Distance in kilometers rounded to specified precision
 */
export function milesToKm(miles: number, precision: number = 2): number {
	const km = miles * CONVERSION_FACTORS.MILES_TO_KM;
	return parseFloat(km.toFixed(precision));
}

/**
 * Format distance for display with both units
 * @param km - Distance in kilometers
 * @param precision - Number of decimal places (default: 2)
 * @returns Object with formatted km and miles values
 */
export function formatDistance(km: number, precision: number = 2) {
	return {
		km: parseFloat(km.toFixed(precision)),
		miles: kmToMiles(km, precision)
	};
}

/**
 * Enhanced error handling utility with specific error categorization
 * @param error - Error object (unknown type)
 * @param fallbackMessage - Default message if error is not an Error instance
 * @returns Formatted error message string with appropriate specificity
 */
export function formatErrorMessage(
	error: unknown,
	fallbackMessage: string = 'An unexpected error occurred'
): string {
	if (error instanceof Error) {
		return categorizeErrorMessage(error.message);
	}

	if (typeof error === 'string') {
		return categorizeErrorMessage(error);
	}

	return fallbackMessage;
}

/**
 * Categorize and enhance error messages for better user experience
 * @param message - Raw error message
 * @returns Enhanced, user-friendly error message
 */
function categorizeErrorMessage(message: string): string {
	const lowerMessage = message.toLowerCase();

	// Network and timeout errors
	if (lowerMessage.includes('timeout') || lowerMessage.includes('aborted')) {
		return 'Request timed out. Please check your connection and try again.';
	}

	if (lowerMessage.includes('network') || lowerMessage.includes('fetch')) {
		return 'Network error. Please check your internet connection.';
	}

	// Geocoding and address errors
	if (lowerMessage.includes('address not found') || lowerMessage.includes('geocoding failed')) {
		return 'Address not found. Please check the address format and try again.';
	}

	if (lowerMessage.includes('invalid address')) {
		return 'Invalid address format. Please enter a valid street address, city, and state.';
	}

	if (lowerMessage.includes('no results found')) {
		return 'Location not found. Try using a more general address (e.g., "San Francisco, CA").';
	}

	// API and server errors
	if (lowerMessage.includes('500') || lowerMessage.includes('internal server')) {
		return 'Server error. Please try again in a few moments.';
	}

	if (lowerMessage.includes('503') || lowerMessage.includes('service unavailable')) {
		return 'Service temporarily unavailable. Please try again later.';
	}

	if (lowerMessage.includes('400') || lowerMessage.includes('bad request')) {
		return 'Invalid request. Please check your input and try again.';
	}

	// CORS and connection errors
	if (lowerMessage.includes('cors') || lowerMessage.includes('cross-origin')) {
		return 'Connection error. Please refresh the page and try again.';
	}

	// Return original message if no specific category matches
	return message;
}

/**
 * Error severity levels for styling and user feedback
 */
export const ERROR_TYPES = {
	NETWORK: 'network',
	VALIDATION: 'validation',
	SERVER: 'server',
	TIMEOUT: 'timeout',
	GENERAL: 'general'
} as const;

export type ErrorType = (typeof ERROR_TYPES)[keyof typeof ERROR_TYPES];

/**
 * Determine error type for appropriate styling and handling
 * @param message - Error message
 * @returns Error type for UI styling
 */
export function getErrorType(message: string): ErrorType {
	const lowerMessage = message.toLowerCase();

	if (lowerMessage.includes('timeout') || lowerMessage.includes('aborted')) {
		return ERROR_TYPES.TIMEOUT;
	}

	if (lowerMessage.includes('network') || lowerMessage.includes('connection')) {
		return ERROR_TYPES.NETWORK;
	}

	if (
		lowerMessage.includes('invalid') ||
		lowerMessage.includes('format') ||
		lowerMessage.includes('not found')
	) {
		return ERROR_TYPES.VALIDATION;
	}

	if (
		lowerMessage.includes('server') ||
		lowerMessage.includes('500') ||
		lowerMessage.includes('503')
	) {
		return ERROR_TYPES.SERVER;
	}

	return ERROR_TYPES.GENERAL;
}
