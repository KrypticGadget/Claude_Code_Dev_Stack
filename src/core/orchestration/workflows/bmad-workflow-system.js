/**
 * BMAD Workflow System v3.6.9
 * Complete Business Model, Architecture, Design workflow orchestration
 * with Agile methodology integration
 */

const { EventEmitter } = require('events');
const fs = require('fs').promises;
const path = require('path');

class BMADWorkflowSystem extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            workingDirectory: config.workingDirectory || process.cwd(),
            agentRegistry: config.agentRegistry || './agent-registry.json',
            bmadCore: config.bmadCore || './core/orchestration/bmad',
            performanceMonitoring: config.performanceMonitoring || true,
            remoteCollaboration: config.remoteCollaboration || true,
            qualityGates: config.qualityGates || 'adaptive',
            ...config
        };
        
        this.phases = {
            BUSINESS_MODEL: 'business_model',
            ARCHITECTURE: 'architecture',
            DESIGN: 'design',
            DEVELOPMENT: 'development'
        };
        
        this.currentPhase = null;
        this.currentSprint = null;
        this.workflows = new Map();
        this.agents = new Map();
        this.milestones = new Map();
        this.userStories = new Map();
        this.acceptanceCriteria = new Map();
        this.qualityGates = new Map();
        this.stakeholders = new Map();
        this.performanceMetrics = new Map();
        
        this.initializeSystem();
    }

    async initializeSystem() {
        try {
            console.log('🚀 Initializing BMAD Workflow System...');
            
            // Load agent registry
            await this.loadAgentRegistry();
            
            // Initialize BMAD workflows
            await this.initializeBMADWorkflows();
            
            // Setup agile methodology integration
            await this.setupAgileIntegration();
            
            // Configure quality gates
            await this.configureQualityGates();
            
            // Initialize performance monitoring
            if (this.config.performanceMonitoring) {
                await this.initializePerformanceMonitoring();
            }
            
            // Setup remote collaboration
            if (this.config.remoteCollaboration) {
                await this.setupRemoteCollaboration();
            }
            
            console.log('✅ BMAD Workflow System initialized successfully');
            this.emit('system:initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize BMAD Workflow System:', error);
            this.emit('system:error', error);
        }
    }

    async loadAgentRegistry() {
        const registryPath = path.resolve(this.config.workingDirectory, this.config.agentRegistry);
        const registryData = await fs.readFile(registryPath, 'utf8');
        const registry = JSON.parse(registryData);
        
        // Load all agents
        for (const [agentId, agentConfig] of Object.entries(registry.agents)) {
            this.agents.set(agentId, {
                ...agentConfig,
                status: 'ready',
                currentTask: null,
                workload: 0
            });
        }
        
        console.log(`📋 Loaded ${this.agents.size} agents from registry`);
    }

    async initializeBMADWorkflows() {
        // Business Model Analysis Workflow
        this.workflows.set('business-model-analysis', {
            id: 'business-model-analysis',
            name: 'Business Model Analysis',
            phase: this.phases.BUSINESS_MODEL,
            agents: [
                'agent-bmad-business-model',
                'agent-bmad-market-research',
                'agent-business-analyst',
                'agent-ceo-strategy'
            ],
            deliverables: [
                'business-model-canvas',
                'value-proposition-canvas',
                'market-research-report',
                'competitive-analysis',
                'revenue-model-specification'
            ],
            acceptanceCriteria: [
                'validated-value-proposition',
                'identified-target-market',
                'feasible-revenue-streams',
                'competitive-differentiation'
            ],
            estimatedDuration: '2-3 sprints',
            dependencies: []
        });

        // Architecture Planning Workflow
        this.workflows.set('architecture-planning', {
            id: 'architecture-planning',
            name: 'Architecture Planning',
            phase: this.phases.ARCHITECTURE,
            agents: [
                'agent-bmad-architecture-design',
                'agent-bmad-technical-planning',
                'agent-tech-specs',
                'agent-technical-cto',
                'agent-frontend-architecture',
                'agent-backend-services',
                'agent-database-architecture'
            ],
            deliverables: [
                'system-architecture-document',
                'technology-stack-selection',
                'scalability-plan',
                'integration-blueprint',
                'technical-specifications',
                'deployment-strategy'
            ],
            acceptanceCriteria: [
                'scalable-architecture-design',
                'technology-stack-validated',
                'performance-requirements-met',
                'security-requirements-addressed'
            ],
            estimatedDuration: '3-4 sprints',
            dependencies: ['business-model-analysis']
        });

        // Design Implementation Workflow
        this.workflows.set('design-implementation', {
            id: 'design-implementation',
            name: 'Design Implementation',
            phase: this.phases.DESIGN,
            agents: [
                'agent-bmad-design',
                'agent-bmad-user-experience',
                'agent-bmad-visual-design',
                'agent-ui-ux-designer',
                'agent-user-researcher',
                'agent-react-specialist'
            ],
            deliverables: [
                'user-experience-design',
                'interface-mockups',
                'design-system',
                'interactive-prototypes',
                'user-journey-maps',
                'accessibility-guidelines'
            ],
            acceptanceCriteria: [
                'user-centered-design',
                'accessibility-compliant',
                'responsive-design',
                'brand-consistency',
                'usability-validated'
            ],
            estimatedDuration: '2-3 sprints',
            dependencies: ['architecture-planning']
        });

        // Development Coordination Workflow
        this.workflows.set('development-coordination', {
            id: 'development-coordination',
            name: 'Development Coordination',
            phase: this.phases.DEVELOPMENT,
            agents: [
                'agent-project-manager',
                'agent-scrum-master',
                'agent-react-specialist',
                'agent-backend-services',
                'agent-api-integration',
                'agent-qa-tester',
                'agent-devops-deployment'
            ],
            deliverables: [
                'sprint-plans',
                'developed-features',
                'tested-components',
                'deployment-packages',
                'documentation',
                'performance-reports'
            ],
            acceptanceCriteria: [
                'functional-requirements-met',
                'quality-standards-maintained',
                'performance-benchmarks-achieved',
                'security-validated'
            ],
            estimatedDuration: 'Ongoing sprints',
            dependencies: ['design-implementation']
        });

        console.log(`📊 Initialized ${this.workflows.size} BMAD workflows`);
    }

    async setupAgileIntegration() {
        // Sprint Planning Integration
        this.agileConfig = {
            sprintDuration: 14, // days
            velocityTracking: true,
            burndownCharts: true,
            retrospectives: true,
            dailyStandups: true,
            sprintReviews: true,
            backlogGrooming: true
        };

        // User Story Templates
        this.userStoryTemplate = {
            id: '',
            title: '',
            description: '',
            asA: '',
            iWant: '',
            soThat: '',
            acceptanceCriteria: [],
            priority: 'medium',
            storyPoints: 0,
            phase: '',
            workflow: '',
            assignedAgent: '',
            status: 'backlog',
            sprint: null,
            epic: null,
            tags: [],
            dependencies: [],
            blockers: [],
            testCases: [],
            definition_of_done: []
        };

        // Acceptance Criteria Template
        this.acceptanceCriteriaTemplate = {
            id: '',
            userStoryId: '',
            description: '',
            givenWhenThen: {
                given: '',
                when: '',
                then: ''
            },
            priority: 'must',
            testable: true,
            validated: false,
            validationMethod: '',
            notes: ''
        };

        console.log('🔄 Agile methodology integration configured');
    }

    async configureQualityGates() {
        // Business Model Quality Gates
        this.qualityGates.set('business-model-validation', {
            phase: this.phases.BUSINESS_MODEL,
            criteria: [
                'market-size-validated',
                'customer-segments-identified',
                'value-proposition-tested',
                'revenue-model-feasible',
                'competitive-advantage-clear'
            ],
            automatedChecks: [
                'market-research-completeness',
                'financial-model-validation'
            ],
            manualReviews: [
                'stakeholder-approval',
                'executive-sign-off'
            ],
            exitCriteria: 'all-criteria-met'
        });

        // Architecture Quality Gates
        this.qualityGates.set('architecture-validation', {
            phase: this.phases.ARCHITECTURE,
            criteria: [
                'scalability-requirements-met',
                'performance-benchmarks-defined',
                'security-architecture-approved',
                'technology-stack-justified',
                'integration-points-specified'
            ],
            automatedChecks: [
                'architecture-linting',
                'dependency-analysis',
                'security-scan'
            ],
            manualReviews: [
                'technical-review-board',
                'security-team-approval'
            ],
            exitCriteria: 'technical-approval-received'
        });

        // Design Quality Gates
        this.qualityGates.set('design-validation', {
            phase: this.phases.DESIGN,
            criteria: [
                'user-experience-validated',
                'accessibility-compliance',
                'design-system-consistency',
                'responsive-design-verified',
                'usability-testing-passed'
            ],
            automatedChecks: [
                'accessibility-scan',
                'design-token-validation',
                'responsive-breakpoint-test'
            ],
            manualReviews: [
                'ux-review',
                'stakeholder-approval',
                'user-acceptance-testing'
            ],
            exitCriteria: 'user-validation-successful'
        });

        // Development Quality Gates
        this.qualityGates.set('development-validation', {
            phase: this.phases.DEVELOPMENT,
            criteria: [
                'code-coverage-threshold',
                'performance-benchmarks-met',
                'security-vulnerabilities-resolved',
                'functional-tests-passing',
                'integration-tests-passing'
            ],
            automatedChecks: [
                'unit-tests',
                'integration-tests',
                'security-scan',
                'performance-tests',
                'code-quality-analysis'
            ],
            manualReviews: [
                'code-review',
                'qa-testing',
                'user-acceptance-testing'
            ],
            exitCriteria: 'all-tests-passing'
        });

        console.log(`🛡️ Configured ${this.qualityGates.size} quality gates`);
    }

    async initializePerformanceMonitoring() {
        this.performanceMetrics.set('workflow-velocity', {
            metric: 'story-points-per-sprint',
            target: 50,
            current: 0,
            trend: 'stable'
        });

        this.performanceMetrics.set('cycle-time', {
            metric: 'days-from-start-to-done',
            target: 5,
            current: 0,
            trend: 'improving'
        });

        this.performanceMetrics.set('quality-score', {
            metric: 'defect-rate-percentage',
            target: 2,
            current: 0,
            trend: 'stable'
        });

        this.performanceMetrics.set('stakeholder-satisfaction', {
            metric: 'satisfaction-score',
            target: 4.5,
            current: 0,
            trend: 'improving'
        });

        console.log('📊 Performance monitoring initialized');
    }

    async setupRemoteCollaboration() {
        this.collaborationConfig = {
            realTimeEditing: true,
            videoConferencing: true,
            asyncCommunication: true,
            documentSharing: true,
            versionControl: true,
            timeZoneSupport: true,
            notificationSystem: true
        };

        this.stakeholders.set('product-owner', {
            role: 'Product Owner',
            timezone: 'UTC-8',
            availability: '9am-5pm',
            communication: ['email', 'slack', 'video'],
            permissions: ['approve-requirements', 'prioritize-backlog']
        });

        this.stakeholders.set('technical-lead', {
            role: 'Technical Lead',
            timezone: 'UTC-5',
            availability: '8am-6pm',
            communication: ['slack', 'github', 'video'],
            permissions: ['approve-architecture', 'review-code']
        });

        this.stakeholders.set('ux-lead', {
            role: 'UX Lead',
            timezone: 'UTC+1',
            availability: '9am-5pm',
            communication: ['figma', 'slack', 'video'],
            permissions: ['approve-designs', 'conduct-user-research']
        });

        console.log('🌐 Remote collaboration configured');
    }

    // Sprint Planning with BMAD Integration
    async planSprint(sprintNumber, duration = 14) {
        console.log(`📅 Planning Sprint ${sprintNumber}...`);
        
        const sprint = {
            number: sprintNumber,
            startDate: new Date(),
            endDate: new Date(Date.now() + duration * 24 * 60 * 60 * 1000),
            duration: duration,
            capacity: await this.calculateTeamCapacity(),
            goals: [],
            userStories: [],
            bmadPhase: this.currentPhase,
            qualityGates: [],
            milestones: []
        };

        // Assign BMAD-driven user stories
        const prioritizedStories = await this.prioritizeUserStoriesForPhase(this.currentPhase);
        const sprintStories = await this.selectStoriesForSprint(prioritizedStories, sprint.capacity);
        
        sprint.userStories = sprintStories;
        sprint.goals = await this.generateSprintGoals(sprintStories);
        sprint.qualityGates = await this.getQualityGatesForPhase(this.currentPhase);

        this.currentSprint = sprint;
        this.emit('sprint:planned', sprint);
        
        return sprint;
    }

    // User Story Management
    async createUserStory(storyData) {
        const story = {
            ...this.userStoryTemplate,
            ...storyData,
            id: this.generateId('story'),
            createdAt: new Date(),
            updatedAt: new Date()
        };

        // Auto-assign to appropriate BMAD workflow
        story.workflow = await this.determineWorkflowForStory(story);
        story.phase = await this.determinePhaseForStory(story);
        
        // Generate acceptance criteria
        if (!story.acceptanceCriteria || story.acceptanceCriteria.length === 0) {
            story.acceptanceCriteria = await this.generateAcceptanceCriteria(story);
        }

        this.userStories.set(story.id, story);
        this.emit('story:created', story);
        
        return story;
    }

    async generateAcceptanceCriteria(story) {
        const criteria = [];
        
        // Generate BMAD-specific acceptance criteria based on phase
        switch (story.phase) {
            case this.phases.BUSINESS_MODEL:
                criteria.push({
                    ...this.acceptanceCriteriaTemplate,
                    id: this.generateId('criteria'),
                    userStoryId: story.id,
                    description: 'Business model validation completed',
                    givenWhenThen: {
                        given: 'A business model hypothesis',
                        when: 'Market research is conducted',
                        then: 'The model should be validated or invalidated with evidence'
                    }
                });
                break;
                
            case this.phases.ARCHITECTURE:
                criteria.push({
                    ...this.acceptanceCriteriaTemplate,
                    id: this.generateId('criteria'),
                    userStoryId: story.id,
                    description: 'Architecture design meets scalability requirements',
                    givenWhenThen: {
                        given: 'A system architecture design',
                        when: 'Load testing is performed',
                        then: 'The system should handle expected load without degradation'
                    }
                });
                break;
                
            case this.phases.DESIGN:
                criteria.push({
                    ...this.acceptanceCriteriaTemplate,
                    id: this.generateId('criteria'),
                    userStoryId: story.id,
                    description: 'Design meets accessibility standards',
                    givenWhenThen: {
                        given: 'A user interface design',
                        when: 'Accessibility testing is performed',
                        then: 'The design should meet WCAG 2.1 AA standards'
                    }
                });
                break;
                
            case this.phases.DEVELOPMENT:
                criteria.push({
                    ...this.acceptanceCriteriaTemplate,
                    id: this.generateId('criteria'),
                    userStoryId: story.id,
                    description: 'Feature implementation meets functional requirements',
                    givenWhenThen: {
                        given: 'A developed feature',
                        when: 'Automated tests are executed',
                        then: 'All tests should pass with >90% code coverage'
                    }
                });
                break;
        }
        
        return criteria;
    }

    // Progress Tracking
    async trackBMADProgress() {
        const progress = {
            currentPhase: this.currentPhase,
            currentSprint: this.currentSprint?.number || 0,
            completedMilestones: Array.from(this.milestones.values()).filter(m => m.completed),
            totalMilestones: this.milestones.size,
            completedStories: Array.from(this.userStories.values()).filter(s => s.status === 'done'),
            totalStories: this.userStories.size,
            qualityGatesPassed: Array.from(this.qualityGates.values()).filter(q => q.status === 'passed'),
            totalQualityGates: this.qualityGates.size,
            teamVelocity: this.calculateTeamVelocity(),
            burndownData: this.generateBurndownData(),
            riskAssessment: await this.assessProjectRisks()
        };

        // Calculate overall completion percentage
        progress.completionPercentage = this.calculateOverallCompletion(progress);
        
        this.emit('progress:updated', progress);
        return progress;
    }

    // Quality Assurance
    async executeQualityGate(gateId) {
        console.log(`🛡️ Executing quality gate: ${gateId}`);
        
        const gate = this.qualityGates.get(gateId);
        if (!gate) {
            throw new Error(`Quality gate ${gateId} not found`);
        }

        const results = {
            gateId: gateId,
            startTime: new Date(),
            automatedChecks: {},
            manualReviews: {},
            overallStatus: 'pending',
            passed: false,
            blockers: [],
            recommendations: []
        };

        // Execute automated checks
        for (const check of gate.automatedChecks) {
            try {
                results.automatedChecks[check] = await this.executeAutomatedCheck(check);
            } catch (error) {
                results.automatedChecks[check] = { status: 'failed', error: error.message };
                results.blockers.push(`Automated check failed: ${check}`);
            }
        }

        // Schedule manual reviews
        for (const review of gate.manualReviews) {
            results.manualReviews[review] = { status: 'pending', assignee: null, dueDate: null };
        }

        // Evaluate overall status
        results.passed = await this.evaluateQualityGateResults(gate, results);
        results.overallStatus = results.passed ? 'passed' : 'failed';
        results.endTime = new Date();

        this.emit('quality-gate:executed', results);
        return results;
    }

    // Stakeholder Communication
    async generateProgressReport(stakeholderRole) {
        const progress = await this.trackBMADProgress();
        
        const report = {
            reportDate: new Date(),
            stakeholder: stakeholderRole,
            executiveSummary: this.generateExecutiveSummary(progress),
            currentPhase: {
                name: this.currentPhase,
                status: await this.getPhaseStatus(this.currentPhase),
                completionPercentage: await this.getPhaseCompletion(this.currentPhase),
                nextMilestone: await this.getNextMilestone(this.currentPhase)
            },
            sprintSummary: {
                currentSprint: this.currentSprint?.number || 0,
                velocity: progress.teamVelocity,
                burndown: progress.burndownData,
                completedStories: progress.completedStories.length,
                remainingStories: progress.totalStories - progress.completedStories.length
            },
            qualityMetrics: this.generateQualityMetrics(),
            riskAssessment: progress.riskAssessment,
            upcomingMilestones: await this.getUpcomingMilestones(),
            actionItems: await this.generateActionItems(stakeholderRole),
            recommendations: await this.generateRecommendations(progress)
        };

        this.emit('report:generated', { stakeholder: stakeholderRole, report });
        return report;
    }

    // Agent Coordination
    async coordinateAgents(workflow, userStory) {
        console.log(`🤝 Coordinating agents for workflow: ${workflow.id}`);
        
        const coordination = {
            workflowId: workflow.id,
            userStoryId: userStory.id,
            assignedAgents: [],
            tasks: [],
            dependencies: [],
            estimatedCompletion: new Date(),
            status: 'coordinating'
        };

        // Assign agents based on workflow requirements
        for (const agentId of workflow.agents) {
            const agent = this.agents.get(agentId);
            if (agent && agent.status === 'ready') {
                const task = await this.createAgentTask(agent, workflow, userStory);
                coordination.assignedAgents.push(agentId);
                coordination.tasks.push(task);
                
                // Update agent status
                agent.status = 'assigned';
                agent.currentTask = task.id;
                agent.workload += task.estimatedEffort;
            }
        }

        // Identify dependencies between tasks
        coordination.dependencies = await this.identifyTaskDependencies(coordination.tasks);
        
        // Calculate estimated completion
        coordination.estimatedCompletion = await this.calculateEstimatedCompletion(coordination.tasks, coordination.dependencies);
        
        coordination.status = 'coordinated';
        this.emit('agents:coordinated', coordination);
        
        return coordination;
    }

    // Utility Methods
    generateId(prefix) {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async calculateTeamCapacity() {
        const availableAgents = Array.from(this.agents.values()).filter(agent => agent.status === 'ready');
        return availableAgents.reduce((total, agent) => total + (agent.capacity || 8), 0);
    }

    async prioritizeUserStoriesForPhase(phase) {
        return Array.from(this.userStories.values())
            .filter(story => story.phase === phase)
            .sort((a, b) => b.priority - a.priority);
    }

    async selectStoriesForSprint(stories, capacity) {
        let selectedStories = [];
        let remainingCapacity = capacity;
        
        for (const story of stories) {
            if (story.storyPoints <= remainingCapacity) {
                selectedStories.push(story);
                remainingCapacity -= story.storyPoints;
            }
        }
        
        return selectedStories;
    }

    calculateOverallCompletion(progress) {
        const milestoneWeight = 0.3;
        const storyWeight = 0.4;
        const qualityWeight = 0.3;
        
        const milestoneCompletion = progress.completedMilestones.length / progress.totalMilestones;
        const storyCompletion = progress.completedStories.length / progress.totalStories;
        const qualityCompletion = progress.qualityGatesPassed.length / progress.totalQualityGates;
        
        return Math.round(
            (milestoneCompletion * milestoneWeight + 
             storyCompletion * storyWeight + 
             qualityCompletion * qualityWeight) * 100
        );
    }

    // API Methods for External Integration
    async getWorkflowStatus(workflowId) {
        const workflow = this.workflows.get(workflowId);
        if (!workflow) return null;
        
        return {
            ...workflow,
            status: await this.calculateWorkflowStatus(workflow),
            progress: await this.calculateWorkflowProgress(workflow),
            blockers: await this.getWorkflowBlockers(workflow),
            estimatedCompletion: await this.estimateWorkflowCompletion(workflow)
        };
    }

    async transitionToNextPhase() {
        const currentQualityGate = this.qualityGates.get(`${this.currentPhase}-validation`);
        const gateResults = await this.executeQualityGate(currentQualityGate.id);
        
        if (gateResults.passed) {
            const phases = Object.values(this.phases);
            const currentIndex = phases.indexOf(this.currentPhase);
            
            if (currentIndex < phases.length - 1) {
                this.currentPhase = phases[currentIndex + 1];
                this.emit('phase:transitioned', { from: phases[currentIndex], to: this.currentPhase });
                console.log(`🔄 Transitioned to phase: ${this.currentPhase}`);
            } else {
                this.emit('project:completed');
                console.log('🎉 Project completed successfully!');
            }
        } else {
            console.log(`❌ Cannot transition to next phase. Quality gate failed.`);
            this.emit('phase:transition-blocked', { phase: this.currentPhase, reasons: gateResults.blockers });
        }
    }

    // Start the BMAD workflow system
    async startBMADWorkflow(projectType = 'greenfield-fullstack') {
        console.log(`🚀 Starting BMAD workflow for ${projectType}...`);
        
        this.currentPhase = this.phases.BUSINESS_MODEL;
        
        // Initialize first sprint
        const firstSprint = await this.planSprint(1);
        
        // Create initial user stories for business model phase
        await this.createInitialUserStories();
        
        // Begin workflow coordination
        const businessModelWorkflow = this.workflows.get('business-model-analysis');
        await this.coordinateAgents(businessModelWorkflow, Array.from(this.userStories.values())[0]);
        
        this.emit('workflow:started', { projectType, phase: this.currentPhase, sprint: firstSprint });
        
        return {
            status: 'started',
            currentPhase: this.currentPhase,
            currentSprint: firstSprint,
            nextMilestone: await this.getNextMilestone(this.currentPhase)
        };
    }

    async createInitialUserStories() {
        // Business Model Analysis user stories
        await this.createUserStory({
            title: 'Define Value Proposition',
            description: 'As a product manager, I want to define the core value proposition so that we understand what unique value we provide to customers',
            asA: 'product manager',
            iWant: 'to define the core value proposition',
            soThat: 'we understand what unique value we provide to customers',
            priority: 'high',
            storyPoints: 8,
            phase: this.phases.BUSINESS_MODEL
        });

        await this.createUserStory({
            title: 'Conduct Market Research',
            description: 'As a business analyst, I want to conduct comprehensive market research so that we understand our target market and competition',
            asA: 'business analyst',
            iWant: 'to conduct comprehensive market research',
            soThat: 'we understand our target market and competition',
            priority: 'high',
            storyPoints: 13,
            phase: this.phases.BUSINESS_MODEL
        });

        await this.createUserStory({
            title: 'Design Revenue Model',
            description: 'As a CEO, I want to design a sustainable revenue model so that the business can generate profit',
            asA: 'CEO',
            iWant: 'to design a sustainable revenue model',
            soThat: 'the business can generate profit',
            priority: 'high',
            storyPoints: 8,
            phase: this.phases.BUSINESS_MODEL
        });
    }
}

module.exports = BMADWorkflowSystem;