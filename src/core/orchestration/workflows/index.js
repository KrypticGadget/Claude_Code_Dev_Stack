/**
 * BMAD Workflow System Entry Point
 * Main entry point for the complete BMAD workflow orchestration system
 */

const BMADOrchestrator = require('./bmad-orchestrator');
const fs = require('fs').promises;
const path = require('path');

class BMADWorkflowManager {
    constructor() {
        this.orchestrator = null;
        this.config = null;
        this.isInitialized = false;
    }

    async initialize(configPath = null) {
        try {
            console.log('🚀 Initializing BMAD Workflow System...');
            
            // Load configuration
            this.config = await this.loadConfiguration(configPath);
            
            // Initialize orchestrator
            this.orchestrator = new BMADOrchestrator(this.config);
            
            // Wait for orchestrator to be ready
            await new Promise((resolve, reject) => {
                this.orchestrator.once('orchestrator:ready', resolve);
                this.orchestrator.once('orchestrator:error', reject);
            });
            
            this.isInitialized = true;
            console.log('✅ BMAD Workflow System initialized successfully');
            
            return this.orchestrator;
            
        } catch (error) {
            console.error('❌ Failed to initialize BMAD Workflow System:', error);
            throw error;
        }
    }

    async loadConfiguration(configPath) {
        const defaultConfig = {
            workingDirectory: process.cwd(),
            projectType: 'greenfield-fullstack',
            teamSize: 8,
            industryType: 'technology',
            complianceRequirements: [],
            remoteTeam: true,
            agentRegistry: './agent-registry.json',
            bmadCore: './core/orchestration/bmad',
            performanceMonitoring: true,
            remoteCollaboration: true,
            qualityGates: 'adaptive',
            sprintDuration: 14,
            velocityTracking: true,
            burndownCharts: true,
            retrospectives: true,
            dailyStandups: true,
            sprintReviews: true,
            backlogGrooming: true
        };

        if (configPath) {
            try {
                const configFile = await fs.readFile(configPath, 'utf8');
                const fileConfig = JSON.parse(configFile);
                return { ...defaultConfig, ...fileConfig };
            } catch (error) {
                console.warn(`Warning: Could not load config file ${configPath}, using defaults`);
                return defaultConfig;
            }
        }

        return defaultConfig;
    }

    async startProject(projectConfig = {}) {
        if (!this.isInitialized) {
            throw new Error('BMAD Workflow System not initialized. Call initialize() first.');
        }

        console.log('🚀 Starting new BMAD project...');
        return await this.orchestrator.startProject(projectConfig);
    }

    async executeWorkflow(workflowId, context = {}) {
        if (!this.isInitialized) {
            throw new Error('BMAD Workflow System not initialized. Call initialize() first.');
        }

        return await this.orchestrator.executeWorkflowStep(workflowId, context);
    }

    // Quick setup methods for different project types
    async setupStartupMVP(projectName, config = {}) {
        const startupConfig = {
            name: projectName,
            type: 'greenfield-fullstack',
            teamSize: 4,
            industryType: 'startup',
            timeline: '3-months',
            budget: 'lean',
            focusArea: 'speed-to-market',
            qualityGates: 'minimal',
            ...config
        };

        await this.initialize();
        return await this.startProject(startupConfig);
    }

    async setupEnterpriseProject(projectName, config = {}) {
        const enterpriseConfig = {
            name: projectName,
            type: 'enterprise-application',
            teamSize: 12,
            industryType: 'enterprise',
            timeline: '12-months',
            budget: 'comprehensive',
            complianceRequirements: ['SOC2', 'GDPR'],
            qualityGates: 'comprehensive',
            ...config
        };

        await this.initialize();
        return await this.startProject(enterpriseConfig);
    }

    async setupAPIProject(projectName, config = {}) {
        const apiConfig = {
            name: projectName,
            type: 'api-service',
            teamSize: 6,
            industryType: 'technology',
            timeline: '6-months',
            focusArea: 'api-design',
            qualityGates: 'api-focused',
            ...config
        };

        await this.initialize();
        return await this.startProject(apiConfig);
    }

    async setupMobileProject(projectName, config = {}) {
        const mobileConfig = {
            name: projectName,
            type: 'mobile-application',
            teamSize: 8,
            industryType: 'mobile',
            timeline: '9-months',
            focusArea: 'user-experience',
            qualityGates: 'mobile-optimized',
            ...config
        };

        await this.initialize();
        return await this.startProject(mobileConfig);
    }

    // Utility methods
    getStatus() {
        if (!this.isInitialized) {
            return { status: 'not_initialized' };
        }
        return this.orchestrator.getOrchestrationStatus();
    }

    async getProjectStatus() {
        if (!this.isInitialized) {
            throw new Error('BMAD Workflow System not initialized');
        }
        return await this.orchestrator.getComprehensiveProjectStatus();
    }

    // Dashboard access
    getDashboard(dashboardType = 'executive') {
        if (!this.isInitialized) {
            throw new Error('BMAD Workflow System not initialized');
        }
        return this.orchestrator.dashboards[dashboardType];
    }

    // Component access
    getWorkflowSystem() {
        return this.orchestrator?.bmadWorkflowSystem;
    }

    getAgileIntegration() {
        return this.orchestrator?.agileIntegration;
    }

    getUserStoryManagement() {
        return this.orchestrator?.userStoryManagement;
    }

    getProgressTracking() {
        return this.orchestrator?.progressTracking;
    }

    getStakeholderCommunication() {
        return this.orchestrator?.stakeholderCommunication;
    }

    // Event subscription
    on(event, handler) {
        if (this.orchestrator) {
            this.orchestrator.on(event, handler);
        }
    }

    off(event, handler) {
        if (this.orchestrator) {
            this.orchestrator.off(event, handler);
        }
    }
}

// Factory functions for quick setup
const BMADWorkflows = {
    // Main manager class
    Manager: BMADWorkflowManager,

    // Quick setup functions
    async createStartupMVP(projectName, config = {}) {
        const manager = new BMADWorkflowManager();
        return await manager.setupStartupMVP(projectName, config);
    },

    async createEnterpriseProject(projectName, config = {}) {
        const manager = new BMADWorkflowManager();
        return await manager.setupEnterpriseProject(projectName, config);
    },

    async createAPIProject(projectName, config = {}) {
        const manager = new BMADWorkflowManager();
        return await manager.setupAPIProject(projectName, config);
    },

    async createMobileProject(projectName, config = {}) {
        const manager = new BMADWorkflowManager();
        return await manager.setupMobileProject(projectName, config);
    },

    // Component exports
    BMADOrchestrator: require('./bmad-orchestrator'),
    BMADWorkflowSystem: require('./bmad-workflow-system'),
    AgileIntegration: require('./agile-integration'),
    UserStoryManagement: require('./user-story-management'),
    ProgressTracking: require('./progress-tracking'),
    StakeholderCommunication: require('./stakeholder-communication')
};

module.exports = BMADWorkflows;

// CLI support
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];

    async function runCLI() {
        const manager = new BMADWorkflowManager();

        try {
            switch (command) {
                case 'init':
                    await manager.initialize(args[1]);
                    console.log('✅ BMAD Workflow System initialized');
                    break;

                case 'start':
                    const projectName = args[1] || 'New BMAD Project';
                    const projectType = args[2] || 'startup-mvp';
                    
                    let result;
                    switch (projectType) {
                        case 'startup-mvp':
                            result = await manager.setupStartupMVP(projectName);
                            break;
                        case 'enterprise':
                            result = await manager.setupEnterpriseProject(projectName);
                            break;
                        case 'api':
                            result = await manager.setupAPIProject(projectName);
                            break;
                        case 'mobile':
                            result = await manager.setupMobileProject(projectName);
                            break;
                        default:
                            throw new Error(`Unknown project type: ${projectType}`);
                    }
                    
                    console.log('✅ Project started:', result.project.name);
                    console.log(`📊 Current phase: ${result.currentPhase}`);
                    console.log(`🏃 First sprint: #${result.firstSprint.number}`);
                    break;

                case 'status':
                    await manager.initialize();
                    const status = await manager.getProjectStatus();
                    console.log(JSON.stringify(status, null, 2));
                    break;

                case 'help':
                default:
                    console.log(`
BMAD Workflow System CLI

Usage:
  node index.js <command> [options]

Commands:
  init [config-file]           Initialize BMAD system
  start <name> <type>          Start new project (startup-mvp|enterprise|api|mobile)
  status                       Get current project status
  help                         Show this help

Examples:
  node index.js init config.json
  node index.js start "My App" startup-mvp
  node index.js start "Enterprise System" enterprise
  node index.js status
                    `);
            }
        } catch (error) {
            console.error('❌ Error:', error.message);
            process.exit(1);
        }
    }

    runCLI();
}