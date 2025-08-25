#!/usr/bin/env node
/**
 * Claude Code Dev Stack - Cross-Platform Statusline Setup
 * Configures statusline with proper paths for Windows, Linux, and macOS
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

function setupStatusline() {
    const homeDir = os.homedir();
    const claudeDir = path.join(homeDir, '.claude');
    const settingsPath = path.join(claudeDir, 'settings.json');
    const hooksDir = path.join(claudeDir, 'hooks');
    
    // Determine the correct Python command and path format
    const isWindows = process.platform === 'win32';
    const pythonCmd = isWindows ? 'python' : 'python3';
    
    // Build the statusline script path
    const statuslineScript = path.join(hooksDir, 'claude_statusline.py');
    
    // Format the command based on OS
    let statuslineCommand;
    if (isWindows) {
        // Windows: Use double quotes and escaped backslashes
        const escapedPath = statuslineScript.replace(/\\/g, '\\\\');
        statuslineCommand = `${pythonCmd} "${escapedPath}"`;
    } else {
        // Linux/macOS: Use single quotes
        statuslineCommand = `${pythonCmd} '${statuslineScript}'`;
    }
    
    console.log('Setting up cross-platform statusline...');
    console.log(`Platform: ${process.platform}`);
    console.log(`Python command: ${pythonCmd}`);
    console.log(`Statusline path: ${statuslineScript}`);
    console.log(`Command: ${statuslineCommand}`);
    
    // Read existing settings
    let settings = {};
    if (fs.existsSync(settingsPath)) {
        try {
            const content = fs.readFileSync(settingsPath, 'utf8');
            settings = JSON.parse(content);
        } catch (error) {
            console.error('Error reading settings.json:', error.message);
            settings = {};
        }
    }
    
    // Update statusLine configuration
    settings.statusLine = {
        type: "command",
        command: statuslineCommand,
        padding: 0
    };
    
    // Ensure v3Features statusLine is enabled
    if (!settings.v3Features) {
        settings.v3Features = {};
    }
    if (!settings.v3Features.statusLine) {
        settings.v3Features.statusLine = {};
    }
    settings.v3Features.statusLine.enabled = true;
    settings.v3Features.statusLine.updateInterval = 100;
    settings.v3Features.statusLine.showInPrompt = true;
    settings.v3Features.statusLine.components = [
        "model",
        "git", 
        "phase",
        "agents",
        "tokens",
        "health"
    ];
    
    // Write updated settings
    try {
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
        console.log('✓ Statusline configuration updated successfully');
        
        // Verify the statusline script exists
        if (!fs.existsSync(statuslineScript)) {
            console.warn(`⚠ Warning: Statusline script not found at ${statuslineScript}`);
            console.log('  Run ccds-setup to install the statusline scripts');
        } else {
            console.log('✓ Statusline script found');
            
            // Test the command
            const { execSync } = require('child_process');
            try {
                const testCmd = isWindows 
                    ? `echo {"model":{"display_name":"Test"}} | ${statuslineCommand}`
                    : `echo '{"model":{"display_name":"Test"}}' | ${statuslineCommand}`;
                
                const result = execSync(testCmd, { encoding: 'utf8', stdio: 'pipe' });
                console.log('✓ Statusline test successful:', result.trim());
            } catch (error) {
                console.warn('⚠ Statusline test failed:', error.message);
            }
        }
        
    } catch (error) {
        console.error('Error writing settings.json:', error.message);
        process.exit(1);
    }
}

// Run setup
setupStatusline();