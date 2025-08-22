#!/usr/bin/env python3
"""
CodeBoarding Integration Module
Integrates visual documentation pipeline with existing CodeBoarding patterns
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CodeBoardingIntegrator:
    """Handles integration with CodeBoarding onboarding patterns"""
    
    def __init__(self, project_root: Path, visual_docs_output: Path):
        self.project_root = project_root
        self.visual_docs_output = visual_docs_output
        self.onboarding_dir = project_root / "docs" / "onboarding"
        
        # CodeBoarding pattern configurations
        self.codeboarding_config = {
            'badges': [
                '[![CodeBoarding](https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square)](https://github.com/CodeBoarding/CodeBoarding)',
                '[![Demo](https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square)](https://www.codeboarding.org/demo)',
                '[![Contact](https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square)](mailto:contact@codeboarding.org)'
            ],
            'faq_link': 'For more detailed questions, please refer to our [FAQ](https://github.com/CodeBoarding/CodeBoarding/blob/main/FAQ.md).',
            'visual_guidelines': self._load_visual_guidelines(),
            'mermaid_patterns': self._load_mermaid_patterns()
        }
    
    def integrate_visual_docs(self, analysis: Dict[str, Any], generated_diagrams: Dict[str, Path]) -> Dict[str, Path]:
        """Main integration method that updates onboarding docs with visual content"""
        integration_results = {}
        
        try:
            # Update main onboarding file
            main_onboarding = self._update_main_onboarding(analysis, generated_diagrams)
            if main_onboarding:
                integration_results['main_onboarding'] = main_onboarding
            
            # Update component detail files
            component_files = self._update_component_files(analysis, generated_diagrams)
            integration_results['component_files'] = component_files
            
            # Create visual assets directory
            assets_dir = self._create_visual_assets_directory(generated_diagrams)
            if assets_dir:
                integration_results['assets_directory'] = assets_dir
            
            # Update onboarding patterns with new visual examples
            patterns_updated = self._update_onboarding_patterns(generated_diagrams)
            integration_results['patterns_updated'] = patterns_updated
            
            # Generate CodeBoarding-compatible README
            readme_file = self._generate_codeboarding_readme(analysis, generated_diagrams)
            if readme_file:
                integration_results['readme'] = readme_file
            
            logger.info(f"CodeBoarding integration completed: {len(integration_results)} items updated")
            return integration_results
            
        except Exception as e:
            logger.error(f"CodeBoarding integration failed: {e}")
            return {}
    
    def _load_visual_guidelines(self) -> Dict[str, Any]:
        """Load existing visual guidelines from onboarding docs"""
        guidelines = {}
        guidelines_file = self.onboarding_dir / "guidelines" / "visual-guidelines.md"
        
        if guidelines_file.exists():
            try:
                with open(guidelines_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract key patterns from guidelines
                guidelines.update({
                    'max_components': self._extract_max_components(content),
                    'preferred_direction': self._extract_preferred_direction(content),
                    'relationship_patterns': self._extract_relationship_patterns(content),
                    'color_scheme': self._extract_color_scheme(content)
                })
                
            except Exception as e:
                logger.warning(f"Failed to load visual guidelines: {e}")
        
        return guidelines
    
    def _load_mermaid_patterns(self) -> List[Dict[str, Any]]:
        """Load existing Mermaid patterns from onboarding docs"""
        patterns = []
        patterns_file = self.onboarding_dir / "patterns" / "mermaid-patterns.md"
        
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract Mermaid code blocks with context
                mermaid_blocks = re.findall(
                    r'### (.*?)\n.*?```mermaid\n(.*?)\n```.*?\*\*Usage\*\*: (.*?)\n',
                    content, re.DOTALL
                )
                
                for title, diagram_code, usage in mermaid_blocks:
                    patterns.append({
                        'title': title.strip(),
                        'code': diagram_code.strip(),
                        'usage': usage.strip(),
                        'type': self._determine_pattern_type(diagram_code)
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to load Mermaid patterns: {e}")
        
        return patterns
    
    def _extract_max_components(self, content: str) -> int:
        """Extract maximum component count from guidelines"""
        match = re.search(r'Maximum.*?(\d+).*?components', content, re.IGNORECASE)
        return int(match.group(1)) if match else 8
    
    def _extract_preferred_direction(self, content: str) -> str:
        """Extract preferred diagram direction"""
        if 'Left-to-Right (LR)' in content and 'Recommended Default' in content:
            return 'LR'
        return 'LR'  # Default
    
    def _extract_relationship_patterns(self, content: str) -> List[str]:
        """Extract relationship patterns from guidelines"""
        patterns = []
        
        # Look for relationship pattern table
        pattern_matches = re.findall(r'\| `"([^"]+)"` \|', content)
        if pattern_matches:
            patterns.extend(pattern_matches)
        else:
            # Default patterns from CodeBoarding
            patterns = ["uses", "built on", "feeds into", "orchestrates", "contains", "manages"]
        
        return patterns
    
    def _extract_color_scheme(self, content: str) -> Dict[str, str]:
        """Extract color scheme information"""
        # Default CodeBoarding color scheme
        return {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728'
        }
    
    def _determine_pattern_type(self, diagram_code: str) -> str:
        """Determine the type of Mermaid pattern"""
        if 'graph LR' in diagram_code:
            return 'architecture'
        elif 'graph TD' in diagram_code:
            return 'hierarchy'
        elif 'flowchart' in diagram_code:
            return 'workflow'
        else:
            return 'generic'
    
    def _update_main_onboarding(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> Optional[Path]:
        """Update main onboarding documentation file"""
        main_file = self.onboarding_dir / "on_boarding.md"
        
        if not main_file.exists():
            # Create new main onboarding file
            return self._create_main_onboarding(analysis, diagrams)
        else:
            # Update existing file
            return self._update_existing_onboarding(main_file, analysis, diagrams)
    
    def _create_main_onboarding(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> Path:
        """Create new main onboarding file"""
        project_name = self.project_root.name
        
        # Find the main architecture diagram
        main_diagram = self._find_main_diagram(diagrams)
        main_diagram_content = self._get_diagram_content(main_diagram) if main_diagram else self._generate_fallback_diagram(analysis)
        
        # Generate component sections
        component_sections = self._generate_component_sections(analysis, diagrams)
        
        content = f"""# {project_name}

{main_diagram_content}

{self._format_codeboarding_badges()}

## Component Details

{component_sections}

## FAQ

{self.codeboarding_config['faq_link']}
"""
        
        main_file = self.onboarding_dir / "on_boarding.md"
        self.onboarding_dir.mkdir(parents=True, exist_ok=True)
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created main onboarding file: {main_file}")
        return main_file
    
    def _update_existing_onboarding(self, main_file: Path, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> Path:
        """Update existing onboarding file with new visual content"""
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update main diagram if found
            main_diagram = self._find_main_diagram(diagrams)
            if main_diagram:
                new_diagram_content = self._get_diagram_content(main_diagram)
                content = self._replace_main_diagram(content, new_diagram_content)
            
            # Update component sections
            component_sections = self._generate_component_sections(analysis, diagrams)
            content = self._update_component_sections(content, component_sections)
            
            # Ensure CodeBoarding badges are present
            if not any(badge in content for badge in ['CodeBoarding', 'Generated%20by']):
                content = self._add_codeboarding_badges(content)
            
            # Add timestamp comment
            timestamp_comment = f"<!-- Updated by Visual Documentation Pipeline on {datetime.now().isoformat()} -->\n"
            content = timestamp_comment + content
            
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated existing onboarding file: {main_file}")
            return main_file
            
        except Exception as e:
            logger.error(f"Failed to update existing onboarding file: {e}")
            return None
    
    def _find_main_diagram(self, diagrams: Dict[str, Path]) -> Optional[Path]:
        """Find the main system architecture diagram"""
        # Look for system/architecture diagrams first
        priorities = ['system_architecture', 'system_overview', 'architecture', 'main', 'overview']
        
        for priority in priorities:
            for name, path in diagrams.items():
                if priority in name.lower():
                    return path
        
        # Return first available diagram
        if diagrams:
            return next(iter(diagrams.values()))
        
        return None
    
    def _get_diagram_content(self, diagram_path: Path) -> str:
        """Get diagram content for embedding in markdown"""
        if not diagram_path or not diagram_path.exists():
            return ""
        
        if diagram_path.suffix == '.mmd':
            # Mermaid diagram
            try:
                with open(diagram_path, 'r', encoding='utf-8') as f:
                    mermaid_content = f.read()
                
                return f"""```mermaid
{mermaid_content}
```"""
            except Exception as e:
                logger.warning(f"Failed to read Mermaid diagram: {e}")
                return ""
        
        elif diagram_path.suffix in ['.svg', '.png']:
            # Image diagram
            relative_path = self._get_relative_path_for_onboarding(diagram_path)
            return f"![System Architecture]({relative_path})"
        
        elif diagram_path.suffix == '.html':
            # Interactive diagram - create link
            relative_path = self._get_relative_path_for_onboarding(diagram_path)
            return f"[Interactive System Architecture]({relative_path})"
        
        return ""
    
    def _generate_fallback_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate a simple fallback diagram if none exists"""
        components = analysis.get('components', [])
        
        if not components:
            return """```mermaid
graph LR
    System["System"] --> Components["Components"]
    Components --> Documentation["Documentation"]
```"""
        
        # Create simple diagram from first few components
        diagram_lines = ["graph LR"]
        
        for i, comp in enumerate(components[:4]):
            comp_name = Path(comp['file']).stem
            clean_name = comp_name.replace('_', ' ').title()
            node_id = f"Comp{i+1}"
            
            diagram_lines.append(f'    {node_id}["{clean_name}"]')
            
            if i > 0:
                prev_id = f"Comp{i}"
                diagram_lines.append(f'    {prev_id} --> {node_id}')
        
        return f"""```mermaid
{chr(10).join(diagram_lines)}
```"""
    
    def _generate_component_sections(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> str:
        """Generate component detail sections"""
        sections = []
        components = analysis.get('components', [])
        
        for component in components[:8]:  # Follow CodeBoarding guidelines
            file_name = Path(component['file']).stem
            display_name = file_name.replace('_', ' ').title()
            
            # Find related diagram
            related_diagram = self._find_component_diagram(file_name, diagrams)
            diagram_content = ""
            
            if related_diagram:
                diagram_content = self._get_diagram_content(related_diagram)
            
            # Create component section
            section = f"""### {display_name}

{component.get('docstring', 'No description available')}

**Purpose**: {self._infer_component_purpose(component)}

{diagram_content}

**Related Classes/Methods**:
{self._format_component_details(component)}
"""
            
            sections.append(section)
        
        return '\n\n'.join(sections)
    
    def _find_component_diagram(self, component_name: str, diagrams: Dict[str, Path]) -> Optional[Path]:
        """Find diagram related to specific component"""
        for name, path in diagrams.items():
            if component_name.lower() in name.lower():
                return path
        return None
    
    def _infer_component_purpose(self, component: Dict[str, Any]) -> str:
        """Infer component purpose from its structure"""
        classes_count = len(component.get('classes', []))
        functions_count = len(component.get('functions', []))
        
        if classes_count > functions_count:
            return f"Object-oriented component with {classes_count} classes providing structured functionality"
        elif functions_count > 0:
            return f"Functional component providing {functions_count} utility functions"
        else:
            return "Configuration or data component"
    
    def _format_component_details(self, component: Dict[str, Any]) -> str:
        """Format component classes and methods for display"""
        details = []
        
        # Add classes
        for cls in component.get('classes', [])[:3]:  # Limit display
            class_info = f"- **{cls['name']}**: {cls.get('docstring', 'Class definition')}"
            if cls.get('methods'):
                method_list = ', '.join(cls['methods'][:5])
                class_info += f" (Methods: {method_list})"
            details.append(class_info)
        
        # Add functions
        for func in component.get('functions', [])[:3]:  # Limit display
            func_info = f"- **{func['name']}()**: {func.get('docstring', 'Function definition')}"
            details.append(func_info)
        
        return '\n'.join(details) if details else "No major classes or functions found"
    
    def _format_codeboarding_badges(self) -> str:
        """Format CodeBoarding badges for markdown"""
        return ''.join(self.codeboarding_config['badges'])
    
    def _replace_main_diagram(self, content: str, new_diagram: str) -> str:
        """Replace main diagram in existing content"""
        # Look for existing Mermaid diagram
        pattern = r'```mermaid\n.*?\n```'
        
        if re.search(pattern, content, re.DOTALL):
            return re.sub(pattern, new_diagram, content, count=1, flags=re.DOTALL)
        else:
            # Insert after title
            lines = content.split('\n')
            title_line = -1
            
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    title_line = i
                    break
            
            if title_line >= 0:
                lines.insert(title_line + 2, new_diagram)
                lines.insert(title_line + 3, "")
                return '\n'.join(lines)
            else:
                return new_diagram + '\n\n' + content
    
    def _update_component_sections(self, content: str, new_sections: str) -> str:
        """Update component sections in existing content"""
        # Look for "## Component Details" section
        pattern = r'## Component Details.*?(?=## |$)'
        
        replacement = f"## Component Details\n\n{new_sections}\n\n"
        
        if re.search(pattern, content, re.DOTALL):
            return re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # Add before FAQ section
            faq_pattern = r'## FAQ'
            if re.search(faq_pattern, content):
                return re.sub(faq_pattern, replacement + "## FAQ", content)
            else:
                return content + '\n\n' + replacement
    
    def _add_codeboarding_badges(self, content: str) -> str:
        """Add CodeBoarding badges to content"""
        badges = self._format_codeboarding_badges()
        
        # Insert after first Mermaid diagram
        mermaid_pattern = r'(```mermaid\n.*?\n```)'
        
        if re.search(mermaid_pattern, content, re.DOTALL):
            return re.sub(mermaid_pattern, r'\1\n\n' + badges + '\n', content, count=1, flags=re.DOTALL)
        else:
            # Insert after title
            lines = content.split('\n')
            if lines and lines[0].startswith('# '):
                lines.insert(2, badges)
                lines.insert(3, "")
                return '\n'.join(lines)
            else:
                return badges + '\n\n' + content
    
    def _get_relative_path_for_onboarding(self, file_path: Path) -> str:
        """Get relative path for onboarding directory"""
        try:
            return str(file_path.relative_to(self.onboarding_dir))
        except ValueError:
            # File is outside onboarding directory, copy it to assets
            assets_dir = self.onboarding_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            dest_path = assets_dir / file_path.name
            import shutil
            shutil.copy2(file_path, dest_path)
            
            return f"assets/{file_path.name}"
    
    def _update_component_files(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> List[Path]:
        """Update individual component detail files"""
        component_files = []
        components_dir = self.onboarding_dir / "components"
        components_dir.mkdir(exist_ok=True)
        
        for component in analysis.get('components', []):
            try:
                file_name = Path(component['file']).stem
                component_file = self._create_component_detail_file(component, diagrams, components_dir)
                if component_file:
                    component_files.append(component_file)
                    
            except Exception as e:
                logger.warning(f"Failed to create component file for {component.get('file', 'unknown')}: {e}")
        
        return component_files
    
    def _create_component_detail_file(self, component: Dict[str, Any], diagrams: Dict[str, Path], output_dir: Path) -> Optional[Path]:
        """Create detailed component documentation file"""
        file_name = Path(component['file']).stem
        display_name = file_name.replace('_', ' ').title()
        
        # Find related diagram
        related_diagram = self._find_component_diagram(file_name, diagrams)
        diagram_content = ""
        
        if related_diagram:
            diagram_content = self._get_diagram_content(related_diagram)
        
        content = f"""# {display_name} Component

{component.get('docstring', 'No description available')}

## Purpose

{self._infer_component_purpose(component)}

## Structure

{diagram_content}

## Classes and Methods

{self._format_detailed_component_info(component)}

## Usage Examples

```python
# Example usage of {file_name}
from {file_name} import *

# TODO: Add specific usage examples
```

## Dependencies

{self._format_component_dependencies(component)}

---

{self._format_codeboarding_badges()}
"""
        
        component_file = output_dir / f"{file_name}.md"
        with open(component_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created component detail file: {component_file}")
        return component_file
    
    def _format_detailed_component_info(self, component: Dict[str, Any]) -> str:
        """Format detailed component information"""
        info_sections = []
        
        # Classes section
        classes = component.get('classes', [])
        if classes:
            classes_info = ["### Classes\n"]
            for cls in classes:
                classes_info.append(f"#### {cls['name']}")
                classes_info.append(f"{cls.get('docstring', 'No description available')}")
                
                if cls.get('bases'):
                    classes_info.append(f"**Inherits from**: {', '.join(cls['bases'])}")
                
                if cls.get('methods'):
                    classes_info.append("**Methods**:")
                    for method in cls['methods']:
                        classes_info.append(f"- `{method}()`")
                
                classes_info.append("")
            
            info_sections.append('\n'.join(classes_info))
        
        # Functions section
        functions = component.get('functions', [])
        if functions:
            functions_info = ["### Functions\n"]
            for func in functions:
                functions_info.append(f"#### {func['name']}()")
                functions_info.append(f"{func.get('docstring', 'No description available')}")
                
                if func.get('args'):
                    functions_info.append(f"**Parameters**: {', '.join(func['args'])}")
                
                functions_info.append("")
            
            info_sections.append('\n'.join(functions_info))
        
        return '\n'.join(info_sections) if info_sections else "No major classes or functions found."
    
    def _format_component_dependencies(self, component: Dict[str, Any]) -> str:
        """Format component dependencies"""
        imports = component.get('imports', [])
        
        if not imports:
            return "No external dependencies detected."
        
        deps_info = ["### External Dependencies\n"]
        for imp in imports[:10]:  # Limit display
            deps_info.append(f"- `{imp}`")
        
        if len(imports) > 10:
            deps_info.append(f"- ... and {len(imports) - 10} more")
        
        return '\n'.join(deps_info)
    
    def _create_visual_assets_directory(self, diagrams: Dict[str, Path]) -> Optional[Path]:
        """Create visual assets directory and copy diagrams"""
        assets_dir = self.onboarding_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        try:
            import shutil
            copied_files = 0
            
            for name, diagram_path in diagrams.items():
                if diagram_path and diagram_path.exists():
                    dest_path = assets_dir / f"{name}{diagram_path.suffix}"
                    shutil.copy2(diagram_path, dest_path)
                    copied_files += 1
            
            logger.info(f"Copied {copied_files} diagrams to assets directory")
            return assets_dir
            
        except Exception as e:
            logger.error(f"Failed to create visual assets directory: {e}")
            return None
    
    def _update_onboarding_patterns(self, diagrams: Dict[str, Path]) -> Dict[str, int]:
        """Update onboarding patterns with new examples"""
        patterns_dir = self.onboarding_dir / "patterns"
        patterns_dir.mkdir(exist_ok=True)
        
        updates = {'examples_added': 0, 'patterns_updated': 0}
        
        # Update Mermaid patterns with real examples
        mermaid_patterns_file = patterns_dir / "mermaid-patterns.md"
        if mermaid_patterns_file.exists():
            try:
                with open(mermaid_patterns_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add new examples section
                new_examples = self._generate_pattern_examples(diagrams)
                if new_examples:
                    content += f"\n\n## Generated Examples\n\n{new_examples}"
                    updates['examples_added'] = len(diagrams)
                
                with open(mermaid_patterns_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updates['patterns_updated'] = 1
                
            except Exception as e:
                logger.warning(f"Failed to update Mermaid patterns: {e}")
        
        return updates
    
    def _generate_pattern_examples(self, diagrams: Dict[str, Path]) -> str:
        """Generate pattern examples from generated diagrams"""
        examples = []
        
        for name, diagram_path in diagrams.items():
            if diagram_path and diagram_path.suffix == '.mmd':
                try:
                    with open(diagram_path, 'r', encoding='utf-8') as f:
                        diagram_content = f.read()
                    
                    example = f"""### {name.replace('_', ' ').title()}
Generated from project analysis.

```mermaid
{diagram_content}
```

**Usage**: Auto-generated system documentation
**Type**: {self._determine_pattern_type(diagram_content)}
"""
                    examples.append(example)
                    
                except Exception as e:
                    logger.warning(f"Failed to read diagram {diagram_path}: {e}")
        
        return '\n\n'.join(examples)
    
    def _generate_codeboarding_readme(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> Optional[Path]:
        """Generate CodeBoarding-compatible README for the project"""
        project_name = self.project_root.name
        
        readme_content = f"""# {project_name}

Comprehensive documentation with visual architecture diagrams.

## Quick Start

1. Explore the [Interactive Documentation](docs/visual/interactive/index.html)
2. View [System Architecture](docs/onboarding/on_boarding.md)
3. Browse [Component Details](docs/onboarding/components/)

## Documentation Structure

- **Visual Documentation**: Interactive diagrams and component exploration
- **Onboarding Guides**: Step-by-step project understanding
- **Component References**: Detailed API documentation

## Generated Content

This documentation includes:
- {len(diagrams)} architectural diagrams
- {len(analysis.get('components', []))} component analyses
- Interactive exploration tools
- Visual learning aids

{self._format_codeboarding_badges()}

## More Information

{self.codeboarding_config['faq_link']}
"""
        
        readme_file = self.project_root / "README_VISUAL_DOCS.md"
        
        try:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info(f"Generated CodeBoarding README: {readme_file}")
            return readme_file
            
        except Exception as e:
            logger.error(f"Failed to generate README: {e}")
            return None