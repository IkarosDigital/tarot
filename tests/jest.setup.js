// jest.setup.js
require('@testing-library/jest-dom');

// Mock window.location
const mockLocation = {
    href: '',
    pathname: '/',
    search: '',
    hash: '',
    reload: jest.fn()
};

Object.defineProperty(window, 'location', {
    value: mockLocation,
    writable: true
});

// Mock sessionStorage
const mockSessionStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};

Object.defineProperty(window, 'sessionStorage', {
    value: mockSessionStorage
});

// Mock fetch
global.fetch = jest.fn();

// Mock console methods
global.console = {
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    info: jest.fn(),
    debug: jest.fn(),
};

// Clear all mocks after each test
afterEach(() => {
    jest.clearAllMocks();
});
