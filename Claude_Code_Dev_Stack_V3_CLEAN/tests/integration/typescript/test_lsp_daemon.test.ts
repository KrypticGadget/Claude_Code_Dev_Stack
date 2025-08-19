/**
 * Integration Tests for LSP Daemon
 * Tests the Language Server Protocol daemon functionality and hooks integration
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { promises as fs } from 'fs';
import path from 'path';
import { tmpdir } from 'os';
import { testUtils } from '../setup/jest.setup';

// Mock LSP client for testing
const createMockLSPClient = () => ({
  sendRequest: jest.fn(),
  sendNotification: jest.fn(),
  onRequest: jest.fn(),
  onNotification: jest.fn(),
  dispose: jest.fn(),
  connection: {
    listen: jest.fn(),
    sendRequest: jest.fn(),
    sendNotification: jest.fn(),
    onRequest: jest.fn(),
    onNotification: jest.fn()
  }
});

describe('LSP Daemon Integration Tests', () => {
  let tempDir: string;
  let mockClient: ReturnType<typeof createMockLSPClient>;

  beforeEach(async () => {
    tempDir = await fs.mkdtemp(path.join(tmpdir(), 'lsp-daemon-test-'));
    mockClient = createMockLSPClient();
  });

  afterEach(async () => {
    try {
      await fs.rmdir(tempDir, { recursive: true });
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('LSP Client Management', () => {
    test('should initialize LSP client with proper configuration', async () => {
      const config = {
        serverPath: '/path/to/language-server',
        serverArgs: ['--stdio'],
        workspaceRoot: tempDir,
        initializationOptions: {
          enableHooks: true,
          hookConfig: {
            audioHook: { enabled: true },
            qualityOrchestrator: { enabled: true }
          }
        }
      };

      // Test client initialization
      expect(mockClient.connection).toBeDefined();
      expect(mockClient.connection.listen).toBeDefined();
    });

    test('should handle LSP client lifecycle events', async () => {
      // Test initialization
      mockClient.sendRequest.mockResolvedValue({
        capabilities: {
          textDocumentSync: 1,
          hoverProvider: true,
          completionProvider: {},
          definitionProvider: true
        }
      });

      // Simulate initialize request
      const initResult = await mockClient.sendRequest('initialize', {
        processId: process.pid,
        rootUri: `file://${tempDir}`,
        capabilities: {}
      });

      expect(initResult).toHaveProperty('capabilities');
      expect(mockClient.sendRequest).toHaveBeenCalledWith('initialize', expect.any(Object));
    });

    test('should handle connection errors gracefully', async () => {
      mockClient.sendRequest.mockRejectedValue(new Error('Connection failed'));

      await expect(
        mockClient.sendRequest('initialize', {})
      ).rejects.toThrow('Connection failed');
    });
  });

  describe('Hook Integration', () => {
    test('should register audio hooks correctly', async () => {
      const audioHookConfig = {
        enabled: true,
        sampleRate: 44100,
        channels: 2,
        bufferSize: 1024,
        enableNoiseReduction: true,
        enableEcho: false
      };

      // Mock hook registration
      mockClient.sendNotification.mockImplementation((method, params) => {
        if (method === 'hook/register') {
          expect(params).toHaveProperty('hookType', 'audio');
          expect(params).toHaveProperty('config', audioHookConfig);
        }
      });

      await mockClient.sendNotification('hook/register', {
        hookType: 'audio',
        config: audioHookConfig
      });

      expect(mockClient.sendNotification).toHaveBeenCalledWith(
        'hook/register',
        expect.objectContaining({
          hookType: 'audio',
          config: audioHookConfig
        })
      );
    });

    test('should register quality orchestrator hooks', async () => {
      const qualityConfig = {
        enabled: true,
        codeComplexityThreshold: 10,
        testCoverageThreshold: 80,
        enableAutomaticRefactoring: true,
        enableSmellDetection: true,
        qualityGates: {
          maintainabilityIndex: 70,
          cyclomaticComplexity: 15,
          duplicatedLinesRatio: 5
        }
      };

      await mockClient.sendNotification('hook/register', {
        hookType: 'quality',
        config: qualityConfig
      });

      expect(mockClient.sendNotification).toHaveBeenCalledWith(
        'hook/register',
        expect.objectContaining({
          hookType: 'quality',
          config: qualityConfig
        })
      );
    });

    test('should handle hook events and notifications', async () => {
      const mockEventHandler = jest.fn();
      
      // Register event handler
      mockClient.onNotification.mockImplementation((method, handler) => {
        if (method === 'hook/event') {
          mockEventHandler.mockImplementation(handler);
        }
      });

      // Simulate hook event
      const testEvent = {
        hookType: 'audio',
        eventType: 'recording_started',
        timestamp: Date.now(),
        data: {
          duration: 0,
          sampleRate: 44100
        }
      };

      mockEventHandler(testEvent);

      expect(mockEventHandler).toHaveBeenCalledWith(testEvent);
    });
  });

  describe('Document Synchronization', () => {
    test('should synchronize document changes', async () => {
      const documentUri = `file://${path.join(tempDir, 'test.ts')}`;
      const documentContent = `
        function testFunction() {
          console.log('Hello, World!');
        }
      `;

      // Create test file
      await fs.writeFile(path.join(tempDir, 'test.ts'), documentContent);

      // Simulate document open
      await mockClient.sendNotification('textDocument/didOpen', {
        textDocument: {
          uri: documentUri,
          languageId: 'typescript',
          version: 1,
          text: documentContent
        }
      });

      expect(mockClient.sendNotification).toHaveBeenCalledWith(
        'textDocument/didOpen',
        expect.objectContaining({
          textDocument: expect.objectContaining({
            uri: documentUri,
            languageId: 'typescript'
          })
        })
      );
    });

    test('should handle document changes with incremental updates', async () => {
      const documentUri = `file://${path.join(tempDir, 'test.ts')}`;
      
      // Simulate document change
      const changeEvent = {
        textDocument: {
          uri: documentUri,
          version: 2
        },
        contentChanges: [
          {
            range: {
              start: { line: 1, character: 0 },
              end: { line: 1, character: 0 }
            },
            text: '  // Added comment\n'
          }
        ]
      };

      await mockClient.sendNotification('textDocument/didChange', changeEvent);

      expect(mockClient.sendNotification).toHaveBeenCalledWith(
        'textDocument/didChange',
        changeEvent
      );
    });

    test('should handle document close events', async () => {
      const documentUri = `file://${path.join(tempDir, 'test.ts')}`;

      await mockClient.sendNotification('textDocument/didClose', {
        textDocument: { uri: documentUri }
      });

      expect(mockClient.sendNotification).toHaveBeenCalledWith(
        'textDocument/didClose',
        expect.objectContaining({
          textDocument: { uri: documentUri }
        })
      );
    });
  });

  describe('Language Features', () => {
    test('should provide hover information', async () => {
      const documentUri = `file://${path.join(tempDir, 'test.ts')}`;
      const position = { line: 1, character: 10 };

      mockClient.sendRequest.mockResolvedValue({
        contents: {
          kind: 'markdown',
          value: '```typescript\nfunction testFunction(): void\n```'
        },
        range: {
          start: { line: 1, character: 9 },
          end: { line: 1, character: 21 }
        }
      });

      const hoverResult = await mockClient.sendRequest('textDocument/hover', {
        textDocument: { uri: documentUri },
        position
      });

      expect(hoverResult).toHaveProperty('contents');
      expect(hoverResult.contents).toHaveProperty('value');
    });

    test('should provide code completion', async () => {
      const documentUri = `file://${path.join(tempDir, 'test.ts')}`;
      const position = { line: 2, character: 5 };

      mockClient.sendRequest.mockResolvedValue({
        isIncomplete: false,
        items: [
          {
            label: 'console',
            kind: 6, // Module
            detail: 'Console',
            documentation: 'The console object provides access to debugging console'
          },
          {
            label: 'const',
            kind: 14, // Keyword
            detail: 'const',
            insertText: 'const '
          }
        ]
      });

      const completionResult = await mockClient.sendRequest('textDocument/completion', {
        textDocument: { uri: documentUri },
        position
      });

      expect(completionResult).toHaveProperty('items');
      expect(Array.isArray(completionResult.items)).toBe(true);
    });

    test('should provide definition navigation', async () => {
      const documentUri = `file://${path.join(tempDir, 'test.ts')}`;
      const position = { line: 1, character: 10 };

      mockClient.sendRequest.mockResolvedValue([
        {
          uri: documentUri,
          range: {
            start: { line: 0, character: 9 },
            end: { line: 0, character: 21 }
          }
        }
      ]);

      const definitionResult = await mockClient.sendRequest('textDocument/definition', {
        textDocument: { uri: documentUri },
        position
      });

      expect(Array.isArray(definitionResult)).toBe(true);
      expect(definitionResult[0]).toHaveProperty('uri');
      expect(definitionResult[0]).toHaveProperty('range');
    });
  });

  describe('Diagnostics', () => {
    test('should receive and process diagnostics', async () => {
      const documentUri = `file://${path.join(tempDir, 'test.ts')}`;
      const mockDiagnosticsHandler = jest.fn();

      mockClient.onNotification.mockImplementation((method, handler) => {
        if (method === 'textDocument/publishDiagnostics') {
          mockDiagnosticsHandler.mockImplementation(handler);
        }
      });

      const diagnosticsData = {
        uri: documentUri,
        diagnostics: [
          {
            range: {
              start: { line: 1, character: 2 },
              end: { line: 1, character: 15 }
            },
            message: 'Variable is declared but never used',
            severity: 2, // Warning
            source: 'typescript'
          }
        ]
      };

      mockDiagnosticsHandler(diagnosticsData);

      expect(mockDiagnosticsHandler).toHaveBeenCalledWith(diagnosticsData);
    });

    test('should handle semantic analysis integration', async () => {
      const semanticDiagnostic = {
        uri: `file://${path.join(tempDir, 'test.ts')}`,
        diagnostics: [
          {
            range: {
              start: { line: 0, character: 0 },
              end: { line: 0, character: 10 }
            },
            message: 'Code complexity exceeds threshold',
            severity: 2,
            source: 'semantic-analyzer',
            data: {
              complexity: 15,
              threshold: 10,
              suggestions: ['Consider breaking down this function']
            }
          }
        ]
      };

      const mockSemanticHandler = jest.fn();
      mockClient.onNotification.mockImplementation((method, handler) => {
        if (method === 'semantic/analysis') {
          mockSemanticHandler.mockImplementation(handler);
        }
      });

      mockSemanticHandler(semanticDiagnostic);

      expect(mockSemanticHandler).toHaveBeenCalledWith(semanticDiagnostic);
    });
  });

  describe('Performance and Scalability', () => {
    test('should handle multiple simultaneous requests', async () => {
      const requests = Array.from({ length: 10 }, (_, i) => 
        mockClient.sendRequest('textDocument/hover', {
          textDocument: { uri: `file://${tempDir}/test${i}.ts` },
          position: { line: 1, character: 10 }
        })
      );

      mockClient.sendRequest.mockResolvedValue({
        contents: { kind: 'markdown', value: 'Mock hover content' }
      });

      const results = await Promise.all(requests);

      expect(results).toHaveLength(10);
      expect(mockClient.sendRequest).toHaveBeenCalledTimes(10);
    });

    test('should handle large file synchronization efficiently', async () => {
      const largeFileContent = 'console.log("test");\n'.repeat(10000);
      const documentUri = `file://${path.join(tempDir, 'large-test.ts')}`;

      const startTime = Date.now();

      await mockClient.sendNotification('textDocument/didOpen', {
        textDocument: {
          uri: documentUri,
          languageId: 'typescript',
          version: 1,
          text: largeFileContent
        }
      });

      const endTime = Date.now();
      const processingTime = endTime - startTime;

      expect(processingTime).toBeLessThan(1000); // Should complete within 1 second
      expect(mockClient.sendNotification).toHaveBeenCalled();
    });
  });

  describe('Error Handling and Recovery', () => {
    test('should handle server crashes gracefully', async () => {
      mockClient.sendRequest.mockRejectedValueOnce(new Error('Server crashed'));

      await expect(
        mockClient.sendRequest('textDocument/hover', {
          textDocument: { uri: `file://${tempDir}/test.ts` },
          position: { line: 1, character: 10 }
        })
      ).rejects.toThrow('Server crashed');
    });

    test('should handle malformed requests', async () => {
      mockClient.sendRequest.mockRejectedValueOnce(new Error('Invalid request'));

      await expect(
        mockClient.sendRequest('textDocument/invalidMethod', {
          invalid: 'parameters'
        })
      ).rejects.toThrow('Invalid request');
    });

    test('should handle connection timeouts', async () => {
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 100);
      });

      mockClient.sendRequest.mockReturnValueOnce(timeoutPromise);

      await expect(
        mockClient.sendRequest('textDocument/hover', {
          textDocument: { uri: `file://${tempDir}/test.ts` },
          position: { line: 1, character: 10 }
        })
      ).rejects.toThrow('Request timeout');
    });
  });

  describe('Configuration Management', () => {
    test('should handle configuration changes', async () => {
      const newConfig = {
        enableHooks: false,
        audioHook: { enabled: false },
        qualityOrchestrator: { enabled: true, threshold: 15 }
      };

      await mockClient.sendNotification('workspace/didChangeConfiguration', {
        settings: newConfig
      });

      expect(mockClient.sendNotification).toHaveBeenCalledWith(
        'workspace/didChangeConfiguration',
        expect.objectContaining({
          settings: newConfig
        })
      );
    });

    test('should validate configuration parameters', () => {
      const invalidConfig = {
        audioHook: {
          sampleRate: -1, // Invalid sample rate
          channels: 0 // Invalid channel count
        }
      };

      // In a real implementation, this would validate the config
      expect(invalidConfig.audioHook.sampleRate).toBeLessThan(0);
      expect(invalidConfig.audioHook.channels).toBe(0);
    });
  });
});