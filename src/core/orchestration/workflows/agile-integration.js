/**
 * Agile Integration System for BMAD Workflows
 * Integrates Scrum, Kanban, and agile best practices with BMAD methodology
 */

const { EventEmitter } = require('events');

class AgileIntegration extends EventEmitter {
    constructor(bmadSystem) {
        super();
        this.bmadSystem = bmadSystem;
        this.scrumEvents = new Map();
        this.kanbanBoard = new Map();
        this.retrospectives = [];
        this.burndownCharts = new Map();
        this.velocityHistory = [];
        this.impediments = [];
        
        this.initializeAgileFramework();
    }

    initializeAgileFramework() {
        this.setupScrumEvents();
        this.setupKanbanBoard();
        this.initializeMetrics();
        console.log('🔄 Agile integration framework initialized');
    }

    setupScrumEvents() {
        // Sprint Planning
        this.scrumEvents.set('sprint-planning', {
            frequency: 'sprint-start',
            duration: '4-8 hours',
            participants: ['product-owner', 'scrum-master', 'development-team'],
            artifacts: ['product-backlog', 'sprint-backlog', 'sprint-goal'],
            bmadIntegration: {
                phaseAlignment: true,
                workflowCoordination: true,
                qualityGatePlanning: true
            }
        });

        // Daily Standups
        this.scrumEvents.set('daily-standup', {
            frequency: 'daily',
            duration: '15 minutes',
            participants: ['development-team', 'scrum-master'],
            artifacts: ['sprint-backlog-updates', 'impediment-log'],
            bmadIntegration: {
                phaseProgressTracking: true,
                agentCoordination: true,
                workflowStatusUpdates: true
            }
        });

        // Sprint Review
        this.scrumEvents.set('sprint-review', {
            frequency: 'sprint-end',
            duration: '2-4 hours',
            participants: ['product-owner', 'stakeholders', 'development-team'],
            artifacts: ['potentially-shippable-increment', 'updated-product-backlog'],
            bmadIntegration: {
                phaseDeliverableReview: true,
                stakeholderFeedback: true,
                qualityGateValidation: true
            }
        });

        // Sprint Retrospective
        this.scrumEvents.set('sprint-retrospective', {
            frequency: 'sprint-end',
            duration: '1-3 hours',
            participants: ['development-team', 'scrum-master'],
            artifacts: ['improvement-actions', 'team-agreements'],
            bmadIntegration: {
                workflowOptimization: true,
                agentPerformanceReview: true,
                processImprovement: true
            }
        });

        // Backlog Refinement
        this.scrumEvents.set('backlog-refinement', {
            frequency: 'ongoing',
            duration: '1-2 hours per week',
            participants: ['product-owner', 'development-team'],
            artifacts: ['refined-user-stories', 'acceptance-criteria', 'estimates'],
            bmadIntegration: {
                workflowStoryMapping: true,
                phaseRequirements: true,
                agentTaskPlanning: true
            }
        });
    }

    setupKanbanBoard() {
        const columns = [
            { id: 'backlog', name: 'Backlog', wipLimit: null },
            { id: 'bmad-analysis', name: 'BMAD Analysis', wipLimit: 3 },
            { id: 'in-progress', name: 'In Progress', wipLimit: 5 },
            { id: 'review', name: 'Review', wipLimit: 3 },
            { id: 'quality-gate', name: 'Quality Gate', wipLimit: 2 },
            { id: 'done', name: 'Done', wipLimit: null }
        ];

        columns.forEach(column => {
            this.kanbanBoard.set(column.id, {
                ...column,
                items: [],
                policies: this.getColumnPolicies(column.id)
            });
        });
    }

    getColumnPolicies(columnId) {
        const policies = {
            'backlog': {
                entryRules: ['user-story-written', 'acceptance-criteria-defined'],
                exitRules: ['priority-assigned', 'estimate-provided']
            },
            'bmad-analysis': {
                entryRules: ['backlog-exit-criteria-met', 'bmad-workflow-identified'],
                exitRules: ['bmad-analysis-complete', 'agent-assigned']
            },
            'in-progress': {
                entryRules: ['agent-assigned', 'dependencies-resolved'],
                exitRules: ['work-completed', 'peer-review-requested']
            },
            'review': {
                entryRules: ['work-completed', 'self-testing-passed'],
                exitRules: ['review-approved', 'quality-checks-passed']
            },
            'quality-gate': {
                entryRules: ['review-approved', 'automated-tests-passed'],
                exitRules: ['quality-gate-passed', 'stakeholder-approved']
            },
            'done': {
                entryRules: ['quality-gate-passed', 'acceptance-criteria-met'],
                exitRules: ['retrospective-complete']
            }
        };

        return policies[columnId] || {};
    }

    initializeMetrics() {
        // Velocity tracking
        this.velocityMetrics = {
            targetVelocity: 40,
            currentVelocity: 0,
            historicalVelocity: [],
            trend: 'stable'
        };

        // Cycle time tracking
        this.cycleTimeMetrics = {
            targetCycleTime: 5, // days
            currentCycleTime: 0,
            historicalCycleTime: [],
            bottlenecks: []
        };

        // Quality metrics
        this.qualityMetrics = {
            defectRate: 0,
            targetDefectRate: 2, // percentage
            escapedDefects: 0,
            qualityGatePassRate: 0
        };
    }

    // Sprint Planning with BMAD Integration
    async conductSprintPlanning(sprintNumber) {
        console.log(`📋 Conducting Sprint Planning for Sprint ${sprintNumber}...`);

        const planning = {
            sprintNumber,
            startTime: new Date(),
            duration: 0,
            participants: [],
            agenda: [
                'Review previous sprint',
                'Assess current BMAD phase',
                'Review product backlog',
                'Select user stories for sprint',
                'Map stories to BMAD workflows',
                'Assign agents and tasks',
                'Define sprint goal',
                'Plan quality gates',
                'Estimate capacity'
            ],
            outcomes: {}
        };

        // Phase 1: Sprint Planning Part 1 (What)
        planning.outcomes.phase1 = await this.sprintPlanningPhase1(sprintNumber);

        // Phase 2: Sprint Planning Part 2 (How)
        planning.outcomes.phase2 = await this.sprintPlanningPhase2(planning.outcomes.phase1);

        planning.endTime = new Date();
        planning.duration = planning.endTime - planning.startTime;

        this.emit('sprint-planning:completed', planning);
        return planning;
    }

    async sprintPlanningPhase1(sprintNumber) {
        // What will be delivered?
        const currentPhase = this.bmadSystem.currentPhase;
        const availableStories = await this.bmadSystem.prioritizeUserStoriesForPhase(currentPhase);
        const teamCapacity = await this.bmadSystem.calculateTeamCapacity();
        
        const phase1Results = {
            selectedStories: await this.bmadSystem.selectStoriesForSprint(availableStories, teamCapacity),
            sprintGoal: await this.generateSprintGoal(currentPhase, availableStories),
            capacityPlanning: {
                totalCapacity: teamCapacity,
                commitmentLevel: 0.8, // Leave 20% buffer
                adjustedCapacity: teamCapacity * 0.8
            },
            bmadAlignment: {
                primaryPhase: currentPhase,
                supportingPhases: await this.identifySupportingPhases(currentPhase),
                qualityGates: await this.identifyRequiredQualityGates(currentPhase)
            }
        };

        return phase1Results;
    }

    async sprintPlanningPhase2(phase1Results) {
        // How will the work get done?
        const phase2Results = {
            taskBreakdown: {},
            agentAssignments: {},
            dependencies: [],
            risks: [],
            definitionOfDone: await this.getDefinitionOfDone(),
            bmadWorkflowMapping: {}
        };

        // Break down each story into tasks
        for (const story of phase1Results.selectedStories) {
            const tasks = await this.breakdownStoryIntoTasks(story);
            phase2Results.taskBreakdown[story.id] = tasks;

            // Map to BMAD workflows
            const workflow = await this.bmadSystem.determineWorkflowForStory(story);
            phase2Results.bmadWorkflowMapping[story.id] = workflow;

            // Assign agents
            const agentAssignment = await this.bmadSystem.coordinateAgents(
                this.bmadSystem.workflows.get(workflow), 
                story
            );
            phase2Results.agentAssignments[story.id] = agentAssignment;
        }

        // Identify cross-story dependencies
        phase2Results.dependencies = await this.identifySprintDependencies(phase2Results.taskBreakdown);

        // Assess risks
        phase2Results.risks = await this.assessSprintRisks(phase1Results, phase2Results);

        return phase2Results;
    }

    // Daily Standup with BMAD Progress Tracking
    async conductDailyStandup() {
        const standup = {
            date: new Date(),
            participants: await this.getStandupParticipants(),
            updates: {},
            impediments: [],
            bmadProgress: {},
            actionItems: []
        };

        // Collect updates from each agent
        for (const [agentId, agent] of this.bmadSystem.agents) {
            if (agent.status === 'assigned' || agent.status === 'in-progress') {
                standup.updates[agentId] = await this.collectAgentUpdate(agent);
            }
        }

        // Track BMAD phase progress
        standup.bmadProgress = await this.bmadSystem.trackBMADProgress();

        // Identify new impediments
        standup.impediments = await this.identifyImpediments();

        // Generate action items
        standup.actionItems = await this.generateStandupActionItems(standup);

        this.emit('daily-standup:completed', standup);
        return standup;
    }

    async collectAgentUpdate(agent) {
        return {
            agentId: agent.id,
            yesterday: await this.getAgentYesterdayWork(agent),
            today: await this.getAgentTodayPlans(agent),
            blockers: await this.getAgentBlockers(agent),
            bmadContribution: await this.getAgentBMADContribution(agent),
            estimatedCompletion: await this.getAgentTaskCompletion(agent)
        };
    }

    // Sprint Review with BMAD Deliverable Assessment
    async conductSprintReview(sprintNumber) {
        console.log(`🔍 Conducting Sprint Review for Sprint ${sprintNumber}...`);

        const review = {
            sprintNumber,
            date: new Date(),
            participants: await this.getReviewParticipants(),
            agenda: [
                'Sprint goal assessment',
                'Completed user stories demonstration',
                'BMAD deliverable review',
                'Quality gate status',
                'Stakeholder feedback',
                'Product backlog updates',
                'Next sprint planning'
            ],
            outcomes: {}
        };

        // Assess sprint goal achievement
        review.outcomes.goalAchievement = await this.assessSprintGoalAchievement(sprintNumber);

        // Review completed stories
        review.outcomes.completedStories = await this.getCompletedStories(sprintNumber);

        // BMAD deliverable assessment
        review.outcomes.bmadDeliverables = await this.assessBMADDeliverables();

        // Quality gate status
        review.outcomes.qualityGates = await this.getQualityGateStatus();

        // Collect stakeholder feedback
        review.outcomes.stakeholderFeedback = await this.collectStakeholderFeedback();

        // Update product backlog
        review.outcomes.backlogUpdates = await this.updateProductBacklog(review.outcomes);

        this.emit('sprint-review:completed', review);
        return review;
    }

    // Sprint Retrospective with Process Improvement
    async conductSprintRetrospective(sprintNumber) {
        console.log(`🔄 Conducting Sprint Retrospective for Sprint ${sprintNumber}...`);

        const retrospective = {
            sprintNumber,
            date: new Date(),
            participants: await this.getRetrospectiveParticipants(),
            format: 'start-stop-continue',
            outcomes: {
                whatWentWell: [],
                whatCouldImprove: [],
                actionItems: [],
                bmadProcessImprovements: [],
                agentPerformanceInsights: []
            }
        };

        // Collect team feedback
        retrospective.outcomes.whatWentWell = await this.collectPositiveFeedback();
        retrospective.outcomes.whatCouldImprove = await this.collectImprovementAreas();

        // BMAD-specific retrospective items
        retrospective.outcomes.bmadProcessImprovements = await this.identifyBMADProcessImprovements();

        // Agent performance insights
        retrospective.outcomes.agentPerformanceInsights = await this.analyzeAgentPerformance();

        // Generate action items
        retrospective.outcomes.actionItems = await this.generateRetrospectiveActions(retrospective.outcomes);

        // Update team agreements
        await this.updateTeamAgreements(retrospective.outcomes.actionItems);

        this.retrospectives.push(retrospective);
        this.emit('sprint-retrospective:completed', retrospective);
        
        return retrospective;
    }

    // Kanban Flow Management
    async moveItem(itemId, fromColumn, toColumn) {
        const fromCol = this.kanbanBoard.get(fromColumn);
        const toCol = this.kanbanBoard.get(toColumn);

        if (!fromCol || !toCol) {
            throw new Error(`Invalid column transition: ${fromColumn} -> ${toColumn}`);
        }

        // Check WIP limits
        if (toCol.wipLimit && toCol.items.length >= toCol.wipLimit) {
            throw new Error(`WIP limit exceeded for column: ${toColumn}`);
        }

        // Validate transition rules
        await this.validateTransitionRules(itemId, fromColumn, toColumn);

        // Move item
        const itemIndex = fromCol.items.findIndex(item => item.id === itemId);
        if (itemIndex === -1) {
            throw new Error(`Item ${itemId} not found in column ${fromColumn}`);
        }

        const item = fromCol.items.splice(itemIndex, 1)[0];
        item.movedAt = new Date();
        item.previousColumn = fromColumn;
        toCol.items.push(item);

        // Update cycle time
        await this.updateCycleTime(item, toColumn);

        // Trigger events
        this.emit('kanban:item-moved', { item, fromColumn, toColumn });

        return { success: true, item, newPosition: toCol.items.length - 1 };
    }

    async validateTransitionRules(itemId, fromColumn, toColumn) {
        const toCol = this.kanbanBoard.get(toColumn);
        const policies = toCol.policies;

        if (!policies || !policies.entryRules) {
            return true; // No specific rules
        }

        // Check each entry rule
        for (const rule of policies.entryRules) {
            const isValid = await this.checkRule(itemId, rule);
            if (!isValid) {
                throw new Error(`Entry rule failed for ${toColumn}: ${rule}`);
            }
        }

        return true;
    }

    // Metrics and Analytics
    calculateVelocity(sprintNumber) {
        const completedStories = Array.from(this.bmadSystem.userStories.values())
            .filter(story => story.sprint === sprintNumber && story.status === 'done');
        
        const velocity = completedStories.reduce((total, story) => total + story.storyPoints, 0);
        
        this.velocityHistory.push({
            sprint: sprintNumber,
            velocity: velocity,
            date: new Date()
        });

        // Update current velocity
        this.velocityMetrics.currentVelocity = velocity;
        this.velocityMetrics.historicalVelocity = this.velocityHistory.slice(-6); // Last 6 sprints
        this.velocityMetrics.trend = this.calculateVelocityTrend();

        return velocity;
    }

    calculateCycleTime(item) {
        if (!item.startDate || !item.completionDate) {
            return null;
        }

        const cycleTime = (item.completionDate - item.startDate) / (1000 * 60 * 60 * 24); // days
        
        this.cycleTimeMetrics.historicalCycleTime.push({
            itemId: item.id,
            cycleTime: cycleTime,
            date: new Date()
        });

        // Update current cycle time (average of last 10 items)
        const recentCycleTimes = this.cycleTimeMetrics.historicalCycleTime.slice(-10);
        this.cycleTimeMetrics.currentCycleTime = recentCycleTimes.reduce((sum, ct) => sum + ct.cycleTime, 0) / recentCycleTimes.length;

        return cycleTime;
    }

    generateBurndownChart(sprintNumber) {
        const sprint = this.bmadSystem.currentSprint;
        if (!sprint || sprint.number !== sprintNumber) {
            return null;
        }

        const totalStoryPoints = sprint.userStories.reduce((total, story) => total + story.storyPoints, 0);
        const sprintDays = sprint.duration;
        
        const idealBurndown = [];
        const actualBurndown = [];

        // Generate ideal burndown
        for (let day = 0; day <= sprintDays; day++) {
            idealBurndown.push({
                day: day,
                remaining: totalStoryPoints - (totalStoryPoints * day / sprintDays)
            });
        }

        // Calculate actual burndown (would be updated daily)
        const completedStoryPoints = sprint.userStories
            .filter(story => story.status === 'done')
            .reduce((total, story) => total + story.storyPoints, 0);

        actualBurndown.push({
            day: this.getCurrentSprintDay(sprint),
            remaining: totalStoryPoints - completedStoryPoints
        });

        return {
            sprintNumber,
            totalStoryPoints,
            idealBurndown,
            actualBurndown,
            projectedCompletion: this.projectSprintCompletion(actualBurndown, idealBurndown)
        };
    }

    // Integration Points
    async integrateWithProjectManagement() {
        // Integration with external project management tools
        return {
            jira: await this.setupJiraIntegration(),
            azureDevOps: await this.setupAzureDevOpsIntegration(),
            trello: await this.setupTrelloIntegration(),
            asana: await this.setupAsanaIntegration()
        };
    }

    async integrateWithPerformanceMonitoring() {
        // Integration with monitoring and analytics
        return {
            prometheus: await this.setupPrometheusMetrics(),
            grafana: await this.setupGrafanaDashboards(),
            newRelic: await this.setupNewRelicTracking(),
            datadog: await this.setupDatadogMetrics()
        };
    }

    // Utility Methods
    getCurrentSprintDay(sprint) {
        const today = new Date();
        const sprintStart = new Date(sprint.startDate);
        return Math.ceil((today - sprintStart) / (1000 * 60 * 60 * 24));
    }

    calculateVelocityTrend() {
        if (this.velocityHistory.length < 3) return 'insufficient-data';
        
        const recent = this.velocityHistory.slice(-3);
        const trend = recent[2].velocity - recent[0].velocity;
        
        if (trend > 5) return 'improving';
        if (trend < -5) return 'declining';
        return 'stable';
    }

    async generateSprintGoal(phase, stories) {
        const phaseGoals = {
            'business_model': 'Validate business model and establish market fit',
            'architecture': 'Design scalable system architecture and select technology stack',
            'design': 'Create user-centered design system and validate user experience',
            'development': 'Deliver working software that meets acceptance criteria'
        };

        const baseGoal = phaseGoals[phase] || 'Complete planned user stories';
        const storyCount = stories.length;
        const totalPoints = stories.reduce((sum, story) => sum + story.storyPoints, 0);

        return `${baseGoal}. Complete ${storyCount} user stories (${totalPoints} story points) focused on ${phase} phase deliverables.`;
    }

    // Export agile metrics for reporting
    getAgileMetrics() {
        return {
            velocity: this.velocityMetrics,
            cycleTime: this.cycleTimeMetrics,
            quality: this.qualityMetrics,
            kanbanFlow: this.getKanbanFlowMetrics(),
            sprintHealth: this.getSprintHealthMetrics(),
            teamPerformance: this.getTeamPerformanceMetrics()
        };
    }

    getKanbanFlowMetrics() {
        const flowMetrics = {};
        
        for (const [columnId, column] of this.kanbanBoard) {
            flowMetrics[columnId] = {
                itemCount: column.items.length,
                wipLimit: column.wipLimit,
                wipUtilization: column.wipLimit ? (column.items.length / column.wipLimit) : null,
                averageAge: this.calculateAverageAge(column.items)
            };
        }

        return flowMetrics;
    }

    calculateAverageAge(items) {
        if (items.length === 0) return 0;
        
        const now = new Date();
        const totalAge = items.reduce((sum, item) => {
            const age = (now - new Date(item.createdAt)) / (1000 * 60 * 60 * 24); // days
            return sum + age;
        }, 0);

        return totalAge / items.length;
    }
}

module.exports = AgileIntegration;