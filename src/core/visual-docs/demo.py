#!/usr/bin/env python3
"""
Visual Documentation Pipeline Demo
Demonstrates the capabilities of the visual documentation system
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.visual_docs_pipeline import VisualDocsPipeline, create_default_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_current_project():
    """Demo the pipeline on the current visual-docs project"""
    
    print("=" * 60)
    print("VISUAL DOCUMENTATION PIPELINE DEMO")
    print("=" * 60)
    
    # Use the parent directory (Claude_Code_Dev_Stack_V3_CLEAN) as the project
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent  # Go up to Claude_Code_Dev_Stack_V3_CLEAN
    
    print(f"Demo project: {project_root}")
    print(f"Target: Visual documentation of the Claude Code Dev Stack")
    
    # Create configuration
    config = create_default_config(project_root)
    config.output_dir = current_dir / "demo_output"
    config.source_dirs = [
        project_root / "core",
        current_dir  # Include visual-docs itself
    ]
    config.diagram_formats = ["mermaid", "d3"]  # Start with basic formats
    config.generate_screenshots = False  # Disable for demo
    config.generate_videos = False  # Disable for demo
    config.integration_mode = "standalone"  # Don't modify existing docs
    
    print(f"Output directory: {config.output_dir}")
    
    try:
        # Create pipeline
        print("\n1. Initializing pipeline...")
        pipeline = VisualDocsPipeline(config)
        
        # Analyze project
        print("\n2. Analyzing project structure...")
        analysis = pipeline.analyze_codebase()
        
        components_found = len(analysis.get('components', []))
        print(f"   Found {components_found} Python components")
        
        if components_found == 0:
            print("   No components found - creating sample analysis")
            analysis = create_sample_analysis()
        
        # Generate diagrams
        print("\n3. Generating diagrams...")
        diagrams = pipeline.generate_diagrams(analysis)
        print(f"   Created {len(diagrams)} diagram specifications")
        
        # Render diagrams
        print("\n4. Rendering diagrams...")
        rendered_files = pipeline.render_diagrams(diagrams)
        print(f"   Rendered {len(rendered_files)} diagram files")
        
        # Generate interactive docs
        print("\n5. Creating interactive documentation...")
        interactive_docs = pipeline.generate_interactive_docs(analysis, rendered_files)
        print(f"   Generated: {interactive_docs}")
        
        # Summary
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"📁 Output: {config.output_dir}")
        print(f"📊 Diagrams: {len(rendered_files)}")
        print(f"📖 Interactive docs: {interactive_docs}")
        print(f"🎯 Components analyzed: {components_found}")
        
        print(f"\n🔗 Open {interactive_docs} in your browser to explore!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}", exc_info=True)
        return False

def create_sample_analysis():
    """Create sample analysis data for demonstration"""
    return {
        'timestamp': '2024-01-01T00:00:00',
        'project_root': str(Path.cwd()),
        'components': [
            {
                'file': 'pipeline/visual_docs_pipeline.py',
                'classes': [
                    {
                        'name': 'VisualDocsPipeline',
                        'bases': [],
                        'docstring': 'Main pipeline for generating visual documentation',
                        'methods': ['analyze_codebase', 'generate_diagrams', 'render_diagrams']
                    },
                    {
                        'name': 'DocumentationConfig',
                        'bases': [],
                        'docstring': 'Configuration for visual documentation generation',
                        'methods': []
                    }
                ],
                'functions': [
                    {
                        'name': 'create_default_config',
                        'docstring': 'Create default configuration for a project',
                        'args': ['project_root']
                    }
                ],
                'imports': ['pathlib', 'json', 'logging'],
                'docstring': 'Visual Documentation Pipeline - Creates comprehensive visual documentation from code and patterns'
            },
            {
                'file': 'generators/mermaid_generator.py',
                'classes': [
                    {
                        'name': 'MermaidGenerator',
                        'bases': [],
                        'docstring': 'Generator for Mermaid diagrams following CodeBoarding patterns',
                        'methods': ['generate', '_generate_content', '_render_to_svg']
                    }
                ],
                'functions': [],
                'imports': ['subprocess', 'pathlib'],
                'docstring': 'Mermaid Diagram Generator - Generates Mermaid diagrams from code analysis and patterns'
            },
            {
                'file': 'generators/d3_generator.py',
                'classes': [
                    {
                        'name': 'D3Generator',
                        'bases': [],
                        'docstring': 'Generator for interactive D3.js visualizations',
                        'methods': ['generate', '_generate_data', '_generate_html']
                    }
                ],
                'functions': [],
                'imports': ['json', 'pathlib'],
                'docstring': 'D3.js Interactive Diagram Generator - Generates interactive D3.js visualizations for complex data relationships'
            },
            {
                'file': 'components/interactive_generator.py',
                'classes': [
                    {
                        'name': 'InteractiveGenerator',
                        'bases': [],
                        'docstring': 'Generator for interactive HTML documentation',
                        'methods': ['generate', '_generate_main_page', '_generate_component_pages']
                    }
                ],
                'functions': [],
                'imports': ['pathlib', 'json'],
                'docstring': 'Interactive Documentation Generator - Creates interactive HTML documentation with embedded diagrams and examples'
            }
        ],
        'dependencies': [],
        'flows': [],
        'architecture': {}
    }

def demo_specific_features():
    """Demo specific features of the pipeline"""
    
    print("\n" + "=" * 60)
    print("FEATURE DEMONSTRATIONS")
    print("=" * 60)
    
    current_dir = Path(__file__).parent
    
    # Demo 1: Mermaid Generation
    print("\n📊 Demo: Mermaid Diagram Generation")
    try:
        from generators.mermaid_generator import MermaidGenerator
        
        # Create sample config
        sample_config = type('Config', (), {
            'output_dir': current_dir / "demo_output",
            'integration_mode': 'standalone'
        })()
        
        generator = MermaidGenerator(sample_config)
        
        # Create sample diagram spec
        diagram_spec = type('DiagramSpec', (), {
            'name': 'demo_architecture',
            'type': 'mermaid',
            'source_files': [],
            'metadata': {
                'modules': {
                    'pipeline': [{'file': 'pipeline/visual_docs_pipeline.py'}],
                    'generators': [{'file': 'generators/mermaid_generator.py'}],
                    'components': [{'file': 'components/interactive_generator.py'}]
                },
                'title': 'Demo System Architecture',
                'template': 'architecture'
            }
        })()
        
        result = generator.generate(diagram_spec)
        if result:
            print(f"   ✓ Generated: {result}")
        else:
            print("   ⚠ Mermaid generation not available (missing tools)")
            
    except Exception as e:
        print(f"   ❌ Mermaid demo failed: {e}")
    
    # Demo 2: Interactive Documentation
    print("\n📖 Demo: Interactive Documentation Generation")
    try:
        from components.interactive_generator import InteractiveGenerator
        
        sample_config = type('Config', (), {
            'output_dir': current_dir / "demo_output"
        })()
        
        generator = InteractiveGenerator(sample_config)
        
        sample_analysis = create_sample_analysis()
        sample_diagrams = {}
        
        result = generator.generate(sample_analysis, sample_diagrams)
        print(f"   ✓ Generated: {result}")
        
    except Exception as e:
        print(f"   ❌ Interactive docs demo failed: {e}")
    
    # Demo 3: Configuration
    print("\n⚙️ Demo: Configuration System")
    try:
        config = create_default_config(current_dir.parent)
        print(f"   ✓ Project root: {config.project_root}")
        print(f"   ✓ Output dir: {config.output_dir}")
        print(f"   ✓ Source dirs: {len(config.source_dirs)} directories")
        print(f"   ✓ Formats: {config.diagram_formats}")
        
    except Exception as e:
        print(f"   ❌ Configuration demo failed: {e}")

def check_dependencies():
    """Check and report on available dependencies"""
    
    print("\n" + "=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60)
    
    dependencies = {
        'Core Python': ['ast', 'pathlib', 'json', 'logging'],
        'Optional Tools': ['mermaid-cli', 'plantuml', 'ffmpeg'],
        'Python Packages': ['playwright', 'selenium', 'Pillow', 'matplotlib']
    }
    
    for category, deps in dependencies.items():
        print(f"\n{category}:")
        
        for dep in deps:
            try:
                if dep in ['ast', 'pathlib', 'json', 'logging']:
                    # Core Python modules
                    __import__(dep)
                    status = "✓"
                elif dep in ['mermaid-cli', 'plantuml', 'ffmpeg']:
                    # External tools
                    import subprocess
                    result = subprocess.run([dep.split('-')[0], '--version'], 
                                          capture_output=True, timeout=5)
                    status = "✓" if result.returncode == 0 else "✗"
                else:
                    # Python packages
                    __import__(dep.replace('-', '_'))
                    status = "✓"
                    
            except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
                status = "✗"
            
            print(f"  {status} {dep}")
    
    print(f"\n💡 Note: ✗ indicates optional dependencies that enhance functionality")

def main():
    """Main demo function"""
    
    print("🎨 Visual Documentation Pipeline Demo")
    print("This demo showcases the visual documentation generation capabilities.")
    
    # Check dependencies first
    check_dependencies()
    
    # Demo specific features
    demo_specific_features()
    
    # Run main demo
    success = demo_current_project()
    
    if success:
        print("\n🎉 Demo completed successfully!")
        print("📚 Explore the generated documentation to see all features.")
    else:
        print("\n⚠️ Demo encountered issues.")
        print("📋 Check the logs above for troubleshooting information.")
    
    print(f"\n📖 See README.md for full usage instructions.")
    print(f"⚙️ See example_config.json for configuration options.")

if __name__ == "__main__":
    main()