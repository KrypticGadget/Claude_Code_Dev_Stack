/**
 * BMAD Orchestrator - Main coordination system
 * Integrates all BMAD workflow components and provides unified API
 */

const { EventEmitter } = require('events');
const BMADWorkflowSystem = require('./bmad-workflow-system');
const AgileIntegration = require('./agile-integration');
const UserStoryManagement = require('./user-story-management');
const ProgressTracking = require('./progress-tracking');
const StakeholderCommunication = require('./stakeholder-communication');

class BMADOrchestrator extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            workingDirectory: config.workingDirectory || process.cwd(),
            projectType: config.projectType || 'greenfield-fullstack',
            teamSize: config.teamSize || 8,
            industryType: config.industryType || 'technology',
            complianceRequirements: config.complianceRequirements || [],
            remoteTeam: config.remoteTeam || true,
            ...config
        };
        
        this.status = 'initializing';
        this.components = new Map();
        this.integrationPoints = new Map();
        this.eventHandlers = new Map();
        
        this.initializeOrchestrator();
    }

    async initializeOrchestrator() {
        try {
            console.log('🎭 Initializing BMAD Orchestrator...');
            
            // Initialize core BMAD workflow system
            this.bmadWorkflowSystem = new BMADWorkflowSystem(this.config);
            this.components.set('workflow', this.bmadWorkflowSystem);
            
            // Initialize supporting systems
            this.agileIntegration = new AgileIntegration(this.bmadWorkflowSystem);
            this.components.set('agile', this.agileIntegration);
            
            this.userStoryManagement = new UserStoryManagement(this.bmadWorkflowSystem);
            this.components.set('stories', this.userStoryManagement);
            
            this.progressTracking = new ProgressTracking(this.bmadWorkflowSystem);
            this.components.set('progress', this.progressTracking);
            
            this.stakeholderCommunication = new StakeholderCommunication(this.bmadWorkflowSystem);
            this.components.set('communication', this.stakeholderCommunication);
            
            // Attach progress tracking to BMAD system
            this.bmadWorkflowSystem.progressTracking = this.progressTracking;
            
            // Setup cross-component integration
            await this.setupIntegrationPoints();
            
            // Setup event routing
            this.setupEventRouting();
            
            // Initialize dashboards and monitoring
            await this.initializeDashboards();
            
            this.status = 'ready';
            console.log('✅ BMAD Orchestrator initialized successfully');
            this.emit('orchestrator:ready');
            
        } catch (error) {
            this.status = 'error';
            console.error('❌ Failed to initialize BMAD Orchestrator:', error);
            this.emit('orchestrator:error', error);
        }
    }

    async setupIntegrationPoints() {
        // Sprint Planning Integration
        this.integrationPoints.set('sprint-planning', {
            description: 'Integrate sprint planning with BMAD workflows',
            components: ['workflow', 'agile', 'stories', 'progress'],
            handler: async (sprintNumber) => {
                // Coordinate sprint planning across all components
                const currentPhase = this.bmadWorkflowSystem.currentPhase;
                const phaseWorkflows = Array.from(this.bmadWorkflowSystem.workflows.values())
                    .filter(w => w.phase === currentPhase);
                
                // Plan sprint with BMAD context
                const sprint = await this.agileIntegration.conductSprintPlanning(sprintNumber);
                
                // Generate phase-appropriate user stories
                await this.generatePhaseUserStories(currentPhase, sprint);
                
                // Update progress tracking
                await this.progressTracking.trackMilestoneProgress(`${currentPhase}-milestone`);
                
                // Communicate to stakeholders
                const plan = this.stakeholderCommunication.communicationPlans.get(`${currentPhase}_phase`);
                if (plan) {
                    for (const stakeholderId of plan.stakeholders) {
                        await this.stakeholderCommunication.sendNotification('sprint_planned', {
                            sprintNumber,
                            phase: currentPhase,
                            stakeholderId
                        });
                    }
                }
                
                return sprint;
            }
        });

        // Quality Gate Integration
        this.integrationPoints.set('quality-gate-execution', {
            description: 'Execute quality gates with stakeholder approval',
            components: ['workflow', 'progress', 'communication'],
            handler: async (gateId) => {
                // Execute quality gate
                const gateResults = await this.bmadWorkflowSystem.executeQualityGate(gateId);
                
                // Update progress
                await this.progressTracking.trackMilestoneProgress(gateId);
                
                // Notify stakeholders of results
                if (gateResults.passed) {
                    await this.stakeholderCommunication.sendNotification('quality_gate_passed', {
                        gateId,
                        results: gateResults
                    });
                } else {
                    await this.stakeholderCommunication.sendNotification('quality_gate_failure', {
                        gateId,
                        results: gateResults
                    });
                }
                
                // Request approvals if needed
                if (gateResults.passed && this.requiresStakeholderApproval(gateId)) {
                    await this.requestQualityGateApproval(gateId, gateResults);
                }
                
                return gateResults;
            }
        });

        // Phase Transition Integration
        this.integrationPoints.set('phase-transition', {
            description: 'Coordinate phase transitions across all systems',
            components: ['workflow', 'agile', 'stories', 'progress', 'communication'],
            handler: async (fromPhase, toPhase) => {
                console.log(`🔄 Orchestrating phase transition: ${fromPhase} → ${toPhase}`);
                
                // Validate transition readiness
                const readiness = await this.validatePhaseTransitionReadiness(fromPhase, toPhase);
                if (!readiness.ready) {
                    throw new Error(`Phase transition not ready: ${readiness.blockers.join(', ')}`);
                }
                
                // Execute transition
                await this.bmadWorkflowSystem.transitionToNextPhase();
                
                // Update agile boards for new phase
                await this.agileIntegration.setupPhaseKanbanColumns(toPhase);
                
                // Generate user stories for new phase
                await this.generatePhaseUserStories(toPhase);
                
                // Update progress tracking
                await this.progressTracking.trackBMADPhaseProgress();
                
                // Communicate transition to stakeholders
                const communicationPlan = this.stakeholderCommunication.communicationPlans.get(`${toPhase}_phase`);
                if (communicationPlan) {
                    for (const stakeholderId of communicationPlan.stakeholders) {
                        await this.stakeholderCommunication.generateStakeholderReport(stakeholderId);
                    }
                }
                
                this.emit('phase:transitioned', { fromPhase, toPhase });
                return { success: true, newPhase: toPhase };
            }
        });

        // Stakeholder Feedback Integration
        this.integrationPoints.set('stakeholder-feedback', {
            description: 'Integrate stakeholder feedback into workflow planning',
            components: ['communication', 'stories', 'workflow'],
            handler: async (feedback) => {
                // Analyze feedback impact
                const impact = await this.analyzeStakeholderFeedbackImpact(feedback);
                
                // Generate user stories from feedback
                if (impact.requiresNewStories) {
                    for (const storyRequirement of impact.storyRequirements) {
                        await this.userStoryManagement.createStoryFromTemplate(
                            storyRequirement.template,
                            storyRequirement.customizations
                        );
                    }
                }
                
                // Update workflow priorities
                if (impact.requiresPriorityChanges) {
                    await this.updateWorkflowPriorities(impact.priorityChanges);
                }
                
                // Schedule stakeholder follow-up
                if (impact.requiresFollowUp) {
                    await this.stakeholderCommunication.scheduleMeeting(
                        'feedback_followup',
                        [feedback.stakeholderId],
                        impact.followUpAgenda,
                        impact.suggestedDate
                    );
                }
                
                return impact;
            }
        });
    }

    setupEventRouting() {
        // Route events between components
        this.bmadWorkflowSystem.on('phase:transitioned', async (data) => {
            await this.handleIntegrationPoint('phase-transition', data.from, data.to);
        });

        this.agileIntegration.on('sprint-planning:completed', async (planning) => {
            await this.progressTracking.trackMilestoneProgress('sprint-planning-complete');
        });

        this.userStoryManagement.on('story:created', async (story) => {
            // Auto-assign to appropriate workflow
            const workflow = await this.bmadWorkflowSystem.determineWorkflowForStory(story);
            story.workflow = workflow;
            
            // Update progress tracking
            await this.progressTracking.trackWorkflowProgress(workflow);
        });

        this.progressTracking.on('milestone:progress-updated', async (data) => {
            // Notify stakeholders of milestone progress
            if (data.progress.overallProgress % 25 === 0) { // Notify at 25% intervals
                const communicationPlan = this.stakeholderCommunication.communicationPlans.get(`${data.milestone.phase}_phase`);
                if (communicationPlan) {
                    for (const stakeholderId of communicationPlan.stakeholders) {
                        await this.stakeholderCommunication.sendNotification('milestone_progress', {
                            milestone: data.milestone,
                            progress: data.progress,
                            stakeholderId
                        });
                    }
                }
            }
        });

        this.stakeholderCommunication.on('approval:processed', async (approval) => {
            if (approval.status === 'approved') {
                // Continue workflow progression
                await this.handleApprovalApproved(approval);
            } else if (approval.status === 'rejected') {
                // Handle approval rejection
                await this.handleApprovalRejected(approval);
            }
        });
    }

    async initializeDashboards() {
        this.dashboards = {
            executive: await this.createExecutiveDashboard(),
            project_manager: await this.createProjectManagerDashboard(),
            development_team: await this.createDevelopmentTeamDashboard(),
            bmad_coordinator: await this.createBMADCoordinatorDashboard()
        };

        console.log('📊 Dashboards initialized');
    }

    // Main Orchestration Methods
    async startProject(projectConfig = {}) {
        console.log('🚀 Starting BMAD project...');
        
        const project = {
            id: this.generateProjectId(),
            name: projectConfig.name || 'BMAD Project',
            type: projectConfig.type || this.config.projectType,
            startDate: new Date(),
            config: { ...this.config, ...projectConfig },
            status: 'started'
        };

        // Initialize project-specific configurations
        await this.configureProjectSettings(project);
        
        // Start BMAD workflow
        const workflowResult = await this.bmadWorkflowSystem.startBMADWorkflow(project.type);
        
        // Plan first sprint
        const firstSprint = await this.handleIntegrationPoint('sprint-planning', 1);
        
        // Generate initial stakeholder reports
        await this.generateInitialStakeholderReports();
        
        // Setup monitoring and alerts
        await this.setupProjectMonitoring(project);
        
        this.emit('project:started', { project, workflow: workflowResult, sprint: firstSprint });
        
        return {
            project,
            status: 'started',
            currentPhase: this.bmadWorkflowSystem.currentPhase,
            firstSprint,
            nextMilestone: workflowResult.nextMilestone
        };
    }

    async executeWorkflowStep(stepId, context = {}) {
        console.log(`⚡ Executing workflow step: ${stepId}`);
        
        const step = {
            id: stepId,
            startTime: new Date(),
            context,
            status: 'executing'
        };

        try {
            // Determine which integration point to use
            const integrationPoint = this.determineIntegrationPoint(stepId);
            
            if (integrationPoint) {
                step.result = await this.handleIntegrationPoint(integrationPoint, ...Object.values(context));
            } else {
                // Direct workflow execution
                step.result = await this.bmadWorkflowSystem.executeWorkflowStep(stepId, context);
            }
            
            step.status = 'completed';
            step.endTime = new Date();
            step.duration = step.endTime - step.startTime;
            
            this.emit('workflow:step-completed', step);
            
        } catch (error) {
            step.status = 'failed';
            step.error = error.message;
            step.endTime = new Date();
            
            console.error(`❌ Workflow step failed: ${stepId}`, error);
            this.emit('workflow:step-failed', step);
            
            throw error;
        }
        
        return step;
    }

    async handleIntegrationPoint(pointId, ...args) {
        const integrationPoint = this.integrationPoints.get(pointId);
        if (!integrationPoint) {
            throw new Error(`Integration point ${pointId} not found`);
        }

        console.log(`🔗 Handling integration point: ${pointId}`);
        
        try {
            const result = await integrationPoint.handler(...args);
            this.emit('integration:success', { pointId, result });
            return result;
        } catch (error) {
            console.error(`❌ Integration point failed: ${pointId}`, error);
            this.emit('integration:failed', { pointId, error });
            throw error;
        }
    }

    // Project Management Methods
    async generatePhaseUserStories(phase, sprint = null) {
        const phaseTemplates = this.getPhaseStoryTemplates(phase);
        const stories = [];
        
        for (const template of phaseTemplates) {
            const customizations = {
                phase: phase,
                sprint: sprint?.number || null,
                createdBy: 'bmad-orchestrator'
            };
            
            const story = await this.userStoryManagement.createStoryFromTemplate(template.id, customizations);
            stories.push(story);
        }
        
        return stories;
    }

    getPhaseStoryTemplates(phase) {
        const phaseTemplateMap = {
            'business_model': [
                'business-model-canvas',
                'market-research',
                'revenue-model-validation'
            ],
            'architecture': [
                'system-architecture',
                'database-design',
                'technology-stack-selection'
            ],
            'design': [
                'user-experience-design',
                'visual-design',
                'design-system-creation'
            ],
            'development': [
                'feature-implementation',
                'api-development',
                'testing-implementation'
            ]
        };

        const templateIds = phaseTemplateMap[phase] || [];
        return templateIds.map(id => ({ id, phase }));
    }

    async validatePhaseTransitionReadiness(fromPhase, toPhase) {
        const readiness = {
            ready: true,
            blockers: [],
            warnings: [],
            requirements: []
        };

        // Check milestone completion
        const phaseMilestones = Array.from(this.progressTracking.milestones.values())
            .filter(m => m.phase === fromPhase);
        
        for (const milestone of phaseMilestones) {
            if (milestone.status !== 'completed') {
                readiness.ready = false;
                readiness.blockers.push(`Milestone not completed: ${milestone.name}`);
            }
        }

        // Check quality gates
        const phaseQualityGates = Array.from(this.bmadWorkflowSystem.qualityGates.values())
            .filter(qg => qg.phase === fromPhase);
        
        for (const gate of phaseQualityGates) {
            if (gate.status !== 'passed') {
                readiness.ready = false;
                readiness.blockers.push(`Quality gate not passed: ${gate.id}`);
            }
        }

        // Check pending approvals
        const pendingApprovals = Array.from(this.stakeholderCommunication.approvals.values())
            .filter(a => a.status === 'pending' && a.context.phase === fromPhase);
        
        if (pendingApprovals.length > 0) {
            readiness.ready = false;
            readiness.blockers.push(`Pending approvals: ${pendingApprovals.length}`);
        }

        // Check user story completion
        const phaseStories = Array.from(this.bmadWorkflowSystem.userStories.values())
            .filter(s => s.phase === fromPhase);
        
        const incompleteStories = phaseStories.filter(s => s.status !== 'done');
        if (incompleteStories.length > 0) {
            readiness.warnings.push(`Incomplete stories: ${incompleteStories.length}`);
        }

        return readiness;
    }

    // Dashboard Creation Methods
    async createExecutiveDashboard() {
        return {
            id: 'executive-dashboard',
            name: 'Executive Dashboard',
            widgets: [
                {
                    type: 'project-health',
                    size: 'large',
                    data_source: () => this.progressTracking.calculateKPIs()
                },
                {
                    type: 'phase-progress',
                    size: 'medium',
                    data_source: () => this.progressTracking.trackBMADPhaseProgress()
                },
                {
                    type: 'milestone-timeline',
                    size: 'large',
                    data_source: () => this.progressTracking.getMilestonesSummary()
                },
                {
                    type: 'budget-status',
                    size: 'small',
                    data_source: () => this.getProjectBudgetStatus()
                },
                {
                    type: 'risk-summary',
                    size: 'medium',
                    data_source: () => this.getProjectRiskSummary()
                },
                {
                    type: 'stakeholder-satisfaction',
                    size: 'small',
                    data_source: () => this.stakeholderCommunication.getCommunicationMetrics()
                }
            ],
            refresh_rate: 'hourly',
            access_roles: ['ceo', 'cto', 'finance_director']
        };
    }

    async createProjectManagerDashboard() {
        return {
            id: 'project-manager-dashboard',
            name: 'Project Manager Dashboard',
            widgets: [
                {
                    type: 'sprint-board',
                    size: 'large',
                    data_source: () => this.agileIntegration.getKanbanFlowMetrics()
                },
                {
                    type: 'velocity-chart',
                    size: 'medium',
                    data_source: () => this.agileIntegration.getAgileMetrics().velocity
                },
                {
                    type: 'team-capacity',
                    size: 'small',
                    data_source: () => this.bmadWorkflowSystem.calculateTeamCapacity()
                },
                {
                    type: 'impediments',
                    size: 'medium',
                    data_source: () => this.getActiveImpediments()
                },
                {
                    type: 'upcoming-deadlines',
                    size: 'medium',
                    data_source: () => this.progressTracking.getUpcomingDeadlines()
                }
            ],
            refresh_rate: 'real_time',
            access_roles: ['project_manager', 'scrum_master']
        };
    }

    async createDevelopmentTeamDashboard() {
        return {
            id: 'development-team-dashboard',
            name: 'Development Team Dashboard',
            widgets: [
                {
                    type: 'current-sprint',
                    size: 'large',
                    data_source: () => this.getCurrentSprintData()
                },
                {
                    type: 'agent-assignments',
                    size: 'medium',
                    data_source: () => this.getAgentAssignments()
                },
                {
                    type: 'quality-metrics',
                    size: 'small',
                    data_source: () => this.progressTracking.getQualityMetrics()
                },
                {
                    type: 'technical-debt',
                    size: 'small',
                    data_source: () => this.getTechnicalDebtMetrics()
                },
                {
                    type: 'workflow-status',
                    size: 'medium',
                    data_source: () => this.getWorkflowStatusSummary()
                }
            ],
            refresh_rate: 'real_time',
            access_roles: ['development_team', 'technical_lead']
        };
    }

    async createBMADCoordinatorDashboard() {
        return {
            id: 'bmad-coordinator-dashboard',
            name: 'BMAD Coordinator Dashboard',
            widgets: [
                {
                    type: 'bmad-phase-flow',
                    size: 'large',
                    data_source: () => this.getBMADPhaseFlow()
                },
                {
                    type: 'workflow-efficiency',
                    size: 'medium',
                    data_source: () => this.progressTracking.calculateKPI('workflow-efficiency')
                },
                {
                    type: 'deliverable-tracking',
                    size: 'medium',
                    data_source: () => this.getDeliverableTracking()
                },
                {
                    type: 'quality-gates',
                    size: 'small',
                    data_source: () => this.getQualityGateStatus()
                },
                {
                    type: 'stakeholder-alignment',
                    size: 'medium',
                    data_source: () => this.getStakeholderAlignment()
                }
            ],
            refresh_rate: 'hourly',
            access_roles: ['bmad_coordinator', 'workflow_manager']
        };
    }

    // API Methods
    getOrchestrationStatus() {
        return {
            status: this.status,
            components: Array.from(this.components.keys()).map(key => ({
                name: key,
                status: this.components.get(key).status || 'unknown'
            })),
            currentPhase: this.bmadWorkflowSystem?.currentPhase,
            activeSprint: this.bmadWorkflowSystem?.currentSprint?.number,
            projectHealth: this.getProjectHealthSummary(),
            lastUpdate: new Date()
        };
    }

    async getComprehensiveProjectStatus() {
        return {
            project: this.getProjectSummary(),
            bmad: await this.progressTracking.trackBMADPhaseProgress(),
            agile: this.agileIntegration.getAgileMetrics(),
            stories: this.userStoryManagement.getStoryMetrics(),
            progress: this.progressTracking.getProgressSummary(),
            communication: this.stakeholderCommunication.getCommunicationMetrics(),
            dashboards: Object.keys(this.dashboards),
            integrationPoints: Array.from(this.integrationPoints.keys()),
            timestamp: new Date()
        };
    }

    // Utility Methods
    generateProjectId() {
        return `BMAD-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    determineIntegrationPoint(stepId) {
        const stepIntegrationMap = {
            'plan-sprint': 'sprint-planning',
            'execute-quality-gate': 'quality-gate-execution',
            'transition-phase': 'phase-transition',
            'process-feedback': 'stakeholder-feedback'
        };

        return stepIntegrationMap[stepId];
    }

    getProjectHealthSummary() {
        if (!this.progressTracking) return 'unknown';
        
        try {
            const kpis = this.progressTracking.getKPIsSummary();
            const projectHealth = kpis.find(kpi => kpi.id === 'project-health');
            return projectHealth ? projectHealth.performance : 'unknown';
        } catch (error) {
            return 'error';
        }
    }

    // Event handling for component coordination
    async handleApprovalApproved(approval) {
        switch (approval.type) {
            case 'business_model':
                await this.handleIntegrationPoint('phase-transition', 'business_model', 'architecture');
                break;
            case 'architecture_design':
                await this.handleIntegrationPoint('phase-transition', 'architecture', 'design');
                break;
            case 'design_system':
                await this.handleIntegrationPoint('phase-transition', 'design', 'development');
                break;
            default:
                console.log(`Approval approved: ${approval.type}`);
        }
    }

    async handleApprovalRejected(approval) {
        // Create corrective user stories
        const correctionStory = await this.userStoryManagement.createStoryFromTemplate('correction-required', {
            approvalType: approval.type,
            rejectionComments: approval.comments,
            priority: 'high'
        });

        // Notify relevant stakeholders
        await this.stakeholderCommunication.sendNotification('approval_rejected', {
            approval,
            correctionStory
        });
    }
}

module.exports = BMADOrchestrator;