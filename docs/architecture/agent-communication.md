# Agent Communication Patterns (v2.1)

This document describes how agents communicate and coordinate within the Claude Code Agent System v2.1 using the 4-stack architecture.

## Overview

The 28 agents work together through structured communication patterns orchestrated by @agent-master-orchestrator. Each agent uses @agent- prefix for deterministic routing and follows the 4-stack system for optimal coordination.

## Communication Flow

### 1. Sequential Communication
Agents pass information in a defined sequence:

```
@agent-business-analyst → @agent-technical-cto → @agent-project-manager → Development Agents
```

**Example**:
```
@agent-business-analyst Output:
- Market size: $5B
- Competition: 3 major players
- ROI projection: 250% Year 2

@agent-technical-cto Input: (receives above)
@agent-technical-cto Output:
- Tech stack: React + Node.js + PostgreSQL
- Feasibility: High
- Time estimate: 6 months
```

### 2. Parallel Communication Across Stacks
Multiple agents work simultaneously across the 4-stack system:

```
Stack 2: Architecture         Stack 3: Implementation      Stack 4: Operations
@agent-frontend-architecture  @agent-production-frontend   @agent-testing-automation
@agent-database-architecture  @agent-backend-services      @agent-devops-engineering
@agent-api-integration       @agent-mobile-development    @agent-security-architecture
```

### 3. Hub Communication with @agent-master-orchestrator
Central orchestration using slash commands:

```
/start-project → @agent-master-orchestrator
                          │
        ┌─────────────────┼─────────────────┐
Stack 1: Business    Stack 2: Technical    Stack 3: Implementation
@agent-business-analyst  @agent-technical-cto    @agent-backend-services
@agent-financial-analyst @agent-technical-specifications @agent-production-frontend
@agent-ceo-strategy     @agent-database-architecture @agent-mobile-development
```

## Data Exchange Formats

### Standard Output Format (v2.1)
Each agent produces structured output with @agent- routing:

```yaml
agent: @agent-business-analyst
stack: 1
timestamp: 2024-01-15T10:30:00Z
status: completed
cost_optimization: enabled
output:
  analysis:
    market_size: "$5B"
    growth_rate: "15% YoY"
  recommendations:
    - "Focus on SMB segment"
    - "Freemium pricing model"
  next_agents:
    - @agent-technical-cto
    - @agent-financial-analyst
  routing: deterministic
```

### Integration Points

#### Upstream Dependencies with 4-Stack Routing
Agents receive input based on stack position:
```
@agent-technical-specifications:
  stack: 2
  receives_from:
    - @agent-business-analyst (Stack 1)
    - @agent-technical-cto (Stack 1)
    - @agent-project-manager (Stack 1)
  slash_command: /technical-specs
```

#### Downstream Consumers
Agents provide output to next stack:
```
@agent-frontend-architecture:
  stack: 2
  provides_to:
    - @agent-frontend-mockup (Stack 2)
    - @agent-production-frontend (Stack 3)
    - @agent-mobile-development (Stack 3)
  routing: @agent-prefix
```

## Coordination Patterns (v2.1 4-Stack System)

### 1. Stack-Based Sequential Flow
Follows the 4-stack architecture:

```
Stack 1: Business → Stack 2: Architecture → Stack 3: Implementation → Stack 4: Operations
/analyze → /design → /build → /deploy
```

### 2. Agile Pattern with Slash Commands
Iterative cycles using commands:

```
/sprint-plan → /develop → /test → /review → /iterate
@agent-project-manager ↔ Development Agents ↔ @agent-testing-automation
```

### 3. Concurrent Pattern Across Stacks
Maximize parallel execution within stacks:

```
Stack 1 (Business)    Stack 2 (Technical)    Stack 3 (Development)
    Parallel              Parallel               Parallel
@agent-business-analyst  @agent-frontend-architecture  @agent-production-frontend
@agent-financial-analyst @agent-database-architecture  @agent-backend-services
@agent-ceo-strategy     @agent-api-integration        @agent-mobile-development
```

## Message Types

### 1. Task Assignment (v2.1)
```json
{
  "type": "task_assignment",
  "from": "@agent-master-orchestrator",
  "to": "@agent-database-architecture",
  "stack": 2,
  "task": "Design multi-tenant schema",
  "slash_command": "/database-design",
  "context": {
    "project_type": "saas",
    "requirements": ["data_isolation", "scalability"],
    "cost_optimization": "enabled"
  }
}
```

### 2. Status Update with Stack Info
```json
{
  "type": "status_update",
  "from": "@agent-backend-services",
  "stack": 3,
  "status": "in_progress",
  "progress": 65,
  "eta": "2 hours",
  "routing": "deterministic"
}
```

### 3. Cross-Stack Deliverable Handoff
```json
{
  "type": "deliverable",
  "from": "@agent-frontend-mockup",
  "from_stack": 2,
  "to": ["@agent-production-frontend", "@agent-ui-ux-design"],
  "to_stacks": [3, 2],
  "deliverable": {
    "type": "wireframes",
    "files": ["dashboard.html", "login.html"],
    "notes": "Mobile-first responsive design",
    "agent_prefix": "@agent-"
  }
}
```

## Conflict Resolution

### Priority Rules
1. Business requirements override technical preferences
2. Security requirements override performance optimizations
3. User experience overrides developer convenience
4. Compliance requirements override all

### Conflict Escalation
```
Agent Conflict → Master Orchestrator → Human Decision Point
```

## Best Practices

### 1. Clear Handoffs
- Always specify what's completed
- List what's needed next
- Include relevant context

### 2. Validation Points
- Verify input before processing
- Validate output before handoff
- Check integration compatibility

### 3. Error Handling
- Report blockers immediately
- Suggest alternatives
- Maintain project momentum

## Communication Examples

### Example 1: API Design Flow with Slash Commands
```bash
/api-service "Payment Processing"
1. @agent-business-analyst: "Need payment processing" (Stack 1)
2. @agent-technical-cto: "Recommend Stripe + backup provider" (Stack 1)
3. @agent-api-integration-specialist: "Design unified payment interface" (Stack 2)
4. @agent-backend-services: "Implement payment service" (Stack 3)
5. @agent-testing-automation: "Create payment test suite" (Stack 4)
```

### Example 2: Frontend Feature Flow Across Stacks
```bash
/frontend "User Dashboard"
1. @agent-ui-ux-design: "User dashboard wireframes" (Stack 2)
2. @agent-frontend-mockup: "HTML/CSS prototype" (Stack 2)
3. @agent-frontend-architecture: "Component structure" (Stack 2)
4. @agent-production-frontend: "React implementation" (Stack 3)
5. @agent-testing-automation: "Component tests" (Stack 4)
```

## Monitoring & Optimization (v2.1)

### Communication Metrics with 60% Cost Optimization
- Agent routing efficiency (@agent- prefix)
- Stack transition latency
- Parallel execution rate within stacks
- Slash command response time
- Cost reduction per workflow

### Optimization Strategies for 4-Stack System
- Maximize intra-stack parallelization
- Use deterministic @agent- routing
- Leverage slash commands for quick access
- Batch operations within same stack
- Enable automatic cost optimization

## v2.1 Communication Benefits

1. **Deterministic Routing**: @agent- prefix ensures predictable agent selection
2. **Stack Isolation**: Clear boundaries between business, technical, implementation, and operations
3. **Cost Efficiency**: 60% reduction through optimized routing and parallel execution
4. **Slash Commands**: Quick access to common workflows
5. **Context Preservation**: Seamless handoffs between agents and stacks

---

This v2.1 communication system leverages the 4-stack architecture with @agent- prefixed routing and slash commands to ensure efficient, cost-optimized coordination between all 28 agents.