#!/usr/bin/env python3
"""
PlantUML Diagram Generator
Generates PlantUML diagrams for detailed architectural documentation
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import logging

logger = logging.getLogger(__name__)

class PlantUMLGenerator:
    """Generator for PlantUML diagrams"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir / "diagrams" / "plantuml"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # PlantUML templates for different diagram types
        self.templates = {
            'class': self._get_class_template(),
            'sequence': self._get_sequence_template(),
            'component': self._get_component_template(),
            'deployment': self._get_deployment_template(),
            'usecase': self._get_usecase_template()
        }
    
    def generate(self, diagram_spec) -> Optional[Path]:
        """Generate PlantUML diagram from specification"""
        try:
            # Determine diagram type
            diagram_type = self._determine_diagram_type(diagram_spec)
            
            # Generate PlantUML content
            plantuml_content = self._generate_content(diagram_spec, diagram_type)
            
            # Save PlantUML file
            output_file = self.output_dir / f"{diagram_spec.name}.puml"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(plantuml_content)
            
            # Render to SVG/PNG if PlantUML is available
            svg_file = self._render_to_svg(output_file)
            png_file = self._render_to_png(output_file)
            
            logger.info(f"Generated PlantUML diagram: {output_file}")
            return svg_file or output_file
            
        except Exception as e:
            logger.error(f"Failed to generate PlantUML diagram: {e}")
            return None
    
    def _determine_diagram_type(self, diagram_spec) -> str:
        """Determine the appropriate PlantUML diagram type"""
        metadata = diagram_spec.metadata
        
        # Check if we have class information
        if 'component' in metadata:
            component = metadata['component']
            if component.get('classes'):
                return 'class'
        
        # Check for sequence/flow information
        if 'flow' in diagram_spec.name or 'sequence' in diagram_spec.name:
            return 'sequence'
        
        # Check for deployment/architecture
        if 'architecture' in diagram_spec.name or 'system' in diagram_spec.name:
            return 'component'
        
        # Default to component diagram
        return 'component'
    
    def _generate_content(self, diagram_spec, diagram_type: str) -> str:
        """Generate PlantUML diagram content"""
        metadata = diagram_spec.metadata
        
        if diagram_type == 'class':
            return self._generate_class_diagram(metadata)
        elif diagram_type == 'sequence':
            return self._generate_sequence_diagram(metadata)
        elif diagram_type == 'component':
            return self._generate_component_diagram(metadata)
        elif diagram_type == 'deployment':
            return self._generate_deployment_diagram(metadata)
        elif diagram_type == 'usecase':
            return self._generate_usecase_diagram(metadata)
        else:
            return self._generate_generic_diagram(metadata)
    
    def _generate_class_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate UML class diagram"""
        component = metadata.get('component', {})
        title = metadata.get('title', 'Class Diagram')
        
        lines = [
            '@startuml',
            f'title {title}',
            '',
            '!theme plain',
            'skinparam classAttributeIconSize 0',
            ''
        ]
        
        # Generate classes
        classes = component.get('classes', [])
        for cls in classes:
            class_name = cls['name']
            lines.append(f'class {class_name} {{')
            
            # Add methods
            methods = cls.get('methods', [])
            for method in methods[:10]:  # Limit methods for readability
                lines.append(f'  +{method}()')
            
            lines.append('}')
            lines.append('')
            
            # Add inheritance relationships
            bases = cls.get('bases', [])
            for base in bases:
                lines.append(f'{base} <|-- {class_name}')
        
        # Add relationships between classes
        if len(classes) > 1:
            lines.append('')
            lines.append('note as N1')
            lines.append('  Component relationships')
            lines.append('  based on code analysis')
            lines.append('end note')
        
        lines.append('')
        lines.append('@enduml')
        
        return '\n'.join(lines)
    
    def _generate_sequence_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate UML sequence diagram"""
        title = metadata.get('title', 'Sequence Diagram')
        
        lines = [
            '@startuml',
            f'title {title}',
            '',
            '!theme plain',
            'participant User',
            'participant System',
            'participant Database',
            '',
            'User -> System: Request',
            'activate System',
            'System -> Database: Query',
            'activate Database',
            'Database --> System: Result',
            'deactivate Database',
            'System --> User: Response',
            'deactivate System',
            '',
            '@enduml'
        ]
        
        return '\n'.join(lines)
    
    def _generate_component_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate UML component diagram"""
        modules = metadata.get('modules', {})
        title = metadata.get('title', 'Component Diagram')
        
        lines = [
            '@startuml',
            f'title {title}',
            '',
            '!theme plain',
            ''
        ]
        
        # Generate components from modules
        for module_name, components in modules.items():
            clean_name = module_name.replace('.', '_').replace('/', '_') or 'Core'
            display_name = module_name.replace('.', ' ').title() or 'Core'
            
            lines.append(f'package "{display_name}" {{')
            
            # Add sub-components
            for comp in components[:5]:  # Limit components
                comp_name = Path(comp['file']).stem
                lines.append(f'  component {comp_name}')
            
            lines.append('}')
            lines.append('')
        
        # Add relationships
        module_names = list(modules.keys())
        for i, module in enumerate(module_names[:-1]):
            next_module = module_names[i + 1]
            src_clean = module.replace('.', '_').replace('/', '_') or 'Core'
            dst_clean = next_module.replace('.', '_').replace('/', '_') or 'Core'
            
            # Find representative components
            src_comp = Path(modules[module][0]['file']).stem if modules[module] else src_clean
            dst_comp = Path(modules[next_module][0]['file']).stem if modules[next_module] else dst_clean
            
            lines.append(f'{src_comp} --> {dst_comp} : uses')
        
        lines.append('')
        lines.append('@enduml')
        
        return '\n'.join(lines)
    
    def _generate_deployment_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate UML deployment diagram"""
        title = metadata.get('title', 'Deployment Diagram')
        
        lines = [
            '@startuml',
            f'title {title}',
            '',
            '!theme plain',
            '',
            'node "Application Server" {',
            '  artifact "Web Application"',
            '  artifact "API Service"',
            '}',
            '',
            'node "Database Server" {',
            '  artifact "Database"',
            '}',
            '',
            'node "Client" {',
            '  artifact "Web Browser"',
            '}',
            '',
            '[Web Browser] --> [Web Application] : HTTP',
            '[Web Application] --> [API Service] : REST',
            '[API Service] --> [Database] : SQL',
            '',
            '@enduml'
        ]
        
        return '\n'.join(lines)
    
    def _generate_usecase_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate UML use case diagram"""
        title = metadata.get('title', 'Use Case Diagram')
        
        lines = [
            '@startuml',
            f'title {title}',
            '',
            '!theme plain',
            '',
            'actor User',
            'actor Admin',
            '',
            'rectangle "System" {',
            '  usecase "View Data" as UC1',
            '  usecase "Edit Data" as UC2',
            '  usecase "Manage Users" as UC3',
            '}',
            '',
            'User --> UC1',
            'User --> UC2',
            'Admin --> UC1',
            'Admin --> UC2',
            'Admin --> UC3',
            '',
            '@enduml'
        ]
        
        return '\n'.join(lines)
    
    def _generate_generic_diagram(self, metadata: Dict[str, Any]) -> str:
        """Generate generic component diagram as fallback"""
        title = metadata.get('title', 'System Diagram')
        
        lines = [
            '@startuml',
            f'title {title}',
            '',
            '!theme plain',
            '',
            'component "Component A"',
            'component "Component B"',
            'component "Component C"',
            '',
            '[Component A] --> [Component B]',
            '[Component B] --> [Component C]',
            '',
            '@enduml'
        ]
        
        return '\n'.join(lines)
    
    def _render_to_svg(self, plantuml_file: Path) -> Optional[Path]:
        """Render PlantUML file to SVG"""
        try:
            svg_file = plantuml_file.with_suffix('.svg')
            
            # Try using plantuml.jar
            result = subprocess.run([
                'java', '-jar', 'plantuml.jar', '-tsvg',
                str(plantuml_file), '-o', str(plantuml_file.parent)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and svg_file.exists():
                logger.info(f"Rendered PlantUML SVG: {svg_file}")
                return svg_file
            else:
                # Try plantuml command
                result = subprocess.run([
                    'plantuml', '-tsvg', str(plantuml_file)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and svg_file.exists():
                    logger.info(f"Rendered PlantUML SVG: {svg_file}")
                    return svg_file
                
                logger.warning(f"PlantUML rendering failed: {result.stderr}")
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"PlantUML not available or failed: {e}")
            return None
    
    def _render_to_png(self, plantuml_file: Path) -> Optional[Path]:
        """Render PlantUML file to PNG"""
        try:
            png_file = plantuml_file.with_suffix('.png')
            
            # Try using plantuml.jar
            result = subprocess.run([
                'java', '-jar', 'plantuml.jar', '-tpng',
                str(plantuml_file), '-o', str(plantuml_file.parent)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and png_file.exists():
                logger.info(f"Rendered PlantUML PNG: {png_file}")
                return png_file
            else:
                # Try plantuml command
                result = subprocess.run([
                    'plantuml', '-tpng', str(plantuml_file)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and png_file.exists():
                    logger.info(f"Rendered PlantUML PNG: {png_file}")
                    return png_file
                
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def _get_class_template(self) -> str:
        """Template for class diagrams"""
        return '''@startuml
title {title}

!theme plain
skinparam classAttributeIconSize 0

{classes}

{relationships}

@enduml'''
    
    def _get_sequence_template(self) -> str:
        """Template for sequence diagrams"""
        return '''@startuml
title {title}

!theme plain

{participants}

{interactions}

@enduml'''
    
    def _get_component_template(self) -> str:
        """Template for component diagrams"""
        return '''@startuml
title {title}

!theme plain

{components}

{relationships}

@enduml'''
    
    def _get_deployment_template(self) -> str:
        """Template for deployment diagrams"""
        return '''@startuml
title {title}

!theme plain

{nodes}

{connections}

@enduml'''
    
    def _get_usecase_template(self) -> str:
        """Template for use case diagrams"""
        return '''@startuml
title {title}

!theme plain

{actors}

{usecases}

{relationships}

@enduml'''