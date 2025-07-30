# Agent Customization Guide

Learn how to customize and extend the Claude Code Agent System for your specific needs.

## Understanding Agent Structure

Each agent file has two main parts:

### 1. Frontmatter (Metadata)
```yaml
---
name: agent-name-here
description: When and how this agent should be activated
tools: Read, Write, Edit, Bash, Grep, Glob
---
```

### 2. Agent Instructions
The markdown content that defines the agent's behavior, expertise, and workflow.

## Safe Customization Practices

### ✅ What You Can Safely Modify

#### 1. Agent Instructions
Customize the agent's behavior while maintaining core functionality:

```markdown
## Core Responsibilities
- [Add your custom responsibilities]
- [Modify existing ones for your needs]

## Workflow Process
1. [Adjust steps to match your process]
2. [Add domain-specific steps]
```

#### 2. Quality Standards
Add your organization's specific standards:

```markdown
## Quality Standards
- Follow company coding standards
- Adhere to internal security policies
- Use approved libraries only
- Include specific documentation requirements
```

#### 3. Domain-Specific Expertise
Add industry or technology-specific knowledge:

```markdown
## Expertise Areas
- **Your Industry**: Specific regulations and requirements
- **Your Tech Stack**: Preferred tools and frameworks
- **Your Patterns**: Company-specific design patterns
```

### ⚠️ What to Modify Carefully

#### 1. Agent Name
- Changing the name breaks prompts that reference it
- If you must rename, update all references

#### 2. Description
- Keep activation triggers intact
- Add to description rather than replacing
- Test that agent still activates properly

#### 3. Tools
- Only remove tools you won't use
- Never add tools that don't exist
- Test functionality after changes

### ❌ What Not to Modify

1. **Frontmatter Format**: Must remain valid YAML
2. **Core Agent Purpose**: Don't fundamentally change what an agent does
3. **Integration Points**: Maintain compatibility with other agents

## Common Customization Scenarios

### Scenario 1: Company-Specific Standards

**Original:**
```markdown
## Best Practices
- Follow clean code principles
- Write comprehensive tests
```

**Customized:**
```markdown
## Best Practices
- Follow clean code principles
- Write comprehensive tests
- Adhere to ACME Corp coding standards (link to internal wiki)
- Use company-approved security libraries
- Include JIRA ticket numbers in commits
```

### Scenario 2: Technology Stack Preferences

**For Backend Services Agent:**
```markdown
## Technology Preferences
- Primary Language: Python 3.11+
- Web Framework: FastAPI
- ORM: SQLAlchemy 2.0
- Testing: pytest with 90% coverage minimum
- API Style: REST with OpenAPI 3.0 documentation
```

### Scenario 3: Industry-Specific Requirements

**For Security Architecture Agent (Healthcare):**
```markdown
## Compliance Requirements
- HIPAA compliance mandatory
- PHI encryption at rest and in transit
- Audit logging for all data access
- Annual security assessments required
- BAA required for third-party services
```

### Scenario 4: Workflow Integration

**For Project Manager Agent:**
```markdown
## Workflow Integration
- Create JIRA epics for major features
- Update Confluence with sprint reports
- Slack notifications for milestones
- Weekly stakeholder email updates
- Integration with company PM tools
```

## Creating Custom Agent Variants

### Step 1: Copy Existing Agent
```bash
cp business-analyst-agent.md business-analyst-fintech-agent.md
```

### Step 2: Update Metadata
```yaml
---
name: business-analyst-fintech
description: Business analysis specialist for fintech applications. Use for financial services projects requiring regulatory compliance and financial modeling expertise.
tools: Read, Write, Edit, Bash, Grep, Glob
---
```

### Step 3: Customize Content
Add domain-specific expertise:
```markdown
# FinTech Business Analyst

You are a business analyst specializing in financial technology...

## Additional Expertise Areas
- **Regulatory Compliance**: PCI-DSS, PSD2, KYC/AML
- **Financial Products**: Payments, lending, investment
- **Risk Management**: Fraud detection, credit scoring
```

### Step 4: Install Custom Agent
```bash
cp business-analyst-fintech-agent.md ~/.config/claude/agents/
```

## Organization-Wide Customization

### Creating a Company Agent Pack

1. **Fork the Repository**
```bash
git fork https://github.com/original/claude-code-agent-system
cd claude-code-agent-system
```

2. **Create Company Branch**
```bash
git checkout -b acme-corp-customizations
```

3. **Customize Agents**
- Add company standards
- Include internal tools
- Reference internal documentation

4. **Create Install Script**
```bash
#!/bin/bash
# install-acme-agents.sh
echo "Installing ACME Corp Agent System..."
# Custom installation steps
```

5. **Document Changes**
Create `ACME-CUSTOMIZATIONS.md`:
```markdown
# ACME Corp Customizations

## Modified Agents
- backend-services: Uses company Python standards
- security-architecture: Includes SOC2 requirements
- devops-engineering: Configured for AWS-only

## Custom Agents
- acme-compliance-agent: Internal compliance checks
- acme-data-privacy-agent: GDPR/CCPA specialist
```

## Testing Customizations

### 1. Activation Testing
Test that your customized agent still activates:
```
> Use the business-analyst-fintech agent to analyze mobile payment opportunity
```

### 2. Functionality Testing
Verify core functionality remains intact:
- Check all tools still work
- Verify agent produces expected outputs
- Test integration with other agents

### 3. Workflow Testing
Test in real workflows:
```
> Use the master-orchestrator agent to build a fintech application
[Verify your custom agent is invoked appropriately]
```

## Advanced Customization Techniques

### 1. Conditional Behavior
Add environment-specific behavior:
```markdown
## Environment-Specific Standards
- Development: Relaxed security for faster iteration
- Staging: Full security with test data
- Production: Maximum security, audit logging enabled
```

### 2. Template Integration
Reference company templates:
```markdown
## Document Templates
- Use architecture-template.md for all designs
- Follow api-spec-template.yaml for APIs
- Use test-plan-template.md for test strategies
```

### 3. Tool Preferences
Specify preferred tools:
```markdown
## Preferred Tools
- IDE: VSCode with company extensions
- Version Control: GitHub Enterprise
- CI/CD: Jenkins with company pipelines
- Monitoring: DataDog with custom dashboards
```

## Maintaining Custom Agents

### Version Control
1. Track all customizations in git
2. Document why changes were made
3. Tag stable versions

### Updates
When updating the base agents:
1. Review changes in new version
2. Merge carefully to preserve customizations
3. Test thoroughly after updates

### Documentation
Maintain documentation for:
- What was customized and why
- Dependencies on internal systems
- Testing procedures
- Rollback procedures

## Sharing Customizations

### Within Your Organization
1. Create internal repository
2. Set up automated deployment
3. Train team on customizations
4. Gather feedback and iterate

### With the Community
Consider contributing generally useful customizations:
1. Remove company-specific information
2. Create pull request
3. Document use cases
4. Provide examples

## Best Practices

### 1. Start Small
- Customize one agent at a time
- Test thoroughly before proceeding
- Document as you go

### 2. Preserve Core Functionality
- Don't break existing features
- Maintain backward compatibility
- Keep agent interactions intact

### 3. Document Everything
- Why customizations were made
- How to use custom features
- Testing procedures
- Rollback plans

### 4. Version Management
- Tag stable versions
- Keep original agents as backup
- Track changes systematically

### 5. Team Alignment
- Get team buy-in before major changes
- Train team on customizations
- Create internal documentation
- Regular reviews and updates

## Troubleshooting Custom Agents

### Agent Not Activating
1. Check frontmatter syntax
2. Verify description includes triggers
3. Test with exact agent name

### Functionality Broken
1. Compare with original agent
2. Check tool requirements
3. Verify syntax in instructions

### Integration Issues
1. Ensure agent name consistency
2. Check workflow compatibility
3. Test with other agents

Remember: Customization makes the system more powerful for your specific needs, but always preserve core functionality and maintain good documentation!