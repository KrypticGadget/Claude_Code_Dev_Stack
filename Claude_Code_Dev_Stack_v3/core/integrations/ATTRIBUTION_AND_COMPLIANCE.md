# Claude Code Browser Integration - Attribution and Compliance

## Overview

This integration incorporates the Claude Code Browser by @zainhoda into the Claude Code Dev Stack v3.0 system while maintaining full AGPL-3.0 license compliance and proper attribution.

## Original Project Attribution

### Claude Code Browser
- **Author**: @zainhoda
- **Repository**: https://github.com/zainhoda/claude-code-browser
- **License**: AGPL-3.0
- **Original Capabilities**:
  - Session monitoring and browsing
  - Project organization
  - Session content display
  - Todo tracking

## Integration Components

### Dev Stack Integration Layer (New Work)
- **Author**: Claude Code Dev Stack v3.0
- **License**: AGPL-3.0 (compatible derivative work)
- **Components Created**:
  - `browser_adapter.py` - Integration adapter with WebSocket and HTTP APIs
  - `browser_integration_hook.py` - Hook system integration
  - `start_browser_integration.py` - Startup and lifecycle management
  - Enhanced `BrowserMonitor.tsx` - PWA frontend integration
  - Real-time WebSocket communication
  - Dev Stack command parsing and execution
  - Hook system integration

## License Compliance

### AGPL-3.0 Requirements Met

1. **Source Code Availability** ✅
   - All integration code is available in this repository
   - No proprietary or closed-source components
   - Full source provided for derivative works

2. **Attribution Maintained** ✅
   - Original author @zainhoda properly credited in all files
   - Original repository linked and referenced
   - Clear distinction between original and integration work

3. **License Compatibility** ✅
   - Both original and integration work under AGPL-3.0
   - No license conflicts or incompatibilities
   - Derivative work properly licensed under AGPL-3.0

4. **Network Copyleft Compliance** ✅
   - Source code available for network-accessible services
   - Integration services covered under AGPL-3.0
   - Users can access and modify integration source

## Technical Integration Approach

### Adapter Pattern Implementation
The integration uses the adapter pattern to:
- Maintain separation between original and integration code
- Provide clear interfaces for Dev Stack systems
- Enable independent evolution of both systems
- Ensure license compliance through clear boundaries

### Integration Points
1. **Data Access**: Reads Claude Code Browser data files
2. **WebSocket API**: Provides real-time updates
3. **HTTP API**: REST endpoints for browser data
4. **Command Parsing**: Extracts Dev Stack commands from sessions
5. **Hook Integration**: Connects to Dev Stack orchestration
6. **PWA Frontend**: Enhanced browser monitoring interface

### No Modifications to Original Code
- Original Claude Code Browser code remains untouched
- Integration works with existing data formats
- No changes required to original project
- Full compatibility maintained

## Installation and Usage

### Prerequisites
```bash
# Install required dependencies
pip install websockets aiohttp aiofiles

# Ensure Claude Code Browser data directory exists
mkdir -p ~/.claude/projects
```

### Starting the Integration
```bash
# Basic startup
python start_browser_integration.py

# Custom ports
python start_browser_integration.py --websocket-port 8081 --http-port 8082

# Check dependencies
python start_browser_integration.py --check-only

# Show attribution
python start_browser_integration.py --attribution
```

### PWA Integration
The enhanced BrowserMonitor component in the PWA provides:
- Real-time session monitoring
- Dev Stack command interface
- Command execution and history
- WebSocket connectivity indicator
- Attribution display

## API Endpoints

### HTTP API
- `GET /api/projects` - List all projects
- `GET /api/projects/{name}` - Get project details
- `GET /api/sessions/{uuid}` - Get session details
- `GET /api/status` - Integration status
- `GET /api/attribution` - Attribution information
- `POST /api/commands/execute` - Execute Dev Stack commands

### WebSocket API
- `projects_update` - Real-time project updates
- `session_content` - Session content with parsed commands
- `command_executed` - Command execution results
- `system_status` - System status updates

## Dev Stack Command Support

### Parsed Command Types
- `@agent-{name}` - Agent mentions
- `!orchestrate {request}` - Orchestration commands
- `?status {query}` - Status queries
- `@context {operation}` - Context operations
- `%mcp-{command}` - MCP commands
- `#hook-{name}` - Hook triggers

### Command Execution
Commands found in browser sessions can be:
- Executed through the PWA interface
- Triggered via WebSocket messages
- Processed through the Dev Stack orchestrator
- Logged with execution history

## Quality Assurance

### Code Quality
- Full type hints in Python code
- Comprehensive error handling
- Logging and monitoring
- Clean separation of concerns

### License Compliance
- Attribution headers in all files
- Clear license statements
- Compliance verification functions
- Legal notice generation

### Testing
- Dependency checking
- Integration testing capabilities
- Error handling verification
- Attribution validation

## Contributing

### Guidelines for Contributors
1. Maintain AGPL-3.0 license compliance
2. Preserve attribution to @zainhoda
3. Follow adapter pattern for new features
4. Document license implications of changes
5. Ensure derivative works are AGPL-3.0

### Adding New Features
When adding features to the integration:
1. Keep original and integration code separate
2. Use clear interfaces and adapters
3. Maintain license compatibility
4. Update attribution documentation
5. Verify compliance requirements

## Legal Notices

### AGPL-3.0 License Notice
This integration is licensed under the GNU Affero General Public License v3.0. This means:
- Source code must remain available
- Network use triggers copyleft requirements
- Derivative works must be AGPL-3.0 licensed
- Attribution must be maintained

### Original Work Recognition
The Claude Code Browser by @zainhoda is the foundation for this integration. The original work includes:
- Core session management concepts
- Data storage formats
- Project organization structure
- Browser interface patterns

### Derivative Work Declaration
This integration constitutes a derivative work under copyright law and AGPL-3.0 licensing. All integration components are properly licensed under AGPL-3.0 to maintain compliance.

## Contact and Support

### Integration Issues
- File issues in the Claude Code Dev Stack repository
- Include "browser integration" in issue titles
- Provide clear reproduction steps

### Original Project Issues
- File issues with the original Claude Code Browser repository
- Do not file integration-specific issues with the original project
- Respect the original maintainer's contribution guidelines

## Version History

### v3.0.0 (Current)
- Initial integration with Claude Code Dev Stack v3.0
- WebSocket and HTTP API implementation
- Dev Stack command parsing
- PWA frontend integration
- Real-time monitoring capabilities
- Full AGPL-3.0 compliance implementation

---

**Attribution Statement**: This integration builds upon the excellent work of @zainhoda's Claude Code Browser while adding Dev Stack-specific capabilities. We gratefully acknowledge the original contribution and maintain full compliance with AGPL-3.0 licensing requirements.