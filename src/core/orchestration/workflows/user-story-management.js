/**
 * User Story Management System for BMAD Workflows
 * Manages user stories, acceptance criteria, and requirements traceability
 */

const { EventEmitter } = require('events');

class UserStoryManagement extends EventEmitter {
    constructor(bmadSystem) {
        super();
        this.bmadSystem = bmadSystem;
        this.storyTemplates = new Map();
        this.epicTemplates = new Map();
        this.acceptanceCriteriaPatterns = new Map();
        this.requirementsTraceability = new Map();
        this.storyRelationships = new Map();
        
        this.initializeTemplates();
    }

    initializeTemplates() {
        this.setupStoryTemplates();
        this.setupEpicTemplates();
        this.setupAcceptanceCriteriaPatterns();
        console.log('📝 User story management system initialized');
    }

    setupStoryTemplates() {
        // Business Model Phase Stories
        this.storyTemplates.set('business-model-canvas', {
            phase: 'business_model',
            template: {
                title: 'Create Business Model Canvas for {domain}',
                description: 'As a {role}, I want to create a comprehensive business model canvas so that {outcome}',
                acceptanceCriteria: [
                    'Value propositions are clearly defined',
                    'Customer segments are identified and validated',
                    'Revenue streams are specified',
                    'Key partnerships are identified',
                    'Cost structure is analyzed',
                    'Key activities and resources are mapped'
                ],
                estimatedPoints: 8,
                tags: ['business-model', 'canvas', 'strategy'],
                relatedWorkflows: ['business-model-analysis']
            }
        });

        this.storyTemplates.set('market-research', {
            phase: 'business_model',
            template: {
                title: 'Conduct Market Research for {target_market}',
                description: 'As a {role}, I want to conduct comprehensive market research so that {outcome}',
                acceptanceCriteria: [
                    'Market size is quantified',
                    'Target customer personas are defined',
                    'Competitive landscape is mapped',
                    'Market trends are analyzed',
                    'Pricing strategies are researched',
                    'Market entry barriers are identified'
                ],
                estimatedPoints: 13,
                tags: ['market-research', 'analysis', 'validation'],
                relatedWorkflows: ['business-model-analysis']
            }
        });

        // Architecture Phase Stories
        this.storyTemplates.set('system-architecture', {
            phase: 'architecture',
            template: {
                title: 'Design System Architecture for {system_type}',
                description: 'As a {role}, I want to design a scalable system architecture so that {outcome}',
                acceptanceCriteria: [
                    'Architecture diagram is created',
                    'Technology stack is selected and justified',
                    'Scalability requirements are addressed',
                    'Security considerations are included',
                    'Integration points are specified',
                    'Performance requirements are defined'
                ],
                estimatedPoints: 21,
                tags: ['architecture', 'design', 'scalability'],
                relatedWorkflows: ['architecture-planning']
            }
        });

        this.storyTemplates.set('database-design', {
            phase: 'architecture',
            template: {
                title: 'Design Database Schema for {domain}',
                description: 'As a {role}, I want to design an optimized database schema so that {outcome}',
                acceptanceCriteria: [
                    'Entity-relationship diagram is created',
                    'Data normalization is applied',
                    'Indexing strategy is defined',
                    'Performance considerations are addressed',
                    'Security measures are included',
                    'Backup and recovery strategy is planned'
                ],
                estimatedPoints: 13,
                tags: ['database', 'schema', 'optimization'],
                relatedWorkflows: ['architecture-planning']
            }
        });

        // Design Phase Stories
        this.storyTemplates.set('user-experience-design', {
            phase: 'design',
            template: {
                title: 'Design User Experience for {feature}',
                description: 'As a {role}, I want to design an intuitive user experience so that {outcome}',
                acceptanceCriteria: [
                    'User journey maps are created',
                    'Wireframes are designed',
                    'User flows are documented',
                    'Accessibility standards are met',
                    'Usability testing is conducted',
                    'Design system components are defined'
                ],
                estimatedPoints: 8,
                tags: ['ux', 'design', 'usability'],
                relatedWorkflows: ['design-implementation']
            }
        });

        this.storyTemplates.set('visual-design', {
            phase: 'design',
            template: {
                title: 'Create Visual Design for {component}',
                description: 'As a {role}, I want to create compelling visual designs so that {outcome}',
                acceptanceCriteria: [
                    'Visual mockups are created',
                    'Brand guidelines are followed',
                    'Color palette is defined',
                    'Typography system is established',
                    'Icon library is created',
                    'Responsive design is ensured'
                ],
                estimatedPoints: 5,
                tags: ['visual-design', 'branding', 'responsive'],
                relatedWorkflows: ['design-implementation']
            }
        });

        // Development Phase Stories
        this.storyTemplates.set('feature-implementation', {
            phase: 'development',
            template: {
                title: 'Implement {feature_name} Feature',
                description: 'As a {role}, I want to implement {feature_name} so that {outcome}',
                acceptanceCriteria: [
                    'Feature functionality is implemented',
                    'Unit tests are written and passing',
                    'Integration tests are implemented',
                    'Code review is completed',
                    'Documentation is updated',
                    'Performance benchmarks are met'
                ],
                estimatedPoints: 8,
                tags: ['implementation', 'feature', 'development'],
                relatedWorkflows: ['development-coordination']
            }
        });

        this.storyTemplates.set('api-development', {
            phase: 'development',
            template: {
                title: 'Develop {api_name} API',
                description: 'As a {role}, I want to develop a reliable API so that {outcome}',
                acceptanceCriteria: [
                    'API endpoints are implemented',
                    'OpenAPI specification is created',
                    'Authentication is implemented',
                    'Rate limiting is configured',
                    'Error handling is robust',
                    'API documentation is complete'
                ],
                estimatedPoints: 13,
                tags: ['api', 'backend', 'integration'],
                relatedWorkflows: ['development-coordination']
            }
        });
    }

    setupEpicTemplates() {
        this.epicTemplates.set('business-model-validation', {
            name: 'Business Model Validation',
            description: 'Validate the business model through market research, customer validation, and financial modeling',
            phase: 'business_model',
            expectedStories: 8,
            estimatedPoints: 89,
            duration: '3-4 sprints',
            successCriteria: [
                'Validated value proposition',
                'Identified target market',
                'Proven revenue model',
                'Competitive positioning established'
            ]
        });

        this.epicTemplates.set('system-architecture-design', {
            name: 'System Architecture Design',
            description: 'Design comprehensive system architecture including technology stack, scalability, and security',
            phase: 'architecture',
            expectedStories: 12,
            estimatedPoints: 144,
            duration: '4-5 sprints',
            successCriteria: [
                'Scalable architecture designed',
                'Technology stack selected',
                'Security framework established',
                'Performance requirements defined'
            ]
        });

        this.epicTemplates.set('user-experience-optimization', {
            name: 'User Experience Optimization',
            description: 'Create optimal user experience through research, design, and validation',
            phase: 'design',
            expectedStories: 10,
            estimatedPoints: 89,
            duration: '3-4 sprints',
            successCriteria: [
                'User-centered design created',
                'Accessibility compliance achieved',
                'Usability validated',
                'Design system established'
            ]
        });

        this.epicTemplates.set('mvp-development', {
            name: 'MVP Development',
            description: 'Develop minimum viable product with core features and functionality',
            phase: 'development',
            expectedStories: 20,
            estimatedPoints: 233,
            duration: '6-8 sprints',
            successCriteria: [
                'Core features implemented',
                'Quality benchmarks met',
                'User acceptance achieved',
                'Production ready'
            ]
        });
    }

    setupAcceptanceCriteriaPatterns() {
        // Business Model patterns
        this.acceptanceCriteriaPatterns.set('business-validation', [
            {
                type: 'market-validation',
                pattern: 'Given a target market hypothesis, when market research is conducted, then the market size and opportunity should be quantified with supporting data'
            },
            {
                type: 'customer-validation',
                pattern: 'Given customer personas, when customer interviews are conducted, then the persona assumptions should be validated or refined based on evidence'
            },
            {
                type: 'value-proposition-validation',
                pattern: 'Given a value proposition, when customer feedback is collected, then the value proposition should resonate with target customers'
            }
        ]);

        // Architecture patterns
        this.acceptanceCriteriaPatterns.set('architecture-validation', [
            {
                type: 'scalability-validation',
                pattern: 'Given scalability requirements, when load testing is performed, then the system should handle expected load without performance degradation'
            },
            {
                type: 'security-validation',
                pattern: 'Given security requirements, when security testing is performed, then no critical vulnerabilities should be found'
            },
            {
                type: 'integration-validation',
                pattern: 'Given integration requirements, when integration testing is performed, then all systems should communicate reliably'
            }
        ]);

        // Design patterns
        this.acceptanceCriteriaPatterns.set('design-validation', [
            {
                type: 'usability-validation',
                pattern: 'Given usability requirements, when user testing is conducted, then users should be able to complete tasks efficiently'
            },
            {
                type: 'accessibility-validation',
                pattern: 'Given accessibility requirements, when accessibility testing is performed, then the design should meet WCAG 2.1 AA standards'
            },
            {
                type: 'responsive-validation',
                pattern: 'Given responsive design requirements, when tested across devices, then the design should work effectively on all target screen sizes'
            }
        ]);

        // Development patterns
        this.acceptanceCriteriaPatterns.set('development-validation', [
            {
                type: 'functional-validation',
                pattern: 'Given functional requirements, when feature testing is performed, then all specified functionality should work as expected'
            },
            {
                type: 'performance-validation',
                pattern: 'Given performance requirements, when performance testing is conducted, then response times should meet specified benchmarks'
            },
            {
                type: 'quality-validation',
                pattern: 'Given quality requirements, when code review is performed, then code should meet quality standards and have adequate test coverage'
            }
        ]);
    }

    // Create User Story from Template
    async createStoryFromTemplate(templateId, customizations = {}) {
        const template = this.storyTemplates.get(templateId);
        if (!template) {
            throw new Error(`Story template ${templateId} not found`);
        }

        const story = {
            id: this.generateStoryId(),
            templateId: templateId,
            title: this.interpolateTemplate(template.template.title, customizations),
            description: this.interpolateTemplate(template.template.description, customizations),
            asA: customizations.role || 'user',
            iWant: customizations.want || 'functionality',
            soThat: customizations.outcome || 'value is delivered',
            phase: template.phase,
            workflow: template.template.relatedWorkflows[0],
            acceptanceCriteria: await this.generateAcceptanceCriteriaFromTemplate(template, customizations),
            estimatedPoints: template.template.estimatedPoints,
            priority: customizations.priority || 'medium',
            tags: [...template.template.tags, ...(customizations.tags || [])],
            status: 'backlog',
            createdAt: new Date(),
            updatedAt: new Date(),
            createdBy: customizations.createdBy || 'system',
            epic: customizations.epic || null,
            sprint: null,
            assignedAgent: null,
            dependencies: customizations.dependencies || [],
            blockers: [],
            comments: [],
            attachments: [],
            testCases: [],
            bmadMetadata: {
                phaseAlignment: template.phase,
                workflowIntegration: template.template.relatedWorkflows,
                qualityGates: await this.getRequiredQualityGates(template.phase),
                stakeholders: await this.identifyStakeholders(template.phase)
            }
        };

        // Add to system
        this.bmadSystem.userStories.set(story.id, story);
        
        // Create requirements traceability
        await this.createRequirementsTraceability(story);
        
        this.emit('story:created', story);
        return story;
    }

    // Create Epic from Template
    async createEpicFromTemplate(templateId, customizations = {}) {
        const template = this.epicTemplates.get(templateId);
        if (!template) {
            throw new Error(`Epic template ${templateId} not found`);
        }

        const epic = {
            id: this.generateEpicId(),
            templateId: templateId,
            name: customizations.name || template.name,
            description: customizations.description || template.description,
            phase: template.phase,
            expectedStories: template.expectedStories,
            estimatedPoints: template.estimatedPoints,
            duration: template.duration,
            successCriteria: template.successCriteria,
            status: 'planning',
            priority: customizations.priority || 'high',
            createdAt: new Date(),
            updatedAt: new Date(),
            createdBy: customizations.createdBy || 'system',
            stakeholders: customizations.stakeholders || [],
            budget: customizations.budget || null,
            timeline: customizations.timeline || null,
            risks: customizations.risks || [],
            assumptions: customizations.assumptions || [],
            stories: [],
            bmadMetadata: {
                phaseAlignment: template.phase,
                milestones: await this.generateEpicMilestones(template),
                qualityGates: await this.getRequiredQualityGates(template.phase),
                deliverables: await this.getExpectedDeliverables(template.phase)
            }
        };

        this.emit('epic:created', epic);
        return epic;
    }

    // Generate Acceptance Criteria
    async generateAcceptanceCriteriaFromTemplate(template, customizations) {
        const criteria = [];
        const patterns = this.acceptanceCriteriaPatterns.get(`${template.phase}-validation`) || [];

        // Add template-specific criteria
        for (const criteriaText of template.template.acceptanceCriteria) {
            criteria.push({
                id: this.generateCriteriaId(),
                description: this.interpolateTemplate(criteriaText, customizations),
                priority: 'must',
                type: 'functional',
                testable: true,
                automatable: false,
                validated: false,
                validationMethod: 'manual',
                givenWhenThen: null,
                notes: ''
            });
        }

        // Add pattern-based criteria
        for (const pattern of patterns) {
            criteria.push({
                id: this.generateCriteriaId(),
                description: `Pattern: ${pattern.type}`,
                priority: 'should',
                type: 'behavioral',
                testable: true,
                automatable: true,
                validated: false,
                validationMethod: 'automated',
                givenWhenThen: this.parseGivenWhenThen(pattern.pattern),
                notes: `Generated from ${pattern.type} pattern`
            });
        }

        return criteria;
    }

    // Requirements Traceability
    async createRequirementsTraceability(story) {
        const traceability = {
            storyId: story.id,
            businessRequirements: await this.identifyBusinessRequirements(story),
            functionalRequirements: await this.identifyFunctionalRequirements(story),
            nonFunctionalRequirements: await this.identifyNonFunctionalRequirements(story),
            testCases: [],
            implementationTasks: [],
            qualityGates: story.bmadMetadata.qualityGates,
            stakeholders: story.bmadMetadata.stakeholders,
            traceMatrix: {
                businessToFunctional: {},
                functionalToTest: {},
                testToImplementation: {},
                implementationToQuality: {}
            }
        };

        this.requirementsTraceability.set(story.id, traceability);
        return traceability;
    }

    // Story Relationships
    async createStoryRelationship(sourceStoryId, targetStoryId, relationshipType) {
        const validTypes = ['depends-on', 'blocks', 'relates-to', 'duplicates', 'epic-child', 'split-from'];
        
        if (!validTypes.includes(relationshipType)) {
            throw new Error(`Invalid relationship type: ${relationshipType}`);
        }

        const relationship = {
            id: this.generateRelationshipId(),
            sourceStoryId,
            targetStoryId,
            type: relationshipType,
            createdAt: new Date(),
            createdBy: 'system',
            notes: ''
        };

        const key = `${sourceStoryId}:${targetStoryId}`;
        this.storyRelationships.set(key, relationship);

        // Update story dependencies
        if (relationshipType === 'depends-on') {
            const sourceStory = this.bmadSystem.userStories.get(sourceStoryId);
            if (sourceStory) {
                sourceStory.dependencies.push(targetStoryId);
                sourceStory.updatedAt = new Date();
            }
        }

        this.emit('story:relationship-created', relationship);
        return relationship;
    }

    // Story Estimation
    async estimateStory(storyId, method = 'planning-poker') {
        const story = this.bmadSystem.userStories.get(storyId);
        if (!story) {
            throw new Error(`Story ${storyId} not found`);
        }

        const estimation = {
            storyId: storyId,
            method: method,
            participants: [],
            estimates: [],
            consensus: null,
            complexity: await this.analyzeStoryComplexity(story),
            risks: await this.identifyEstimationRisks(story),
            assumptions: [],
            finalEstimate: null,
            confidence: null,
            sessionDate: new Date()
        };

        // Analyze story complexity
        estimation.complexity = await this.analyzeStoryComplexity(story);
        
        // Generate initial estimate based on template and complexity
        estimation.finalEstimate = await this.generateInitialEstimate(story, estimation.complexity);
        
        // Set confidence based on complexity and risks
        estimation.confidence = await this.calculateEstimationConfidence(estimation);

        // Update story
        story.estimatedPoints = estimation.finalEstimate;
        story.estimationConfidence = estimation.confidence;
        story.estimationHistory = story.estimationHistory || [];
        story.estimationHistory.push(estimation);
        story.updatedAt = new Date();

        this.emit('story:estimated', { story, estimation });
        return estimation;
    }

    // Story Validation
    async validateStory(storyId) {
        const story = this.bmadSystem.userStories.get(storyId);
        if (!story) {
            throw new Error(`Story ${storyId} not found`);
        }

        const validation = {
            storyId: storyId,
            validationDate: new Date(),
            isValid: true,
            errors: [],
            warnings: [],
            suggestions: [],
            checklist: {
                hasTitle: !!story.title,
                hasDescription: !!story.description,
                hasAcceptanceCriteria: story.acceptanceCriteria && story.acceptanceCriteria.length > 0,
                hasEstimate: !!story.estimatedPoints,
                hasPriority: !!story.priority,
                hasPhase: !!story.phase,
                hasWorkflow: !!story.workflow,
                followsINVEST: await this.checkINVESTCriteria(story),
                meetsBMADRequirements: await this.checkBMADRequirements(story)
            }
        };

        // Validate INVEST criteria
        const investResults = await this.validateINVEST(story);
        validation.checklist.followsINVEST = investResults.valid;
        if (!investResults.valid) {
            validation.errors.push(...investResults.errors);
            validation.warnings.push(...investResults.warnings);
        }

        // Validate BMAD requirements
        const bmadResults = await this.validateBMADRequirements(story);
        validation.checklist.meetsBMADRequirements = bmadResults.valid;
        if (!bmadResults.valid) {
            validation.errors.push(...bmadResults.errors);
        }

        // Check for completeness
        const completenessResults = await this.validateCompleteness(story);
        if (!completenessResults.valid) {
            validation.errors.push(...completenessResults.errors);
        }

        validation.isValid = validation.errors.length === 0;

        this.emit('story:validated', { story, validation });
        return validation;
    }

    // INVEST Validation (Independent, Negotiable, Valuable, Estimable, Small, Testable)
    async validateINVEST(story) {
        const results = {
            valid: true,
            errors: [],
            warnings: [],
            criteria: {
                independent: true,
                negotiable: true,
                valuable: true,
                estimable: true,
                small: true,
                testable: true
            }
        };

        // Independent: Check for minimal dependencies
        if (story.dependencies && story.dependencies.length > 3) {
            results.criteria.independent = false;
            results.warnings.push('Story has many dependencies - consider breaking down');
        }

        // Negotiable: Check if description allows for discussion
        if (!story.description || story.description.length < 50) {
            results.criteria.negotiable = false;
            results.errors.push('Story description too brief for meaningful negotiation');
        }

        // Valuable: Check if outcome is specified
        if (!story.soThat || story.soThat === 'value is delivered') {
            results.criteria.valuable = false;
            results.errors.push('Story does not clearly specify value or outcome');
        }

        // Estimable: Check if story can be estimated
        if (!story.estimatedPoints) {
            results.criteria.estimable = false;
            results.warnings.push('Story has not been estimated');
        }

        // Small: Check if story points are reasonable
        if (story.estimatedPoints && story.estimatedPoints > 21) {
            results.criteria.small = false;
            results.warnings.push('Story is too large - consider breaking down');
        }

        // Testable: Check if acceptance criteria exist
        if (!story.acceptanceCriteria || story.acceptanceCriteria.length === 0) {
            results.criteria.testable = false;
            results.errors.push('Story lacks testable acceptance criteria');
        }

        results.valid = Object.values(results.criteria).every(Boolean) && results.errors.length === 0;
        return results;
    }

    // Utility Methods
    interpolateTemplate(template, values) {
        let result = template;
        for (const [key, value] of Object.entries(values)) {
            result = result.replace(new RegExp(`{${key}}`, 'g'), value);
        }
        return result;
    }

    parseGivenWhenThen(pattern) {
        const givenMatch = pattern.match(/Given (.+?), when/i);
        const whenMatch = pattern.match(/when (.+?), then/i);
        const thenMatch = pattern.match(/then (.+)$/i);

        return {
            given: givenMatch ? givenMatch[1] : '',
            when: whenMatch ? whenMatch[1] : '',
            then: thenMatch ? thenMatch[1] : ''
        };
    }

    generateStoryId() {
        return `STORY-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    generateEpicId() {
        return `EPIC-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    generateCriteriaId() {
        return `AC-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    generateRelationshipId() {
        return `REL-${Date.now()}-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    }

    async analyzeStoryComplexity(story) {
        let complexity = 'low';
        let score = 0;

        // Factors that increase complexity
        if (story.dependencies && story.dependencies.length > 0) score += story.dependencies.length;
        if (story.phase === 'architecture') score += 3;
        if (story.phase === 'development') score += 2;
        if (story.acceptanceCriteria && story.acceptanceCriteria.length > 5) score += 2;
        if (story.tags.includes('integration')) score += 2;
        if (story.tags.includes('security')) score += 2;
        if (story.tags.includes('performance')) score += 1;

        if (score >= 8) complexity = 'high';
        else if (score >= 4) complexity = 'medium';

        return {
            level: complexity,
            score: score,
            factors: await this.identifyComplexityFactors(story)
        };
    }

    async generateInitialEstimate(story, complexity) {
        const template = this.storyTemplates.get(story.templateId);
        let baseEstimate = template ? template.template.estimatedPoints : 5;

        // Adjust based on complexity
        switch (complexity.level) {
            case 'high':
                baseEstimate *= 1.5;
                break;
            case 'medium':
                baseEstimate *= 1.2;
                break;
            default:
                // low complexity, no adjustment
                break;
        }

        // Adjust based on dependencies
        if (story.dependencies && story.dependencies.length > 0) {
            baseEstimate += story.dependencies.length * 0.5;
        }

        return Math.round(baseEstimate);
    }

    // API Methods
    async getStoriesByPhase(phase) {
        return Array.from(this.bmadSystem.userStories.values())
            .filter(story => story.phase === phase);
    }

    async getStoriesByWorkflow(workflowId) {
        return Array.from(this.bmadSystem.userStories.values())
            .filter(story => story.workflow === workflowId);
    }

    async getStoriesByEpic(epicId) {
        return Array.from(this.bmadSystem.userStories.values())
            .filter(story => story.epic === epicId);
    }

    async getBacklog() {
        return Array.from(this.bmadSystem.userStories.values())
            .filter(story => story.status === 'backlog')
            .sort((a, b) => {
                // Sort by priority first, then by created date
                const priorityWeight = { high: 3, medium: 2, low: 1 };
                const aPriority = priorityWeight[a.priority] || 1;
                const bPriority = priorityWeight[b.priority] || 1;
                
                if (aPriority !== bPriority) {
                    return bPriority - aPriority;
                }
                
                return new Date(b.createdAt) - new Date(a.createdAt);
            });
    }

    getStoryTemplates() {
        return Array.from(this.storyTemplates.entries()).map(([id, template]) => ({
            id,
            name: template.template.title,
            phase: template.phase,
            description: template.template.description,
            estimatedPoints: template.template.estimatedPoints,
            tags: template.template.tags
        }));
    }

    getEpicTemplates() {
        return Array.from(this.epicTemplates.entries()).map(([id, template]) => ({
            id,
            name: template.name,
            phase: template.phase,
            description: template.description,
            expectedStories: template.expectedStories,
            estimatedPoints: template.estimatedPoints,
            duration: template.duration
        }));
    }

    // Export for reporting
    getStoryMetrics() {
        const stories = Array.from(this.bmadSystem.userStories.values());
        
        return {
            total: stories.length,
            byStatus: this.groupByProperty(stories, 'status'),
            byPhase: this.groupByProperty(stories, 'phase'),
            byPriority: this.groupByProperty(stories, 'priority'),
            totalPoints: stories.reduce((sum, story) => sum + (story.estimatedPoints || 0), 0),
            averagePoints: stories.length > 0 ? stories.reduce((sum, story) => sum + (story.estimatedPoints || 0), 0) / stories.length : 0,
            completionRate: stories.filter(s => s.status === 'done').length / stories.length * 100
        };
    }

    groupByProperty(array, property) {
        return array.reduce((groups, item) => {
            const key = item[property] || 'unknown';
            groups[key] = (groups[key] || 0) + 1;
            return groups;
        }, {});
    }
}

module.exports = UserStoryManagement;