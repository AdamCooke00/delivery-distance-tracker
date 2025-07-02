import { describe, it, expect } from 'vitest';
import {
	kmToMiles,
	milesToKm,
	formatDistance,
	formatErrorMessage,
	CONVERSION_FACTORS,
	REQUEST_TIMEOUTS
} from './units';

describe('Unit Conversion Utilities', () => {
	describe('CONVERSION_FACTORS', () => {
		it('should have correct conversion constants', () => {
			expect(CONVERSION_FACTORS.KM_TO_MILES).toBe(0.621371);
			expect(CONVERSION_FACTORS.MILES_TO_KM).toBe(1.609344);
		});
	});

	describe('REQUEST_TIMEOUTS', () => {
		it('should have timeout constants', () => {
			expect(REQUEST_TIMEOUTS.API_REQUEST).toBe(10000);
			expect(REQUEST_TIMEOUTS.GEOCODING_REQUEST).toBe(15000);
		});
	});

	describe('kmToMiles', () => {
		it('should convert kilometers to miles correctly', () => {
			expect(kmToMiles(10)).toBe(6.21);
			expect(kmToMiles(100)).toBe(62.14);
			expect(kmToMiles(1.609344)).toBe(1.0); // 1 mile in km
		});

		it('should handle precision parameter', () => {
			expect(kmToMiles(10, 1)).toBe(6.2);
			expect(kmToMiles(10, 3)).toBe(6.214);
			expect(kmToMiles(10, 0)).toBe(6);
		});

		it('should handle zero and negative values', () => {
			expect(kmToMiles(0)).toBe(0);
			expect(kmToMiles(-10)).toBe(-6.21);
		});
	});

	describe('milesToKm', () => {
		it('should convert miles to kilometers correctly', () => {
			expect(milesToKm(10)).toBe(16.09);
			expect(milesToKm(1)).toBe(1.61);
			expect(milesToKm(0.621371)).toBe(1.0); // 1 km in miles
		});

		it('should handle precision parameter', () => {
			expect(milesToKm(10, 1)).toBe(16.1);
			expect(milesToKm(10, 3)).toBe(16.093);
			expect(milesToKm(10, 0)).toBe(16);
		});

		it('should handle zero and negative values', () => {
			expect(milesToKm(0)).toBe(0);
			expect(milesToKm(-10)).toBe(-16.09);
		});
	});

	describe('formatDistance', () => {
		it('should return object with both km and miles', () => {
			const result = formatDistance(10);
			expect(result).toEqual({
				km: 10,
				miles: 6.21
			});
		});

		it('should handle precision parameter', () => {
			const result = formatDistance(10.12345, 1);
			expect(result).toEqual({
				km: 10.1,
				miles: 6.3
			});
		});

		it('should handle decimal input correctly', () => {
			const result = formatDistance(14.6);
			expect(result).toEqual({
				km: 14.6,
				miles: 9.07
			});
		});
	});

	describe('formatErrorMessage', () => {
		it('should return error message for Error instances', () => {
			const error = new Error('Test error message');
			expect(formatErrorMessage(error)).toBe('Test error message');
		});

		it('should return string errors directly', () => {
			expect(formatErrorMessage('String error')).toBe('String error');
		});

		it('should return fallback message for non-Error objects', () => {
			expect(formatErrorMessage({})).toBe('An unexpected error occurred');
			expect(formatErrorMessage(null)).toBe('An unexpected error occurred');
			expect(formatErrorMessage(undefined)).toBe('An unexpected error occurred');
			expect(formatErrorMessage(123)).toBe('An unexpected error occurred');
		});

		it('should allow custom fallback message', () => {
			expect(formatErrorMessage({}, 'Custom fallback')).toBe('Custom fallback');
		});

		it('should handle special error types', () => {
			// Test with TypeError
			const typeError = new TypeError('Type error message');
			expect(formatErrorMessage(typeError)).toBe('Type error message');

			// Test with ReferenceError
			const refError = new ReferenceError('Reference error message');
			expect(formatErrorMessage(refError)).toBe('Reference error message');
		});
	});

	describe('conversion accuracy', () => {
		it('should maintain accuracy for round-trip conversions', () => {
			const originalKm = 100;
			const miles = kmToMiles(originalKm, 6); // Higher precision
			const backToKm = milesToKm(miles, 6);

			// Should be very close (within rounding error)
			expect(Math.abs(originalKm - backToKm)).toBeLessThan(0.01);
		});

		it('should handle edge cases', () => {
			expect(kmToMiles(0.001)).toBe(0.0);
			expect(milesToKm(0.001)).toBe(0.0);
			expect(formatDistance(0.001).km).toBe(0.0);
			expect(formatDistance(0.001).miles).toBe(0.0);
		});
	});
});
