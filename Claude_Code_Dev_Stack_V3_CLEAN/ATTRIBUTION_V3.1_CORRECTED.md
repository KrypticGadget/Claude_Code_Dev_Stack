# 📜 Claude Code Dev Stack V3.1 - Attribution & Credits (CORRECTED)

## What Each Repository ACTUALLY Does

### ✅ **ALREADY INTEGRATED & WORKING:**

1. **claude-code-browser** by @zainhoda
   - **What it ACTUALLY does**: Browse Claude Code chat sessions, view tools/hooks/debug info
   - **NOT**: Browser automation (that's Playwright MCP)
   - **Status**: ✅ Already integrated in `integrations/browser/`
   - **License**: AGPL-3.0

2. **claude-powerline** by @Owloops  
   - **What it does**: Statusline with real-time metrics
   - **Status**: ✅ Already integrated in `integrations/statusline/`
   - **License**: MIT

3. **Claude-Code-MCP-Manager** by @qdhenry
   - **What it does**: MCP service management
   - **Status**: ✅ Already integrated in `integrations/mcp-manager/`

### 🔄 **CLONED BUT EMPTY (Need to re-clone):**

4. **openapi-mcp-codegen** by cnoe-io
   - **What it does**: Python-based OpenAPI to MCP generator
   - **Status**: ⚠️ Directory exists but empty - need to clone
   - **Action**: Re-clone and extract ~500 lines

5. **openapi-mcp-generator** by harsha-iiiv
   - **What it does**: Node.js-based OpenAPI to MCP generator
   - **Status**: ⚠️ Directory exists but empty - need to clone
   - **Action**: Re-clone and extract ~400 lines

### ✅ **CLONED & READY TO EXTRACT:**

6. **cli-lsp-client** by @eli0shin
   - **What it ACTUALLY does**: LSP diagnostics with daemon for 16 languages
   - **Perfect for**: Real-time error detection in our IDE
   - **Status**: ✅ Cloned and ready
   - **Action**: Extract daemon logic (~600 lines)

### 📦 **REPOSITORIES TO EVALUATE & CLONE:**

7. **github/github-mcp-server**
   - **What it does**: Official GitHub MCP server with OAuth, dynamic toolsets
   - **Value**: Production-ready, maintained by GitHub
   - **Action**: Clone and integrate fully (not build our own)

8. **bartolli/codanna**
   - **What it does**: Tree-sitter AST parsing, symbol resolution, semantic search
   - **Value**: Advanced code understanding
   - **Action**: Extract ~450 lines of semantic analysis

9. **RazBrry/AicodeGuard**
   - **What it does**: AI bailout detection patterns
   - **Value**: Detect when AI is avoiding implementation
   - **Action**: Extract patterns (~100 lines)

10. **bmad-code-org/BMAD-METHOD**
    - **What it does**: Two-phase planning with context preservation
    - **Value**: Prevents AI context loss
    - **Action**: Integrate planning methodology

11. **CodeBoarding/CodeBoarding**
    - **What it does**: Interactive codebase maps, visual documentation
    - **Value**: Auto-generated onboarding diagrams
    - **Action**: Extract diagram generation patterns

### ❌ **NOT NEEDED (Skip):**

- **cc-statusline** by chongdashu - Different statusline (we use claude-powerline)
- **claude-code-app** by 9cat - Redundant with our mobile app
- **sugyan/claude-code-webui** - We have our own web UI
- **gabriel-dehan/claude_hooks** - We have our own hook system
- **siteboon/claudecodeui** - Redundant UI
- **aaronearles/home** - Can't find/private repo
- **OpenAPITools/openapi-generator** - Too heavy

## Updated Integration Plan

### Phase 1: Fix Missing Clones
1. Re-clone openapi-mcp-codegen (Python generator)
2. Re-clone openapi-mcp-generator (Node.js generator) 
3. Clone github/github-mcp-server
4. Clone bartolli/codanna
5. Clone RazBrry/AicodeGuard
6. Clone bmad-code-org/BMAD-METHOD
7. Clone CodeBoarding/CodeBoarding

### Phase 2: Extract Core Features
1. **MCP Generators**: Extract from openapi-mcp-codegen and openapi-mcp-generator
2. **LSP Daemon**: Extract from cli-lsp-client (already cloned)
3. **GitHub MCP**: Integrate github-mcp-server fully
4. **Semantic Analysis**: Extract tree-sitter logic from codanna
5. **AI Patterns**: Extract bailout detection from AicodeGuard
6. **Planning**: Integrate BMAD two-phase methodology
7. **Documentation**: Extract diagram generation from CodeBoarding

### Phase 3: Integration
1. Create unified MCP generator API
2. Setup LSP with 16 language support
3. Configure GitHub MCP with OAuth
4. Implement semantic code analysis
5. Add visual documentation pipeline

## License Compliance
All components used in compliance with their respective licenses:
- AGPL-3.0: claude-code-browser
- MIT: claude-powerline, cli-lsp-client
- [To be verified]: Other repositories after cloning

---
*This corrected version accurately reflects what each repository actually does*