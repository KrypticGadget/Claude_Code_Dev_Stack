---
name: resume-project
description: Resume an existing project by analyzing current state and continuing development
color: purple
---

Use the master-orchestrator agent to resume the current project by analyzing all existing files, documentation, and previous work to understand the project state and continue development where it left off.

First, perform a comprehensive analysis of the current project:
1. Read all README files and documentation
2. Analyze the project structure and architecture
3. Review configuration files (package.json, requirements.txt, etc.)
4. Examine existing code to understand implemented features
5. Check for TODO comments or incomplete implementations
6. Review any existing tests to understand coverage
7. Look for CLAUDE.md or similar project notes

Then provide a detailed summary:
- Project overview and purpose
- Current implementation status
- Completed features and components
- Pending tasks and TODOs
- Recommended next steps
- Any blockers or issues found

Finally, ask the user which aspect they'd like to continue working on or if they have specific tasks in mind.

Variables:
- focus: Specific area to focus on (optional)
- deep_scan: Whether to perform deep code analysis (default: true)

Example usage:
- Basic: /resume-project
- With focus: /resume-project focus:"frontend implementation"
- Quick scan: /resume-project deep_scan:false