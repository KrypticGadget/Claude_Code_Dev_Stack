#!/usr/bin/env node

/**
 * Semantic Analysis API - Main Entry Point
 * 
 * Starts the semantic analysis server with configuration from environment variables
 * and command line arguments.
 */

import { SemanticAnalysisServer, ServerConfig } from './server';
import { Command } from 'commander';
import * as fs from 'fs';
import * as path from 'path';

// Package information
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));

// Command line interface
const program = new Command();

program
  .name('semantic-api')
  .description('Semantic Analysis API Server - Tree-sitter based semantic analysis for 16+ programming languages')
  .version(packageJson.version);

program
  .command('start')
  .description('Start the semantic analysis server')
  .option('-p, --port <port>', 'Server port', (value) => parseInt(value), 3001)
  .option('-h, --host <host>', 'Server host', '0.0.0.0')
  .option('--no-websocket', 'Disable WebSocket support')
  .option('--no-caching', 'Disable caching')
  .option('--no-rate-limit', 'Disable rate limiting')
  .option('--max-cache-size <size>', 'Maximum cache size', (value) => parseInt(value), 1000)
  .option('--rate-limit-window <ms>', 'Rate limit window in milliseconds', (value) => parseInt(value), 15 * 60 * 1000)
  .option('--rate-limit-max <requests>', 'Maximum requests per window', (value) => parseInt(value), 1000)
  .option('--cors-origins <origins>', 'CORS allowed origins (comma-separated)', '*')
  .option('--config <file>', 'Configuration file path')
  .action(async (options) => {
    try {
      console.log('🚀 Starting Semantic Analysis API Server...');
      console.log(`📦 Version: ${packageJson.version}`);
      console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);

      // Load configuration
      const config = await loadConfiguration(options);
      
      // Validate configuration
      validateConfiguration(config);

      // Create and start server
      const server = new SemanticAnalysisServer(config);
      
      // Setup graceful shutdown
      setupGracefulShutdown(server);
      
      // Start the server
      await server.start();
      
      console.log('✅ Semantic Analysis API Server started successfully!');
      console.log(`📊 Server status available at: http://${config.host}:${config.port}/api/v1/health`);
      console.log(`📖 API documentation at: http://${config.host}:${config.port}/api/docs`);
      
      if (config.enableWebSocket) {
        console.log(`🔌 WebSocket endpoint: ws://${config.host}:${config.port}/ws`);
      }

    } catch (error) {
      console.error('❌ Failed to start server:', error.message);
      process.exit(1);
    }
  });

program
  .command('health')
  .description('Check server health')
  .option('-u, --url <url>', 'Server URL', 'http://localhost:3001')
  .action(async (options) => {
    try {
      const response = await fetch(`${options.url}/api/v1/health`);
      const health = await response.json();
      
      console.log('🏥 Server Health Status:');
      console.log(`Status: ${health.status}`);
      console.log(`Uptime: ${health.uptime?.formatted || 'Unknown'}`);
      console.log(`Memory: ${health.memory?.rss || 'Unknown'}`);
      
      process.exit(response.ok ? 0 : 1);
    } catch (error) {
      console.error('❌ Health check failed:', error.message);
      process.exit(1);
    }
  });

program
  .command('benchmark')
  .description('Run performance benchmarks')
  .option('-c, --concurrency <number>', 'Number of concurrent requests', (value) => parseInt(value), 10)
  .option('-r, --requests <number>', 'Total number of requests', (value) => parseInt(value), 1000)
  .option('-u, --url <url>', 'Server URL', 'http://localhost:3001')
  .action(async (options) => {
    console.log('🏃 Running performance benchmarks...');
    await runBenchmarks(options);
  });

// Parse command line arguments
program.parse();

/**
 * Load configuration from environment variables, command line options, and config file
 */
async function loadConfiguration(options: any): Promise<ServerConfig> {
  let config: Partial<ServerConfig> = {};

  // Load from config file if specified
  if (options.config) {
    try {
      const configFile = path.resolve(options.config);
      const fileConfig = JSON.parse(fs.readFileSync(configFile, 'utf8'));
      config = { ...config, ...fileConfig };
      console.log(`📁 Loaded configuration from: ${configFile}`);
    } catch (error) {
      console.warn(`⚠️  Failed to load config file: ${error.message}`);
    }
  }

  // Override with environment variables
  const envConfig: Partial<ServerConfig> = {
    port: process.env.PORT ? parseInt(process.env.PORT) : undefined,
    host: process.env.HOST,
    enableWebSocket: process.env.ENABLE_WEBSOCKET !== 'false',
    enableCaching: process.env.ENABLE_CACHING !== 'false',
    enableRateLimit: process.env.ENABLE_RATE_LIMIT !== 'false',
    maxCacheSize: process.env.MAX_CACHE_SIZE ? parseInt(process.env.MAX_CACHE_SIZE) : undefined,
    rateLimitWindow: process.env.RATE_LIMIT_WINDOW ? parseInt(process.env.RATE_LIMIT_WINDOW) : undefined,
    rateLimitMax: process.env.RATE_LIMIT_MAX ? parseInt(process.env.RATE_LIMIT_MAX) : undefined,
    corsOrigins: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : undefined
  };

  // Override with command line options
  const cliConfig: Partial<ServerConfig> = {
    port: options.port,
    host: options.host,
    enableWebSocket: options.websocket,
    enableCaching: options.caching,
    enableRateLimit: options.rateLimit,
    maxCacheSize: options.maxCacheSize,
    rateLimitWindow: options.rateLimitWindow,
    rateLimitMax: options.rateLimitMax,
    corsOrigins: options.corsOrigins === '*' ? ['*'] : options.corsOrigins.split(',')
  };

  // Merge configurations (CLI > ENV > File > Defaults)
  const finalConfig = {
    port: 3001,
    host: '0.0.0.0',
    enableWebSocket: true,
    enableCaching: true,
    enableRateLimit: true,
    maxCacheSize: 1000,
    rateLimitWindow: 15 * 60 * 1000,
    rateLimitMax: 1000,
    corsOrigins: ['*'],
    ...config,
    ...envConfig,
    ...cliConfig
  };

  return finalConfig as ServerConfig;
}

/**
 * Validate server configuration
 */
function validateConfiguration(config: ServerConfig): void {
  const errors: string[] = [];

  if (config.port < 1 || config.port > 65535) {
    errors.push('Port must be between 1 and 65535');
  }

  if (!config.host) {
    errors.push('Host is required');
  }

  if (config.maxCacheSize < 1) {
    errors.push('Max cache size must be greater than 0');
  }

  if (config.rateLimitWindow < 1000) {
    errors.push('Rate limit window must be at least 1000ms');
  }

  if (config.rateLimitMax < 1) {
    errors.push('Rate limit max must be greater than 0');
  }

  if (errors.length > 0) {
    throw new Error(`Configuration validation failed:\n${errors.join('\n')}`);
  }
}

/**
 * Setup graceful shutdown handlers
 */
function setupGracefulShutdown(server: SemanticAnalysisServer): void {
  const shutdownSignals = ['SIGTERM', 'SIGINT', 'SIGUSR1', 'SIGUSR2'];
  
  shutdownSignals.forEach((signal) => {
    process.on(signal, async () => {
      console.log(`\n🛑 Received ${signal}, starting graceful shutdown...`);
      
      try {
        await server.stop();
        console.log('✅ Server stopped gracefully');
        process.exit(0);
      } catch (error) {
        console.error('❌ Error during shutdown:', error);
        process.exit(1);
      }
    });
  });

  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    console.error('💥 Uncaught Exception:', error);
    process.exit(1);
  });

  // Handle unhandled promise rejections
  process.on('unhandledRejection', (reason, promise) => {
    console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
  });
}

/**
 * Run performance benchmarks
 */
async function runBenchmarks(options: any): Promise<void> {
  const { concurrency, requests, url } = options;
  
  console.log(`🎯 Target: ${url}`);
  console.log(`📊 Concurrency: ${concurrency}`);
  console.log(`📈 Total Requests: ${requests}`);
  
  const startTime = Date.now();
  const requestsPerWorker = Math.ceil(requests / concurrency);
  const workers: Promise<any>[] = [];

  // Create concurrent workers
  for (let i = 0; i < concurrency; i++) {
    workers.push(runBenchmarkWorker(url, requestsPerWorker, i));
  }

  // Wait for all workers to complete
  const results = await Promise.all(workers);
  const endTime = Date.now();
  
  // Calculate statistics
  const totalTime = endTime - startTime;
  const totalRequests = results.reduce((sum, result) => sum + result.completed, 0);
  const totalErrors = results.reduce((sum, result) => sum + result.errors, 0);
  const responseTimes = results.flatMap(result => result.responseTimes);
  
  const avgResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;
  const minResponseTime = Math.min(...responseTimes);
  const maxResponseTime = Math.max(...responseTimes);
  
  // Sort for percentiles
  responseTimes.sort((a, b) => a - b);
  const p50 = responseTimes[Math.floor(responseTimes.length * 0.5)];
  const p95 = responseTimes[Math.floor(responseTimes.length * 0.95)];
  const p99 = responseTimes[Math.floor(responseTimes.length * 0.99)];

  // Display results
  console.log('\n📊 Benchmark Results:');
  console.log(`⏱️  Total Time: ${totalTime}ms`);
  console.log(`📈 Requests/Second: ${Math.round((totalRequests / totalTime) * 1000)}`);
  console.log(`✅ Successful Requests: ${totalRequests}`);
  console.log(`❌ Failed Requests: ${totalErrors}`);
  console.log(`📊 Success Rate: ${((totalRequests / (totalRequests + totalErrors)) * 100).toFixed(2)}%`);
  console.log('\n⏰ Response Times:');
  console.log(`  Average: ${avgResponseTime.toFixed(2)}ms`);
  console.log(`  Minimum: ${minResponseTime}ms`);
  console.log(`  Maximum: ${maxResponseTime}ms`);
  console.log(`  50th Percentile: ${p50}ms`);
  console.log(`  95th Percentile: ${p95}ms`);
  console.log(`  99th Percentile: ${p99}ms`);
}

/**
 * Run benchmark worker
 */
async function runBenchmarkWorker(url: string, requests: number, workerId: number): Promise<any> {
  const result = {
    completed: 0,
    errors: 0,
    responseTimes: [] as number[]
  };

  const testPayload = {
    code: 'function example(param: string): string { return `Hello, ${param}!`; }',
    language: 'typescript',
    fileId: `benchmark-${workerId}-${Date.now()}.ts`
  };

  for (let i = 0; i < requests; i++) {
    try {
      const startTime = Date.now();
      
      const response = await fetch(`${url}/api/v1/analysis/parse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testPayload)
      });

      const endTime = Date.now();
      const responseTime = endTime - startTime;

      if (response.ok) {
        result.completed++;
        result.responseTimes.push(responseTime);
      } else {
        result.errors++;
      }
    } catch (error) {
      result.errors++;
    }
  }

  return result;
}

// If this module is run directly, parse command line arguments
if (require.main === module) {
  // This will trigger the commander parsing and execution
}