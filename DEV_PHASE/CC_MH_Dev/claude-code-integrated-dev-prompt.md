# 🚀 Claude Code Dev Stack v2.1 - Integrated Development Prompt

## Project: Complete Stack Evolution with @-mention Subagents + Hooks + MCP + Meta-Prompting

This comprehensive prompt integrates the new @-mention deterministic subagent system, model selection (Opus/Haiku), automatic microcompact, PDF reading, Hooks execution layer, and minimal MCP integration.

---

## 🎯 Architecture Overview

```
Current: Meta-Prompting → Agent Orchestration → Slash Commands → Planning Phase
Target:  Meta-Prompting → @-mention Agents → [HOOKS EXECUTION] → Slash Commands → Planning Phase → [MCP EXTERNAL OPS]
```

### Core Enhancements
1. **@-mention Subagents** - Deterministic agent invocation with `@agent-name[model]`
2. **Model Optimization** - Opus 4 for complex tasks, Haiku 3.5 for simple tasks (60% cost reduction)
3. **Microcompact** - Automatic context management for extended sessions
4. **PDF Reading** - Direct document analysis capability
5. **Hooks Ensure Execution** - Transform decisions into guaranteed implementation
6. **Minimal MCP Usage** - 3-5 MCPs maximum (Tier 1 universal + project-specific)

---

## Phase 1: Foundation Infrastructure (Week 1)

### 1.1 Windows PowerShell Support
```
/backend-service "PowerShell installation scripts"
@backend-engineer @devops-automation
Context: Windows-native installation system
Requirements:
- install.ps1: Main agent installer
- install-commands.ps1: Slash commands installer
- install-all.ps1: Combined installer with hooks setup
- install-hooks.ps1: Hooks system installer
Features:
- One-line execution: iwr -useb URL | iex
- Automatic .claude directory structure creation
- Hooks configuration during install
- @-mention support documentation
```

### 1.2 Hooks Foundation Layer with Microcompact Support
```
/devops "Hooks execution layer implementation"
@devops-automation @system-architect[opus]
Context: Create deterministic execution system with microcompact awareness
Priority Components:
1. session_loader.py - Restore agent state, planning context, meta-prompting state
2. session_saver.py - Persist all context (microcompact-aware)
3. quality_gate.py - Enforce coding standards automatically
4. agent_mention_parser.py - Parse and route @-mentions
5. settings.json - Hook configuration with model preferences

Directory Structure:
.claude/
├── hooks/
│   ├── session_loader.py
│   ├── session_saver.py
│   ├── quality_gate.py
│   └── agent_mention_parser.py
├── config/
│   ├── coding_standards.json
│   └── agent_models.json
└── state/
    ├── agent_state.md
    ├── meta_prompt_state.json
    └── microcompact_state.json
```

### 1.3 Session Continuity Implementation with Model Tracking
```
/code-implementation "Session continuity hooks with v2.1 features"
@backend-engineer @devops-automation
File: .claude/hooks/session_loader.py
```python
def load_agent_context():
    context_parts = []
    
    # Load meta-prompting state
    if os.path.exists(".claude/state/meta_prompt_state.json"):
        with open(".claude/state/meta_prompt_state.json") as f:
            meta_state = json.load(f)
            context_parts.append(f"## Meta-Prompting State\n```json\n{json.dumps(meta_state, indent=2)}\n```")
    
    # Load @-mention routing history
    if os.path.exists(".claude/state/agent_routing.json"):
        with open(".claude/state/agent_routing.json") as f:
            routing = json.load(f)
            recent = routing[-10:]
            context_parts.append(f"## Recent Agent Routing\n{format_routing(recent)}")
    
    # Load model usage for cost awareness
    if os.path.exists(".claude/state/model_usage.json"):
        with open(".claude/state/model_usage.json") as f:
            usage = json.load(f)
            context_parts.append(f"## Model Usage\nToday's savings: ${usage.get('savings', 0):.2f}")
    
    return "\n\n".join(context_parts)
```

---

## Phase 2: MCP Integration Layer (Week 2)

### 2.1 Tier 1 Universal MCPs with Agent Bindings
```
/integration "MCP Tier 1 setup with @-mention bindings"
@integration-specialist @devops-automation[haiku]
Context: Universal tools with deterministic agent routing
MCPs:
1. Playwright - @testing-engineer[haiku] @qa-lead
2. Obsidian - @documentation[haiku] @ai-architect[opus]
3. Brave Search - @requirements-analyst @business-analyst[opus]

Create: /mcp-configs/tier1-universal-v21.json
{
  "universal_mcps": {
    "playwright": {
      "purpose": "Browser testing",
      "install": "claude mcp add playwright npx @playwright/mcp@latest",
      "primary_agents": ["@testing-engineer[haiku]", "@qa-lead"],
      "usage_pattern": "Use Haiku for routine tests, default for complex scenarios"
    },
    "obsidian": {
      "purpose": "Knowledge management",
      "install": "claude mcp add obsidian",
      "primary_agents": ["@documentation[haiku]", "@ai-architect[opus]"],
      "usage_pattern": "Haiku for notes, Opus for architecture decisions"
    },
    "brave-search": {
      "purpose": "Research",
      "install": "claude mcp add brave-search",
      "primary_agents": ["@requirements-analyst", "@business-analyst[opus]"],
      "usage_pattern": "Opus for market analysis, default for general research"
    }
  }
}
```

### 2.2 MCP-Agent Integration Patterns
```
/documentation "MCP integration patterns"
File: MCP_INTEGRATION_GUIDE.md

## Agent-MCP Workflows

### Database Workflow
1. Agent: /database-design "schema for e-commerce"
2. MCP: Execute schema in MongoDB
3. Agent: /documentation "database schema docs"

### Testing Workflow  
1. Agent: /frontend-mockup "checkout flow"
2. MCP: Test with Playwright in real browsers
3. Agent: /test-suite "generate test cases"

### Deployment Workflow
1. Agent: /devops "deployment strategy"
2. MCP: Deploy to GCP/Vercel
3. Agent: /documentation "deployment guide"
```

### 2.3 MCP Hooks Integration
```
/backend-service "MCP gateway hooks"
Files:
- .claude/hooks/mcp_gateway.py - Validate MCP usage
- .claude/hooks/mcp_pipeline.py - Manage MCP data flow

Hook Configuration:
{
  "PreToolUse": [
    {"matcher": "mcp__.*", "hooks": [{"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/mcp_gateway.py"}]}
  ],
  "PostToolUse": [
    {"matcher": "mcp__.*", "hooks": [{"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/mcp_pipeline.py"}]}
  ]
}
```

---

## Phase 3: Meta-Prompting Master Document (Week 2-3)

### 3.1 Create Master Prompting Guide v2.1
```
/documentation "Master Meta-Prompting Guide with @-mentions"
@documentation[haiku] @technical-writer[haiku] @ai-architect[opus]
File: MASTER_PROMPTING_GUIDE.md

Structure:
1. AIMS Methodology with @-mention enhancement
2. Complete Agent Reference (28 agents with @-syntax and model recommendations)
3. Cost Optimization Patterns (Opus vs Haiku usage)
4. Microcompact-Aware Prompting
5. PDF Integration Examples
6. Session-Aware Prompting with hooks
7. Ultrathink Planning Mode with deterministic routing
8. Cross-LLM Compatibility (how to request @-mentions in other LLMs)

Key Sections:
## @-mention Syntax
- Basic: @agent-name
- With model: @agent-name[opus] or @agent-name[haiku]
- Multiple agents: @ai-architect[opus] @backend-engineer @testing-engineer[haiku]

## Cost Optimization Matrix
| Task Type | Recommended Model | Agents |
|-----------|------------------|---------|
| Architecture | Opus | @system-architect[opus] @ai-architect[opus] |
| Planning | Opus | @business-analyst[opus] @strategic-advisor[opus] |
| Implementation | Default | @backend-engineer @frontend-architect |
| Testing | Haiku | @testing-engineer[haiku] @qa-lead[haiku] |
| Documentation | Haiku | @documentation[haiku] @technical-writer[haiku] |

## PDF-Driven Workflows
- Requirements: "Read specs from requirements.pdf" @requirements-analyst
- Architecture: "Review design.pdf" @system-architect[opus]
- Legacy code: "Analyze old-system.pdf" @code-reviewer[haiku]
```

### 3.2 Ultrathink Planning Mode Integration v2.1
```
/code-implementation "Ultrathink triggers with deterministic routing"
@ai-architect[opus] @system-architect[opus]
Add to MASTER_PROMPTING_GUIDE.md:

## Ultrathink Planning Mode v2.1

Trigger: "Let's ultrathink about [complex problem]"

Enhanced with @-mentions:
"Let's ultrathink about microservices migration @system-architect[opus] @database-architect[opus] @devops-automation"

Automatic features:
1. Specified agents WILL participate (guaranteed)
2. Model selection optimizes cost/quality
3. Session state loaded via hooks
4. PDF documents auto-included if referenced
5. Microcompact handles long planning sessions
6. All decisions persisted to Obsidian MCP

Example with full integration:
"Let's ultrathink about scaling to 1M users. Read current architecture from system-design.pdf. @performance-specialist[opus] @cloud-infrastructure @database-architect[opus]. Focus on cost optimization."
```

---

## Phase 4: Agent Enhancement with Hooks (Week 3)

### 4.1 Agent State Management
```
/backend-service "Agent orchestrator hook"
File: .claude/hooks/agent_orchestrator.py

Features:
- Track active agent assignments
- Manage agent handoffs
- Persist orchestration state
- Trigger appropriate workflows

Integration:
{
  "UserPromptSubmit": [
    {"hooks": [{"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/agent_orchestrator.py"}]}
  ]
}
```

### 4.2 Planning Phase Automation
```
/devops "Planning trigger automation"
File: .claude/hooks/planning_trigger.py

Triggers on:
- Requirements file changes
- Architecture document updates
- New feature requests
- Major refactoring needs

def should_trigger_planning(file_path):
    triggers = ["requirements.txt", "REQUIREMENTS.md", "ARCHITECTURE.md"]
    return any(t in file_path for t in triggers)
```

---

## Phase 5: Quality Assurance Integration (Week 3-4)

### 5.1 Automated Quality Gates
```
/quality-assurance "Quality enforcement system"
File: .claude/hooks/quality_gate.py

Enforces:
- Coding standards (naming, patterns)
- Documentation requirements
- Test coverage minimums
- Security best practices

Configuration: .claude/config/coding_standards.json
{
  "naming": {
    "functions": "camelCase",
    "classes": "PascalCase",
    "files": "kebab-case"
  },
  "required_docs": ["README.md", "API.md"],
  "min_test_coverage": 80
}
```

### 5.2 Test Automation with MCP
```
/test-suite "Automated testing workflow"
Integration Pattern:
1. Hook detects code change
2. Agent generates test cases
3. Playwright MCP executes browser tests
4. Results persisted to Obsidian MCP
5. Hook triggers documentation update
```

---

## Phase 6: Documentation and Repository Update (Week 4)

### 6.1 Updated README Structure
```
/documentation "Comprehensive README update"
New Sections:
## ⚡ Quick Install

### Windows PowerShell (with Hooks)
```powershell
iwr -useb https://raw.githubusercontent.com/.../install-all.ps1 | iex
```

### Linux/macOS (with Hooks)
```bash
curl -sL https://raw.githubusercontent.com/.../install-all.sh | bash
```

## 🔧 Hooks System
- Automated execution layer
- Session continuity
- Quality enforcement
- Agent state management

## 🌐 MCP Integration
- Tier 1: Playwright, Obsidian, Brave Search
- Tier 2: Project-specific (Database + Deploy)
- Agents design, MCPs execute

## 🧠 Meta-Prompting
- MASTER_PROMPTING_GUIDE.md for any LLM
- Ultrathink planning mode
- Cross-session orchestration
```

### 6.2 Repository Structure
```
/project-structure "Final repository layout"
/
├── install.ps1                    # Windows installer
├── install-hooks.ps1              # Hooks setup
├── install-all.ps1                # Complete setup
├── MASTER_PROMPTING_GUIDE.md      # Meta-prompting bible
├── MCP_INTEGRATION_GUIDE.md       # MCP patterns
├── HOOKS_IMPLEMENTATION.md        # Hooks documentation
├── .claude/                       # Claude configuration
│   ├── hooks/                     # Execution layer
│   ├── config/                    # Standards & settings
│   └── state/                     # Persistent context
├── /mcp-configs/                  # MCP templates
│   ├── tier1-universal.json
│   ├── mongodb-stack.json
│   └── gcp-deployment.json
└── /hooks-templates/              # Hook patterns
    ├── session-continuity.py
    ├── quality-gates.py
    └── agent-orchestration.py
```

---

## 🎯 Success Metrics & Validation (Updated for v2.1)

### Foundation Success (Week 1)
- [ ] Windows PowerShell installation works
- [ ] @-mention routing functions correctly
- [ ] Model selection (Opus/Haiku) tracked properly
- [ ] Session continuity maintains context through microcompact
- [ ] PDF reading integrated with agents
- [ ] Cost savings tracked and reported

### Integration Success (Week 2-3)
- [ ] Tier 1 MCPs work with @-mentioned agents
- [ ] Agent-MCP workflows use optimal models
- [ ] Hooks track all @-mentions and model usage
- [ ] Microcompact preserves critical state
- [ ] Meta-prompting guide includes all v2.1 features

### Full Stack Success (Week 4)
- [ ] Ultrathink mode uses deterministic @-mentions
- [ ] Cost reduced by 40-60% through Haiku usage
- [ ] Extended sessions work without manual intervention
- [ ] PDF-driven development workflows functional
- [ ] Cross-session orchestration seamless

### v2.1 Specific Metrics
- [ ] @-mention success rate: 100% (agents always respond when mentioned)
- [ ] Cost optimization: 40%+ savings on routine tasks
- [ ] Session length: 4x longer without manual /compact
- [ ] PDF integration: All agents can read and analyze PDFs
- [ ] Model usage tracking: Complete cost visibility

---

## 📋 Implementation Checklist (v2.1)

### Immediate Actions
1. [ ] Create .claude directory structure
2. [ ] Implement session continuity hooks with microcompact awareness
3. [ ] Add agent_mention_parser.py hook
4. [ ] Add model_tracker.py hook
5. [ ] Configure agent_models.json
6. [ ] Install Tier 1 MCPs
7. [ ] Write MASTER_PROMPTING_GUIDE.md v2.1

### Repository Updates
1. [ ] Add PowerShell installers with @-mention support
2. [ ] Create v2.1 hooks templates
3. [ ] Document @-mention syntax
4. [ ] Add model selection guide
5. [ ] Include PDF workflow examples
6. [ ] Update all READMEs for v2.1

### Testing Protocol
1. [ ] Test @-mention routing: `@system-architect[opus] design a system`
2. [ ] Verify model selection: Check model_usage.json
3. [ ] Test microcompact: Work for 2+ hours continuously
4. [ ] Test PDF reading: `Read requirements from spec.pdf`
5. [ ] Verify cost tracking: Review COST_SAVINGS.md

---

## 🚀 Execution Commands (v2.1 Enhanced)

Start development with:
```
/new-project "Claude Code Dev Stack v2.1 with @-mentions"
@ai-architect[opus] @project-init[opus] @devops-automation
Context: Repository enhancement project
Features:
- Deterministic @-mention agent routing
- Model selection (Opus/Haiku) for cost optimization
- Microcompact-aware hooks for extended sessions
- PDF reading integration
- Enhanced meta-prompting methodology
Tech Stack: Python hooks, PowerShell installers, JSON configs
Constraints: Maintain backward compatibility, optimize costs with Haiku

Initial setup:
1. Read existing docs from old-readme.pdf if available
2. Use @documentation[haiku] for routine documentation
3. Use @testing-engineer[haiku] for test generation
4. Track all costs in model_usage.json
```

Then proceed phase by phase using the specific @-mentions and model selections shown above.

---

## 💡 Key Innovation (v2.1)

This integrated approach creates a **deterministic, cost-optimized development ecosystem**:
- **@-mentions** guarantee agent participation
- **Model selection** optimizes cost without sacrificing quality
- **Microcompact** enables marathon development sessions
- **PDF integration** leverages existing documentation
- **Hooks** ensure everything executes reliably
- **MCPs** handle external operations efficiently

The result: A development environment where you have precise control over which agents work on what, at what cost, for as long as needed, with perfect execution and state management.

**Bottom line**: v2.1 transforms Claude Code from an intelligent assistant to a precision development instrument with deterministic control and optimized costs.