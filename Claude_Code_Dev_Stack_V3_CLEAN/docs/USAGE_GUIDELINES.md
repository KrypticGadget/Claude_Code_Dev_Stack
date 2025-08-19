# Usage Guidelines for Integrated Components
## Claude Code Dev Stack V3.0

This document provides comprehensive guidelines for using the integrated open-source components within the Claude Code Dev Stack, ensuring compliance with all license requirements and best practices.

## 📋 General Usage Principles

### License Compliance
- **Respect Original Licenses**: All usage must comply with original component licenses
- **Maintain Attribution**: Proper attribution must be maintained for all components
- **Document Modifications**: Any changes to integrated components must be documented
- **Preserve Copyright**: Original copyright notices must be preserved

### Best Practices
- **Keep Attribution Current**: Update attribution when components are modified
- **Monitor License Changes**: Track any license changes in upstream components
- **Contribute Back**: Consider contributing improvements back to original projects
- **Legal Review**: Seek legal advice for complex licensing situations

## 🔧 Component-Specific Usage Guidelines

### 1. OpenAPI MCP Python Generator

#### License: Apache 2.0
#### Usage Guidelines:
```python
# ✅ Proper usage - with attribution
from core.generators.python import OpenAPIMCPGenerator
# Based on openapi-mcp-codegen by CNOE.io (Apache 2.0)

generator = OpenAPIMCPGenerator()
result = generator.generate_from_spec('api.yaml')
```

#### Requirements:
- ✅ Include Apache 2.0 license text in distributions
- ✅ Preserve copyright notices in modified files
- ✅ Document any modifications made
- ✅ Include NOTICE file if distributing

#### Permitted Uses:
- ✅ Commercial use
- ✅ Modification and distribution
- ✅ Private use
- ✅ Patent use (with Apache 2.0 grant)

#### Restrictions:
- ❌ Cannot use Apache trademarks without permission
- ❌ No warranty provided
- ❌ Patent grant terminates if you sue for patent infringement

### 2. OpenAPI MCP Node.js Generator

#### License: MIT
#### Usage Guidelines:
```javascript
// ✅ Proper usage - with attribution
const { OpenAPIMCPGenerator } = require('core/generators/nodejs');
// Based on openapi-mcp-generator by harsha-iiiv (MIT)

const generator = new OpenAPIMCPGenerator();
const result = generator.generateFromSpec('api.yaml');
```

#### Requirements:
- ✅ Include MIT license text in distributions
- ✅ Preserve copyright notices
- ✅ Include license in substantial portions

#### Permitted Uses:
- ✅ Commercial use
- ✅ Modification and distribution
- ✅ Private use
- ✅ No patent provisions

#### Restrictions:
- ❌ No warranty provided
- ❌ No liability protection

### 3. LSP Client Daemon

#### License: MIT
#### Usage Guidelines:
```python
# ✅ Proper usage - with attribution
from core.lsp import LSPClient
# Based on cli-lsp-client by eli0shin (MIT)

client = LSPClient(language='python')
diagnostics = client.get_diagnostics('file.py')
```

#### Requirements:
- ✅ Include MIT license text in distributions
- ✅ Preserve copyright notices
- ✅ Include license in substantial portions

### 4. Semantic Code Analysis (Codanna)

#### License: Apache 2.0
#### Usage Guidelines:
```python
# ✅ Proper usage - with attribution
from core.semantic import SemanticAnalyzer
# Based on codanna by Angel Bartolli (Apache 2.0)

analyzer = SemanticAnalyzer()
symbols = analyzer.analyze_code(source_code)
```

#### Requirements:
- ✅ Include Apache 2.0 license text in distributions
- ✅ Preserve copyright notices in modified files
- ✅ Document any modifications made
- ✅ Include NOTICE file if distributing

### 5. BMAD Planning Methodology

#### License: MIT
#### Special Considerations: Trademark Notice
#### Usage Guidelines:
```python
# ✅ Proper usage - with attribution and trademark notice
from core.orchestration.bmad import BMADPlanner
# Based on BMAD-METHOD by BMad Code, LLC (MIT)
# BMAD™ and BMAD-METHOD™ are trademarks of BMad Code, LLC

planner = BMADPlanner()
plan = planner.create_plan(context)
```

#### Requirements:
- ✅ Include MIT license text in distributions
- ✅ Preserve copyright notices
- ✅ Respect trademark rights (BMAD™, BMAD-METHOD™)
- ✅ Include trademark notices in documentation

#### Trademark Usage:
- ✅ Use trademarks for attribution and reference
- ❌ Cannot use trademarks in product names without permission
- ❌ Cannot suggest endorsement by BMad Code, LLC

### 6. AI Bailout Detection (AicodeGuard)

#### License: No explicit license
#### Usage Guidelines:
```python
# ⚠️ Cautious usage - no explicit license
from core.patterns import BailoutDetector
# Based on patterns from AicodeGuard by RazBrry
# Usage under GitHub Terms of Service - seeking license clarification

detector = BailoutDetector()
result = detector.analyze_pattern(code)
```

#### Special Considerations:
- ⚠️ **Limited Integration**: Only pattern extraction, not direct code usage
- ⚠️ **Seeking Clarification**: Attempting to contact author for license clarity
- ⚠️ **Conservative Approach**: Prepared to remove if license issues arise
- ⚠️ **Documentation**: Clear documentation of usage assumptions

## 📝 Distribution Guidelines

### When Distributing the Software

#### Required Inclusions:
1. **Main ATTRIBUTION.md File**: Include our comprehensive attribution file
2. **Component License Texts**: Include all license texts for integrated components
3. **Copyright Notices**: Preserve all original copyright notices
4. **Modification Documentation**: Document any changes made

#### Distribution Checklist:
- [ ] ATTRIBUTION.md included in distribution
- [ ] All license texts included
- [ ] Copyright notices preserved
- [ ] Component-specific attribution files included
- [ ] Modification documentation provided
- [ ] Trademark notices included where applicable

### Binary Distributions
For binary distributions (compiled software), ensure:
- License and attribution information is accessible to end users
- Copyright notices are displayed in application credits or documentation
- License texts are included in installer or documentation package

### Source Distributions
For source distributions, ensure:
- All source files maintain original copyright headers
- License files are included in root directory
- Attribution information is prominently displayed
- Build scripts respect license requirements

## 🤝 Contributing Guidelines

### Contributing to Integrated Components
When contributing improvements to integrated components:

1. **Upstream First**: Consider contributing to original project first
2. **License Compatibility**: Ensure contributions are compatible with existing licenses
3. **Attribution**: Maintain proper attribution for all contributions
4. **Documentation**: Update attribution documentation for significant changes

### Adding New Components
Before integrating new components:

1. **License Review**: Verify license compatibility
2. **Legal Approval**: Obtain legal approval for complex licenses
3. **Attribution Planning**: Plan attribution and documentation strategy
4. **Integration Documentation**: Document integration approach and modifications

## ⚠️ Important Warnings

### License Violations to Avoid
- ❌ **Removing Attribution**: Never remove copyright notices or attribution
- ❌ **License Mixing**: Be careful when combining components with different licenses
- ❌ **Trademark Misuse**: Don't use trademarks to suggest endorsement
- ❌ **Patent Issues**: Be aware of patent implications, especially with Apache 2.0
- ❌ **GPL Contamination**: Avoid accidentally including GPL code without compliance

### Common Mistakes
- Forgetting to include license texts in distributions
- Removing copyright headers from source files
- Not documenting modifications to Apache 2.0 licensed code
- Using trademarks inappropriately
- Assuming public repositories are license-free

## 📞 Support and Contact

### For License Questions
- **Internal Legal**: [your-legal@domain.com]
- **Project Maintainers**: [maintainers@domain.com]
- **Community Forum**: [forum-url]

### Component-Specific Support
- **OpenAPI MCP Python**: https://github.com/cnoe-io/openapi-mcp-codegen/issues
- **OpenAPI MCP Node.js**: https://github.com/harsha-iiiv/openapi-mcp-generator/issues
- **LSP Client**: https://github.com/eli0shin/cli-lsp-client/issues
- **Codanna**: https://github.com/bartolli/codanna/issues
- **BMAD Method**: https://github.com/bmad-code-org/BMAD-METHOD/issues
- **AicodeGuard**: https://github.com/RazBrry/AicodeGuard/issues

## 📚 Additional Resources

### License Information
- [Apache License 2.0 Explained](https://www.apache.org/licenses/LICENSE-2.0)
- [MIT License Explained](https://opensource.org/licenses/MIT)
- [Open Source Initiative](https://opensource.org/)

### Best Practices
- [Open Source License Compliance](https://opensource.com/article/17/9/open-source-licensing)
- [Software Freedom Law Center](https://softwarefreedom.org/)
- [GitHub License Help](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)

## 🔄 Updates and Maintenance

### Regular Reviews
- **Quarterly**: Review all component licenses for changes
- **Before Releases**: Verify attribution completeness
- **Annual**: Legal compliance review
- **As Needed**: Update for new integrations

### Monitoring
- Monitor upstream repositories for license changes
- Track new versions of integrated components
- Stay informed about license compatibility issues
- Maintain relationships with component authors

---

**Last Updated**: January 19, 2025  
**Version**: 1.0  
**Next Review**: April 19, 2025