import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
	getSafeStringParam,
	getSafeNumberParam,
	isValidAddress,
	createSafeUrlParams,
	safeParseurlParams
} from './url';

describe('URL Utilities', () => {
	let searchParams: URLSearchParams;

	beforeEach(() => {
		searchParams = new URLSearchParams();
	});

	describe('getSafeStringParam', () => {
		it('should return valid string parameter', () => {
			searchParams.set('test', 'valid string');
			expect(getSafeStringParam(searchParams, 'test')).toBe('valid string');
		});

		it('should return null for missing parameter', () => {
			expect(getSafeStringParam(searchParams, 'missing')).toBeNull();
		});

		it('should return null for empty string', () => {
			searchParams.set('test', '   ');
			expect(getSafeStringParam(searchParams, 'test')).toBeNull();
		});

		it('should return null for string exceeding max length', () => {
			const longString = 'a'.repeat(501);
			searchParams.set('test', longString);
			expect(getSafeStringParam(searchParams, 'test')).toBeNull();
		});

		it('should sanitize dangerous characters', () => {
			searchParams.set('test', 'hello<script>alert("xss")</script>');
			expect(getSafeStringParam(searchParams, 'test')).toBe('helloscriptalert(xss)/script');
		});

		it('should respect custom max length', () => {
			searchParams.set('test', 'hello world');
			expect(getSafeStringParam(searchParams, 'test', 5)).toBeNull();
			expect(getSafeStringParam(searchParams, 'test', 20)).toBe('hello world');
		});

		it('should handle parsing errors gracefully', () => {
			// Mock console.warn to avoid noise in tests
			const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

			// Create a corrupted URLSearchParams object
			const mockParams = {
				get: () => {
					throw new Error('Parse error');
				}
			} as URLSearchParams;

			expect(getSafeStringParam(mockParams, 'test')).toBeNull();
			expect(consoleSpy).toHaveBeenCalled();

			consoleSpy.mockRestore();
		});
	});

	describe('getSafeNumberParam', () => {
		it('should return valid number parameter', () => {
			searchParams.set('test', '42.5');
			expect(getSafeNumberParam(searchParams, 'test')).toBe(42.5);
		});

		it('should return null for missing parameter', () => {
			expect(getSafeNumberParam(searchParams, 'missing')).toBeNull();
		});

		it('should return null for invalid numbers', () => {
			searchParams.set('test', 'not-a-number');
			expect(getSafeNumberParam(searchParams, 'test')).toBeNull();
		});

		it('should return null for NaN and Infinity', () => {
			searchParams.set('nan', 'NaN');
			searchParams.set('inf', 'Infinity');
			expect(getSafeNumberParam(searchParams, 'nan')).toBeNull();
			expect(getSafeNumberParam(searchParams, 'inf')).toBeNull();
		});

		it('should respect min and max bounds', () => {
			searchParams.set('test', '50');
			expect(getSafeNumberParam(searchParams, 'test', 0, 100)).toBe(50);
			expect(getSafeNumberParam(searchParams, 'test', 60, 100)).toBeNull();
			expect(getSafeNumberParam(searchParams, 'test', 0, 40)).toBeNull();
		});

		it('should handle negative numbers', () => {
			searchParams.set('test', '-25');
			expect(getSafeNumberParam(searchParams, 'test')).toBe(-25);
		});

		it('should handle decimal numbers', () => {
			searchParams.set('test', '3.14159');
			expect(getSafeNumberParam(searchParams, 'test')).toBe(3.14159);
		});
	});

	describe('isValidAddress', () => {
		it('should return true for valid addresses', () => {
			expect(isValidAddress('123 Main St, San Francisco, CA')).toBe(true);
			expect(isValidAddress('Empire State Building, NYC')).toBe(true);
			expect(isValidAddress('London, UK')).toBe(true);
		});

		it('should return false for invalid addresses', () => {
			expect(isValidAddress('')).toBe(false);
			expect(isValidAddress('   ')).toBe(false);
			expect(isValidAddress('ab')).toBe(false); // Too short
			expect(isValidAddress('123 456 789')).toBe(false); // Just numbers
			expect(isValidAddress('<script>alert("xss")</script>')).toBe(false); // Dangerous chars
		});

		it('should return false for very long addresses', () => {
			const longAddress = 'a'.repeat(501);
			expect(isValidAddress(longAddress)).toBe(false);
		});

		it('should require at least one letter', () => {
			expect(isValidAddress('123 456')).toBe(false);
			expect(isValidAddress('123 Main St')).toBe(true);
		});

		it('should handle non-string inputs', () => {
			expect(isValidAddress(null as unknown as string)).toBe(false);
			expect(isValidAddress(undefined as unknown as string)).toBe(false);
			expect(isValidAddress(123 as unknown as string)).toBe(false);
		});
	});

	describe('createSafeUrlParams', () => {
		it('should create URLSearchParams from valid object', () => {
			const params = createSafeUrlParams({
				source: 'New York, NY',
				destination: 'Los Angeles, CA',
				miles: 2794,
				km: null
			});

			expect(params.get('source')).toBe('New York, NY');
			expect(params.get('destination')).toBe('Los Angeles, CA');
			expect(params.get('miles')).toBe('2794');
			expect(params.has('km')).toBe(false);
		});

		it('should filter out null and undefined values', () => {
			const params = createSafeUrlParams({
				valid: 'test',
				nullValue: null,
				undefinedValue: undefined,
				empty: ''
			});

			expect(params.get('valid')).toBe('test');
			expect(params.has('nullValue')).toBe(false);
			expect(params.has('undefinedValue')).toBe(false);
			expect(params.has('empty')).toBe(false);
		});

		it('should sanitize dangerous characters', () => {
			const params = createSafeUrlParams({
				test: 'hello<script>world'
			});

			expect(params.get('test')).toBe('helloscriptworld');
		});

		it('should handle very long values', () => {
			const longValue = 'a'.repeat(1001);
			const params = createSafeUrlParams({
				test: longValue
			});

			expect(params.has('test')).toBe(false);
		});
	});

	describe('safeParseurlParams', () => {
		beforeEach(() => {
			// Mock window.location for tests
			Object.defineProperty(window, 'location', {
				writable: true,
				value: { origin: 'http://localhost:3000' }
			});
		});

		it('should parse valid URL string', () => {
			const params = safeParseurlParams('http://example.com?test=value&num=42');
			expect(params.get('test')).toBe('value');
			expect(params.get('num')).toBe('42');
		});

		it('should parse URL object', () => {
			const url = new URL('http://example.com?test=value');
			const params = safeParseurlParams(url);
			expect(params.get('test')).toBe('value');
		});

		it('should handle relative URLs', () => {
			const params = safeParseurlParams('/page?test=value');
			expect(params.get('test')).toBe('value');
		});

		it('should return empty URLSearchParams for invalid URLs', () => {
			const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

			// Test with a truly invalid URL that will cause URL constructor to throw
			const params = safeParseurlParams('http://[invalid');
			expect(params.toString()).toBe('');
			expect(consoleSpy).toHaveBeenCalled();

			consoleSpy.mockRestore();
		});

		it('should handle URLs with fragments', () => {
			const params = safeParseurlParams('http://example.com/page?test=value#section');
			expect(params.get('test')).toBe('value');
		});
	});

	describe('integration scenarios', () => {
		it('should handle complex address validation workflow', () => {
			const testParams = new URLSearchParams(
				'source=123%20Main%20St&destination=Los%20Angeles%2C%20CA&miles=invalid'
			);

			const source = getSafeStringParam(testParams, 'source');
			const destination = getSafeStringParam(testParams, 'destination');
			const miles = getSafeNumberParam(testParams, 'miles');

			expect(isValidAddress(source!)).toBe(true);
			expect(isValidAddress(destination!)).toBe(true);
			expect(miles).toBeNull();
		});

		it('should create safe round-trip parameters', () => {
			const originalData = {
				source: 'New York, NY',
				destination: 'Los Angeles, CA',
				miles: 2794.5,
				km: 4493.2
			};

			const params = createSafeUrlParams(originalData);
			const urlString = params.toString();
			const parsedParams = safeParseurlParams(`http://example.com?${urlString}`);

			expect(getSafeStringParam(parsedParams, 'source')).toBe(originalData.source);
			expect(getSafeStringParam(parsedParams, 'destination')).toBe(originalData.destination);
			expect(getSafeNumberParam(parsedParams, 'miles')).toBe(originalData.miles);
			expect(getSafeNumberParam(parsedParams, 'km')).toBe(originalData.km);
		});
	});
});
