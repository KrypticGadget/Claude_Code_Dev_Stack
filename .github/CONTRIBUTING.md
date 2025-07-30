# Contributing to Claude Code Agent System

Thank you for your interest in contributing to the Claude Code Agent System! This project thrives on community contributions, and we welcome improvements, new agents, and enhancements.

## Table of Contents
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Adding New Agents](#adding-new-agents)
- [Agent Standards](#agent-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Code of Conduct](#code-of-conduct)

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/claude-code-agent-system.git
   cd claude-code-agent-system
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Types of Contributions We Welcome

- **New Agents**: Specialized agents for new domains or technologies
- **Agent Improvements**: Enhancements to existing agent capabilities
- **Documentation**: Improvements to guides, examples, or README
- **Examples**: Real-world project examples using the agent system
- **Bug Fixes**: Fixes for issues in scripts or configurations
- **Workflow Patterns**: New orchestration patterns or optimizations

### Before You Start

1. Check existing issues and PRs to avoid duplicates
2. For major changes, open an issue first to discuss
3. Ensure your contribution aligns with the project's goals

## Adding New Agents

### Agent Template

Create your agent configuration following this structure:

```markdown
---
name: your-agent-name
description: Detailed description of when this agent should be invoked. Include trigger phrases like "Use proactively" or "MUST BE USED" for automatic invocation.
tools: Read, Write, Edit, Bash, Grep, Glob  # Or omit to use all tools
---

# Agent Full Name

You are a [specific role] specializing in [domain expertise].

## Core Responsibilities
- [Specific responsibility with measurable outcomes]
- [Another responsibility with clear deliverables]
- [Additional responsibilities as needed]

## Expertise Areas
- **[Domain 1]**: [Specific capabilities and knowledge]
- **[Domain 2]**: [Specific capabilities and knowledge]
- **[Domain 3]**: [Specific capabilities and knowledge]

## Workflow Process
When invoked, follow these steps:
1. [First action - assessment or analysis]
2. [Second action - planning or design]
3. [Third action - implementation]
4. [Fourth action - validation]
5. [Fifth action - documentation or handoff]

## Integration Points
- **Receives from**: [List agents that provide input]
- **Provides to**: [List agents that receive output]
- **Collaborates with**: [List agents for parallel work]

## Deliverables
For each task, provide:
- **Analysis**: [What analysis format/content]
- **Documentation**: [What documentation to create]
- **Code/Output**: [What tangible outputs]
- **Recommendations**: [What recommendations format]

## Quality Standards
- [Specific quality requirement]
- [Another quality standard]
- [Additional standards as needed]

## Best Practices
- [Domain-specific best practice]
- [Another best practice]
- [Additional practices]
```

### Agent Naming Conventions

- Use lowercase with hyphens: `my-new-agent.md`
- End with `-agent` suffix: `database-migration-agent.md`
- Be descriptive but concise: `graphql-api-agent.md`

## Agent Standards

### Required Elements

1. **Clear Trigger Description**: The description field must clearly indicate when the agent should be invoked
2. **Specific Role Definition**: Define the agent's expertise clearly
3. **Actionable Workflows**: Provide step-by-step processes
4. **Integration Points**: Specify how the agent works with others
5. **Measurable Deliverables**: Define what the agent produces

### Quality Guidelines

- **Expertise Depth**: Agents should be deep experts in their domain
- **Clear Boundaries**: Define what the agent does and doesn't do
- **Practical Examples**: Include code examples where relevant
- **Error Handling**: Address common failure scenarios
- **Best Practices**: Include industry standards and best practices

## Testing Requirements

### Before Submitting

1. **Validate Format**:
   ```bash
   # Check your agent has required frontmatter
   grep -E "^name:|^description:" Config_Files/your-agent.md
   ```

2. **Test in Claude Code**:
   - Install your agent locally
   - Test with at least 3 different prompts
   - Verify integration with related agents

3. **Document Test Cases**:
   Include test examples in your PR:
   ```
   Test 1: Basic functionality
   > Use the your-agent agent to [test case]
   Expected: [expected outcome]
   
   Test 2: Integration test
   > Use the your-agent agent after technical-cto agent
   Expected: [expected interaction]
   ```

## Pull Request Process

### PR Requirements

1. **Title Format**: 
   - New agent: `feat: Add [agent-name] agent`
   - Improvement: `enhance: Improve [agent-name] capabilities`
   - Fix: `fix: Correct [issue] in [agent-name]`
   - Docs: `docs: Update [what was updated]`

2. **Description Template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] New agent
   - [ ] Agent enhancement
   - [ ] Bug fix
   - [ ] Documentation update
   
   ## Testing
   - [ ] Tested locally with Claude Code
   - [ ] Follows agent standards
   - [ ] Documentation updated
   
   ## Test Cases
   [Include test cases and results]
   ```

3. **File Changes**:
   - Place new agents in `Config_Files/`
   - Update README.md if adding new capabilities
   - Add examples if introducing new patterns

### Review Process

1. Automated checks will validate structure
2. Maintainers will review for quality and standards
3. Community feedback period (usually 48 hours)
4. Merge upon approval

### After Merge

- Your contribution will be included in the next release
- You'll be added to the contributors list
- Consider helping review other PRs!

## Code of Conduct

### Our Standards

- **Be Respectful**: Treat all contributors with respect
- **Be Collaborative**: Work together to improve the project
- **Be Constructive**: Provide helpful feedback
- **Be Inclusive**: Welcome contributors of all backgrounds

### Unacceptable Behavior

- Harassment or discrimination
- Destructive criticism
- Off-topic or spam contributions
- Violation of agent quality standards

## Recognition

Contributors are recognized in:
- The project README
- Release notes
- Special thanks in documentation

## Questions?

- Open an issue for questions
- Join discussions in the issues section
- Tag maintainers for urgent matters

---

Thank you for contributing to make Claude Code Agent System better for everyone!

Together, we're building the future of AI-assisted software development.