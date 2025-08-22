#!/usr/bin/env node

/**
 * Code Sandbox MCP Server
 * Provides secure code execution capabilities via Docker containers
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import { randomUUID } from 'crypto';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

class CodeSandboxMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'code-sandbox-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.supportedLanguages = {
      javascript: { image: 'node:18-alpine', ext: '.js', cmd: ['node'] },
      typescript: { image: 'node:18-alpine', ext: '.ts', cmd: ['npx', 'ts-node'] },
      python: { image: 'python:3.11-alpine', ext: '.py', cmd: ['python'] },
      bash: { image: 'alpine:latest', ext: '.sh', cmd: ['sh'] },
      go: { image: 'golang:1.21-alpine', ext: '.go', cmd: ['go', 'run'] },
      rust: { image: 'rust:1.70-alpine', ext: '.rs', cmd: ['rustc', '--edition', '2021', '-o', '/tmp/binary', '&&', '/tmp/binary'] },
    };
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'execute_code',
          description: 'Execute code in a secure sandbox environment',
          inputSchema: {
            type: 'object',
            properties: {
              language: {
                type: 'string',
                description: 'Programming language',
                enum: Object.keys(this.supportedLanguages),
              },
              code: {
                type: 'string',
                description: 'Code to execute',
              },
              timeout: {
                type: 'number',
                description: 'Execution timeout in seconds (default: 30)',
                default: 30,
              },
              dependencies: {
                type: 'array',
                description: 'Additional dependencies to install',
                items: { type: 'string' },
              },
            },
            required: ['language', 'code'],
          },
        },
        {
          name: 'create_sandbox',
          description: 'Create a persistent sandbox environment',
          inputSchema: {
            type: 'object',
            properties: {
              language: {
                type: 'string',
                description: 'Programming language',
                enum: Object.keys(this.supportedLanguages),
              },
              name: {
                type: 'string',
                description: 'Sandbox name (optional)',
              },
              dependencies: {
                type: 'array',
                description: 'Dependencies to pre-install',
                items: { type: 'string' },
              },
            },
            required: ['language'],
          },
        },
        {
          name: 'list_sandboxes',
          description: 'List active sandbox environments',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'delete_sandbox',
          description: 'Delete a sandbox environment',
          inputSchema: {
            type: 'object',
            properties: {
              sandboxId: {
                type: 'string',
                description: 'Sandbox ID to delete',
              },
            },
            required: ['sandboxId'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'execute_code':
            return await this.executeCode(args);
          case 'create_sandbox':
            return await this.createSandbox(args);
          case 'list_sandboxes':
            return await this.listSandboxes();
          case 'delete_sandbox':
            return await this.deleteSandbox(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async executeCode(args) {
    const { language, code, timeout = 30, dependencies = [] } = args;
    
    if (!this.supportedLanguages[language]) {
      throw new Error(`Unsupported language: ${language}`);
    }

    const sandboxId = randomUUID();
    const config = this.supportedLanguages[language];
    
    try {
      // Create temporary directory for code
      const tempDir = path.join(os.tmpdir(), `sandbox-${sandboxId}`);
      await fs.mkdir(tempDir, { recursive: true });
      
      const codeFile = path.join(tempDir, `main${config.ext}`);
      await fs.writeFile(codeFile, code);

      // Build Docker command
      const dockerArgs = [
        'run',
        '--rm',
        '--memory=512m',
        '--cpus=1',
        '--network=none',
        '--user=1000:1000',
        `--volume=${tempDir}:/workspace`,
        '--workdir=/workspace',
        `--timeout=${timeout}`,
        config.image,
      ];

      // Install dependencies if needed
      if (dependencies.length > 0) {
        const installCmd = this.getInstallCommand(language, dependencies);
        if (installCmd) {
          dockerArgs.push('sh', '-c', `${installCmd} && ${config.cmd.join(' ')} main${config.ext}`);
        } else {
          dockerArgs.push(...config.cmd, `main${config.ext}`);
        }
      } else {
        dockerArgs.push(...config.cmd, `main${config.ext}`);
      }

      const result = await this.runDocker(dockerArgs, timeout * 1000);
      
      // Cleanup
      await fs.rm(tempDir, { recursive: true, force: true });

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              sandboxId,
              language,
              exitCode: result.exitCode,
              stdout: result.stdout,
              stderr: result.stderr,
              executionTime: result.executionTime,
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Execution failed: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async createSandbox(args) {
    const { language, name, dependencies = [] } = args;
    const sandboxId = name || randomUUID();
    const config = this.supportedLanguages[language];

    try {
      const dockerArgs = [
        'run',
        '-d',
        '--name', `sandbox-${sandboxId}`,
        '--memory=1g',
        '--cpus=2',
        '--network=claude-network',
        config.image,
        'tail', '-f', '/dev/null'
      ];

      await this.runDocker(dockerArgs);

      // Install dependencies if provided
      if (dependencies.length > 0) {
        const installCmd = this.getInstallCommand(language, dependencies);
        if (installCmd) {
          await this.runDocker(['exec', `sandbox-${sandboxId}`, 'sh', '-c', installCmd]);
        }
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              sandboxId,
              language,
              status: 'created',
              dependencies,
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to create sandbox: ${error.message}`);
    }
  }

  async listSandboxes() {
    try {
      const result = await this.runDocker(['ps', '--filter', 'name=sandbox-', '--format', 'table {{.Names}}\\t{{.Status}}\\t{{.CreatedAt}}']);
      
      return {
        content: [
          {
            type: 'text',
            text: result.stdout,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to list sandboxes: ${error.message}`);
    }
  }

  async deleteSandbox(args) {
    const { sandboxId } = args;

    try {
      await this.runDocker(['stop', `sandbox-${sandboxId}`]);
      await this.runDocker(['rm', `sandbox-${sandboxId}`]);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              sandboxId,
              status: 'deleted',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to delete sandbox: ${error.message}`);
    }
  }

  getInstallCommand(language, dependencies) {
    const commands = {
      javascript: `npm install ${dependencies.join(' ')}`,
      typescript: `npm install ${dependencies.join(' ')}`,
      python: `pip install ${dependencies.join(' ')}`,
      go: `go mod init sandbox && go get ${dependencies.join(' ')}`,
    };
    return commands[language];
  }

  runDocker(args, timeout = 30000) {
    return new Promise((resolve, reject) => {
      const process = spawn('docker', args);
      let stdout = '';
      let stderr = '';
      const startTime = Date.now();

      const timer = setTimeout(() => {
        process.kill('SIGKILL');
        reject(new Error('Execution timeout'));
      }, timeout);

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        clearTimeout(timer);
        const executionTime = Date.now() - startTime;
        
        resolve({
          exitCode: code,
          stdout: stdout.trim(),
          stderr: stderr.trim(),
          executionTime,
        });
      });

      process.on('error', (error) => {
        clearTimeout(timer);
        reject(error);
      });
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Code Sandbox MCP Server running');
  }
}

// Create and start server
const server = new CodeSandboxMCPServer();
server.run().catch(console.error);