# MCP (Model Context Protocol) Integration Guide

Complete guide to the 3 MCP integrations in Claude Code Dev Stack: Playwright, Obsidian, and Brave Search.

## Overview

MCPs extend Claude's capabilities with specialized tools for web automation, knowledge management, and internet search.

### Available MCPs

1. **Playwright** - Web automation and testing
2. **Obsidian** - Knowledge base integration
3. **Brave Search** - Web search capabilities

## Playwright MCP

### Purpose
Automate web browsers for testing, scraping, and interaction with web applications.

### Capabilities
- Browser automation (Chrome, Firefox, Safari)
- Web scraping and data extraction
- Automated testing of web applications
- Screenshot capture and visual regression
- Form filling and interaction
- Multi-page workflows

### Installation
```bash
# Install Playwright MCP
npm install @anthropic/mcp-playwright

# Install browsers
npx playwright install
```

### Usage Examples

#### Basic Web Automation
```javascript
// Navigate and interact with a website
await playwright.navigate('https://example.com');
await playwright.click('button#submit');
await playwright.fill('input#email', 'user@example.com');
```

#### Web Scraping
```javascript
// Extract data from a webpage
const data = await playwright.evaluate(() => {
  return {
    title: document.title,
    headers: Array.from(document.querySelectorAll('h1')).map(h => h.textContent),
    links: Array.from(document.querySelectorAll('a')).map(a => ({
      text: a.textContent,
      href: a.href
    }))
  };
});
```

#### Visual Testing
```javascript
// Capture screenshots for comparison
await playwright.screenshot({ path: 'homepage.png' });
await playwright.screenshot({ 
  path: 'mobile-view.png',
  viewport: { width: 375, height: 812 }
});
```

### Integration with Agents

Playwright MCP works seamlessly with:
- **testing-automation**: Automated E2E testing
- **frontend-mockup**: Visual verification
- **quality-assurance**: Cross-browser testing
- **api-integration-specialist**: Web API testing

### Best Practices
1. Use page objects for maintainable tests
2. Implement proper wait strategies
3. Handle errors gracefully
4. Clean up browser instances
5. Use headless mode for CI/CD

## Obsidian MCP

### Purpose
Integrate with Obsidian knowledge bases for documentation, note-taking, and knowledge management.

### Capabilities
- Read and write Markdown notes
- Search across knowledge base
- Create linked documentation
- Manage project notes
- Build documentation wikis
- Sync with code repositories

### Installation
```bash
# Install Obsidian MCP
npm install @anthropic/mcp-obsidian

# Configure vault path
export OBSIDIAN_VAULT_PATH="/path/to/your/vault"
```

### Configuration
```json
{
  "mcp": {
    "obsidian": {
      "vaultPath": "/path/to/vault",
      "defaultFolder": "Projects",
      "fileExtension": ".md",
      "frontmatterTemplate": {
        "created": "{{date}}",
        "tags": [],
        "project": ""
      }
    }
  }
}
```

### Usage Examples

#### Create Project Documentation
```javascript
// Create a new project note
await obsidian.createNote({
  title: "Project: E-commerce Platform",
  folder: "Projects/2024",
  content: `# E-commerce Platform

## Overview
Multi-vendor marketplace with real-time inventory

## Architecture
- Frontend: React + Next.js
- Backend: Node.js + PostgreSQL
- Cache: Redis
- Queue: RabbitMQ

## Progress
- [x] Initial setup
- [ ] User authentication
- [ ] Product catalog
- [ ] Payment integration`
});
```

#### Search Knowledge Base
```javascript
// Search for related documentation
const results = await obsidian.search({
  query: "authentication OAuth2",
  folder: "Technical Docs",
  limit: 10
});
```

#### Link Related Notes
```javascript
// Create interconnected documentation
await obsidian.linkNotes({
  from: "API Documentation",
  to: ["Architecture Overview", "Security Guidelines"],
  bidirectional: true
});
```

### Integration with Agents

Obsidian MCP enhances:
- **technical-documentation**: Structured docs
- **usage-guide**: User manuals
- **project-manager**: Project wikis
- **business-analyst**: Research notes
- **technical-specifications**: Spec documents

### Templates

#### Project Template
```markdown
---
created: {{date}}
tags: [project, active]
status: planning
---

# {{title}}

## Project Overview
[Brief description]

## Objectives
1. 
2. 
3. 

## Technical Stack
- Frontend: 
- Backend: 
- Database: 
- Infrastructure: 

## Timeline
- [ ] Phase 1: 
- [ ] Phase 2: 
- [ ] Phase 3: 

## Resources
- [[Architecture Diagram]]
- [[API Documentation]]
- [[Deployment Guide]]
```

### Best Practices
1. Use consistent naming conventions
2. Leverage tags for organization
3. Create template notes
4. Regular backups
5. Use wikilinks for navigation

## Brave Search MCP

### Purpose
Access real-time web search results for research, validation, and current information.

### Capabilities
- Web search with filters
- News and current events
- Technical documentation lookup
- Package/library research
- Competitor analysis
- Market research

### Installation
```bash
# Install Brave Search MCP
npm install @anthropic/mcp-brave-search

# Set API key
export BRAVE_SEARCH_API_KEY="your-api-key"
```

### Configuration
```json
{
  "mcp": {
    "braveSearch": {
      "apiKey": "${BRAVE_SEARCH_API_KEY}",
      "defaultCountry": "US",
      "safeSearch": "moderate",
      "resultCount": 10
    }
  }
}
```

### Usage Examples

#### Technical Research
```javascript
// Search for technical documentation
const results = await braveSearch.search({
  query: "React Server Components best practices 2024",
  type: "web",
  freshness: "month"
});
```

#### Market Analysis
```javascript
// Research competitors
const competitors = await braveSearch.search({
  query: "B2B SaaS collaboration tools market leaders",
  type: "news",
  count: 20
});
```

#### Package Research
```javascript
// Find npm packages
const packages = await braveSearch.search({
  query: "site:npmjs.com real-time websocket library",
  type: "web"
});
```

### Search Operators
- `site:` - Search within specific site
- `filetype:` - Find specific file types
- `"exact phrase"` - Exact match search
- `-exclude` - Exclude terms
- `OR` - Either term
- `*` - Wildcard

### Integration with Agents

Brave Search MCP supports:
- **business-analyst**: Market research
- **technical-cto**: Tech evaluation
- **security-architecture**: Vulnerability research
- **mobile-development**: Platform updates
- **api-integration-specialist**: API documentation

### Best Practices
1. Use specific search queries
2. Apply appropriate filters
3. Verify information freshness
4. Cross-reference multiple sources
5. Cache frequent searches

## MCP Orchestration

### Combining MCPs
```javascript
// Example: Research and document a new technology

// 1. Search for information
const research = await braveSearch.search({
  query: "WebAssembly performance benchmarks 2024"
});

// 2. Create documentation
await obsidian.createNote({
  title: "WebAssembly Performance Analysis",
  content: formatResearchResults(research)
});

// 3. Test example implementations
await playwright.navigate('https://webassembly.org/demo/');
const performance = await playwright.evaluate(() => {
  // Measure performance metrics
});
```

### MCP + Agent Workflows

#### Automated Documentation
```bash
# 1. Research topic
business-analyst + Brave Search → Market analysis

# 2. Document findings  
technical-documentation + Obsidian → Structured docs

# 3. Verify examples
testing-automation + Playwright → Validate code samples
```

#### Competitive Analysis
```bash
# 1. Find competitors
Brave Search → Competitor list

# 2. Analyze websites
Playwright → Feature extraction

# 3. Document analysis
Obsidian → Competitive matrix
```

## Troubleshooting

### Common Issues

#### Playwright
- **Browser not found**: Run `npx playwright install`
- **Timeout errors**: Increase timeout or add wait conditions
- **Selector not found**: Verify element exists and is visible

#### Obsidian
- **Vault not found**: Check OBSIDIAN_VAULT_PATH
- **Permission denied**: Ensure write permissions
- **Note conflicts**: Use unique titles or timestamps

#### Brave Search
- **API key invalid**: Verify BRAVE_SEARCH_API_KEY
- **Rate limited**: Implement caching and throttling
- **No results**: Broaden search terms

### Debug Mode
```bash
# Enable MCP debug logging
export MCP_DEBUG=true

# Check MCP status
npm run mcp:status

# Test individual MCPs
npm run mcp:test playwright
npm run mcp:test obsidian
npm run mcp:test brave-search
```

## Security Considerations

### API Keys
- Store in environment variables
- Never commit to version control
- Rotate regularly
- Use separate keys for dev/prod

### Data Handling
- Sanitize search queries
- Validate Obsidian file paths
- Secure Playwright sessions
- Handle sensitive data carefully

### Rate Limiting
- Brave Search: 2000 queries/month (free tier)
- Implement caching layer
- Queue requests appropriately
- Monitor usage

## Future Enhancements

### Planned MCPs
- GitHub integration
- Slack workspace
- Notion databases
- Linear issues
- Figma designs

### Upcoming Features
- MCP chaining workflows
- Automated sync between MCPs
- Enhanced error handling
- Performance monitoring
- Usage analytics

Remember: MCPs are powerful tools that extend Claude's capabilities. Use them wisely to enhance productivity while maintaining security and efficiency.