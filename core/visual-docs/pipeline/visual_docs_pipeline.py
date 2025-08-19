#!/usr/bin/env python3
"""
Visual Documentation Pipeline
Creates comprehensive visual documentation from code and patterns
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentationConfig:
    """Configuration for visual documentation generation"""
    project_root: Path
    output_dir: Path
    source_dirs: List[Path] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=lambda: ["*.py", "*.js", "*.ts", "*.md"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["__pycache__", "node_modules", ".git"])
    diagram_formats: List[str] = field(default_factory=lambda: ["mermaid", "plantuml", "d3"])
    generate_screenshots: bool = True
    generate_videos: bool = False
    integration_mode: str = "codeboarding"  # Integration with CodeBoarding patterns

@dataclass
class DiagramSpec:
    """Specification for a diagram to be generated"""
    name: str
    type: str  # mermaid, plantuml, d3, flowchart, architecture
    source_files: List[Path]
    template: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class VisualDocsPipeline:
    """Main pipeline for generating visual documentation"""
    
    def __init__(self, config: DocumentationConfig):
        self.config = config
        self.project_root = config.project_root
        self.output_dir = config.output_dir
        self.generators = {}
        self.templates = {}
        
        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "diagrams").mkdir(exist_ok=True)
        (self.output_dir / "screenshots").mkdir(exist_ok=True)
        (self.output_dir / "videos").mkdir(exist_ok=True)
        (self.output_dir / "interactive").mkdir(exist_ok=True)
        
        self._initialize_generators()
        self._load_templates()
    
    def _initialize_generators(self):
        """Initialize diagram generators"""
        from ..generators.mermaid_generator import MermaidGenerator
        from ..generators.plantuml_generator import PlantUMLGenerator
        from ..generators.d3_generator import D3Generator
        from ..generators.flowchart_generator import FlowchartGenerator
        
        self.generators = {
            'mermaid': MermaidGenerator(self.config),
            'plantuml': PlantUMLGenerator(self.config),
            'd3': D3Generator(self.config),
            'flowchart': FlowchartGenerator(self.config)
        }
    
    def _load_templates(self):
        """Load documentation templates"""
        templates_dir = Path(__file__).parent.parent / "templates"
        
        for template_file in templates_dir.glob("*.json"):
            template_name = template_file.stem
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    self.templates[template_name] = json.load(f)
                logger.info(f"Loaded template: {template_name}")
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze codebase structure and extract documentation metadata"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'components': [],
            'dependencies': [],
            'flows': [],
            'architecture': {}
        }
        
        # Analyze Python files
        for source_dir in self.config.source_dirs:
            if source_dir.exists():
                self._analyze_python_structure(source_dir, analysis)
        
        # Analyze existing documentation patterns
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            self._analyze_documentation_patterns(docs_dir, analysis)
        
        return analysis
    
    def _analyze_python_structure(self, source_dir: Path, analysis: Dict[str, Any]):
        """Analyze Python source code structure"""
        import ast
        
        for py_file in source_dir.rglob("*.py"):
            if any(excluded in str(py_file) for excluded in self.config.exclude_patterns):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                component_info = {
                    'file': str(py_file.relative_to(self.project_root)),
                    'classes': [],
                    'functions': [],
                    'imports': [],
                    'docstring': ast.get_docstring(tree)
                }
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        component_info['classes'].append({
                            'name': node.name,
                            'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
                            'docstring': ast.get_docstring(node),
                            'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                        })
                    elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:  # Top-level functions
                        component_info['functions'].append({
                            'name': node.name,
                            'docstring': ast.get_docstring(node),
                            'args': [arg.arg for arg in node.args.args]
                        })
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            component_info['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        component_info['imports'].append(node.module)
                
                analysis['components'].append(component_info)
                
            except Exception as e:
                logger.warning(f"Failed to analyze {py_file}: {e}")
    
    def _analyze_documentation_patterns(self, docs_dir: Path, analysis: Dict[str, Any]):
        """Analyze existing documentation for patterns"""
        # Look for onboarding patterns
        onboarding_dir = docs_dir / "onboarding"
        if onboarding_dir.exists():
            patterns_dir = onboarding_dir / "patterns"
            if patterns_dir.exists():
                analysis['codeboarding_patterns'] = {
                    'mermaid_patterns': self._extract_mermaid_patterns(patterns_dir),
                    'component_templates': self._extract_component_templates(patterns_dir),
                    'visual_guidelines': self._extract_visual_guidelines(onboarding_dir / "guidelines")
                }
    
    def _extract_mermaid_patterns(self, patterns_dir: Path) -> List[Dict[str, str]]:
        """Extract Mermaid patterns from existing documentation"""
        patterns = []
        mermaid_file = patterns_dir / "mermaid-patterns.md"
        
        if mermaid_file.exists():
            try:
                with open(mermaid_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract Mermaid code blocks
                import re
                mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
                
                for i, block in enumerate(mermaid_blocks):
                    patterns.append({
                        'id': f'pattern_{i}',
                        'type': 'mermaid',
                        'content': block.strip(),
                        'source': 'codeboarding_patterns'
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to extract Mermaid patterns: {e}")
        
        return patterns
    
    def _extract_component_templates(self, patterns_dir: Path) -> Dict[str, str]:
        """Extract component templates"""
        templates = {}
        template_file = patterns_dir / "component-template.md"
        
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    templates['component'] = f.read()
            except Exception as e:
                logger.warning(f"Failed to extract component template: {e}")
        
        return templates
    
    def _extract_visual_guidelines(self, guidelines_dir: Path) -> Dict[str, Any]:
        """Extract visual guidelines"""
        guidelines = {}
        
        if guidelines_dir and guidelines_dir.exists():
            visual_file = guidelines_dir / "visual-guidelines.md"
            if visual_file.exists():
                try:
                    with open(visual_file, 'r', encoding='utf-8') as f:
                        guidelines['visual'] = f.read()
                except Exception as e:
                    logger.warning(f"Failed to extract visual guidelines: {e}")
        
        return guidelines
    
    def generate_diagrams(self, analysis: Dict[str, Any]) -> List[DiagramSpec]:
        """Generate diagrams based on analysis"""
        diagrams = []
        
        # Generate architecture diagram
        if analysis['components']:
            arch_diagram = self._generate_architecture_diagram(analysis)
            if arch_diagram:
                diagrams.append(arch_diagram)
        
        # Generate component diagrams
        for component in analysis['components']:
            if component['classes'] or component['functions']:
                comp_diagram = self._generate_component_diagram(component)
                if comp_diagram:
                    diagrams.append(comp_diagram)
        
        # Generate flow diagrams from CodeBoarding patterns
        if 'codeboarding_patterns' in analysis:
            flow_diagrams = self._generate_flow_diagrams_from_patterns(analysis['codeboarding_patterns'])
            diagrams.extend(flow_diagrams)
        
        return diagrams
    
    def _generate_architecture_diagram(self, analysis: Dict[str, Any]) -> Optional[DiagramSpec]:
        """Generate overall architecture diagram"""
        components = analysis['components']
        if not components:
            return None
        
        # Group components by directory/module
        modules = {}
        for comp in components:
            module_path = Path(comp['file']).parent
            module_name = str(module_path).replace(os.sep, '.')
            
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(comp)
        
        return DiagramSpec(
            name="system_architecture",
            type="mermaid",
            source_files=[self.project_root / comp['file'] for comp in components],
            template="architecture_template",
            metadata={
                'modules': modules,
                'title': "System Architecture",
                'description': "High-level system architecture and component relationships"
            }
        )
    
    def _generate_component_diagram(self, component: Dict[str, Any]) -> Optional[DiagramSpec]:
        """Generate diagram for individual component"""
        file_path = Path(component['file'])
        component_name = file_path.stem
        
        return DiagramSpec(
            name=f"component_{component_name}",
            type="mermaid",
            source_files=[self.project_root / component['file']],
            template="component_template",
            metadata={
                'component': component,
                'title': f"{component_name} Component",
                'description': component.get('docstring', f"Internal structure of {component_name}")
            }
        )
    
    def _generate_flow_diagrams_from_patterns(self, patterns: Dict[str, Any]) -> List[DiagramSpec]:
        """Generate flow diagrams based on CodeBoarding patterns"""
        diagrams = []
        
        if 'mermaid_patterns' in patterns:
            for i, pattern in enumerate(patterns['mermaid_patterns']):
                diagrams.append(DiagramSpec(
                    name=f"flow_pattern_{i}",
                    type="mermaid",
                    source_files=[],
                    template="flow_template",
                    metadata={
                        'pattern': pattern,
                        'title': f"Flow Pattern {i + 1}",
                        'description': "Generated from CodeBoarding patterns"
                    }
                ))
        
        return diagrams
    
    def render_diagrams(self, diagrams: List[DiagramSpec]) -> Dict[str, Path]:
        """Render all diagrams to files"""
        rendered_files = {}
        
        for diagram in diagrams:
            try:
                generator = self.generators.get(diagram.type)
                if generator:
                    output_file = generator.generate(diagram)
                    if output_file:
                        rendered_files[diagram.name] = output_file
                        logger.info(f"Generated diagram: {diagram.name} -> {output_file}")
                else:
                    logger.warning(f"No generator available for diagram type: {diagram.type}")
                    
            except Exception as e:
                logger.error(f"Failed to render diagram {diagram.name}: {e}")
        
        return rendered_files
    
    def generate_interactive_docs(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> Path:
        """Generate interactive documentation with embedded diagrams"""
        from ..components.interactive_generator import InteractiveGenerator
        
        interactive_gen = InteractiveGenerator(self.config)
        return interactive_gen.generate(analysis, diagrams)
    
    def generate_screenshots(self, interactive_docs: Path) -> List[Path]:
        """Generate screenshots of documentation"""
        if not self.config.generate_screenshots:
            return []
        
        from ..automation.screenshot_generator import ScreenshotGenerator
        
        screenshot_gen = ScreenshotGenerator(self.config)
        return screenshot_gen.generate(interactive_docs)
    
    def generate_videos(self, interactive_docs: Path) -> List[Path]:
        """Generate video documentation"""
        if not self.config.generate_videos:
            return []
        
        from ..automation.video_generator import VideoGenerator
        
        video_gen = VideoGenerator(self.config)
        return video_gen.generate(interactive_docs)
    
    def integrate_with_codeboarding(self, analysis: Dict[str, Any], rendered_files: Dict[str, Path]):
        """Integrate with existing CodeBoarding patterns"""
        if self.config.integration_mode != "codeboarding":
            return
        
        # Update onboarding documentation
        onboarding_dir = self.project_root / "docs" / "onboarding"
        if onboarding_dir.exists():
            self._update_onboarding_docs(onboarding_dir, analysis, rendered_files)
        
        # Generate CodeBoarding-style badges and links
        self._generate_codeboarding_metadata(analysis, rendered_files)
    
    def _update_onboarding_docs(self, onboarding_dir: Path, analysis: Dict[str, Any], rendered_files: Dict[str, Path]):
        """Update onboarding documentation with generated visuals"""
        # Create visual assets directory
        assets_dir = onboarding_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Copy rendered diagrams
        for name, file_path in rendered_files.items():
            if file_path.exists():
                import shutil
                dest_path = assets_dir / f"{name}.svg"
                try:
                    shutil.copy2(file_path, dest_path)
                    logger.info(f"Copied diagram to onboarding assets: {dest_path}")
                except Exception as e:
                    logger.warning(f"Failed to copy diagram {file_path}: {e}")
    
    def _generate_codeboarding_metadata(self, analysis: Dict[str, Any], rendered_files: Dict[str, Path]):
        """Generate CodeBoarding-style metadata and badges"""
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'project': str(self.project_root.name),
            'components_count': len(analysis['components']),
            'diagrams_generated': len(rendered_files),
            'badges': [
                '[![CodeBoarding](https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square)](https://github.com/CodeBoarding/CodeBoarding)',
                '[![Demo](https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square)](https://www.codeboarding.org/demo)',
                '[![Contact](https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square)](mailto:contact@codeboarding.org)'
            ]
        }
        
        metadata_file = self.output_dir / "codeboarding_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Generated CodeBoarding metadata: {metadata_file}")
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete visual documentation pipeline"""
        logger.info("Starting visual documentation pipeline...")
        
        # Step 1: Analyze codebase
        logger.info("Analyzing codebase...")
        analysis = self.analyze_codebase()
        
        # Step 2: Generate diagrams
        logger.info("Generating diagrams...")
        diagrams = self.generate_diagrams(analysis)
        
        # Step 3: Render diagrams
        logger.info("Rendering diagrams...")
        rendered_files = self.render_diagrams(diagrams)
        
        # Step 4: Generate interactive documentation
        logger.info("Generating interactive documentation...")
        interactive_docs = self.generate_interactive_docs(analysis, rendered_files)
        
        # Step 5: Generate screenshots
        screenshots = []
        if self.config.generate_screenshots:
            logger.info("Generating screenshots...")
            screenshots = self.generate_screenshots(interactive_docs)
        
        # Step 6: Generate videos
        videos = []
        if self.config.generate_videos:
            logger.info("Generating videos...")
            videos = self.generate_videos(interactive_docs)
        
        # Step 7: Integrate with CodeBoarding
        logger.info("Integrating with CodeBoarding patterns...")
        self.integrate_with_codeboarding(analysis, rendered_files)
        
        # Generate summary report
        summary = {
            'pipeline_completed': datetime.now().isoformat(),
            'analysis': analysis,
            'diagrams_generated': len(rendered_files),
            'screenshots_generated': len(screenshots),
            'videos_generated': len(videos),
            'interactive_docs': str(interactive_docs),
            'output_directory': str(self.output_dir)
        }
        
        # Save summary
        summary_file = self.output_dir / "pipeline_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Visual documentation pipeline completed. Summary: {summary_file}")
        return summary

def create_default_config(project_root: Union[str, Path]) -> DocumentationConfig:
    """Create default configuration for a project"""
    project_root = Path(project_root)
    
    # Auto-detect source directories
    source_dirs = []
    for potential_dir in ['src', 'lib', 'core', project_root.name]:
        dir_path = project_root / potential_dir
        if dir_path.exists() and dir_path.is_dir():
            source_dirs.append(dir_path)
    
    # If no conventional directories found, use project root
    if not source_dirs:
        source_dirs = [project_root]
    
    return DocumentationConfig(
        project_root=project_root,
        output_dir=project_root / "docs" / "visual",
        source_dirs=source_dirs
    )

def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate visual documentation")
    parser.add_argument("project_root", help="Root directory of the project")
    parser.add_argument("--output", "-o", help="Output directory for documentation")
    parser.add_argument("--screenshots", action="store_true", help="Generate screenshots")
    parser.add_argument("--videos", action="store_true", help="Generate videos")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Create configuration
    if args.config and Path(args.config).exists():
        with open(args.config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        config = DocumentationConfig(**config_data)
    else:
        config = create_default_config(args.project_root)
        
        if args.output:
            config.output_dir = Path(args.output)
        if args.screenshots:
            config.generate_screenshots = True
        if args.videos:
            config.generate_videos = True
    
    # Run pipeline
    pipeline = VisualDocsPipeline(config)
    summary = pipeline.run_full_pipeline()
    
    print(f"Documentation generated successfully!")
    print(f"Output directory: {config.output_dir}")
    print(f"Diagrams: {summary['diagrams_generated']}")
    print(f"Screenshots: {summary['screenshots_generated']}")
    print(f"Videos: {summary['videos_generated']}")

if __name__ == "__main__":
    main()