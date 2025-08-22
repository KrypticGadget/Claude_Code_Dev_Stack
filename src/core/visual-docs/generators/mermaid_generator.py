#!/usr/bin/env python3
"""
Mermaid Diagram Generator
Generates Mermaid diagrams from code analysis and patterns
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import logging

logger = logging.getLogger(__name__)

class MermaidGenerator:
    """Generator for Mermaid diagrams following CodeBoarding patterns"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir / "diagrams" / "mermaid"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load CodeBoarding-compatible templates
        self.templates = {
            'architecture': self._get_architecture_template(),
            'component': self._get_component_template(),
            'flow': self._get_flow_template(),
            'learning_path': self._get_learning_path_template()
        }
    
    def generate(self, diagram_spec) -> Optional[Path]:
        """Generate Mermaid diagram from specification"""
        try:
            # Get template
            template_name = diagram_spec.metadata.get('template', diagram_spec.type)
            if template_name not in self.templates:
                template_name = 'architecture'  # Default fallback
            
            # Generate Mermaid content
            mermaid_content = self._generate_content(diagram_spec, template_name)
            
            # Save Mermaid file
            output_file = self.output_dir / f"{diagram_spec.name}.mmd"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_content)
            
            # Generate SVG if mermaid-cli is available
            svg_file = self._render_to_svg(output_file)
            
            # Generate PNG for screenshots
            png_file = self._render_to_png(output_file)
            
            logger.info(f"Generated Mermaid diagram: {output_file}")
            return svg_file or output_file
            
        except Exception as e:
            logger.error(f"Failed to generate Mermaid diagram: {e}")
            return None
    
    def _generate_content(self, diagram_spec, template_name: str) -> str:
        """Generate Mermaid diagram content"""
        metadata = diagram_spec.metadata
        
        if template_name == 'architecture':
            return self._generate_architecture_diagram(metadata)
        elif template_name == 'component':
            return self._generate_component_diagram(metadata)
        elif template_name == 'flow':
            return self._generate_flow_diagram(metadata)
        elif template_name == 'learning_path':
            return self._generate_learning_path_diagram(metadata)
        else:
            return self._generate_generic_diagram(metadata)
    
    def _generate_architecture_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate system architecture diagram following CodeBoarding patterns"""
        modules = metadata.get('modules', {})
        title = metadata.get('title', 'System Architecture')
        
        # Build nodes and relationships
        nodes = []
        relationships = []
        
        # Create module nodes (limit to 8 as per CodeBoarding guidelines)
        sorted_modules = sorted(modules.items(), key=lambda x: len(x[1]), reverse=True)[:8]
        
        for module_name, components in sorted_modules:
            # Clean module name for display
            display_name = module_name.replace('.', ' ').title()
            if display_name == '':
                display_name = 'Core'
            
            node_id = module_name.replace('.', '_').replace('/', '_') or 'Core'
            nodes.append(f'    {node_id}["{display_name}"]')
            
            # Add component count info
            comp_count = len(components)
            if comp_count > 1:
                nodes.append(f'    {node_id}_info["({comp_count} components)"]')
                relationships.append(f'    {node_id} -.-> {node_id}_info')
        
        # Add relationships based on imports and dependencies
        for i, (module_name, _) in enumerate(sorted_modules[:-1]):
            next_module = sorted_modules[i + 1][0]
            src_id = module_name.replace('.', '_').replace('/', '_') or 'Core'
            dst_id = next_module.replace('.', '_').replace('/', '_') or 'Core'
            
            # Use CodeBoarding relationship patterns
            relationships.append(f'    {src_id} -- "uses" --> {dst_id}')
        
        # Build complete diagram
        diagram_parts = [
            f'graph LR',
            f'    %% {title}',
            *nodes,
            '',
            *relationships
        ]
        
        return '\n'.join(diagram_parts)
    
    def _generate_component_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate component detail diagram"""
        component = metadata.get('component', {})
        title = metadata.get('title', 'Component Details')
        
        nodes = []
        relationships = []
        
        # Main component node
        file_name = Path(component['file']).stem
        main_node = f'Component["{file_name}"]'
        nodes.append(f'    {main_node}')
        
        # Add classes
        classes = component.get('classes', [])[:5]  # Limit per guidelines
        for cls in classes:
            class_id = f"Class_{cls['name']}"
            nodes.append(f'    {class_id}["{cls["name"]}"]')
            relationships.append(f'    Component -- "contains" --> {class_id}')
            
            # Add methods if not too many
            methods = cls.get('methods', [])[:3]
            if methods:
                methods_text = ', '.join(methods)
                method_node = f'{class_id}_methods["({methods_text})"]'
                nodes.append(f'    {method_node}')
                relationships.append(f'    {class_id} -.-> {method_node}')
        
        # Add top-level functions
        functions = component.get('functions', [])[:3]
        if functions:
            for func in functions:
                func_id = f"Func_{func['name']}"
                nodes.append(f'    {func_id}["{func["name"]}()"]')
                relationships.append(f'    Component -- "provides" --> {func_id}')
        
        diagram_parts = [
            f'graph LR',
            f'    %% {title}',
            *nodes,
            '',
            *relationships
        ]
        
        return '\n'.join(diagram_parts)
    
    def _generate_flow_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate flow diagram from patterns"""
        pattern = metadata.get('pattern', {})
        title = metadata.get('title', 'Flow Diagram')
        
        # If we have existing Mermaid content, use it
        if 'content' in pattern:
            return f'%% {title}\n{pattern["content"]}'
        
        # Otherwise generate basic flow
        return f'''graph LR
    %% {title}
    Start["Start"] --> Process["Process"]
    Process --> End["End"]'''
    
    def _generate_learning_path_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate learning path diagram for educational content"""
        components = metadata.get('components', [])
        title = metadata.get('title', 'Learning Path')
        
        if not components:
            return f'''graph LR
    %% {title}
    Basics["Fundamentals"] --> Intermediate["Intermediate"]
    Intermediate --> Advanced["Advanced"]'''
        
        # Create learning progression from components
        nodes = []
        relationships = []
        
        # Sort components by complexity/dependencies
        sorted_components = components[:7]  # Follow CodeBoarding limits
        
        for i, comp in enumerate(sorted_components):
            file_name = Path(comp['file']).stem
            node_id = f"Step{i+1}"
            display_name = file_name.replace('_', ' ').title()
            
            nodes.append(f'    {node_id}["{display_name}"]')
            
            if i > 0:
                prev_node = f"Step{i}"
                relationships.append(f'    {prev_node} -- "leads to" --> {node_id}')
        
        diagram_parts = [
            f'graph LR',
            f'    %% {title}',
            *nodes,
            '',
            *relationships
        ]
        
        return '\n'.join(diagram_parts)
    
    def _generate_generic_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate generic diagram as fallback"""
        title = metadata.get('title', 'Diagram')
        
        return f'''graph LR
    %% {title}
    A["Component A"] --> B["Component B"]
    B --> C["Component C"]'''
    
    def _render_to_svg(self, mermaid_file: Path) -> Optional[Path]:
        """Render Mermaid file to SVG using mermaid-cli"""
        try:
            svg_file = mermaid_file.with_suffix('.svg')
            
            # Try to use mermaid-cli
            result = subprocess.run([
                'mmdc', '-i', str(mermaid_file), '-o', str(svg_file),
                '--theme', 'default', '--backgroundColor', 'white'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and svg_file.exists():
                logger.info(f"Rendered SVG: {svg_file}")
                return svg_file
            else:
                logger.warning(f"mermaid-cli failed: {result.stderr}")
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"mermaid-cli not available or failed: {e}")
            return None
    
    def _render_to_png(self, mermaid_file: Path) -> Optional[Path]:
        """Render Mermaid file to PNG for screenshots"""
        try:
            png_file = mermaid_file.with_suffix('.png')
            
            result = subprocess.run([
                'mmdc', '-i', str(mermaid_file), '-o', str(png_file),
                '--theme', 'default', '--backgroundColor', 'white',
                '--width', '1200', '--height', '800'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and png_file.exists():
                logger.info(f"Rendered PNG: {png_file}")
                return png_file
            else:
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def _get_architecture_template(self) -> str:
        """CodeBoarding-compatible architecture template"""
        return '''graph LR
    %% {title}
    {nodes}
    
    {relationships}'''
    
    def _get_component_template(self) -> str:
        """CodeBoarding-compatible component template"""
        return '''graph LR
    %% {title}
    {component_node}
    {sub_components}
    
    {relationships}'''
    
    def _get_flow_template(self) -> str:
        """CodeBoarding-compatible flow template"""
        return '''graph LR
    %% {title}
    {flow_nodes}
    
    {flow_relationships}'''
    
    def _get_learning_path_template(self) -> str:
        """CodeBoarding-compatible learning path template"""
        return '''graph LR
    %% {title}
    {learning_steps}
    
    {progression_flow}'''
    
    def generate_codeboarding_compatible(self, project_analysis: Dict[str, Any]) -> List[Path]:
        """Generate full set of CodeBoarding-compatible diagrams"""
        generated_files = []
        
        # Main system overview
        if project_analysis.get('components'):
            arch_spec = type('DiagramSpec', (), {
                'name': 'system_overview',
                'type': 'mermaid',
                'metadata': {
                    'modules': self._group_components_by_module(project_analysis['components']),
                    'title': 'System Overview',
                    'template': 'architecture'
                }
            })()
            
            arch_file = self.generate(arch_spec)
            if arch_file:
                generated_files.append(arch_file)
        
        # Component detail diagrams
        for component in project_analysis.get('components', [])[:5]:  # Limit per guidelines
            if component.get('classes') or component.get('functions'):
                comp_spec = type('DiagramSpec', (), {
                    'name': f"component_{Path(component['file']).stem}",
                    'type': 'mermaid',
                    'metadata': {
                        'component': component,
                        'title': f"{Path(component['file']).stem} Component",
                        'template': 'component'
                    }
                })()
                
                comp_file = self.generate(comp_spec)
                if comp_file:
                    generated_files.append(comp_file)
        
        # Learning path if educational content detected
        if self._is_educational_project(project_analysis):
            learning_spec = type('DiagramSpec', (), {
                'name': 'learning_path',
                'type': 'mermaid',
                'metadata': {
                    'components': project_analysis['components'],
                    'title': 'Learning Path',
                    'template': 'learning_path'
                }
            })()
            
            learning_file = self.generate(learning_spec)
            if learning_file:
                generated_files.append(learning_file)
        
        return generated_files
    
    def _group_components_by_module(self, components: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group components by their module/directory"""
        modules = {}
        
        for comp in components:
            module_path = str(Path(comp['file']).parent)
            if module_path not in modules:
                modules[module_path] = []
            modules[module_path].append(comp)
        
        return modules
    
    def _is_educational_project(self, analysis: Dict[str, Any]) -> bool:
        """Detect if this is an educational project"""
        indicators = ['tutorial', 'learn', 'course', 'lesson', 'day', 'step', 'exercise']
        
        project_name = str(analysis.get('project_root', '')).lower()
        return any(indicator in project_name for indicator in indicators)