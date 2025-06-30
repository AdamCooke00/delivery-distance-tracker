import { describe, it, expect } from 'vitest';

describe('Basic Vitest Setup', () => {
	it('should run basic assertions', () => {
		expect(1 + 1).toBe(2);
		expect('hello').toContain('ell');
	});

	it('should have jest-dom matchers available', () => {
		// Create a simple DOM element
		const element = document.createElement('div');
		element.textContent = 'Hello World';
		document.body.appendChild(element);

		// Test jest-dom matcher
		expect(element).toBeInTheDocument();
		expect(element).toHaveTextContent('Hello World');

		// Cleanup
		document.body.removeChild(element);
	});
});
