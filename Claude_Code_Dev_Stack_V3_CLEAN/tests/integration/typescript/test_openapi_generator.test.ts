/**
 * Integration Tests for OpenAPI MCP Generator (TypeScript)
 * Tests the Node.js OpenAPI to MCP tool generation pipeline
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { promises as fs } from 'fs';
import path from 'path';
import { tmpdir } from 'os';
import { getToolsFromOpenApi, McpToolDefinition } from '../../../core/generators/nodejs/src/api';
import { extractToolsFromApi } from '../../../core/generators/nodejs/src/parser/extract-tools';
import { testUtils } from '../setup/jest.setup';

describe('OpenAPI MCP Generator Integration Tests', () => {
  let tempDir: string;
  let mockSpec: any;

  beforeEach(async () => {
    // Create temporary directory for test files
    tempDir = await fs.mkdtemp(path.join(tmpdir(), 'openapi-mcp-test-'));
    
    // Create mock OpenAPI spec
    mockSpec = testUtils.createMockOpenAPISpec();
  });

  afterEach(async () => {
    // Clean up temporary directory
    try {
      await fs.rmdir(tempDir, { recursive: true });
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('API Integration', () => {
    test('should extract tools from valid OpenAPI specification', async () => {
      // Write spec to temp file
      const specFile = path.join(tempDir, 'test-spec.json');
      await fs.writeFile(specFile, JSON.stringify(mockSpec, null, 2));

      const tools = await getToolsFromOpenApi(specFile);

      expect(tools).toHaveLength(3); // getUsers, createUser, getUserById
      expect(tools[0]).toHaveProperty('name');
      expect(tools[0]).toHaveProperty('description');
      expect(tools[0]).toHaveProperty('inputSchema');
      expect(tools[0]).toHaveProperty('operationId');
    });

    test('should handle dereferenced specifications', async () => {
      const specFile = path.join(tempDir, 'test-spec.json');
      await fs.writeFile(specFile, JSON.stringify(mockSpec, null, 2));

      const tools = await getToolsFromOpenApi(specFile, { dereference: true });

      expect(tools).toHaveLength(3);
      expect(tools.every(tool => tool.baseUrl)).toBe(true);
    });

    test('should filter tools by operation IDs', async () => {
      const specFile = path.join(tempDir, 'test-spec.json');
      await fs.writeFile(specFile, JSON.stringify(mockSpec, null, 2));

      const tools = await getToolsFromOpenApi(specFile, {
        excludeOperationIds: ['createUser']
      });

      expect(tools).toHaveLength(2);
      expect(tools.find(tool => tool.operationId === 'createUser')).toBeUndefined();
    });

    test('should apply custom filter function', async () => {
      const specFile = path.join(tempDir, 'test-spec.json');
      await fs.writeFile(specFile, JSON.stringify(mockSpec, null, 2));

      const tools = await getToolsFromOpenApi(specFile, {
        filterFn: (tool: McpToolDefinition) => tool.operationId.includes('get')
      });

      expect(tools).toHaveLength(2); // getUsers, getUserById
      expect(tools.every(tool => tool.operationId.includes('get'))).toBe(true);
    });

    test('should handle base URL override', async () => {
      const specFile = path.join(tempDir, 'test-spec.json');
      await fs.writeFile(specFile, JSON.stringify(mockSpec, null, 2));

      const customBaseUrl = 'https://custom.api.com';
      const tools = await getToolsFromOpenApi(specFile, {
        baseUrl: customBaseUrl
      });

      expect(tools.every(tool => tool.baseUrl === customBaseUrl)).toBe(true);
    });

    test('should handle invalid OpenAPI specification', async () => {
      const invalidSpec = { invalid: 'spec' };
      const specFile = path.join(tempDir, 'invalid-spec.json');
      await fs.writeFile(specFile, JSON.stringify(invalidSpec, null, 2));

      await expect(getToolsFromOpenApi(specFile)).rejects.toThrow();
    });

    test('should handle non-existent specification file', async () => {
      const nonExistentFile = path.join(tempDir, 'non-existent.json');

      await expect(getToolsFromOpenApi(nonExistentFile)).rejects.toThrow();
    });
  });

  describe('Tool Extraction', () => {
    test('should extract correct tool schemas for different HTTP methods', () => {
      const tools = extractToolsFromApi(mockSpec);

      // Test GET operation
      const getUsersTool = tools.find(tool => tool.operationId === 'getUsers');
      expect(getUsersTool).toBeDefined();
      expect(getUsersTool?.method).toBe('GET');
      expect(getUsersTool?.path).toBe('/users');

      // Test POST operation
      const createUserTool = tools.find(tool => tool.operationId === 'createUser');
      expect(createUserTool).toBeDefined();
      expect(createUserTool?.method).toBe('POST');
      expect(createUserTool?.inputSchema.properties).toBeDefined();

      // Test GET with path parameters
      const getUserByIdTool = tools.find(tool => tool.operationId === 'getUserById');
      expect(getUserByIdTool).toBeDefined();
      expect(getUserByIdTool?.method).toBe('GET');
      expect(getUserByIdTool?.path).toBe('/users/{id}');
    });

    test('should handle request body schemas correctly', () => {
      const tools = extractToolsFromApi(mockSpec);
      const createUserTool = tools.find(tool => tool.operationId === 'createUser');

      expect(createUserTool?.inputSchema.properties).toHaveProperty('body');
      expect(createUserTool?.inputSchema.properties.body).toHaveProperty('properties');
    });

    test('should handle path parameters correctly', () => {
      const tools = extractToolsFromApi(mockSpec);
      const getUserByIdTool = tools.find(tool => tool.operationId === 'getUserById');

      expect(getUserByIdTool?.inputSchema.properties).toHaveProperty('path');
      expect(getUserByIdTool?.inputSchema.properties.path.properties).toHaveProperty('id');
    });

    test('should generate proper JSON schemas for tool inputs', () => {
      const tools = extractToolsFromApi(mockSpec);

      tools.forEach(tool => {
        expect(tool.inputSchema).toHaveProperty('type');
        expect(tool.inputSchema).toHaveProperty('properties');
        expect(tool.inputSchema.type).toBe('object');
      });
    });
  });

  describe('Performance Tests', () => {
    test('should handle large OpenAPI specifications efficiently', async () => {
      // Create large spec with many paths
      const largeSpec = {
        ...mockSpec,
        paths: {}
      };

      // Add 100 paths
      for (let i = 0; i < 100; i++) {
        largeSpec.paths[`/resource${i}`] = {
          get: {
            operationId: `getResource${i}`,
            summary: `Get resource ${i}`,
            responses: {
              '200': {
                description: 'Success',
                content: {
                  'application/json': {
                    schema: { type: 'object' }
                  }
                }
              }
            }
          }
        };
      }

      const specFile = path.join(tempDir, 'large-spec.json');
      await fs.writeFile(specFile, JSON.stringify(largeSpec, null, 2));

      const startTime = Date.now();
      const tools = await getToolsFromOpenApi(specFile);
      const processingTime = Date.now() - startTime;

      expect(tools).toHaveLength(100);
      expect(processingTime).toBeLessThan(5000); // Should complete within 5 seconds
    }, 10000);

    test('should handle concurrent tool extraction requests', async () => {
      const specFile = path.join(tempDir, 'concurrent-spec.json');
      await fs.writeFile(specFile, JSON.stringify(mockSpec, null, 2));

      // Create multiple concurrent requests
      const requests = Array.from({ length: 10 }, () => 
        getToolsFromOpenApi(specFile)
      );

      const results = await Promise.all(requests);

      // All requests should succeed
      expect(results).toHaveLength(10);
      results.forEach(tools => {
        expect(tools).toHaveLength(3);
      });
    });
  });

  describe('Error Handling', () => {
    test('should provide meaningful error messages for invalid specs', async () => {
      const invalidSpec = {
        openapi: '3.0.0',
        info: { title: 'Invalid', version: '1.0.0' },
        paths: {
          '/invalid': {
            invalid_method: {
              operationId: 'invalid'
            }
          }
        }
      };

      const specFile = path.join(tempDir, 'invalid-spec.json');
      await fs.writeFile(specFile, JSON.stringify(invalidSpec, null, 2));

      try {
        await getToolsFromOpenApi(specFile);
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
        expect((error as Error).message).toContain('Failed to extract tools from OpenAPI');
      }
    });

    test('should handle malformed JSON gracefully', async () => {
      const malformedFile = path.join(tempDir, 'malformed.json');
      await fs.writeFile(malformedFile, '{ invalid json }');

      await expect(getToolsFromOpenApi(malformedFile)).rejects.toThrow();
    });

    test('should handle YAML specifications', async () => {
      const yamlSpec = `
openapi: 3.0.0
info:
  title: YAML API
  version: 1.0.0
paths:
  /test:
    get:
      operationId: testGet
      responses:
        '200':
          description: Success
`;

      const yamlFile = path.join(tempDir, 'spec.yaml');
      await fs.writeFile(yamlFile, yamlSpec);

      const tools = await getToolsFromOpenApi(yamlFile);
      expect(tools).toHaveLength(1);
      expect(tools[0].operationId).toBe('testGet');
    });
  });

  describe('Schema Validation', () => {
    test('should generate valid JSON schemas for complex request bodies', () => {
      const complexSpec = {
        ...mockSpec,
        paths: {
          '/complex': {
            post: {
              operationId: 'complexPost',
              requestBody: {
                content: {
                  'application/json': {
                    schema: {
                      type: 'object',
                      properties: {
                        user: {
                          type: 'object',
                          properties: {
                            name: { type: 'string' },
                            age: { type: 'number' }
                          },
                          required: ['name']
                        },
                        tags: {
                          type: 'array',
                          items: { type: 'string' }
                        },
                        metadata: {
                          type: 'object',
                          additionalProperties: true
                        }
                      }
                    }
                  }
                }
              },
              responses: {
                '200': { description: 'Success' }
              }
            }
          }
        }
      };

      const tools = extractToolsFromApi(complexSpec);
      const complexTool = tools.find(tool => tool.operationId === 'complexPost');

      expect(complexTool).toBeDefined();
      expect(complexTool?.inputSchema.properties.body).toBeDefined();
      expect(complexTool?.inputSchema.properties.body.properties).toHaveProperty('user');
      expect(complexTool?.inputSchema.properties.body.properties).toHaveProperty('tags');
      expect(complexTool?.inputSchema.properties.body.properties).toHaveProperty('metadata');
    });

    test('should handle OpenAPI 3.0 oneOf/anyOf/allOf schemas', () => {
      const polymorphicSpec = {
        ...mockSpec,
        paths: {
          '/polymorphic': {
            post: {
              operationId: 'polymorphicPost',
              requestBody: {
                content: {
                  'application/json': {
                    schema: {
                      oneOf: [
                        {
                          type: 'object',
                          properties: { type: { const: 'A' }, valueA: { type: 'string' } }
                        },
                        {
                          type: 'object',
                          properties: { type: { const: 'B' }, valueB: { type: 'number' } }
                        }
                      ]
                    }
                  }
                }
              },
              responses: {
                '200': { description: 'Success' }
              }
            }
          }
        }
      };

      const tools = extractToolsFromApi(polymorphicSpec);
      const polymorphicTool = tools.find(tool => tool.operationId === 'polymorphicPost');

      expect(polymorphicTool).toBeDefined();
      expect(polymorphicTool?.inputSchema).toBeDefined();
    });
  });

  describe('Integration with Real APIs', () => {
    test('should handle OpenAPI specs from real-world APIs', async () => {
      // Example: JSONPlaceholder-like API spec
      const realWorldSpec = {
        openapi: '3.0.0',
        info: {
          title: 'JSONPlaceholder API',
          version: '1.0.0'
        },
        servers: [
          { url: 'https://jsonplaceholder.typicode.com' }
        ],
        paths: {
          '/posts': {
            get: {
              operationId: 'getPosts',
              parameters: [
                {
                  name: 'userId',
                  in: 'query',
                  schema: { type: 'integer' }
                }
              ],
              responses: {
                '200': {
                  description: 'List of posts',
                  content: {
                    'application/json': {
                      schema: {
                        type: 'array',
                        items: { $ref: '#/components/schemas/Post' }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        components: {
          schemas: {
            Post: {
              type: 'object',
              properties: {
                id: { type: 'integer' },
                userId: { type: 'integer' },
                title: { type: 'string' },
                body: { type: 'string' }
              }
            }
          }
        }
      };

      const specFile = path.join(tempDir, 'real-world-spec.json');
      await fs.writeFile(specFile, JSON.stringify(realWorldSpec, null, 2));

      const tools = await getToolsFromOpenApi(specFile);

      expect(tools).toHaveLength(1);
      expect(tools[0].operationId).toBe('getPosts');
      expect(tools[0].baseUrl).toBe('https://jsonplaceholder.typicode.com');
      expect(tools[0].inputSchema.properties.query).toBeDefined();
    });
  });
});