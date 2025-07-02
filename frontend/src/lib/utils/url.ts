/**
 * URL parameter validation and sanitization utilities
 * Provides safe handling of URL parameters with validation
 */

/**
 * Safely extract and validate string parameter from URL
 * @param searchParams - URLSearchParams object
 * @param key - Parameter key
 * @param maxLength - Maximum allowed length (default: 500)
 * @returns Validated string or null if invalid
 */
export function getSafeStringParam(
	searchParams: URLSearchParams,
	key: string,
	maxLength: number = 500
): string | null {
	try {
		const value = searchParams.get(key);

		if (!value || typeof value !== 'string') {
			return null;
		}

		// Sanitize and validate
		const trimmed = value.trim();

		// Check length
		if (trimmed.length === 0 || trimmed.length > maxLength) {
			return null;
		}

		// Basic XSS prevention - remove potentially dangerous characters
		const sanitized = trimmed.replace(/[<>"`]/g, '');

		return sanitized;
	} catch (error) {
		console.warn(`Failed to parse URL parameter '${key}':`, error);
		return null;
	}
}

/**
 * Safely extract and validate numeric parameter from URL
 * @param searchParams - URLSearchParams object
 * @param key - Parameter key
 * @param min - Minimum allowed value
 * @param max - Maximum allowed value
 * @returns Validated number or null if invalid
 */
export function getSafeNumberParam(
	searchParams: URLSearchParams,
	key: string,
	min: number = Number.MIN_SAFE_INTEGER,
	max: number = Number.MAX_SAFE_INTEGER
): number | null {
	try {
		const value = searchParams.get(key);

		if (!value) {
			return null;
		}

		const num = parseFloat(value);

		// Check if it's a valid number and within bounds
		if (isNaN(num) || !isFinite(num) || num < min || num > max) {
			return null;
		}

		return num;
	} catch (error) {
		console.warn(`Failed to parse numeric URL parameter '${key}':`, error);
		return null;
	}
}

/**
 * Validate address format for URL parameters
 * @param address - Address string to validate
 * @returns True if address appears valid
 */
export function isValidAddress(address: string): boolean {
	if (!address || typeof address !== 'string') {
		return false;
	}

	const trimmed = address.trim();

	// Basic validation rules
	return (
		trimmed.length >= 3 && // Minimum length
		trimmed.length <= 500 && // Maximum length
		!/^[0-9\s]*$/.test(trimmed) && // Not just numbers and spaces
		!/[<>"`{}|\\^]/.test(trimmed) && // No dangerous characters
		/[a-zA-Z]/.test(trimmed) // Contains at least one letter
	);
}

/**
 * Create safe URL parameters object from form data
 * @param params - Object with parameter values
 * @returns URLSearchParams with validated and sanitized values
 */
export function createSafeUrlParams(
	params: Record<string, string | number | null | undefined>
): URLSearchParams {
	const searchParams = new URLSearchParams();

	Object.entries(params).forEach(([key, value]) => {
		if (value !== null && value !== undefined) {
			const stringValue = String(value).trim();

			// Only add non-empty, validated values
			if (stringValue.length > 0 && stringValue.length <= 1000) {
				// Basic sanitization
				const sanitized = stringValue.replace(/[<>"`]/g, '');
				searchParams.append(key, sanitized);
			}
		}
	});

	return searchParams;
}

/**
 * Safely parse URL search parameters with error handling
 * @param url - URL string or URL object
 * @returns URLSearchParams object or empty one if parsing fails
 */
export function safeParseurlParams(url: string | URL): URLSearchParams {
	try {
		if (typeof url === 'string') {
			// Handle relative URLs and fragments
			const urlObj = new URL(url, window.location.origin);
			return urlObj.searchParams;
		} else {
			return url.searchParams;
		}
	} catch (error) {
		console.warn('Failed to parse URL parameters:', error);
		return new URLSearchParams();
	}
}
