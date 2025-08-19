/**
 * Jest Setup for Integration Tests
 * Configures global test environment and utilities
 */

import { TextEncoder, TextDecoder } from 'util';

// Polyfills for Node.js environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock console methods for cleaner test output
const originalConsole = { ...console };

beforeEach(() => {
  // Reset console mocks before each test
  console.log = jest.fn();
  console.warn = jest.fn();
  console.error = jest.fn();
  console.info = jest.fn();
  console.debug = jest.fn();
});

afterEach(() => {
  // Restore original console after each test
  Object.assign(console, originalConsole);
});

// Global test utilities
export const testUtils = {
  /**
   * Create a mock OpenAPI specification for testing
   */
  createMockOpenAPISpec: () => ({
    openapi: '3.0.0',
    info: {
      title: 'Test API',
      version: '1.0.0',
      description: 'Test API for integration testing'
    },
    servers: [
      {
        url: 'https://api.test.com',
        description: 'Test server'
      }
    ],
    paths: {
      '/users': {
        get: {
          operationId: 'getUsers',
          summary: 'Get all users',
          responses: {
            '200': {
              description: 'Success',
              content: {
                'application/json': {
                  schema: {
                    type: 'array',
                    items: { $ref: '#/components/schemas/User' }
                  }
                }
              }
            }
          }
        },
        post: {
          operationId: 'createUser',
          summary: 'Create a user',
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/User' }
              }
            }
          },
          responses: {
            '201': {
              description: 'Created',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/User' }
                }
              }
            }
          }
        }
      },
      '/users/{id}': {
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' }
          }
        ],
        get: {
          operationId: 'getUserById',
          summary: 'Get user by ID',
          responses: {
            '200': {
              description: 'Success',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/User' }
                }
              }
            },
            '404': {
              description: 'User not found'
            }
          }
        }
      }
    },
    components: {
      schemas: {
        User: {
          type: 'object',
          required: ['id', 'name', 'email'],
          properties: {
            id: {
              type: 'string',
              description: 'Unique identifier'
            },
            name: {
              type: 'string',
              description: 'Full name'
            },
            email: {
              type: 'string',
              format: 'email',
              description: 'Email address'
            },
            age: {
              type: 'integer',
              minimum: 0,
              description: 'Age in years'
            },
            active: {
              type: 'boolean',
              default: true,
              description: 'Whether the user is active'
            }
          }
        }
      }
    }
  }),

  /**
   * Create mock LSP client for testing
   */
  createMockLSPClient: () => ({
    sendRequest: jest.fn(),
    sendNotification: jest.fn(),
    onRequest: jest.fn(),
    onNotification: jest.fn(),
    dispose: jest.fn()
  }),

  /**
   * Create mock HTTP server for API testing
   */
  createMockHTTPServer: (port = 3000) => {
    const handlers = new Map();
    return {
      port,
      handlers,
      get: (path: string, handler: Function) => handlers.set(`GET:${path}`, handler),
      post: (path: string, handler: Function) => handlers.set(`POST:${path}`, handler),
      put: (path: string, handler: Function) => handlers.set(`PUT:${path}`, handler),
      delete: (path: string, handler: Function) => handlers.set(`DELETE:${path}`, handler),
      listen: jest.fn(),
      close: jest.fn()
    };
  },

  /**
   * Wait for a condition to be met with timeout
   */
  waitFor: async (condition: () => boolean, timeout = 5000, interval = 100): Promise<void> => {
    const startTime = Date.now();
    while (!condition() && Date.now() - startTime < timeout) {
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    if (!condition()) {
      throw new Error(`Condition not met within ${timeout}ms`);
    }
  },

  /**
   * Generate test data for performance testing
   */
  generateTestData: (size: number) => {
    return Array.from({ length: size }, (_, i) => ({
      id: i.toString(),
      name: `User ${i}`,
      email: `user${i}@test.com`,
      age: Math.floor(Math.random() * 80) + 18,
      active: Math.random() > 0.5
    }));
  }
};

// Configure test timeouts
jest.setTimeout(30000);

// Global error handler for unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  throw reason;
});

export default testUtils;