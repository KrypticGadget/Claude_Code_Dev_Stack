# 🗂️ Claude Code Dev Stack v2.1 - File Structure & Implementation Guide

## 📥 Artifacts to Download

Download ALL artifacts from our conversation and organize them as follows:

```
claude-code-dev-stack-v21/
├── 📁 implementation-prompts/
│   ├── INTEGRATED_DEV_PROMPT.md          # Artifact: claude-code-integrated-dev-prompt
│   ├── REPO_UPDATE_PROMPT.md             # Artifact: claude-code-update-prompt
│   └── REPO_UPDATE_PLAN.md               # Artifact: repo-update-plan
│
├── 📁 master-docs/
│   ├── MASTER_PROMPTING_GUIDE.md         # Artifact: master-prompting-guide-final
│   ├── V21_FEATURE_SUMMARY.md            # Artifact: v21-feature-summary
│   └── WINDOWS_INSTALL.md                # Artifact: windows-install-readme
│
├── 📁 implementation-guides/
│   ├── HOOKS_IMPLEMENTATION.md           # Artifact: hooks-implementation-guide
│   ├── MCP_INTEGRATION_GUIDE.md          # Artifact: mcp-integration-guide
│   └── README.md                         # Create: Overview linking all guides
│
├── 📁 installation-scripts/
│   ├── install.ps1                       # Artifact: claude-code-install-ps1
│   ├── install-commands.ps1              # Artifact: claude-code-commands-ps1
│   ├── install-all.ps1                   # Artifact: claude-code-full-install
│   └── install-hooks.ps1                 # Extract from: hooks-implementation-guide
│
├── 📁 hook-templates/
│   ├── session_loader.py                 # Extract from: hooks-implementation-guide
│   ├── session_saver.py                  # Extract from: hooks-implementation-guide
│   ├── quality_gate.py                   # Extract from: hooks-implementation-guide
│   ├── agent_mention_parser.py           # Extract from: hooks-implementation-guide
│   ├── model_tracker.py                  # Extract from: hooks-implementation-guide
│   └── planning_trigger.py               # Extract from: hooks-implementation-guide
│
├── 📁 config-templates/
│   ├── agent_models.json                 # Extract from: hooks-implementation-guide
│   ├── coding_standards.json             # Extract from: hooks-implementation-guide
│   ├── mcp_tier1_config.json             # Extract from: mcp-integration-guide
│   └── settings.json                     # Extract from: hooks-implementation-guide
│
└── 📁 quick-start/
    ├── IMPLEMENTATION_ORDER.md           # Create: Step-by-step implementation
    └── CLAUDE_CODE_PROMPT.md             # Create: Single prompt to reference all
```

---

## 🚀 Master Implementation Prompt for Claude Code

Save this as `quick-start/CLAUDE_CODE_PROMPT.md` and use it to implement everything:

```markdown
# Claude Code Dev Stack v2.1 Implementation

I have a complete implementation package in the directory `claude-code-dev-stack-v21/`. Please help me implement the entire stack by:

1. First, read the implementation order from `quick-start/IMPLEMENTATION_ORDER.md`
2. Read the integrated development prompt from `implementation-prompts/INTEGRATED_DEV_PROMPT.md`
3. Reference the Master Prompting Guide at `master-docs/MASTER_PROMPTING_GUIDE.md`
4. Use the guides in `implementation-guides/` for specific implementations

Let's start with Phase 1 using the appropriate @-mentions:
@ai-architect[opus] @system-architect[opus] @devops-automation

Please implement the Windows PowerShell support first by:
- Using scripts from `installation-scripts/`
- Setting up hooks from `hook-templates/`
- Applying configurations from `config-templates/`

After each phase, we'll verify using the success metrics in the integrated development prompt.
```

---

## 📋 Implementation Order Document

Create this as `quick-start/IMPLEMENTATION_ORDER.md`:

```markdown
# Implementation Order for Claude Code Dev Stack v2.1

## Phase 1: Foundation (Day 1-2)
1. Run Windows PowerShell installation scripts
2. Set up .claude directory structure
3. Install foundation hooks (session_loader, session_saver, quality_gate)
4. Configure agent @-mention routing
5. Test session continuity

## Phase 2: Agent Enhancement (Day 3-4)
1. Install agent_mention_parser.py hook
2. Install model_tracker.py hook
3. Configure agent_models.json
4. Test @-mention routing
5. Verify cost tracking

## Phase 3: MCP Integration (Day 5)
1. Install Tier 1 MCPs (Playwright, Obsidian, Brave Search)
2. Configure MCP-agent bindings
3. Test MCP workflows
4. Document integration patterns

## Phase 4: Meta-Prompting (Day 6-7)
1. Deploy MASTER_PROMPTING_GUIDE.md
2. Test in external LLMs
3. Configure ultrathink mode
4. Test PDF integration

## Phase 5: Repository Update (Day 8)
1. Update GitHub repository structure
2. Add all new files
3. Update README with v2.1 features
4. Create release notes
5. Tag as v2.1.0

## Verification Checklist
- [ ] @-mentions work deterministically
- [ ] Model costs tracked and optimized
- [ ] Microcompact preserves state
- [ ] PDFs readable by all agents
- [ ] Hooks execute reliably
- [ ] MCPs limited to 5 total
- [ ] Meta-prompting guide works in other LLMs
```

---

## 🎯 Single Command Implementation

After organizing all files, use this single command in Claude Code:

```bash
/new-project "Implement Claude Code Dev Stack v2.1"
@ai-architect[opus] @project-init[opus] @devops-automation
Context: Complete implementation package at ./claude-code-dev-stack-v21/
Requirements:
- Read all files in implementation-prompts/ for project plan
- Follow implementation order from quick-start/IMPLEMENTATION_ORDER.md
- Use hook templates from hook-templates/
- Apply configurations from config-templates/
- Install scripts from installation-scripts/
Features needed:
- Windows PowerShell support
- @-mention deterministic routing
- Model cost optimization (Opus/Haiku)
- Microcompact-aware hooks
- PDF reading capability
- MCP integration (Tier 1 only to start)
- Complete meta-prompting system

Start with: Read and analyze implementation-prompts/INTEGRATED_DEV_PROMPT.md
Then: Execute Phase 1 from IMPLEMENTATION_ORDER.md

Use @documentation[haiku] for routine docs
Use @testing-engineer[haiku] for test creation
Use @code-reviewer[haiku] for code reviews
Track all costs in model_usage.json
```

---

## 📁 GitHub Repository Structure (Final)

After implementation, your repository should look like:

```
KrypticGadget/Claude_Code_Dev_Stack/
├── .claude/                              # Auto-created by hooks
│   ├── hooks/                           # All Python hooks
│   ├── config/                          # All JSON configs
│   └── state/                           # Runtime state
├── Config_Files/                        # Your existing 28 agents
├── slash-commands/                      # Your existing 18 commands
├── master-prompts/                      # Enhanced with v2.1
├── windows/                             # NEW: Windows support
├── mcp-integration/                     # NEW: MCP configs
├── hooks/                               # NEW: Hook templates
├── docs/                               # Updated documentation
├── install.ps1                         # NEW: Windows installer
├── install-all.ps1                     # NEW: Complete installer
├── MASTER_PROMPTING_GUIDE.md           # NEW: v2.1 guide
├── MCP_INTEGRATION_GUIDE.md            # NEW: MCP guide
├── HOOKS_IMPLEMENTATION.md             # NEW: Hooks guide
└── README.md                           # Updated with v2.1
```

---

## 🔥 Quick Implementation Steps

1. **Create the file structure** above on your local machine
2. **Download all artifacts** and place them in correct folders
3. **Extract code blocks** from guides into individual files
4. **Open Claude Code** in the parent directory
5. **Paste the Single Command Implementation** prompt
6. **Let Claude Code implement everything** systematically

## 💡 Pro Tips

- Start a new Claude Code session for clean implementation
- Use the file structure as your checklist
- Verify each phase before moving to next
- Use @-mentions to ensure right agents work on right tasks
- Monitor costs with the model_tracker.py hook
- Let microcompact handle long sessions automatically

Your ultimate Claude Code Tech Stack is ready for implementation! 🚀
```