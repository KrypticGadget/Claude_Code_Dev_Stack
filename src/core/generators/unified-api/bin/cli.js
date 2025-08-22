#!/usr/bin/env node

/**
 * CLI entry point for the Unified MCP Generator
 */

import { setupCommands } from '../dist/cli/commands.js';

// Get the CLI program and execute
const program = setupCommands();

// Parse command line arguments
program.parse(process.argv);

// If no command was provided, show help
if (!process.argv.slice(2).length) {
  program.outputHelp();
}