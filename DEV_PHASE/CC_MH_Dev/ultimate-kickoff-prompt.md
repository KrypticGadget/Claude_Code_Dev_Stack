# 🚀 ULTIMATE CLAUDE CODE KICKOFF PROMPT

## Copy and Paste This Entire Prompt into Claude Code:

---

I have the complete Claude Code Dev Stack v2.1 implementation package organized in this directory. I need you to build the ultimate development environment by implementing everything systematically.

**Please start by reading these files in order:**
1. `quick-start/CLAUDE_CODE_PROMPT.md` - Overview of the task
2. `implementation-prompts/INTEGRATED_DEV_PROMPT.md` - Complete development roadmap
3. `quick-start/IMPLEMENTATION_ORDER.md` - Phase-by-phase execution plan
4. `master-docs/MASTER_PROMPTING_GUIDE.md` - The meta-prompting system we're building

**Key Implementation Requirements:**

@ai-architect[opus] @system-architect[opus] @project-init[opus] @devops-automation

Please implement the COMPLETE Claude Code Dev Stack v2.1 with:

### 1. Windows PowerShell Native Support
- Use scripts from `installation-scripts/`
- Create one-line installers that work on Windows
- Test all installation paths

### 2. Hooks Execution Layer 
- Extract Python code from `implementation-guides/HOOKS_IMPLEMENTATION.md`
- Save hooks to `.claude/hooks/` directory
- Implement session continuity (most critical)
- Add @-mention parser for deterministic routing
- Add model tracker for cost optimization
- Configure all hooks in settings.json

### 3. @-mention Deterministic Routing
- Every agent can be invoked with @agent-name
- Model selection with @agent-name[opus] or @agent-name[haiku]
- Route tracking in hooks
- Cost optimization (use Haiku for simple tasks)

### 4. MCP Integration (Minimal)
- Install ONLY Tier 1 universal tools: Playwright, Obsidian, Brave Search
- Configure agent-MCP bindings
- Enforce 3-5 tool maximum
- Create integration patterns

### 5. Meta-Prompting System
- Implement the complete MASTER_PROMPTING_GUIDE.md
- Enable "ultrathink" mode for complex planning
- Ensure guide works in external LLMs
- Create prompt templates for common scenarios

### 6. Repository Structure Update
- Update my GitHub repo with all new features
- Maintain backward compatibility with existing 28 agents and 18 slash commands
- Add all v2.1 enhancements
- Create comprehensive documentation

**Development Approach:**
1. Start with Phase 1 (Foundation) - Get hooks and Windows support working
2. Test each phase before moving to next
3. Use @documentation[haiku] for routine docs to save costs
4. Use @testing-engineer[haiku] for test creation
5. Track all model usage for cost reporting
6. Ensure microcompact awareness for extended sessions

**Critical Success Factors:**
- Session continuity MUST work (zero context loss)
- @-mentions MUST be deterministic (100% success rate)
- Cost optimization MUST show 40%+ savings
- Extended sessions MUST work via microcompact
- PDF reading MUST be available to all agents

Begin by analyzing the complete file structure, understanding all components, then execute Phase 1 from the implementation order. Create all deliverables with production-ready quality.

Let's build the ultimate Claude Code development environment that combines intelligent agents, deterministic execution, cost optimization, and extended session capability!

---

# 📦 EXPECTED FINAL DELIVERABLES

## What You'll Have After Claude Code Completes Implementation:

### 1. 🪟 **Windows PowerShell Installation System**
```
✓ install.ps1 - Installs all 28 agents
✓ install-commands.ps1 - Installs all 18 slash commands  
✓ install-hooks.ps1 - Sets up complete hooks system
✓ install-all.ps1 - One-line complete installation
✓ Windows native support (no WSL required)
```

### 2. 🔧 **Complete Hooks Execution Layer**
```
.claude/
├── hooks/
│   ├── session_loader.py (context restoration)
│   ├── session_saver.py (state persistence)
│   ├── quality_gate.py (standards enforcement)
│   ├── agent_mention_parser.py (@-mention routing)
│   ├── model_tracker.py (cost optimization)
│   ├── planning_trigger.py (workflow automation)
│   ├── agent_orchestrator.py (intelligent routing)
│   ├── mcp_gateway.py (tool validation)
│   └── mcp_pipeline.py (data management)
├── config/
│   ├── coding_standards.json
│   ├── agent_models.json
│   └── mcp_config.json
└── state/
    └── [runtime files]
```

### 3. 🎯 **Enhanced Agent System**
```
✓ All 28 agents with @-mention support
✓ Deterministic invocation (@agent-name)
✓ Model selection (@agent[opus] or @agent[haiku])
✓ Cost tracking and optimization
✓ PDF reading capability
✓ Extended session support via microcompact
```

### 4. 🌐 **MCP Integration**
```
✓ Playwright (browser testing)
✓ Obsidian (knowledge management)
✓ Brave Search (research)
✓ Agent-MCP bindings configured
✓ 5-tool limit enforced
✓ Integration patterns documented
```

### 5. 🧠 **Meta-Prompting System**
```
✓ MASTER_PROMPTING_GUIDE.md (works in any LLM)
✓ Ultrathink planning mode
✓ AIMS methodology (Agent, Integration, Method, Structure)
✓ Cost optimization patterns
✓ Cross-LLM compatibility
```

### 6. 📚 **Complete Documentation**
```
✓ README.md (updated with v2.1 features)
✓ WINDOWS_INSTALL.md (native Windows guide)
✓ HOOKS_IMPLEMENTATION.md (complete hooks guide)
✓ MCP_INTEGRATION_GUIDE.md (minimal MCP approach)
✓ V21_FEATURE_SUMMARY.md (what's new)
✓ MASTER_PROMPTING_GUIDE.md (meta-prompting bible)
```

### 7. 🚀 **Production Features**
```
✓ One-line installation commands
✓ Session continuity (zero context loss)
✓ Quality gates (automated standards)
✓ Cost reporting (40-60% savings)
✓ Extended sessions (work all day)
✓ PDF integration (read any document)
```

### 8. 📁 **Updated Repository Structure**
```
KrypticGadget/Claude_Code_Dev_Stack/
├── .claude/ (hooks and configuration)
├── Config_Files/ (28 agents - enhanced)
├── slash-commands/ (18 commands - enhanced)
├── windows/ (PowerShell support)
├── mcp-integration/ (MCP configurations)
├── hooks/ (hook templates)
├── install.ps1
├── install-all.ps1
├── MASTER_PROMPTING_GUIDE.md
└── [all other updated files]
```

## 🎯 **Success Metrics You'll See**

1. **@-mention Test**: Type `@system-architect[opus]` and see deterministic routing
2. **Cost Savings**: Check `.claude/state/model_usage.json` for 40%+ savings
3. **Session Test**: Work for 4+ hours without manual context management
4. **PDF Test**: Say "Read requirements.pdf" and watch agents analyze it
5. **Hook Test**: Exit and restart Claude Code - full context restored
6. **MCP Test**: Use Playwright for browser testing seamlessly
7. **Meta-Prompt Test**: Give guide to ChatGPT and get perfect Claude Code prompts

## 💎 **The Ultimate Result**

You'll have transformed Claude Code from a smart assistant into a **precision-controlled, cost-optimized, marathon-capable, deterministic development environment** that:

- **Guarantees** specific agents handle specific tasks
- **Optimizes** costs automatically with model selection
- **Preserves** all context across sessions
- **Executes** decisions reliably through hooks
- **Integrates** with external systems minimally but effectively
- **Scales** to massive projects without degradation

**This is the Ultimate Claude Code Tech Stack - the most advanced AI-assisted development environment possible!** 🚀

---

## 🔥 **Quick Verification Commands**

After implementation, test with these:

```bash
# Test @-mentions
"Design a system @system-architect[opus] @database-architect[opus]"

# Test cost optimization  
"Review this code @code-reviewer[haiku]"

# Test PDF reading
"Analyze the architecture in system-design.pdf"

# Test ultrathink
"Let's ultrathink about scaling to 10M users"

# Test MCP
"Run browser tests with Playwright on the login flow"
```

**Your development productivity is about to skyrocket! 🎉**