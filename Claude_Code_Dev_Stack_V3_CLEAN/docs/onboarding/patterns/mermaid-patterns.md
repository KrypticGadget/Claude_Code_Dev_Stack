# Mermaid Diagram Patterns

This document outlines the visual patterns and conventions used in onboarding documentation diagrams.

## Core Diagram Types

### 1. System Architecture Diagrams
Used in main onboarding files to show high-level component relationships.

```mermaid
graph LR
    Core["Core Framework"]
    Processing["Data Processing"]
    Interface["User Interface"]
    Storage["Data Storage"]
    
    Interface -- "uses" --> Core
    Processing -- "built on" --> Core
    Processing -- "stores to" --> Storage
    Interface -- "displays from" --> Storage
```

**Usage**: Main system overview showing 4-8 major components
**Direction**: Left-to-Right (LR) for process flow, Top-Down (TD) for hierarchical

### 2. Component Breakdown Diagrams  
Used in component detail files to show internal structure.

```mermaid
graph LR
    Component["Main Component"]
    SubA["Sub-Component A"]
    SubB["Sub-Component B"] 
    SubC["Sub-Component C"]
    
    Component -- "contains" --> SubA
    Component -- "contains" --> SubB
    Component -- "contains" --> SubC
    SubA -- "feeds data to" --> SubB
    SubB -- "processes for" --> SubC
```

**Usage**: Internal component structure showing 3-6 sub-components
**Direction**: Varies based on relationships (LR for flow, TD for hierarchy)

### 3. Learning Path Diagrams
Used in educational content to show progression.

```mermaid
graph LR
    Basics["Fundamentals"]
    Structures["Data Structures"]
    Functions["Functions"]
    OOP["Object-Oriented"]
    Applications["Applications"]
    
    Basics -- "leads to" --> Structures
    Structures -- "enables" --> Functions  
    Functions -- "supports" --> OOP
    OOP -- "used in" --> Applications
```

**Usage**: Sequential learning progression
**Direction**: Left-to-Right (LR) showing prerequisite flow

## Node Styling Patterns

### 1. Standard Nodes
```mermaid
graph LR
    Standard["Standard Component"]
    Core["Core Framework"] 
    Data["Data Layer"]
```

**Format**: `NodeID["Display Name"]`
**Usage**: Standard components and services

### 2. Specialized Nodes (Advanced)
```mermaid
graph LR
    A[Square Node]
    B(Rounded Node)
    C{Decision Node}
    D((Circle Node))
```

**Usage**: Different shapes for different component types (rarely used in current patterns)

## Relationship Patterns

### 1. Functional Relationships
| Pattern | Description | Example Usage |
|---------|-------------|---------------|
| `"uses"` | Dependency/composition | UI uses Core Framework |
| `"built on"` | Foundation dependency | Framework built on Base Classes |
| `"feeds into"` | Data flow | Processing feeds into Storage |
| `"orchestrates"` | Control relationship | Core orchestrates Agents |

### 2. Hierarchical Relationships
| Pattern | Description | Example Usage |
|---------|-------------|---------------|
| `"contains"` | Parent-child | System contains Components |
| `"inherits from"` | Class inheritance | Client inherits from Base |
| `"manages"` | Control hierarchy | Manager manages Workers |

### 3. Data Flow Relationships
| Pattern | Description | Example Usage |
|---------|-------------|---------------|
| `"provides data to"` | Data source | Database provides data to API |
| `"retrieves from"` | Data consumer | Service retrieves from Database |
| `"processes for"` | Data transformation | Engine processes for Output |

## Clickable Link Patterns

### 1. Component Detail Links
```mermaid
graph LR
    Component["Component Name"]
    click Component href "https://github.com/user/repo/blob/main/docs/Component.md" "Details"
```

**Format**: Links to detailed component documentation
**Target**: Separate markdown files with component details

### 2. Code Reference Links (In Documentation)
```markdown
click Component href "https://github.com/user/repo/blob/master/src/component.py#L1-50" "Source Code"
```

**Format**: Direct links to source code with line numbers
**Target**: GitHub source files with specific line ranges

## Layout Guidelines

### 1. Component Count Recommendations
- **Main Overview**: 4-8 major components maximum
- **Component Details**: 3-6 sub-components maximum  
- **Learning Paths**: 4-7 steps maximum

### 2. Direction Guidelines
- **Process Flow**: Left-to-Right (LR)
- **Hierarchy**: Top-Down (TD)
- **Circular Dependencies**: Top-Down (TD) with careful relationship naming

### 3. Relationship Density
- **Maximum 2-3 relationships per node** to maintain readability
- **Avoid crossing lines** where possible
- **Group related components** visually

## Project-Specific Adaptations

### Educational Projects (30-Days-Of-Python)
```mermaid
graph LR
    Day1["Python Fundamentals"] 
    Day2["Data Structures"]
    Day3["Control Flow"]
    Day4["Functions"]
    
    Day1 -- "foundation for" --> Day2
    Day2 -- "enables" --> Day3
    Day3 -- "supports" --> Day4
```

**Pattern**: Linear progression with clear prerequisites
**Focus**: Learning sequence and skill building

### Framework Projects (AdalFlow, BERTopic)
```mermaid
graph LR
    Core["Core Framework"]
    Models["Model Clients"]
    Data["Data Processing"]
    Utils["Utilities"]
    
    Models -- "built on" --> Core
    Data -- "uses" --> Core
    Utils -- "supports" --> Core
    Models -- "processes via" --> Data
```

**Pattern**: Hub-and-spoke with core foundation
**Focus**: Modular architecture and dependencies

### Application Projects (AutoGPT, Archon)
```mermaid
graph LR
    API["Backend API"]
    Core["Agent Core"]
    Data["Data Layer"]
    UI["User Interface"]
    
    UI -- "calls" --> API
    API -- "manages" --> Core
    Core -- "persists to" --> Data
    API -- "serves" --> UI
```

**Pattern**: Service layers with clear separation
**Focus**: System architecture and data flow