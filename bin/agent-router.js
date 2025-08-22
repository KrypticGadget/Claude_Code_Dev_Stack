#!/usr/bin/env node
/**
 * Agent Router - V3.0 Smart Agent Mention Processing
 * Handles @agent-name routing with intelligent orchestration
 */

import fs from 'fs-extra';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import chalk from 'chalk';

const execAsync = promisify(exec);

class AgentRouter {
    constructor() {
        this.claudeDir = path.join(process.env.HOME || process.env.USERPROFILE, '.claude');
        this.stateDir = path.join(this.claudeDir, 'state');
        
        // Agent registry with routing information
        this.agentRegistry = {
            'master-orchestrator': {
                script: 'smart_orchestrator.py',
                model: 'opus',
                priority: 1,
                description: 'Central coordination and workflow orchestration'
            },
            'prompt-engineer': {
                script: 'agent_enhancer_v3.py',
                model: 'opus', 
                priority: 1,
                description: 'Prompt optimization and enhancement'
            },
            'business-analyst': {
                script: 'business_analyst.py',
                model: 'sonnet',
                priority: 3,
                description: 'Market analysis and ROI calculations'
            },
            'technical-cto': {
                script: 'technical_cto.py',
                model: 'opus',
                priority: 3,
                description: 'Technical feasibility and architecture decisions'
            },
            'project-manager': {
                script: 'project_manager.py',
                model: 'haiku',
                priority: 3,
                description: 'Timeline and resource management'
            }
            // Add other agents as needed
        };
        
        this.initializeState();
    }
    
    initializeState() {
        // Ensure state directory exists
        fs.ensureDirSync(this.stateDir);
        
        // Initialize routing state if not exists
        const routingFile = path.join(this.stateDir, 'agent_routing.json');
        if (!fs.existsSync(routingFile)) {
            fs.writeJsonSync(routingFile, []);
        }
        
        // Initialize active agents tracking
        const activeFile = path.join(this.stateDir, 'active_agents.json');
        if (!fs.existsSync(activeFile)) {
            fs.writeJsonSync(activeFile, {});
        }
    }
    
    parseAgentMentions(content) {
        // Enhanced regex to match @agent-name with optional model specification
        const agentPattern = /@agent-([a-z-]+)(?:\[(opus|haiku|sonnet)\])?/g;
        const mentions = [];
        let match;
        
        while ((match = agentPattern.exec(content)) !== null) {
            const agentName = match[1];
            const modelOverride = match[2];
            
            if (this.agentRegistry[agentName]) {
                mentions.push({
                    agent: agentName,
                    model: modelOverride || this.agentRegistry[agentName].model,
                    priority: this.agentRegistry[agentName].priority,
                    timestamp: new Date().toISOString(),
                    fullMatch: match[0]
                });
            }
        }
        
        return mentions;
    }
    
    async routeRequest(userPrompt, mentions) {
        const routingPlan = {
            timestamp: new Date().toISOString(),
            originalPrompt: userPrompt,
            detectedAgents: mentions,
            executionPlan: null,
            success: false
        };
        
        try {
            // If no specific agents mentioned, use smart orchestration
            if (mentions.length === 0) {
                const smartPlan = await this.executeSmartOrchestration(userPrompt);
                routingPlan.executionPlan = smartPlan;
                routingPlan.success = true;
                return routingPlan;
            }
            
            // Sort mentions by priority for sequential execution
            const sortedMentions = mentions.sort((a, b) => a.priority - b.priority);
            
            // Create execution plan
            const executionGroups = this.createExecutionGroups(sortedMentions);
            
            // Execute agent routing
            const results = await this.executeAgentSequence(executionGroups, userPrompt);
            
            routingPlan.executionPlan = {
                groups: executionGroups,
                results: results
            };
            routingPlan.success = true;
            
            // Update active agents tracking
            await this.updateActiveAgents(mentions);
            
            return routingPlan;
            
        } catch (error) {
            routingPlan.error = error.message;
            console.error(chalk.red('Agent routing failed:'), error);
            return routingPlan;
        }
    }
    
    createExecutionGroups(mentions) {
        // Group agents by priority for parallel execution within same priority
        const groups = {};
        
        mentions.forEach(mention => {
            if (!groups[mention.priority]) {
                groups[mention.priority] = [];
            }
            groups[mention.priority].push(mention);
        });
        
        // Convert to sorted array
        return Object.keys(groups)
            .sort((a, b) => parseInt(a) - parseInt(b))
            .map(priority => ({
                priority: parseInt(priority),
                agents: groups[priority],
                parallel: groups[priority].length > 1
            }));
    }
    
    async executeSmartOrchestration(userPrompt) {
        // Use smart orchestrator to determine best agent selection
        const orchestratorPath = path.join(__dirname, '..', 'core', 'hooks', 'hooks', 'smart_orchestrator.py');
        
        if (fs.existsSync(orchestratorPath)) {
            try {
                const { stdout } = await execAsync(`python3 "${orchestratorPath}" "${userPrompt}"`);
                return JSON.parse(stdout);
            } catch (error) {
                console.warn(chalk.yellow('Smart orchestration unavailable, using default routing'));
                return { agents: ['master-orchestrator'], recommendation: 'fallback to master orchestrator' };
            }
        }
        
        return { agents: ['master-orchestrator'], recommendation: 'default routing' };
    }
    
    async executeAgentSequence(executionGroups, userPrompt) {
        const results = [];
        
        for (const group of executionGroups) {
            if (group.parallel && group.agents.length > 1) {
                // Execute agents in parallel
                const promises = group.agents.map(agent => this.executeAgent(agent, userPrompt));
                const groupResults = await Promise.allSettled(promises);
                results.push({
                    group: group.priority,
                    parallel: true,
                    results: groupResults
                });
            } else {
                // Execute agents sequentially
                const groupResults = [];
                for (const agent of group.agents) {
                    const result = await this.executeAgent(agent, userPrompt);
                    groupResults.push(result);
                }
                results.push({
                    group: group.priority,
                    parallel: false,
                    results: groupResults
                });
            }
        }
        
        return results;
    }
    
    async executeAgent(agentMention, userPrompt) {
        const agent = this.agentRegistry[agentMention.agent];
        
        if (!agent) {
            return {
                agent: agentMention.agent,
                success: false,
                error: 'Agent not found in registry'
            };
        }
        
        // Build agent execution context
        const context = {
            agent: agentMention.agent,
            model: agentMention.model,
            prompt: userPrompt,
            timestamp: new Date().toISOString()
        };
        
        try {
            // For now, return routing information
            // In future versions, this would execute the actual agent script
            return {
                agent: agentMention.agent,
                success: true,
                model: agentMention.model,
                action: 'routing_prepared',
                description: agent.description,
                context: context
            };
        } catch (error) {
            return {
                agent: agentMention.agent,
                success: false,
                error: error.message
            };
        }
    }
    
    async updateActiveAgents(mentions) {
        const activeFile = path.join(this.stateDir, 'active_agents.json');
        const active = {};
        
        mentions.forEach(mention => {
            active[mention.agent] = {
                model: mention.model,
                timestamp: mention.timestamp,
                priority: mention.priority
            };
        });
        
        await fs.writeJson(activeFile, active, { spaces: 2 });
    }
    
    async logRouting(routingPlan) {
        const logFile = path.join(this.stateDir, 'routing_history.jsonl');
        const logEntry = JSON.stringify(routingPlan) + '\n';
        
        await fs.appendFile(logFile, logEntry);
        
        // Keep only last 1000 entries
        const lines = (await fs.readFile(logFile, 'utf8')).split('\n').filter(Boolean);
        if (lines.length > 1000) {
            const recent = lines.slice(-1000);
            await fs.writeFile(logFile, recent.join('\n') + '\n');
        }
    }
    
    getStatusLine() {
        // Generate status line for current routing state
        const activeFile = path.join(this.stateDir, 'active_agents.json');
        
        if (fs.existsSync(activeFile)) {
            const active = fs.readJsonSync(activeFile);
            const agentCount = Object.keys(active).length;
            const agentNames = Object.keys(active).slice(0, 3).join(', ');
            
            return `${agentCount} active agents: ${agentNames}${agentCount > 3 ? '...' : ''}`;
        }
        
        return 'No active agents';
    }
}

// CLI interface
async function main() {
    const router = new AgentRouter();
    
    if (process.argv.length < 3) {
        console.log(chalk.blue('Agent Router V3.0'));
        console.log('Usage:');
        console.log('  agent-router.js <user-prompt>');
        console.log('  agent-router.js --status');
        console.log('  agent-router.js --list-agents');
        process.exit(0);
    }
    
    const command = process.argv[2];
    
    if (command === '--status') {
        console.log(router.getStatusLine());
        return;
    }
    
    if (command === '--list-agents') {
        console.log(chalk.blue('Available Agents:'));
        Object.entries(router.agentRegistry).forEach(([name, info]) => {
            console.log(chalk.green(`  @agent-${name}`) + chalk.gray(` (${info.model}) - ${info.description}`));
        });
        return;
    }
    
    const userPrompt = process.argv.slice(2).join(' ');
    const mentions = router.parseAgentMentions(userPrompt);
    
    if (mentions.length > 0) {
        console.log(chalk.blue('Detected Agents:'), mentions.map(m => `@agent-${m.agent}[${m.model}]`).join(', '));
    }
    
    const routingPlan = await router.routeRequest(userPrompt, mentions);
    await router.logRouting(routingPlan);
    
    if (routingPlan.success) {
        console.log(chalk.green('✓ Routing plan created successfully'));
        if (routingPlan.executionPlan?.recommendation) {
            console.log(chalk.blue('Recommendation:'), routingPlan.executionPlan.recommendation);
        }
    } else {
        console.log(chalk.red('✗ Routing failed:'), routingPlan.error);
    }
    
    // Output JSON for programmatic use
    if (process.env.CLAUDE_CODE_JSON_OUTPUT) {
        console.log(JSON.stringify(routingPlan, null, 2));
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export default AgentRouter;