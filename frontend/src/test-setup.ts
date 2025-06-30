import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock global fetch for API testing
Object.defineProperty(window, 'fetch', {
	value: vi.fn(),
	writable: true
});

// Setup Svelte 5 environment
Object.defineProperty(global, 'ResizeObserver', {
	value: vi.fn(() => ({
		observe: vi.fn(),
		unobserve: vi.fn(),
		disconnect: vi.fn()
	})),
	writable: true
});

// Mock window.history for navigation tests
Object.defineProperty(window, 'history', {
	value: {
		replaceState: vi.fn(),
		pushState: vi.fn()
	},
	writable: true
});

// Mock document.head for any dynamic imports
if (!document.head) {
	document.head = document.createElement('head');
	document.documentElement.appendChild(document.head);
}
