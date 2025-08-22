/**
 * Progress Tracking and Monitoring System for BMAD Workflows
 * Comprehensive tracking of BMAD milestones, KPIs, and performance metrics
 */

const { EventEmitter } = require('events');

class ProgressTracking extends EventEmitter {
    constructor(bmadSystem) {
        super();
        this.bmadSystem = bmadSystem;
        this.milestones = new Map();
        this.kpis = new Map();
        this.metrics = new Map();
        this.alerts = new Map();
        this.trends = new Map();
        this.reports = new Map();
        this.dashboards = new Map();
        
        this.initializeProgressTracking();
    }

    initializeProgressTracking() {
        this.setupMilestones();
        this.setupKPIs();
        this.setupMetrics();
        this.setupAlerts();
        this.initializeDashboards();
        console.log('📊 Progress tracking system initialized');
    }

    setupMilestones() {
        // Business Model Phase Milestones
        this.milestones.set('business-model-complete', {
            id: 'business-model-complete',
            name: 'Business Model Validation Complete',
            phase: 'business_model',
            description: 'Business model has been validated through market research and stakeholder approval',
            criteria: [
                'business-model-canvas-approved',
                'market-research-validated',
                'revenue-model-verified',
                'competitive-analysis-complete',
                'stakeholder-sign-off-received'
            ],
            weight: 25, // Percentage of overall project
            dependencies: [],
            estimatedDate: null,
            actualDate: null,
            status: 'pending',
            progress: 0,
            qualityGates: ['business-model-validation'],
            deliverables: [
                'business-model-canvas',
                'market-research-report',
                'competitive-analysis',
                'financial-projections'
            ]
        });

        // Architecture Phase Milestones
        this.milestones.set('architecture-design-complete', {
            id: 'architecture-design-complete',
            name: 'System Architecture Design Complete',
            phase: 'architecture',
            description: 'Complete system architecture designed and approved',
            criteria: [
                'system-architecture-documented',
                'technology-stack-selected',
                'scalability-plan-approved',
                'security-architecture-validated',
                'technical-review-passed'
            ],
            weight: 25,
            dependencies: ['business-model-complete'],
            estimatedDate: null,
            actualDate: null,
            status: 'pending',
            progress: 0,
            qualityGates: ['architecture-validation'],
            deliverables: [
                'system-architecture-document',
                'technology-selection-report',
                'scalability-plan',
                'security-framework'
            ]
        });

        // Design Phase Milestones
        this.milestones.set('design-system-complete', {
            id: 'design-system-complete',
            name: 'Design System Complete',
            phase: 'design',
            description: 'Complete design system with validated user experience',
            criteria: [
                'ux-research-complete',
                'design-system-created',
                'prototypes-validated',
                'accessibility-verified',
                'user-testing-passed'
            ],
            weight: 25,
            dependencies: ['architecture-design-complete'],
            estimatedDate: null,
            actualDate: null,
            status: 'pending',
            progress: 0,
            qualityGates: ['design-validation'],
            deliverables: [
                'design-system',
                'user-journey-maps',
                'interactive-prototypes',
                'accessibility-report'
            ]
        });

        // Development Phase Milestones
        this.milestones.set('mvp-development-complete', {
            id: 'mvp-development-complete',
            name: 'MVP Development Complete',
            phase: 'development',
            description: 'Minimum viable product developed and ready for release',
            criteria: [
                'core-features-implemented',
                'testing-complete',
                'performance-validated',
                'security-verified',
                'deployment-ready'
            ],
            weight: 25,
            dependencies: ['design-system-complete'],
            estimatedDate: null,
            actualDate: null,
            status: 'pending',
            progress: 0,
            qualityGates: ['development-validation'],
            deliverables: [
                'working-software',
                'test-reports',
                'performance-benchmarks',
                'deployment-package'
            ]
        });
    }

    setupKPIs() {
        // Project Health KPIs
        this.kpis.set('project-health', {
            id: 'project-health',
            name: 'Overall Project Health',
            category: 'project',
            type: 'composite',
            target: 85, // Percentage
            current: 0,
            trend: 'stable',
            weight: 1.0,
            components: [
                'schedule-adherence',
                'quality-score',
                'stakeholder-satisfaction',
                'team-velocity'
            ],
            thresholds: {
                excellent: 90,
                good: 80,
                warning: 70,
                critical: 60
            }
        });

        // Schedule Performance KPIs
        this.kpis.set('schedule-adherence', {
            id: 'schedule-adherence',
            name: 'Schedule Adherence',
            category: 'schedule',
            type: 'percentage',
            target: 95,
            current: 0,
            trend: 'stable',
            weight: 0.3,
            formula: '(milestones_on_time / total_milestones) * 100',
            thresholds: {
                excellent: 95,
                good: 85,
                warning: 75,
                critical: 65
            }
        });

        this.kpis.set('sprint-velocity', {
            id: 'sprint-velocity',
            name: 'Sprint Velocity',
            category: 'delivery',
            type: 'story_points',
            target: 40,
            current: 0,
            trend: 'stable',
            weight: 0.2,
            formula: 'avg(completed_story_points_per_sprint)',
            thresholds: {
                excellent: 45,
                good: 35,
                warning: 25,
                critical: 20
            }
        });

        // Quality KPIs
        this.kpis.set('quality-score', {
            id: 'quality-score',
            name: 'Quality Score',
            category: 'quality',
            type: 'composite',
            target: 90,
            current: 0,
            trend: 'stable',
            weight: 0.25,
            components: [
                'defect-rate',
                'quality-gate-pass-rate',
                'code-coverage',
                'user-satisfaction'
            ],
            thresholds: {
                excellent: 95,
                good: 85,
                warning: 75,
                critical: 65
            }
        });

        this.kpis.set('defect-rate', {
            id: 'defect-rate',
            name: 'Defect Rate',
            category: 'quality',
            type: 'percentage',
            target: 2, // Lower is better
            current: 0,
            trend: 'stable',
            weight: 0.15,
            formula: '(defects_found / features_delivered) * 100',
            thresholds: {
                excellent: 1,
                good: 2,
                warning: 4,
                critical: 6
            }
        });

        // Stakeholder KPIs
        this.kpis.set('stakeholder-satisfaction', {
            id: 'stakeholder-satisfaction',
            name: 'Stakeholder Satisfaction',
            category: 'stakeholder',
            type: 'rating',
            target: 4.5, // Out of 5
            current: 0,
            trend: 'stable',
            weight: 0.2,
            formula: 'avg(stakeholder_ratings)',
            thresholds: {
                excellent: 4.5,
                good: 4.0,
                warning: 3.5,
                critical: 3.0
            }
        });

        // BMAD-Specific KPIs
        this.kpis.set('bmad-completion', {
            id: 'bmad-completion',
            name: 'BMAD Phase Completion',
            category: 'bmad',
            type: 'percentage',
            target: 100,
            current: 0,
            trend: 'improving',
            weight: 0.25,
            formula: '(completed_bmad_deliverables / total_bmad_deliverables) * 100',
            thresholds: {
                excellent: 95,
                good: 85,
                warning: 75,
                critical: 65
            }
        });

        this.kpis.set('workflow-efficiency', {
            id: 'workflow-efficiency',
            name: 'Workflow Efficiency',
            category: 'bmad',
            type: 'percentage',
            target: 85,
            current: 0,
            trend: 'stable',
            weight: 0.15,
            formula: '(actual_cycle_time / planned_cycle_time) * 100',
            thresholds: {
                excellent: 90,
                good: 80,
                warning: 70,
                critical: 60
            }
        });
    }

    setupMetrics() {
        // Velocity Metrics
        this.metrics.set('velocity-tracking', {
            id: 'velocity-tracking',
            name: 'Velocity Tracking',
            type: 'time_series',
            unit: 'story_points',
            data: [],
            collection_frequency: 'sprint_end',
            retention_period: '12_months'
        });

        // Cycle Time Metrics
        this.metrics.set('cycle-time', {
            id: 'cycle-time',
            name: 'Cycle Time',
            type: 'time_series',
            unit: 'days',
            data: [],
            collection_frequency: 'story_completion',
            retention_period: '6_months'
        });

        // Lead Time Metrics
        this.metrics.set('lead-time', {
            id: 'lead-time',
            name: 'Lead Time',
            type: 'time_series',
            unit: 'days',
            data: [],
            collection_frequency: 'story_completion',
            retention_period: '6_months'
        });

        // Quality Metrics
        this.metrics.set('defect-density', {
            id: 'defect-density',
            name: 'Defect Density',
            type: 'time_series',
            unit: 'defects_per_story_point',
            data: [],
            collection_frequency: 'weekly',
            retention_period: '6_months'
        });

        // BMAD Phase Metrics
        this.metrics.set('phase-duration', {
            id: 'phase-duration',
            name: 'Phase Duration',
            type: 'categorical',
            unit: 'days',
            data: {},
            collection_frequency: 'phase_completion',
            retention_period: '2_years'
        });

        // Agent Performance Metrics
        this.metrics.set('agent-utilization', {
            id: 'agent-utilization',
            name: 'Agent Utilization',
            type: 'categorical',
            unit: 'percentage',
            data: {},
            collection_frequency: 'daily',
            retention_period: '3_months'
        });
    }

    setupAlerts() {
        // Schedule Alerts
        this.alerts.set('milestone-delay', {
            id: 'milestone-delay',
            name: 'Milestone Delay Alert',
            type: 'schedule',
            severity: 'warning',
            condition: 'milestone_progress < 80% AND days_to_deadline <= 7',
            actions: ['notify_project_manager', 'escalate_to_stakeholders'],
            enabled: true
        });

        this.alerts.set('sprint-velocity-drop', {
            id: 'sprint-velocity-drop',
            name: 'Sprint Velocity Drop',
            type: 'performance',
            severity: 'warning',
            condition: 'current_velocity < (avg_velocity * 0.8)',
            actions: ['notify_scrum_master', 'trigger_retrospective'],
            enabled: true
        });

        // Quality Alerts
        this.alerts.set('quality-gate-failure', {
            id: 'quality-gate-failure',
            name: 'Quality Gate Failure',
            type: 'quality',
            severity: 'critical',
            condition: 'quality_gate_status = "failed"',
            actions: ['block_progression', 'notify_quality_team', 'escalate_immediately'],
            enabled: true
        });

        this.alerts.set('defect-rate-spike', {
            id: 'defect-rate-spike',
            name: 'Defect Rate Spike',
            type: 'quality',
            severity: 'warning',
            condition: 'current_defect_rate > (avg_defect_rate * 2)',
            actions: ['notify_qa_team', 'schedule_code_review'],
            enabled: true
        });

        // BMAD-Specific Alerts
        this.alerts.set('workflow-bottleneck', {
            id: 'workflow-bottleneck',
            name: 'Workflow Bottleneck',
            type: 'workflow',
            severity: 'warning',
            condition: 'workflow_cycle_time > (planned_cycle_time * 1.5)',
            actions: ['notify_workflow_coordinator', 'analyze_bottleneck'],
            enabled: true
        });

        this.alerts.set('stakeholder-satisfaction-drop', {
            id: 'stakeholder-satisfaction-drop',
            name: 'Stakeholder Satisfaction Drop',
            type: 'stakeholder',
            severity: 'high',
            condition: 'stakeholder_satisfaction < 3.5',
            actions: ['schedule_stakeholder_meeting', 'conduct_feedback_session'],
            enabled: true
        });
    }

    initializeDashboards() {
        // Executive Dashboard
        this.dashboards.set('executive', {
            id: 'executive',
            name: 'Executive Dashboard',
            audience: 'executives',
            refresh_rate: 'daily',
            widgets: [
                'project-health-summary',
                'milestone-progress',
                'budget-status',
                'risk-assessment',
                'stakeholder-satisfaction',
                'key-achievements'
            ]
        });

        // Project Management Dashboard
        this.dashboards.set('project-management', {
            id: 'project-management',
            name: 'Project Management Dashboard',
            audience: 'project_managers',
            refresh_rate: 'hourly',
            widgets: [
                'sprint-progress',
                'velocity-chart',
                'burndown-chart',
                'team-capacity',
                'impediments-list',
                'upcoming-milestones'
            ]
        });

        // Development Team Dashboard
        this.dashboards.set('development-team', {
            id: 'development-team',
            name: 'Development Team Dashboard',
            audience: 'development_team',
            refresh_rate: 'real_time',
            widgets: [
                'current-sprint-board',
                'agent-assignments',
                'quality-metrics',
                'technical-debt',
                'deployment-status',
                'test-coverage'
            ]
        });

        // BMAD Workflow Dashboard
        this.dashboards.set('bmad-workflow', {
            id: 'bmad-workflow',
            name: 'BMAD Workflow Dashboard',
            audience: 'workflow_coordinators',
            refresh_rate: 'hourly',
            widgets: [
                'phase-progress',
                'workflow-status',
                'deliverable-completion',
                'quality-gates-status',
                'workflow-efficiency',
                'phase-transitions'
            ]
        });
    }

    // Progress Tracking Methods
    async trackMilestoneProgress(milestoneId) {
        const milestone = this.milestones.get(milestoneId);
        if (!milestone) {
            throw new Error(`Milestone ${milestoneId} not found`);
        }

        const progress = {
            milestoneId: milestoneId,
            timestamp: new Date(),
            criteria: {},
            overallProgress: 0,
            status: 'in_progress',
            blockers: [],
            estimatedCompletion: null
        };

        // Check each criterion
        let completedCriteria = 0;
        for (const criterion of milestone.criteria) {
            const isComplete = await this.checkCriterion(criterion);
            progress.criteria[criterion] = isComplete;
            if (isComplete) completedCriteria++;
        }

        // Calculate overall progress
        progress.overallProgress = (completedCriteria / milestone.criteria.length) * 100;
        milestone.progress = progress.overallProgress;

        // Update milestone status
        if (progress.overallProgress === 100) {
            milestone.status = 'completed';
            milestone.actualDate = new Date();
            progress.status = 'completed';
        } else if (progress.overallProgress > 0) {
            milestone.status = 'in_progress';
            progress.status = 'in_progress';
        }

        // Check for blockers
        progress.blockers = await this.identifyMilestoneBlockers(milestone);

        // Estimate completion date
        if (progress.status !== 'completed') {
            progress.estimatedCompletion = await this.estimateMilestoneCompletion(milestone, progress);
        }

        this.emit('milestone:progress-updated', { milestone, progress });
        return progress;
    }

    async trackBMADPhaseProgress() {
        const currentPhase = this.bmadSystem.currentPhase;
        const phaseWorkflows = Array.from(this.bmadSystem.workflows.values())
            .filter(workflow => workflow.phase === currentPhase);

        const phaseProgress = {
            phase: currentPhase,
            timestamp: new Date(),
            workflows: {},
            overallProgress: 0,
            milestones: {},
            deliverables: {},
            qualityGates: {},
            estimatedCompletion: null,
            blockers: [],
            riskAssessment: await this.assessPhaseRisks(currentPhase)
        };

        // Track workflow progress
        let totalWorkflowProgress = 0;
        for (const workflow of phaseWorkflows) {
            const workflowProgress = await this.trackWorkflowProgress(workflow.id);
            phaseProgress.workflows[workflow.id] = workflowProgress;
            totalWorkflowProgress += workflowProgress.completionPercentage;
        }

        // Track milestone progress for this phase
        const phaseMilestones = Array.from(this.milestones.values())
            .filter(milestone => milestone.phase === currentPhase);

        let totalMilestoneProgress = 0;
        for (const milestone of phaseMilestones) {
            const milestoneProgress = await this.trackMilestoneProgress(milestone.id);
            phaseProgress.milestones[milestone.id] = milestoneProgress;
            totalMilestoneProgress += milestoneProgress.overallProgress;
        }

        // Calculate overall phase progress
        const workflowWeight = 0.6;
        const milestoneWeight = 0.4;
        
        const avgWorkflowProgress = phaseWorkflows.length > 0 ? totalWorkflowProgress / phaseWorkflows.length : 0;
        const avgMilestoneProgress = phaseMilestones.length > 0 ? totalMilestoneProgress / phaseMilestones.length : 0;
        
        phaseProgress.overallProgress = (avgWorkflowProgress * workflowWeight) + (avgMilestoneProgress * milestoneWeight);

        // Track deliverables
        phaseProgress.deliverables = await this.trackPhaseDeliverables(currentPhase);

        // Track quality gates
        phaseProgress.qualityGates = await this.trackPhaseQualityGates(currentPhase);

        // Estimate phase completion
        phaseProgress.estimatedCompletion = await this.estimatePhaseCompletion(currentPhase, phaseProgress);

        // Identify blockers
        phaseProgress.blockers = await this.identifyPhaseBlockers(currentPhase);

        this.emit('phase:progress-updated', phaseProgress);
        return phaseProgress;
    }

    async trackWorkflowProgress(workflowId) {
        const workflow = this.bmadSystem.workflows.get(workflowId);
        if (!workflow) {
            throw new Error(`Workflow ${workflowId} not found`);
        }

        // Get user stories assigned to this workflow
        const workflowStories = Array.from(this.bmadSystem.userStories.values())
            .filter(story => story.workflow === workflowId);

        const progress = {
            workflowId: workflowId,
            timestamp: new Date(),
            totalStories: workflowStories.length,
            completedStories: workflowStories.filter(s => s.status === 'done').length,
            inProgressStories: workflowStories.filter(s => s.status === 'in_progress').length,
            blockedStories: workflowStories.filter(s => s.blockers && s.blockers.length > 0).length,
            totalStoryPoints: workflowStories.reduce((sum, s) => sum + (s.estimatedPoints || 0), 0),
            completedStoryPoints: workflowStories.filter(s => s.status === 'done').reduce((sum, s) => sum + (s.estimatedPoints || 0), 0),
            completionPercentage: 0,
            velocity: await this.calculateWorkflowVelocity(workflowId),
            estimatedCompletion: null,
            blockers: [],
            qualityMetrics: await this.calculateWorkflowQualityMetrics(workflowId)
        };

        // Calculate completion percentage
        if (progress.totalStoryPoints > 0) {
            progress.completionPercentage = (progress.completedStoryPoints / progress.totalStoryPoints) * 100;
        } else if (progress.totalStories > 0) {
            progress.completionPercentage = (progress.completedStories / progress.totalStories) * 100;
        }

        // Estimate completion
        if (progress.completionPercentage < 100 && progress.velocity > 0) {
            const remainingPoints = progress.totalStoryPoints - progress.completedStoryPoints;
            const estimatedSprints = Math.ceil(remainingPoints / progress.velocity);
            const sprintDuration = 14; // days
            progress.estimatedCompletion = new Date(Date.now() + (estimatedSprints * sprintDuration * 24 * 60 * 60 * 1000));
        }

        // Identify blockers
        progress.blockers = await this.identifyWorkflowBlockers(workflowId);

        return progress;
    }

    // KPI Calculation Methods
    async calculateKPIs() {
        const kpiResults = {};

        for (const [kpiId, kpi] of this.kpis) {
            const result = await this.calculateKPI(kpiId);
            kpiResults[kpiId] = result;
            
            // Update KPI with current value
            kpi.current = result.value;
            kpi.trend = result.trend;
            kpi.lastUpdated = new Date();

            // Check thresholds and trigger alerts
            await this.checkKPIThresholds(kpiId, result);
        }

        this.emit('kpis:calculated', kpiResults);
        return kpiResults;
    }

    async calculateKPI(kpiId) {
        const kpi = this.kpis.get(kpiId);
        if (!kpi) {
            throw new Error(`KPI ${kpiId} not found`);
        }

        let value = 0;
        let trend = 'stable';
        let details = {};

        switch (kpiId) {
            case 'project-health':
                value = await this.calculateProjectHealth();
                break;
                
            case 'schedule-adherence':
                value = await this.calculateScheduleAdherence();
                break;
                
            case 'sprint-velocity':
                value = await this.calculateSprintVelocity();
                break;
                
            case 'quality-score':
                value = await this.calculateQualityScore();
                break;
                
            case 'defect-rate':
                value = await this.calculateDefectRate();
                break;
                
            case 'stakeholder-satisfaction':
                value = await this.calculateStakeholderSatisfaction();
                break;
                
            case 'bmad-completion':
                value = await this.calculateBMADCompletion();
                break;
                
            case 'workflow-efficiency':
                value = await this.calculateWorkflowEfficiency();
                break;
                
            default:
                throw new Error(`Unknown KPI calculation for ${kpiId}`);
        }

        // Calculate trend
        trend = await this.calculateKPITrend(kpiId, value);

        return {
            kpiId,
            value,
            trend,
            timestamp: new Date(),
            target: kpi.target,
            performance: this.calculatePerformanceRating(value, kpi.target, kpi.thresholds),
            details
        };
    }

    async calculateProjectHealth() {
        const components = [
            await this.calculateScheduleAdherence(),
            await this.calculateQualityScore(),
            await this.calculateStakeholderSatisfaction() * 20, // Convert 5-point scale to 100
            await this.calculateSprintVelocity() / 40 * 100 // Normalize to percentage
        ];

        return components.reduce((sum, component) => sum + component, 0) / components.length;
    }

    async calculateScheduleAdherence() {
        const milestones = Array.from(this.milestones.values());
        const completedOnTime = milestones.filter(m => 
            m.status === 'completed' && 
            m.actualDate <= m.estimatedDate
        ).length;
        
        return milestones.length > 0 ? (completedOnTime / milestones.length) * 100 : 0;
    }

    async calculateSprintVelocity() {
        if (!this.bmadSystem.currentSprint) return 0;
        
        const completedStories = Array.from(this.bmadSystem.userStories.values())
            .filter(story => 
                story.sprint === this.bmadSystem.currentSprint.number && 
                story.status === 'done'
            );
        
        return completedStories.reduce((sum, story) => sum + (story.estimatedPoints || 0), 0);
    }

    // Report Generation
    async generateProgressReport(reportType = 'comprehensive', stakeholder = 'all') {
        const report = {
            reportId: this.generateReportId(),
            type: reportType,
            stakeholder: stakeholder,
            generatedAt: new Date(),
            period: {
                start: this.getReportPeriodStart(),
                end: new Date()
            },
            sections: {}
        };

        // Executive Summary
        report.sections.executiveSummary = await this.generateExecutiveSummary();

        // Progress Overview
        report.sections.progressOverview = await this.generateProgressOverview();

        // BMAD Phase Analysis
        report.sections.bmadPhaseAnalysis = await this.generateBMADPhaseAnalysis();

        // Milestone Status
        report.sections.milestoneStatus = await this.generateMilestoneStatus();

        // KPI Dashboard
        report.sections.kpiDashboard = await this.generateKPIDashboard();

        // Quality Metrics
        report.sections.qualityMetrics = await this.generateQualityMetrics();

        // Risk Assessment
        report.sections.riskAssessment = await this.generateRiskAssessment();

        // Recommendations
        report.sections.recommendations = await this.generateRecommendations();

        // Appendices
        if (reportType === 'comprehensive') {
            report.sections.appendices = await this.generateAppendices();
        }

        // Store report
        this.reports.set(report.reportId, report);

        this.emit('report:generated', report);
        return report;
    }

    async generateExecutiveSummary() {
        const phaseProgress = await this.trackBMADPhaseProgress();
        const kpis = await this.calculateKPIs();
        
        return {
            currentPhase: this.bmadSystem.currentPhase,
            overallProgress: phaseProgress.overallProgress,
            projectHealth: kpis['project-health'].value,
            keyAchievements: await this.getKeyAchievements(),
            criticalIssues: await this.getCriticalIssues(),
            nextMilestone: await this.getNextMilestone(),
            budgetStatus: await this.getBudgetStatus(),
            timelineStatus: await this.getTimelineStatus()
        };
    }

    // Utility Methods
    generateReportId() {
        return `REPORT-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    getReportPeriodStart() {
        // Default to 30 days ago
        const start = new Date();
        start.setDate(start.getDate() - 30);
        return start;
    }

    calculatePerformanceRating(value, target, thresholds) {
        if (value >= thresholds.excellent) return 'excellent';
        if (value >= thresholds.good) return 'good';
        if (value >= thresholds.warning) return 'warning';
        return 'critical';
    }

    async checkKPIThresholds(kpiId, result) {
        const kpi = this.kpis.get(kpiId);
        const performance = result.performance;

        if (performance === 'critical' || performance === 'warning') {
            // Check if there's an appropriate alert configured
            const relevantAlerts = Array.from(this.alerts.values())
                .filter(alert => alert.enabled && this.isAlertRelevantForKPI(alert, kpiId));

            for (const alert of relevantAlerts) {
                await this.triggerAlert(alert, { kpiId, value: result.value, performance });
            }
        }
    }

    isAlertRelevantForKPI(alert, kpiId) {
        // Map KPIs to relevant alerts
        const kpiAlertMap = {
            'schedule-adherence': ['milestone-delay'],
            'sprint-velocity': ['sprint-velocity-drop'],
            'quality-score': ['quality-gate-failure', 'defect-rate-spike'],
            'stakeholder-satisfaction': ['stakeholder-satisfaction-drop'],
            'workflow-efficiency': ['workflow-bottleneck']
        };

        return kpiAlertMap[kpiId] && kpiAlertMap[kpiId].includes(alert.id);
    }

    async triggerAlert(alert, context) {
        const alertInstance = {
            alertId: alert.id,
            triggeredAt: new Date(),
            severity: alert.severity,
            context: context,
            actions: alert.actions,
            status: 'triggered'
        };

        console.warn(`🚨 Alert triggered: ${alert.name}`, alertInstance);
        this.emit('alert:triggered', alertInstance);

        // Execute alert actions
        for (const action of alert.actions) {
            await this.executeAlertAction(action, alertInstance);
        }

        return alertInstance;
    }

    async executeAlertAction(action, alertInstance) {
        switch (action) {
            case 'notify_project_manager':
                await this.notifyProjectManager(alertInstance);
                break;
            case 'escalate_to_stakeholders':
                await this.escalateToStakeholders(alertInstance);
                break;
            case 'notify_scrum_master':
                await this.notifyScrumMaster(alertInstance);
                break;
            case 'trigger_retrospective':
                await this.triggerRetrospective(alertInstance);
                break;
            case 'block_progression':
                await this.blockProgression(alertInstance);
                break;
            case 'notify_quality_team':
                await this.notifyQualityTeam(alertInstance);
                break;
            default:
                console.log(`Unknown alert action: ${action}`);
        }
    }

    // API Methods for External Integration
    getProgressSummary() {
        return {
            currentPhase: this.bmadSystem.currentPhase,
            milestones: this.getMilestonesSummary(),
            kpis: this.getKPIsSummary(),
            recentAlerts: this.getRecentAlerts(),
            upcomingDeadlines: this.getUpcomingDeadlines()
        };
    }

    getMilestonesSummary() {
        return Array.from(this.milestones.values()).map(milestone => ({
            id: milestone.id,
            name: milestone.name,
            phase: milestone.phase,
            status: milestone.status,
            progress: milestone.progress,
            estimatedDate: milestone.estimatedDate,
            actualDate: milestone.actualDate
        }));
    }

    getKPIsSummary() {
        return Array.from(this.kpis.values()).map(kpi => ({
            id: kpi.id,
            name: kpi.name,
            current: kpi.current,
            target: kpi.target,
            trend: kpi.trend,
            performance: this.calculatePerformanceRating(kpi.current, kpi.target, kpi.thresholds)
        }));
    }

    getRecentAlerts(days = 7) {
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);
        
        return Array.from(this.alerts.values())
            .filter(alert => alert.lastTriggered && alert.lastTriggered >= cutoff)
            .sort((a, b) => b.lastTriggered - a.lastTriggered);
    }

    getUpcomingDeadlines(days = 30) {
        const upcoming = new Date();
        upcoming.setDate(upcoming.getDate() + days);
        
        return Array.from(this.milestones.values())
            .filter(milestone => 
                milestone.estimatedDate && 
                milestone.estimatedDate <= upcoming && 
                milestone.status !== 'completed'
            )
            .sort((a, b) => a.estimatedDate - b.estimatedDate);
    }
}

module.exports = ProgressTracking;