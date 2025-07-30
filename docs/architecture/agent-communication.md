# Agent Communication Patterns

This document describes how agents communicate and coordinate within the Claude Code Agent System.

## Overview

The 28 agents work together through structured communication patterns orchestrated by the Master Orchestrator. Each agent has specific input/output interfaces and collaboration protocols.

## Communication Flow

### 1. Sequential Communication
Agents pass information in a defined sequence:

```
Business Analyst → Technical CTO → Project Manager → Development Agents
```

**Example**:
```
Business Analyst Output:
- Market size: $5B
- Competition: 3 major players
- ROI projection: 250% Year 2

Technical CTO Input: (receives above)
Technical CTO Output:
- Tech stack: React + Node.js + PostgreSQL
- Feasibility: High
- Time estimate: 6 months
```

### 2. Parallel Communication
Multiple agents work simultaneously on independent tasks:

```
Frontend Team          Backend Team          Mobile Team
├─ Frontend Arch      ├─ Backend Services   ├─ Mobile Dev
├─ Frontend Mockup    ├─ Database Arch      └─ UI/UX Design
└─ Production Frontend└─ API Integration
```

### 3. Hub Communication
Central agent coordinates multiple specialists:

```
        ┌─── Business Analyst
        ├─── Financial Analyst
Master ─┼─── CEO Strategy
        ├─── Technical CTO
        └─── Project Manager
```

## Data Exchange Formats

### Standard Output Format
Each agent produces structured output:

```yaml
agent: business-analyst
timestamp: 2024-01-15T10:30:00Z
status: completed
output:
  analysis:
    market_size: "$5B"
    growth_rate: "15% YoY"
  recommendations:
    - "Focus on SMB segment"
    - "Freemium pricing model"
  next_agents:
    - technical-cto
    - financial-analyst
```

### Integration Points

#### Upstream Dependencies
Agents that provide input:
```
technical-specifications:
  receives_from:
    - business-analyst
    - technical-cto
    - project-manager
```

#### Downstream Consumers
Agents that consume output:
```
frontend-architecture:
  provides_to:
    - frontend-mockup
    - production-frontend
    - mobile-development
```

## Coordination Patterns

### 1. Waterfall Pattern
Strict sequential flow for regulated industries:

```
Phase 1: Analysis → Phase 2: Design → Phase 3: Implementation → Phase 4: Testing
```

### 2. Agile Pattern
Iterative cycles with feedback loops:

```
Sprint Planning ↔ Development ↔ Testing ↔ Review → [Repeat]
```

### 3. Concurrent Pattern
Maximize parallel execution:

```
Business Layer ═╦═ Technical Layer ═╦═ Development Layer
                ║                   ║
                ╚═══════╩═══════════╝
                    Integration Point
```

## Message Types

### 1. Task Assignment
```json
{
  "type": "task_assignment",
  "from": "master-orchestrator",
  "to": "database-architecture",
  "task": "Design multi-tenant schema",
  "context": {
    "project_type": "saas",
    "requirements": ["data_isolation", "scalability"]
  }
}
```

### 2. Status Update
```json
{
  "type": "status_update",
  "from": "backend-services",
  "status": "in_progress",
  "progress": 65,
  "eta": "2 hours"
}
```

### 3. Deliverable Handoff
```json
{
  "type": "deliverable",
  "from": "frontend-mockup",
  "to": ["production-frontend", "ui-ux-design"],
  "deliverable": {
    "type": "wireframes",
    "files": ["dashboard.html", "login.html"],
    "notes": "Mobile-first responsive design"
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

### Example 1: API Design Flow
```
1. Business Analyst: "Need payment processing"
2. Technical CTO: "Recommend Stripe + backup provider"
3. API Integration Specialist: "Design unified payment interface"
4. Backend Services: "Implement payment service"
5. Testing Automation: "Create payment test suite"
```

### Example 2: Frontend Feature Flow
```
1. UI/UX Design: "User dashboard wireframes"
2. Frontend Mockup: "HTML/CSS prototype"
3. Frontend Architecture: "Component structure"
4. Production Frontend: "React implementation"
5. Testing Automation: "Component tests"
```

## Monitoring & Optimization

### Communication Metrics
- Message latency between agents
- Handoff success rate
- Rework frequency
- Bottleneck identification

### Optimization Strategies
- Reduce sequential dependencies
- Increase parallel execution
- Cache common requests
- Batch related tasks

---

This communication system ensures efficient, reliable coordination between all 28 agents while maintaining flexibility for different project types and requirements.