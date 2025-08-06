# Master Prompts - Project Initialization (v2.1 4-Stack)

These universal prompts help you start any type of project using the Claude Code Agent System v2.1 with slash commands, @agent- mentions, MCPs, and hooks automation. Replace all variables in square brackets with your specific values.

## Full Project Initialization with Slash Commands

```
/new-project "[PROJECT_TYPE] for [TARGET_AUDIENCE] that [CORE_FUNCTIONALITY]. Key requirements: [REQUIREMENT_1], [REQUIREMENT_2], [REQUIREMENT_3]. Technology preferences: [TECH_STACK]. Budget: [BUDGET_RANGE]. Timeline: [TIMELINE]. Success metrics: [METRIC_1], [METRIC_2]"
```

**MCPs Activated**: GitHub API, Docker, Cloud platforms (based on tech stack)
**Hooks**: Pre-project validation, dependency check, cost estimation

## Business Analysis with @agent- Routing

```
@agent-business-analyst Analyze market opportunity for [PRODUCT/SERVICE] targeting [MARKET_SEGMENT] with [VALUE_PROPOSITION]. Include TAM analysis, competitive landscape, pricing models, and [SPECIFIC_ANALYSIS_FOCUS]
```

**MCPs Activated**: Market data APIs, Analytics tools
**Hooks**: Market validation, competitor analysis automation

## Technical Feasibility Assessment

```
@agent-technical-cto Assess feasibility of [PROJECT_CONCEPT] supporting [USER_COUNT] users with [PERFORMANCE_REQUIREMENT]. Evaluate [TECHNOLOGY_OPTIONS] for [SPECIFIC_CONSTRAINTS]
```

**MCPs Activated**: Performance benchmarking tools, Cloud calculators
**Hooks**: Infrastructure cost optimization, scalability validation

## Project Planning with Automation

```
@agent-project-manager Create project plan for [PROJECT_NAME] with [TEAM_SIZE] developers, [BUDGET] budget, and [DEADLINE] deadline. Include [METHODOLOGY] methodology and [DELIVERABLE_FREQUENCY] deliverables
```

**MCPs Activated**: Jira/Linear API, Calendar integrations
**Hooks**: Sprint automation, milestone tracking

## Financial Projections

```
@agent-financial-analyst Create financial model for [BUSINESS_MODEL] with [PRICING_STRUCTURE] serving [CUSTOMER_SEGMENT]. Project [TIME_HORIZON] with [GROWTH_ASSUMPTIONS]
```

**MCPs Activated**: Financial modeling tools, Market data APIs
**Hooks**: Sensitivity analysis, scenario planning

## Strategic Positioning

```
@agent-ceo-strategy Develop go-to-market strategy for [PRODUCT/SERVICE] differentiating through [UNIQUE_VALUE]. Target market: [MARKET]. Competition: [COMPETITORS]. Distribution: [CHANNELS]
```

**MCPs Activated**: Market intelligence APIs, CRM integrations
**Hooks**: Strategy validation, market fit analysis

## Requirements Gathering with MCPs

```
@agent-technical-specifications Document requirements for [SYSTEM_NAME] supporting [USE_CASES]. Include [FUNCTIONAL_REQUIREMENTS], [NON_FUNCTIONAL_REQUIREMENTS], and [INTEGRATION_REQUIREMENTS]
```

**MCPs Activated**: Documentation tools, Diagram generators
**Hooks**: Requirements validation, traceability matrix

## Architecture Design

```
@agent-software-architect Design architecture for [APPLICATION_TYPE] handling [SCALE_REQUIREMENTS] with [PERFORMANCE_TARGETS]. Consider [CONSTRAINTS] and integrate with [EXISTING_SYSTEMS]
```

**MCPs Activated**: Architecture diagramming tools, Cloud design tools
**Hooks**: Architecture validation, cost optimization

## Quick Start Templates (v2.1)

### Minimal Project Start with Slash Command
```
/new-project "[PROJECT_TYPE] that [CORE_FUNCTION]"
```
*Automatically routes to @agent-master-orchestrator with basic MCPs*

### Business-First Approach
```
/validate-idea "[BUSINESS_IDEA] for [TARGET_MARKET]"
```
*Routes to @agent-business-analyst → @agent-financial-analyst*

### Technical-First Approach
```
/design-solution "[TECHNICAL_SOLUTION] for [PROBLEM_STATEMENT]"
```
*Routes to @agent-technical-cto → @agent-software-architect*

## Multi-Agent Collaboration Examples

### Complete Project Setup
```
/new-project "SaaS platform for project management"

This triggers:
1. @agent-master-orchestrator coordinates overall flow
2. @agent-business-analyst validates market opportunity
3. @agent-technical-cto designs technical approach
4. @agent-project-manager creates implementation plan
5. @agent-devops-engineer sets up CI/CD pipeline

MCPs activated: GitHub, Docker, AWS/GCP, Jira
Hooks: Cost monitoring, progress tracking, quality gates
```

### Rapid Prototyping
```
/rapid-prototype "[APP_IDEA] using [TECH_STACK]"

Agent flow:
@agent-frontend-engineer + @agent-backend-engineer collaborate
MCPs: Framework CLIs, Database tools, Deploy buttons
Hooks: Auto-testing, performance monitoring
```

## Variable Reference

- `[PROJECT_TYPE]`: web application, mobile app, API service, platform, system
- `[TARGET_AUDIENCE]`: B2B companies, consumers, enterprise, specific industry
- `[CORE_FUNCTIONALITY]`: main purpose and key features
- `[REQUIREMENT_N]`: specific functional or technical requirements
- `[TECH_STACK]`: preferred languages, frameworks, databases
- `[BUDGET_RANGE]`: available budget or cost constraints
- `[TIMELINE]`: project deadline or milestones
- `[METRIC_N]`: success criteria and KPIs
- `[MARKET_SEGMENT]`: specific market or industry vertical
- `[VALUE_PROPOSITION]`: unique value offered
- `[USER_COUNT]`: expected number of users
- `[PERFORMANCE_REQUIREMENT]`: response time, throughput, availability
- `[TEAM_SIZE]`: number of developers/resources
- `[METHODOLOGY]`: agile, waterfall, hybrid
- `[TIME_HORIZON]`: projection period (e.g., 5 years)
- `[GROWTH_ASSUMPTIONS]`: growth rate, scaling factors