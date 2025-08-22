/**
 * Stakeholder Communication System for BMAD Workflows
 * Manages communication, reporting, and collaboration with project stakeholders
 */

const { EventEmitter } = require('events');

class StakeholderCommunication extends EventEmitter {
    constructor(bmadSystem) {
        super();
        this.bmadSystem = bmadSystem;
        this.stakeholders = new Map();
        this.communicationPlans = new Map();
        this.reports = new Map();
        this.feedback = new Map();
        this.meetings = new Map();
        this.notifications = new Map();
        this.approvals = new Map();
        
        this.initializeCommunicationSystem();
    }

    initializeCommunicationSystem() {
        this.setupStakeholders();
        this.setupCommunicationPlans();
        this.setupReportTemplates();
        this.setupNotificationRules();
        console.log('📢 Stakeholder communication system initialized');
    }

    setupStakeholders() {
        // Executive Stakeholders
        this.stakeholders.set('ceo', {
            id: 'ceo',
            name: 'Chief Executive Officer',
            role: 'executive',
            influence: 'high',
            interest: 'high',
            communication_preference: 'executive_summary',
            frequency: 'weekly',
            timezone: 'UTC-8',
            channels: ['email', 'executive_dashboard'],
            responsibilities: [
                'strategic_decisions',
                'budget_approval',
                'vision_alignment',
                'final_sign_off'
            ],
            concerns: [
                'business_value',
                'roi',
                'market_opportunity',
                'competitive_advantage'
            ],
            approvals_required: [
                'business_model',
                'major_budget_changes',
                'strategic_pivots'
            ]
        });

        this.stakeholders.set('cto', {
            id: 'cto',
            name: 'Chief Technology Officer',
            role: 'technical_executive',
            influence: 'high',
            interest: 'high',
            communication_preference: 'technical_details',
            frequency: 'bi_weekly',
            timezone: 'UTC-5',
            channels: ['email', 'technical_dashboard', 'video_call'],
            responsibilities: [
                'technology_decisions',
                'architecture_approval',
                'technical_risk_assessment',
                'team_leadership'
            ],
            concerns: [
                'technical_feasibility',
                'scalability',
                'security',
                'technical_debt'
            ],
            approvals_required: [
                'architecture_design',
                'technology_stack',
                'security_framework'
            ]
        });

        this.stakeholders.set('product_owner', {
            id: 'product_owner',
            name: 'Product Owner',
            role: 'product_management',
            influence: 'high',
            interest: 'high',
            communication_preference: 'detailed_progress',
            frequency: 'daily',
            timezone: 'UTC-6',
            channels: ['slack', 'project_dashboard', 'standup_meetings'],
            responsibilities: [
                'requirements_definition',
                'priority_setting',
                'user_story_approval',
                'acceptance_criteria'
            ],
            concerns: [
                'user_value',
                'feature_completeness',
                'user_experience',
                'market_requirements'
            ],
            approvals_required: [
                'user_stories',
                'acceptance_criteria',
                'feature_prioritization'
            ]
        });

        // Technical Stakeholders
        this.stakeholders.set('lead_architect', {
            id: 'lead_architect',
            name: 'Lead Architect',
            role: 'technical_lead',
            influence: 'medium',
            interest: 'high',
            communication_preference: 'technical_details',
            frequency: 'daily',
            timezone: 'UTC+1',
            channels: ['slack', 'technical_documentation', 'code_reviews'],
            responsibilities: [
                'architecture_design',
                'technical_standards',
                'code_quality',
                'technical_mentoring'
            ],
            concerns: [
                'architecture_quality',
                'design_patterns',
                'performance',
                'maintainability'
            ],
            approvals_required: [
                'architecture_documents',
                'design_decisions',
                'technical_standards'
            ]
        });

        this.stakeholders.set('qa_manager', {
            id: 'qa_manager',
            name: 'QA Manager',
            role: 'quality_assurance',
            influence: 'medium',
            interest: 'high',
            communication_preference: 'quality_metrics',
            frequency: 'weekly',
            timezone: 'UTC+0',
            channels: ['email', 'quality_dashboard', 'test_reports'],
            responsibilities: [
                'quality_standards',
                'test_strategy',
                'defect_management',
                'quality_gates'
            ],
            concerns: [
                'quality_metrics',
                'test_coverage',
                'defect_rates',
                'user_acceptance'
            ],
            approvals_required: [
                'test_plans',
                'quality_gates',
                'release_readiness'
            ]
        });

        // Business Stakeholders
        this.stakeholders.set('marketing_director', {
            id: 'marketing_director',
            name: 'Marketing Director',
            role: 'marketing',
            influence: 'medium',
            interest: 'medium',
            communication_preference: 'business_impact',
            frequency: 'bi_weekly',
            timezone: 'UTC-3',
            channels: ['email', 'marketing_dashboard'],
            responsibilities: [
                'market_positioning',
                'go_to_market_strategy',
                'customer_feedback',
                'competitive_analysis'
            ],
            concerns: [
                'market_readiness',
                'competitive_positioning',
                'customer_value',
                'launch_timeline'
            ],
            approvals_required: [
                'market_research',
                'competitive_analysis',
                'launch_strategy'
            ]
        });

        this.stakeholders.set('finance_director', {
            id: 'finance_director',
            name: 'Finance Director',
            role: 'finance',
            influence: 'high',
            interest: 'medium',
            communication_preference: 'financial_metrics',
            frequency: 'monthly',
            timezone: 'UTC-5',
            channels: ['email', 'financial_dashboard'],
            responsibilities: [
                'budget_management',
                'financial_planning',
                'cost_tracking',
                'roi_analysis'
            ],
            concerns: [
                'budget_adherence',
                'roi_projections',
                'cost_optimization',
                'financial_risk'
            ],
            approvals_required: [
                'budget_changes',
                'financial_projections',
                'cost_approvals'
            ]
        });

        // External Stakeholders
        this.stakeholders.set('key_customer', {
            id: 'key_customer',
            name: 'Key Customer Representative',
            role: 'customer',
            influence: 'high',
            interest: 'high',
            communication_preference: 'user_focused',
            frequency: 'monthly',
            timezone: 'UTC-7',
            channels: ['email', 'user_demos', 'feedback_sessions'],
            responsibilities: [
                'user_feedback',
                'requirements_validation',
                'user_acceptance_testing',
                'market_insights'
            ],
            concerns: [
                'user_experience',
                'feature_functionality',
                'performance',
                'reliability'
            ],
            approvals_required: [
                'user_requirements',
                'design_mockups',
                'user_acceptance'
            ]
        });
    }

    setupCommunicationPlans() {
        // BMAD Phase Communication Plans
        this.communicationPlans.set('business_model_phase', {
            phase: 'business_model',
            stakeholders: ['ceo', 'product_owner', 'marketing_director', 'finance_director', 'key_customer'],
            key_messages: [
                'Business model validation progress',
                'Market research findings',
                'Value proposition refinement',
                'Revenue model validation'
            ],
            deliverables_to_communicate: [
                'business_model_canvas',
                'market_research_report',
                'competitive_analysis',
                'financial_projections'
            ],
            communication_frequency: 'weekly',
            escalation_triggers: [
                'market_validation_failure',
                'major_pivot_required',
                'competitive_threat_identified'
            ]
        });

        this.communicationPlans.set('architecture_phase', {
            phase: 'architecture',
            stakeholders: ['cto', 'lead_architect', 'product_owner', 'qa_manager'],
            key_messages: [
                'Architecture design progress',
                'Technology stack decisions',
                'Scalability planning',
                'Security framework implementation'
            ],
            deliverables_to_communicate: [
                'system_architecture_document',
                'technology_selection_report',
                'scalability_plan',
                'security_framework'
            ],
            communication_frequency: 'bi_weekly',
            escalation_triggers: [
                'architecture_bottleneck',
                'technology_risk_identified',
                'scalability_concern'
            ]
        });

        this.communicationPlans.set('design_phase', {
            phase: 'design',
            stakeholders: ['product_owner', 'key_customer', 'marketing_director', 'qa_manager'],
            key_messages: [
                'Design system development',
                'User experience validation',
                'Accessibility compliance',
                'Brand alignment'
            ],
            deliverables_to_communicate: [
                'design_system',
                'user_journey_maps',
                'interactive_prototypes',
                'accessibility_report'
            ],
            communication_frequency: 'weekly',
            escalation_triggers: [
                'user_testing_failure',
                'accessibility_issues',
                'brand_misalignment'
            ]
        });

        this.communicationPlans.set('development_phase', {
            phase: 'development',
            stakeholders: ['cto', 'product_owner', 'qa_manager', 'lead_architect'],
            key_messages: [
                'Development progress',
                'Feature completion',
                'Quality metrics',
                'Performance benchmarks'
            ],
            deliverables_to_communicate: [
                'working_software',
                'test_reports',
                'performance_benchmarks',
                'deployment_package'
            ],
            communication_frequency: 'weekly',
            escalation_triggers: [
                'quality_gate_failure',
                'performance_issues',
                'security_vulnerabilities'
            ]
        });
    }

    setupReportTemplates() {
        // Executive Summary Template
        this.reports.set('executive_summary', {
            name: 'Executive Summary Report',
            audience: ['ceo', 'cto', 'finance_director'],
            frequency: 'weekly',
            sections: [
                'project_health_overview',
                'key_achievements',
                'critical_issues',
                'budget_status',
                'timeline_status',
                'risk_assessment',
                'next_steps',
                'decisions_required'
            ],
            format: 'pdf',
            length: '2_pages',
            style: 'executive'
        });

        // Technical Progress Report
        this.reports.set('technical_progress', {
            name: 'Technical Progress Report',
            audience: ['cto', 'lead_architect', 'qa_manager'],
            frequency: 'bi_weekly',
            sections: [
                'architecture_progress',
                'development_metrics',
                'quality_metrics',
                'performance_benchmarks',
                'technical_debt',
                'security_status',
                'infrastructure_status',
                'technical_risks'
            ],
            format: 'html',
            length: '4_pages',
            style: 'technical'
        });

        // Product Status Report
        this.reports.set('product_status', {
            name: 'Product Status Report',
            audience: ['product_owner', 'marketing_director', 'key_customer'],
            frequency: 'weekly',
            sections: [
                'feature_progress',
                'user_story_completion',
                'user_feedback',
                'market_validation',
                'competitive_analysis',
                'go_to_market_readiness',
                'user_acceptance_results'
            ],
            format: 'html',
            length: '3_pages',
            style: 'product'
        });

        // Financial Status Report
        this.reports.set('financial_status', {
            name: 'Financial Status Report',
            audience: ['ceo', 'finance_director'],
            frequency: 'monthly',
            sections: [
                'budget_vs_actual',
                'cost_breakdown',
                'roi_projections',
                'financial_risks',
                'cost_optimization_opportunities',
                'budget_forecast'
            ],
            format: 'pdf',
            length: '2_pages',
            style: 'financial'
        });
    }

    setupNotificationRules() {
        // Milestone notifications
        this.notifications.set('milestone_completion', {
            trigger: 'milestone_completed',
            stakeholders: 'milestone_dependent',
            urgency: 'high',
            channels: ['email', 'dashboard'],
            template: 'milestone_completion_notification'
        });

        this.notifications.set('milestone_delay', {
            trigger: 'milestone_delayed',
            stakeholders: ['ceo', 'product_owner', 'cto'],
            urgency: 'critical',
            channels: ['email', 'sms', 'dashboard'],
            template: 'milestone_delay_notification'
        });

        // Quality gate notifications
        this.notifications.set('quality_gate_failure', {
            trigger: 'quality_gate_failed',
            stakeholders: ['qa_manager', 'cto', 'product_owner'],
            urgency: 'critical',
            channels: ['email', 'slack', 'dashboard'],
            template: 'quality_gate_failure_notification'
        });

        // Budget notifications
        this.notifications.set('budget_variance', {
            trigger: 'budget_variance_threshold',
            stakeholders: ['finance_director', 'ceo'],
            urgency: 'high',
            channels: ['email', 'dashboard'],
            template: 'budget_variance_notification'
        });

        // Approval notifications
        this.notifications.set('approval_required', {
            trigger: 'approval_requested',
            stakeholders: 'approval_required',
            urgency: 'medium',
            channels: ['email', 'dashboard'],
            template: 'approval_request_notification'
        });
    }

    // Communication Methods
    async generateStakeholderReport(stakeholderId, reportType = 'auto') {
        const stakeholder = this.stakeholders.get(stakeholderId);
        if (!stakeholder) {
            throw new Error(`Stakeholder ${stakeholderId} not found`);
        }

        // Determine report type based on stakeholder if auto
        if (reportType === 'auto') {
            reportType = this.determineReportType(stakeholder);
        }

        const reportTemplate = this.reports.get(reportType);
        if (!reportTemplate) {
            throw new Error(`Report template ${reportType} not found`);
        }

        const report = {
            reportId: this.generateReportId(),
            type: reportType,
            stakeholder: stakeholderId,
            generatedAt: new Date(),
            sections: {},
            metadata: {
                audience: stakeholder.role,
                preference: stakeholder.communication_preference,
                timezone: stakeholder.timezone
            }
        };

        // Generate each section
        for (const section of reportTemplate.sections) {
            report.sections[section] = await this.generateReportSection(section, stakeholder);
        }

        // Apply stakeholder-specific formatting
        report.formatted = await this.formatReportForStakeholder(report, stakeholder);

        // Store report
        this.reports.set(report.reportId, report);

        this.emit('report:generated', { stakeholder: stakeholderId, report });
        return report;
    }

    async generateReportSection(sectionType, stakeholder) {
        switch (sectionType) {
            case 'project_health_overview':
                return await this.generateProjectHealthOverview(stakeholder);
            
            case 'key_achievements':
                return await this.generateKeyAchievements(stakeholder);
            
            case 'critical_issues':
                return await this.generateCriticalIssues(stakeholder);
            
            case 'budget_status':
                return await this.generateBudgetStatus(stakeholder);
            
            case 'timeline_status':
                return await this.generateTimelineStatus(stakeholder);
            
            case 'risk_assessment':
                return await this.generateRiskAssessment(stakeholder);
            
            case 'next_steps':
                return await this.generateNextSteps(stakeholder);
            
            case 'decisions_required':
                return await this.generateDecisionsRequired(stakeholder);
            
            case 'architecture_progress':
                return await this.generateArchitectureProgress(stakeholder);
            
            case 'development_metrics':
                return await this.generateDevelopmentMetrics(stakeholder);
            
            case 'quality_metrics':
                return await this.generateQualityMetrics(stakeholder);
            
            case 'feature_progress':
                return await this.generateFeatureProgress(stakeholder);
            
            case 'user_feedback':
                return await this.generateUserFeedback(stakeholder);
            
            case 'market_validation':
                return await this.generateMarketValidation(stakeholder);
            
            default:
                return { type: sectionType, content: 'Section not implemented', timestamp: new Date() };
        }
    }

    async generateProjectHealthOverview(stakeholder) {
        const phaseProgress = await this.bmadSystem.progressTracking.trackBMADPhaseProgress();
        const kpis = await this.bmadSystem.progressTracking.calculateKPIs();
        
        return {
            type: 'project_health_overview',
            content: {
                currentPhase: this.bmadSystem.currentPhase,
                overallHealth: kpis['project-health']?.value || 0,
                phaseProgress: phaseProgress.overallProgress,
                scheduleStatus: this.determineScheduleStatus(),
                budgetStatus: this.determineBudgetStatus(),
                qualityStatus: kpis['quality-score']?.value || 0,
                riskLevel: await this.assessOverallRiskLevel(),
                summary: this.generateHealthSummary(kpis, phaseProgress)
            },
            timestamp: new Date(),
            stakeholder_focus: this.getStakeholderFocus(stakeholder, 'health')
        };
    }

    async generateKeyAchievements(stakeholder) {
        const achievements = [];
        
        // Get completed milestones
        const completedMilestones = Array.from(this.bmadSystem.progressTracking.milestones.values())
            .filter(m => m.status === 'completed')
            .sort((a, b) => b.actualDate - a.actualDate)
            .slice(0, 5);

        for (const milestone of completedMilestones) {
            achievements.push({
                type: 'milestone',
                title: milestone.name,
                description: milestone.description,
                completedDate: milestone.actualDate,
                impact: await this.assessMilestoneImpact(milestone, stakeholder)
            });
        }

        // Get completed user stories
        const completedStories = Array.from(this.bmadSystem.userStories.values())
            .filter(s => s.status === 'done')
            .sort((a, b) => b.updatedAt - a.updatedAt)
            .slice(0, 10);

        for (const story of completedStories) {
            achievements.push({
                type: 'feature',
                title: story.title,
                description: story.description,
                completedDate: story.updatedAt,
                storyPoints: story.estimatedPoints,
                phase: story.phase
            });
        }

        return {
            type: 'key_achievements',
            content: {
                achievements: achievements.slice(0, 8), // Top 8 achievements
                summary: this.generateAchievementsSummary(achievements, stakeholder)
            },
            timestamp: new Date(),
            stakeholder_focus: this.getStakeholderFocus(stakeholder, 'achievements')
        };
    }

    async generateCriticalIssues(stakeholder) {
        const issues = [];
        
        // Get blocked user stories
        const blockedStories = Array.from(this.bmadSystem.userStories.values())
            .filter(s => s.blockers && s.blockers.length > 0);

        for (const story of blockedStories) {
            issues.push({
                type: 'blocked_story',
                severity: 'high',
                title: `Blocked Story: ${story.title}`,
                description: story.blockers.join(', '),
                impact: await this.assessStoryBlockerImpact(story),
                recommendations: await this.generateBlockerRecommendations(story)
            });
        }

        // Get failed quality gates
        const failedQualityGates = await this.getFailedQualityGates();
        for (const gate of failedQualityGates) {
            issues.push({
                type: 'quality_gate_failure',
                severity: 'critical',
                title: `Quality Gate Failed: ${gate.name}`,
                description: gate.failureReason,
                impact: await this.assessQualityGateImpact(gate),
                recommendations: await this.generateQualityGateRecommendations(gate)
            });
        }

        // Get budget variances
        const budgetIssues = await this.getBudgetVariances();
        for (const issue of budgetIssues) {
            issues.push({
                type: 'budget_variance',
                severity: issue.severity,
                title: `Budget Variance: ${issue.category}`,
                description: issue.description,
                impact: issue.impact,
                recommendations: issue.recommendations
            });
        }

        return {
            type: 'critical_issues',
            content: {
                issues: issues.sort((a, b) => this.getSeverityWeight(b.severity) - this.getSeverityWeight(a.severity)),
                summary: this.generateIssuesSummary(issues, stakeholder),
                escalationRecommended: issues.some(i => i.severity === 'critical')
            },
            timestamp: new Date(),
            stakeholder_focus: this.getStakeholderFocus(stakeholder, 'issues')
        };
    }

    // Notification Methods
    async sendNotification(notificationType, context) {
        const notificationRule = this.notifications.get(notificationType);
        if (!notificationRule) {
            throw new Error(`Notification rule ${notificationType} not found`);
        }

        const notification = {
            id: this.generateNotificationId(),
            type: notificationType,
            context: context,
            sentAt: new Date(),
            recipients: [],
            channels: notificationRule.channels,
            urgency: notificationRule.urgency,
            status: 'pending'
        };

        // Determine recipients
        if (notificationRule.stakeholders === 'milestone_dependent') {
            notification.recipients = await this.getMilestoneDependentStakeholders(context.milestoneId);
        } else if (notificationRule.stakeholders === 'approval_required') {
            notification.recipients = await this.getApprovalRequiredStakeholders(context.approvalType);
        } else if (Array.isArray(notificationRule.stakeholders)) {
            notification.recipients = notificationRule.stakeholders;
        }

        // Send notification through each channel
        for (const channel of notificationRule.channels) {
            for (const recipientId of notification.recipients) {
                const stakeholder = this.stakeholders.get(recipientId);
                if (stakeholder && stakeholder.channels.includes(channel)) {
                    await this.sendNotificationViaChannel(notification, stakeholder, channel);
                }
            }
        }

        notification.status = 'sent';
        this.emit('notification:sent', notification);
        
        return notification;
    }

    async sendNotificationViaChannel(notification, stakeholder, channel) {
        switch (channel) {
            case 'email':
                await this.sendEmailNotification(notification, stakeholder);
                break;
            case 'slack':
                await this.sendSlackNotification(notification, stakeholder);
                break;
            case 'sms':
                await this.sendSMSNotification(notification, stakeholder);
                break;
            case 'dashboard':
                await this.sendDashboardNotification(notification, stakeholder);
                break;
            default:
                console.log(`Unknown notification channel: ${channel}`);
        }
    }

    // Approval Management
    async requestApproval(approvalType, context, stakeholderId) {
        const stakeholder = this.stakeholders.get(stakeholderId);
        if (!stakeholder) {
            throw new Error(`Stakeholder ${stakeholderId} not found`);
        }

        if (!stakeholder.approvals_required.includes(approvalType)) {
            throw new Error(`Stakeholder ${stakeholderId} is not authorized to approve ${approvalType}`);
        }

        const approval = {
            id: this.generateApprovalId(),
            type: approvalType,
            context: context,
            requestedAt: new Date(),
            requestedFrom: stakeholderId,
            status: 'pending',
            deadline: this.calculateApprovalDeadline(approvalType),
            urgency: this.determineApprovalUrgency(approvalType),
            documents: context.documents || [],
            comments: []
        };

        this.approvals.set(approval.id, approval);

        // Send approval notification
        await this.sendNotification('approval_required', {
            approvalId: approval.id,
            approvalType: approvalType,
            stakeholderId: stakeholderId,
            deadline: approval.deadline
        });

        this.emit('approval:requested', approval);
        return approval;
    }

    async processApproval(approvalId, decision, comments = '', stakeholderId) {
        const approval = this.approvals.get(approvalId);
        if (!approval) {
            throw new Error(`Approval ${approvalId} not found`);
        }

        if (approval.requestedFrom !== stakeholderId) {
            throw new Error(`Stakeholder ${stakeholderId} is not authorized to respond to this approval`);
        }

        approval.status = decision; // 'approved', 'rejected', 'needs_revision'
        approval.respondedAt = new Date();
        approval.comments.push({
            stakeholderId: stakeholderId,
            comment: comments,
            timestamp: new Date()
        });

        // Notify relevant parties of approval decision
        await this.sendApprovalDecisionNotification(approval);

        this.emit('approval:processed', approval);
        return approval;
    }

    // Feedback Collection
    async collectStakeholderFeedback(stakeholderId, feedbackType, context) {
        const stakeholder = this.stakeholders.get(stakeholderId);
        if (!stakeholder) {
            throw new Error(`Stakeholder ${stakeholderId} not found`);
        }

        const feedback = {
            id: this.generateFeedbackId(),
            stakeholderId: stakeholderId,
            type: feedbackType,
            context: context,
            collectedAt: new Date(),
            phase: this.bmadSystem.currentPhase,
            rating: null,
            comments: '',
            suggestions: [],
            concerns: [],
            status: 'collected'
        };

        this.feedback.set(feedback.id, feedback);
        this.emit('feedback:collected', feedback);
        
        return feedback;
    }

    async analyzeFeedbackTrends() {
        const allFeedback = Array.from(this.feedback.values());
        
        const analysis = {
            overall_satisfaction: this.calculateAverageSatisfaction(allFeedback),
            trends_by_phase: this.analyzeFeedbackByPhase(allFeedback),
            trends_by_stakeholder: this.analyzeFeedbackByStakeholder(allFeedback),
            common_concerns: this.identifyCommonConcerns(allFeedback),
            improvement_opportunities: this.identifyImprovementOpportunities(allFeedback),
            action_items: this.generateFeedbackActionItems(allFeedback)
        };

        this.emit('feedback:analyzed', analysis);
        return analysis;
    }

    // Meeting Management
    async scheduleMeeting(meetingType, participants, agenda, datetime) {
        const meeting = {
            id: this.generateMeetingId(),
            type: meetingType,
            participants: participants,
            agenda: agenda,
            scheduledAt: datetime,
            timezone: 'UTC',
            duration: this.getMeetingDuration(meetingType),
            location: this.getMeetingLocation(meetingType),
            materials: [],
            status: 'scheduled',
            createdAt: new Date()
        };

        this.meetings.set(meeting.id, meeting);

        // Send meeting invitations
        for (const participantId of participants) {
            await this.sendMeetingInvitation(meeting, participantId);
        }

        this.emit('meeting:scheduled', meeting);
        return meeting;
    }

    // Utility Methods
    determineReportType(stakeholder) {
        const roleReportMap = {
            'executive': 'executive_summary',
            'technical_executive': 'technical_progress',
            'product_management': 'product_status',
            'finance': 'financial_status',
            'marketing': 'product_status',
            'quality_assurance': 'technical_progress'
        };

        return roleReportMap[stakeholder.role] || 'executive_summary';
    }

    getStakeholderFocus(stakeholder, contentType) {
        const focusMap = {
            'health': stakeholder.concerns,
            'achievements': this.getAchievementFocus(stakeholder),
            'issues': this.getIssueFocus(stakeholder)
        };

        return focusMap[contentType] || [];
    }

    getAchievementFocus(stakeholder) {
        const roleAchievementFocus = {
            'executive': ['business_value', 'milestone_completion', 'roi_impact'],
            'technical_executive': ['technical_milestones', 'architecture_progress', 'quality_improvements'],
            'product_management': ['feature_completion', 'user_value', 'market_validation'],
            'finance': ['budget_performance', 'cost_savings', 'roi_achievements'],
            'quality_assurance': ['quality_improvements', 'defect_reduction', 'test_coverage'],
            'marketing': ['market_validation', 'customer_feedback', 'competitive_advantages']
        };

        return roleAchievementFocus[stakeholder.role] || ['general_progress'];
    }

    getSeverityWeight(severity) {
        const weights = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        };
        return weights[severity] || 0;
    }

    generateReportId() {
        return `RPT-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    generateNotificationId() {
        return `NOT-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    generateApprovalId() {
        return `APP-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    generateFeedbackId() {
        return `FBK-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    generateMeetingId() {
        return `MTG-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    // API Methods for External Integration
    getStakeholderDashboard(stakeholderId) {
        const stakeholder = this.stakeholders.get(stakeholderId);
        if (!stakeholder) {
            throw new Error(`Stakeholder ${stakeholderId} not found`);
        }

        return {
            stakeholder: stakeholder,
            recent_reports: this.getRecentReports(stakeholderId),
            pending_approvals: this.getPendingApprovals(stakeholderId),
            recent_notifications: this.getRecentNotifications(stakeholderId),
            upcoming_meetings: this.getUpcomingMeetings(stakeholderId),
            feedback_requests: this.getPendingFeedbackRequests(stakeholderId)
        };
    }

    getAllStakeholders() {
        return Array.from(this.stakeholders.values()).map(stakeholder => ({
            id: stakeholder.id,
            name: stakeholder.name,
            role: stakeholder.role,
            influence: stakeholder.influence,
            interest: stakeholder.interest,
            communication_preference: stakeholder.communication_preference,
            last_interaction: this.getLastInteraction(stakeholder.id)
        }));
    }

    getCommunicationMetrics() {
        return {
            total_stakeholders: this.stakeholders.size,
            reports_generated: this.reports.size,
            notifications_sent: this.notifications.size,
            approvals_processed: Array.from(this.approvals.values()).filter(a => a.status !== 'pending').length,
            feedback_collected: this.feedback.size,
            meetings_scheduled: this.meetings.size,
            stakeholder_satisfaction: this.calculateOverallStakeholderSatisfaction(),
            communication_effectiveness: this.calculateCommunicationEffectiveness()
        };
    }
}

module.exports = StakeholderCommunication;