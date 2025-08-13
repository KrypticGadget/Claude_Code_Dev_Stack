# Claude Code Dev Stack V3.0 - Comprehensive Test Prompts

## Installation Verification
After fresh Windows installation, run these commands to verify:

```powershell
# 1. Download and run installer
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1" -UseBasicParsing | iex

# 2. Verify installation
ls ~/.claude
ls ~/.claude/hooks
ls ~/.claude/agents
ls ~/.claude/audio
cat ~/.claude/settings.json
```

## Test Prompt Sequence

### Phase 1: Basic Functionality Tests

#### Test 1: Agent System
```
@agent-master-orchestrator Create a simple TODO app with React frontend and Node.js backend
```
Expected: Master orchestrator should coordinate multiple agents

#### Test 2: Slash Commands
```
/orchestrate-demo
```
Expected: Full demonstration of V3 orchestration capabilities

#### Test 3: Smart Orchestration
```
Build me a full-stack e-commerce platform with user authentication, product catalog, shopping cart, and payment integration
```
Expected: 
- Status line shows real-time updates
- Context manager tracks tokens
- Smart orchestrator selects appropriate agents
- Parallel execution for independent tasks

### Phase 2: V3 Component Tests

#### Test 4: Status Line
```
Create a complex microservices architecture with 5 services
```
Expected: Status line should show:
- Current model
- Git status
- Phase
- Active agents
- Token usage
- Health status

#### Test 5: Context Management
```
Continue implementing the remaining microservices and add comprehensive documentation
```
Expected: 
- Context preserved from previous task
- Token warning at 80%
- Handoff documentation if approaching limits

#### Test 6: Parallel Execution
```
Simultaneously:
1. Generate API documentation
2. Create test suites
3. Setup Docker configuration
4. Write deployment scripts
```
Expected: Multiple agents execute in parallel

### Phase 3: Advanced Features

#### Test 7: Hierarchical Orchestration
```
@agent-prompt-engineer help me build a SaaS platform
```
Expected: Prompt engineer enhances request, then delegates to master orchestrator

#### Test 8: Audio System
```
Fix this bug in my code: [paste any code with an error]
```
Expected: Phase-appropriate audio notifications

#### Test 9: MCP Integration
```
/mcp-search latest React 19 features
```
Expected: Web search MCP activates and returns results

#### Test 10: Browser Automation
```
/mcp-playwright Navigate to example.com and take a screenshot
```
Expected: Edge browser opens (headed mode), navigates, and captures screenshot

### Phase 4: Stress Tests

#### Test 11: Multi-Agent Coordination
```
I need a complete financial analysis platform with:
- Real-time data ingestion
- Machine learning predictions
- Interactive dashboards
- Mobile app
- API for third-party integrations
- Complete documentation
- DevOps setup
```
Expected: All relevant agents coordinate seamlessly

#### Test 12: Long-Running Task
```
Implement a social media platform clone with all standard features
```
Expected: 
- Proper phase transitions
- Token management
- Context preservation
- No crashes or hangs

### Phase 5: Edge Cases

#### Test 13: Vague Request Enhancement
```
make website
```
Expected: Prompt engineer transforms into detailed requirements

#### Test 14: Error Recovery
```
@agent-nonexistent do something
```
Expected: Graceful error handling

#### Test 15: Handoff Scenario
Create a very long task that will exceed token limits
Expected: Automatic handoff documentation generation

## Verification Checklist

### Core V3 Components
- [ ] Status line updates every 100ms
- [ ] Context manager tracks tokens accurately
- [ ] Smart orchestrator selects correct agents
- [ ] Chat manager generates handoff docs
- [ ] Parallel execution works for independent tasks
- [ ] Audio V3 plays phase-appropriate sounds

### Agent System
- [ ] All 28 agents accessible via @agent-
- [ ] Orchestration patterns work (delegation)
- [ ] Agents under 750 lines
- [ ] V3 enhancements active
- [ ] Hierarchical coordination works

### MCP Features
- [ ] Playwright browser automation (Edge, headed mode)
- [ ] Web search returns results
- [ ] Obsidian integration (if configured)

### Commands
- [ ] /orchestrate-demo works
- [ ] All slash commands accessible
- [ ] MCP commands functional

### Audio System
- [ ] Startup sound plays
- [ ] Phase transition sounds
- [ ] Task completion sounds
- [ ] Error sounds
- [ ] Git operation sounds

### Performance
- [ ] No crashes during long tasks
- [ ] Memory usage reasonable
- [ ] Response times acceptable
- [ ] Parallel execution improves speed

## Troubleshooting Commands

```powershell
# Check logs
cat ~/.claude/logs/*.log

# Test audio
powershell ~/.claude/audio/test_audio.ps1

# Fix Playwright locks
powershell ~/fix-playwright.ps1

# Verify Python
python --version

# Check hooks
ls ~/.claude/hooks/*.py | measure

# Verify settings
cat ~/.claude/settings.json | grep v3Features
```

## Success Criteria

The V3.0 system is considered fully functional when:

1. **All 15 test prompts pass** without errors
2. **Status line** shows real-time updates
3. **Context management** prevents token overflow
4. **Smart orchestration** selects optimal agents
5. **Parallel execution** works for concurrent tasks
6. **Audio notifications** play appropriately
7. **All 28 agents** are accessible and enhanced
8. **MCP tools** function correctly
9. **No crashes** during extended use
10. **Handoff documentation** generates when needed

## Notes for Testing

- Start with a fresh Claude Code instance
- Clear any existing ~/.claude directory before installation
- Test in order to build complexity gradually
- Document any errors or unexpected behavior
- Verify audio is working (volume up)
- Ensure Edge browser is installed for Playwright
- Have a test repository ready for Git operations

## Expected Installation Output

After running the installer, you should see:
- 28 agents installed
- 18 commands installed  
- 19 hooks installed (V3 components)
- MCP configurations set
- 50+ audio files installed
- Settings.json with v3Features enabled

## Final Validation

Run this comprehensive test to validate everything:

```
@agent-master-orchestrator I want to build a complete project management platform similar to Jira with:
- User authentication and authorization
- Project and task management
- Kanban and Scrum boards
- Time tracking
- Reporting and analytics
- Email notifications
- REST API
- Mobile responsive design
- Real-time updates
- File attachments
- Comments and activity feeds
- Integration webhooks
Please coordinate all necessary agents to design, implement, test, and deploy this system.
```

This should trigger:
- Prompt enhancement
- Master orchestration
- Multiple agent coordination
- Parallel execution
- Status line updates
- Context management
- Audio notifications
- Proper phase transitions
- Complete project delivery

Good luck with your V3.0 testing!