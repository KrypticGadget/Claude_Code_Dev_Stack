# Content Structure Guidelines

This document establishes the content structure and writing standards for onboarding documentation to ensure clarity, completeness, and consistency.

## 📚 Content Architecture

### 1. Documentation Hierarchy

**Level 1: Project Overview** (`on_boarding.md`)
- System architecture diagram with 4-8 major components
- High-level component descriptions (2-3 sentences each)
- Clear system purpose and scope statement

**Level 2: Component Details** (Individual component files)
- Component-specific architecture diagrams
- Detailed functional descriptions
- Code references and implementation details

**Level 3: Implementation Guides** (When applicable)
- Usage examples and integration patterns
- Configuration and setup instructions
- Best practices and common pitfalls

### 2. Information Density Guidelines

**Main Overview Page**
- **Target Length**: 500-800 words
- **Component Descriptions**: 50-100 words each
- **Focus**: Understanding relationships and overall system purpose

**Component Detail Pages**
- **Target Length**: 300-600 words per component
- **Sub-component Descriptions**: 30-80 words each
- **Focus**: Specific functionality and implementation details

## ✍️ Writing Standards

### 1. Tone and Style

**Professional and Accessible**
- Use clear, concise language appropriate for technical audience
- Avoid unnecessary jargon while maintaining technical accuracy
- Write in present tense and active voice when possible

**Consistent Terminology**
- Use consistent terms throughout all documentation
- Define technical terms on first use
- Maintain terminology glossary for complex projects

### 2. Component Description Format

**Purpose Statement** (First sentence)
```
{Component Name} {primary responsibility/function} by {how it accomplishes this}.
```

**Example**: 
"The Core Framework provides foundational building blocks by defining base classes and container structures that all other components inherit from."

**Detailed Description** (Following sentences)
- Specific capabilities and features
- Key interfaces and integration points
- Role within larger system architecture

### 3. Relationship Description Standards

**Action-Oriented Language**
Use specific verbs that clearly describe the relationship:

| Relationship Type | Preferred Terms | Example |
|------------------|-----------------|---------|
| **Dependency** | "uses", "depends on", "requires" | "UI uses Core Framework" |
| **Data Flow** | "feeds into", "provides data to", "processes for" | "Data feeds into Processing" |
| **Control** | "orchestrates", "manages", "controls" | "Core orchestrates Agents" |
| **Hierarchy** | "contains", "includes", "comprises" | "System contains Components" |
| **Service** | "serves", "provides", "supplies" | "API serves Frontend" |

## 🔗 Code Reference Standards

### 1. Link Formatting Patterns

**Specific Method/Class References**
```markdown
<a href="https://github.com/user/repo/blob/master/path/file.py#L10-L25" target="_blank" rel="noopener noreferrer">`module.class.method` (10:25)</a>
```

**Components**:
- **Target**: External link with security attributes
- **Format**: Backticks around qualified name + line numbers
- **Line Numbers**: `(start:end)` format for clarity

**Full File References**
```markdown
`module.path` (full file reference)
```

**Usage**: For entire modules or when specific lines aren't relevant

### 2. Code Reference Organization

**Grouping by Relevance**
```markdown
**Related Classes/Methods**:
- {Primary implementation class}
- {Key interface or base class}
- {Supporting utilities}
```

**Order by Importance**
1. Primary implementation or entry point
2. Key interfaces and base classes
3. Supporting utilities and helpers
4. Configuration and setup classes

### 3. Reference Quality Standards

**Accuracy Requirements**
- All links must be tested and functional
- Line numbers should be current and accurate
- Module paths should use correct qualified names

**Maintenance Considerations**
- Prefer stable interfaces over implementation details
- Use full file references for frequently changing code
- Include version or commit information when applicable

## 📝 Section Structure Templates

### 1. Main Onboarding Page Structure

```markdown
# {Project Name} Onboarding

{Mermaid architecture diagram}

{Standard badges}

## Component Details

{2-3 sentence project overview explaining purpose and architecture}

### {Component 1 Name}
{Purpose statement and detailed description}

**Related Classes/Methods**:
- {Code references}

### {Component 2 Name}
{Purpose statement and detailed description}

**Related Classes/Methods**:
- {Code references}

### [FAQ](standard_faq_link)
```

### 2. Component Detail Page Structure

```markdown
# {Component Name}

{Component-specific Mermaid diagram}

{Standard badges}

## Component Details

{Detailed explanation of component purpose and architecture role}

### {Sub-Component 1}
{Sub-component purpose and functionality}

**Related Classes/Methods**:
- {Specific code references}

### {Sub-Component 2}
{Sub-component purpose and functionality}

**Related Classes/Methods**:
- {Specific code references}

### [FAQ](standard_faq_link)
```

## 🎯 Content Quality Standards

### 1. Clarity Requirements

**Comprehension Testing**
- Content should be understandable by developers familiar with the technology stack
- Key concepts should be explainable without extensive domain knowledge
- Relationships between components should be clear from descriptions alone

**Structural Clarity**
- Logical flow from general to specific information
- Clear headings and section organization
- Consistent formatting and style

### 2. Completeness Checklist

**System Overview Page**
- [ ] All major components identified and described
- [ ] System purpose and scope clearly stated
- [ ] Component relationships accurately represented
- [ ] Appropriate level of detail for overview

**Component Detail Pages**
- [ ] Component purpose clearly explained
- [ ] Internal structure documented where relevant
- [ ] Code references accurate and comprehensive
- [ ] Integration points identified

### 3. Consistency Standards

**Cross-Document Consistency**
- [ ] Component names consistent across all documents
- [ ] Relationship descriptions use standard terminology
- [ ] Writing style and tone consistent
- [ ] Technical accuracy maintained

**Template Adherence**
- [ ] Required sections present and properly formatted
- [ ] Standard badges and links included
- [ ] Code reference format followed
- [ ] Visual hierarchy maintained

## 📊 Content Adaptation by Project Type

### Educational Projects
**Focus**: Learning progression and skill building
**Language**: Instructional and encouraging
**Details**: Emphasis on concepts and examples
**Structure**: Sequential with clear prerequisites

```markdown
### {Learning Module}
This component introduces {concept} by {teaching method}. Students will learn to {specific skills} and apply these concepts in {practical context}.
```

### Framework Projects
**Focus**: Architecture and extensibility
**Language**: Technical and precise
**Details**: Emphasis on interfaces and patterns
**Structure**: Modular with clear dependencies

```markdown
### {Framework Component}
{Component} provides {architectural service} through {interface description}. It enables {extensibility features} and integrates with {related components}.
```

### Application Projects
**Focus**: User workflows and system integration
**Language**: Functional and service-oriented
**Details**: Emphasis on responsibilities and data flow
**Structure**: Service layers with clear boundaries

```markdown
### {Service Layer}
{Service} manages {business responsibility} by {implementation approach}. It handles {user interactions} and coordinates with {dependent services}.
```

## 🔍 Review and Validation Process

### 1. Content Review Checklist

**Technical Accuracy**
- [ ] All technical details verified against source code
- [ ] Component relationships accurately represented
- [ ] Code references tested and functional

**Documentation Quality**
- [ ] Writing clear and professional
- [ ] Terminology consistent throughout
- [ ] Appropriate detail level for target audience

**User Experience**
- [ ] Information easy to find and navigate
- [ ] Logical flow from overview to details
- [ ] Clear calls-to-action and next steps

### 2. Maintenance Standards

**Regular Updates**
- Review content when code changes significantly
- Update line references if files are reorganized
- Verify external links remain functional

**Version Alignment**
- Keep documentation synchronized with code versions
- Update component descriptions when functionality changes
- Maintain accuracy of architectural representations

This content structure ensures that all onboarding documentation provides value to developers while maintaining professional quality and consistency with the CodeBoarding standards.