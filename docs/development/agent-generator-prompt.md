# Agent Generator Prompt

Use this prompt to generate new specialized agents for the Claude Code Agent System.

## Generator Prompt Template

```
Create a detailed Claude Code agent configuration for a [AGENT_TYPE] with the following specifications:

**Agent Purpose:** [DESCRIBE_PRIMARY_PURPOSE]

**Core Responsibilities:**
- [RESPONSIBILITY_1]
- [RESPONSIBILITY_2]
- [RESPONSIBILITY_3]

**Primary Tools:** [LIST_TOOLS: Read, Write, Edit, Bash, Grep, Glob]

**Generate a complete agent configuration including:**

1. YAML frontmatter with:
   - name: lowercase-with-hyphens
   - description: Detailed with trigger phrases
   - tools: Specific tool list

2. Comprehensive system prompt with:
   - Role definition and expertise
   - Step-by-step workflows
   - Deliverable formats
   - Quality standards
   - Integration points

3. Specialized sections for:
   - Domain expertise
   - Best practices
   - Success metrics
   - Collaboration protocols
```

## Configuration Requirements

### YAML Frontmatter Format
```yaml
---
name: agent-name-here
description: Detailed description including when to use. Include "MUST BE USED" for critical triggers and "Use proactively" for auto-delegation.
tools: Read, Write, Edit, Bash, Grep, Glob
---
```

### Naming Conventions
- Use lowercase with hyphens (e.g., `business-analyst`, `technical-cto`)
- Keep names descriptive but concise
- Follow existing naming patterns

### Description Guidelines
- Start with primary function
- Include activation triggers
- Specify "MUST BE USED" for critical scenarios
- Add "Use proactively" for automatic delegation
- Be specific about domain expertise

## System Prompt Structure

### 1. Role Definition
```markdown
# [Agent Title]

You are a [role description] specializing in [expertise areas]. Your primary focus is [main objective].

## Core Expertise
- **Domain 1**: Specific expertise
- **Domain 2**: Specific expertise
- **Domain 3**: Specific expertise
```

### 2. Workflow Process
```markdown
## Workflow Process

### Phase 1: [Phase Name]
1. [Specific step]
2. [Specific step]
3. [Specific step]

### Phase 2: [Phase Name]
1. [Specific step]
2. [Specific step]
```

### 3. Deliverables Format
```markdown
## Deliverables

### [Deliverable Type 1]
- Format: [Specific format]
- Contents: [What to include]
- Standards: [Quality requirements]

### [Deliverable Type 2]
- Format: [Specific format]
- Contents: [What to include]
```

### 4. Integration Points
```markdown
## Integration with Other Agents

### Receives From:
- **[Agent Name]**: [What data/context]
- **[Agent Name]**: [What data/context]

### Provides To:
- **[Agent Name]**: [What deliverables]
- **[Agent Name]**: [What deliverables]
```

## Example Configurations

### Example 1: Business Domain Agent
```yaml
---
name: market-research-analyst
description: Market research and competitive analysis specialist. Use proactively for market validation, competitor analysis, and trend identification. MUST BE USED when entering new markets or launching new products.
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Market Research Analyst

You are a market research specialist focused on comprehensive market analysis...
```

### Example 2: Technical Domain Agent
```yaml
---
name: cloud-architecture-specialist
description: Cloud infrastructure and architecture expert. Use for cloud migration, infrastructure design, and cost optimization. MUST BE USED for production deployments on AWS, Azure, or GCP.
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Cloud Architecture Specialist

You are a cloud infrastructure expert specializing in scalable, secure architectures...
```

## Tool Selection Guidelines

### Available Tools
- **Read**: File reading and analysis
- **Write**: File creation
- **Edit**: File modification
- **Bash**: Command execution
- **Grep**: Pattern searching
- **Glob**: File pattern matching

### Tool Selection Criteria
1. **Essential Only**: Include only tools the agent needs
2. **Omit for All**: Leave tools field out to inherit all
3. **Security Considerations**: Limit Bash for non-technical agents
4. **Performance**: Fewer tools = faster activation

## Best Practices

### 1. Clear Boundaries
- Define what the agent does AND doesn't do
- Specify handoff points clearly
- Avoid overlapping responsibilities

### 2. Actionable Outputs
- Provide specific, implementable recommendations
- Include examples where helpful
- Format outputs for easy consumption

### 3. Quality Standards
- Define success criteria
- Include validation steps
- Specify required documentation

### 4. Collaboration Focus
- Clear input requirements
- Standardized output formats
- Explicit integration points

## Testing Your Agent

### 1. Activation Testing
```
> Use the [agent-name] agent to [typical task]
```

### 2. Integration Testing
Test with upstream/downstream agents:
```
> Use the master-orchestrator agent to coordinate [workflow including your agent]
```

### 3. Edge Case Testing
- Test with minimal input
- Test with complex scenarios
- Verify error handling

## Common Patterns

### Pattern 1: Analysis → Recommendation
```markdown
1. Gather relevant data
2. Analyze against criteria
3. Generate recommendations
4. Format deliverables
```

### Pattern 2: Design → Implementation
```markdown
1. Understand requirements
2. Create design/architecture
3. Document approach
4. Prepare for handoff
```

### Pattern 3: Review → Optimization
```markdown
1. Assess current state
2. Identify improvements
3. Prioritize changes
4. Create action plan
```

## Submission Checklist

- [ ] Valid YAML frontmatter
- [ ] Descriptive agent name
- [ ] Clear activation triggers
- [ ] Comprehensive system prompt
- [ ] Defined workflows
- [ ] Integration points specified
- [ ] Quality standards included
- [ ] Testing completed

---

Use this template to create consistent, high-quality agents that integrate seamlessly with the Claude Code Agent System.