/**
 * Agent Manager - Handles installation and management of the 28 specialized agents
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export class AgentManager {
  constructor(options = {}) {
    this.options = options;
    this.agentsPath = path.join(__dirname, '../../core/agents/agents');
    this.installedAgents = new Map();
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;
    
    console.log(chalk.blue('🤖 Initializing Agent Manager...'));
    
    // Load available agents
    await this.loadAvailableAgents();
    
    this.initialized = true;
    console.log(chalk.green('✅ Agent Manager initialized'));
  }

  async loadAvailableAgents() {
    try {
      const agentFiles = await fs.readdir(this.agentsPath);
      const agents = agentFiles
        .filter(file => file.endsWith('.md'))
        .map(file => ({
          name: path.basename(file, '.md'),
          path: path.join(this.agentsPath, file),
          installed: false
        }));

      for (const agent of agents) {
        this.installedAgents.set(agent.name, agent);
      }

      console.log(chalk.blue(`📋 Loaded ${agents.length} available agents`));
    } catch (error) {
      throw new Error(`Failed to load agents: ${error.message}`);
    }
  }

  async install(targetPath = null) {
    console.log(chalk.blue('🚀 Installing all agents...'));
    
    const claudeConfigPath = targetPath || await this.detectClaudeConfigPath();
    const agentsTargetPath = path.join(claudeConfigPath, 'agents');
    
    // Ensure target directory exists
    await fs.ensureDir(agentsTargetPath);
    
    const results = {
      installed: 0,
      failed: 0,
      errors: []
    };

    for (const [agentName, agent] of this.installedAgents) {
      try {
        await this.installSingle(agentName, targetPath);
        results.installed++;
        console.log(chalk.green(`  ✅ ${agentName}`));
      } catch (error) {
        results.failed++;
        results.errors.push({ agent: agentName, error: error.message });
        console.log(chalk.red(`  ❌ ${agentName}: ${error.message}`));
      }
    }

    console.log(chalk.blue(`📊 Installation complete: ${results.installed} installed, ${results.failed} failed`));
    return results;
  }

  async installSingle(agentName, targetPath = null) {
    const agent = this.installedAgents.get(agentName);
    if (!agent) {
      throw new Error(`Agent "${agentName}" not found`);
    }

    const claudeConfigPath = targetPath || await this.detectClaudeConfigPath();
    const agentsTargetPath = path.join(claudeConfigPath, 'agents');
    const targetFilePath = path.join(agentsTargetPath, `${agentName}.md`);

    // Ensure target directory exists
    await fs.ensureDir(agentsTargetPath);

    // Copy agent file
    await fs.copy(agent.path, targetFilePath);

    // Mark as installed
    agent.installed = true;
    agent.installedPath = targetFilePath;

    return {
      success: true,
      agent: agentName,
      path: targetFilePath
    };
  }

  async detectClaudeConfigPath() {
    const possiblePaths = [
      path.join(process.env.HOME || process.env.USERPROFILE, '.claude'),
      path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'claude'),
      path.join(process.cwd(), '.claude')
    ];

    for (const testPath of possiblePaths) {
      if (await fs.pathExists(testPath)) {
        return testPath;
      }
    }

    // Default to home directory
    const defaultPath = path.join(process.env.HOME || process.env.USERPROFILE, '.claude');
    await fs.ensureDir(defaultPath);
    return defaultPath;
  }

  getAgentCount() {
    return this.installedAgents.size;
  }

  getStatus() {
    const installedCount = Array.from(this.installedAgents.values()).filter(a => a.installed).length;
    return {
      available: this.installedAgents.size,
      installed: installedCount,
      initialized: this.initialized
    };
  }

  async listAvailable() {
    const agents = Array.from(this.installedAgents.values()).map(agent => ({
      name: agent.name,
      installed: agent.installed,
      path: agent.path,
      category: this.getAgentCategory(agent.name),
      description: this.getAgentDescription(agent.name)
    }));

    return agents.sort((a, b) => a.name.localeCompare(b.name));
  }

  getAgentCategory(agentName) {
    const categories = {
      'Architecture & Design': [
        'backend-services', 'frontend-architecture', 'database-architecture',
        'security-architecture', 'technical-specifications'
      ],
      'Development & Engineering': [
        'api-integration-specialist', 'middleware-specialist', 'mobile-development',
        'performance-optimization', 'production-frontend'
      ],
      'DevOps & Infrastructure': [
        'devops-engineering', 'integration-setup', 'script-automation', 'testing-automation'
      ],
      'Quality & Management': [
        'quality-assurance', 'project-manager', 'master-orchestrator', 'business-analyst'
      ],
      'Leadership & Strategy': [
        'ceo-strategy', 'technical-cto', 'business-tech-alignment', 'financial-analyst'
      ],
      'User Experience & Design': [
        'ui-ux-design', 'frontend-mockup', 'prompt-engineer', 'usage-guide', 'development-prompt'
      ]
    };

    for (const [category, agents] of Object.entries(categories)) {
      if (agents.includes(agentName)) {
        return category;
      }
    }

    return 'General';
  }

  getAgentDescription(agentName) {
    const descriptions = {
      'backend-services': 'Backend Services Architecture Specialist',
      'frontend-architecture': 'Frontend Architecture Specialist',
      'database-architecture': 'Database Architecture Specialist',
      'security-architecture': 'Security Architecture Specialist',
      'technical-specifications': 'Technical Specifications Specialist',
      'api-integration-specialist': 'API Integration Specialist',
      'middleware-specialist': 'Middleware Development Specialist',
      'mobile-development': 'Mobile Development Specialist',
      'performance-optimization': 'Performance Optimization Specialist',
      'production-frontend': 'Production Frontend Specialist',
      'devops-engineering': 'DevOps Engineering Specialist',
      'integration-setup': 'Integration Setup Specialist',
      'script-automation': 'Script Automation Specialist',
      'testing-automation': 'Testing Automation Specialist',
      'quality-assurance': 'Quality Assurance Specialist',
      'project-manager': 'Project Management Specialist',
      'master-orchestrator': 'Master Orchestrator Agent',
      'business-analyst': 'Business Analysis Specialist',
      'ceo-strategy': 'CEO Strategy Specialist',
      'technical-cto': 'Technical CTO Specialist',
      'business-tech-alignment': 'Business-Tech Alignment Specialist',
      'financial-analyst': 'Financial Analysis Specialist',
      'ui-ux-design': 'UI/UX Design Specialist',
      'frontend-mockup': 'Frontend Mockup Specialist',
      'prompt-engineer': 'Prompt Engineering Specialist',
      'usage-guide': 'Usage Guide Specialist',
      'development-prompt': 'Development Prompt Specialist'
    };

    return descriptions[agentName] || 'Specialized AI Agent';
  }
}