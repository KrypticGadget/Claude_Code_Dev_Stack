#!/usr/bin/env python3
"""
Visual Documentation Pipeline Runner
Main entry point for running the complete visual documentation pipeline
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the current directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.visual_docs_pipeline import VisualDocsPipeline, DocumentationConfig, create_default_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('visual_docs_pipeline.log')
    ]
)

logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive visual documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project
  %(prog)s /path/to/project --output ./docs/visual
  %(prog)s /path/to/project --screenshots --videos
  %(prog)s /path/to/project --config config.json
  %(prog)s /path/to/project --integration codeboarding
        """
    )
    
    parser.add_argument(
        'project_root',
        type=str,
        help='Root directory of the project to document'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for generated documentation (default: PROJECT_ROOT/docs/visual)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file (JSON format)'
    )
    
    parser.add_argument(
        '--screenshots',
        action='store_true',
        help='Generate screenshots of documentation'
    )
    
    parser.add_argument(
        '--videos',
        action='store_true',
        help='Generate video tutorials'
    )
    
    parser.add_argument(
        '--integration',
        choices=['codeboarding', 'standalone'],
        default='codeboarding',
        help='Integration mode (default: codeboarding)'
    )
    
    parser.add_argument(
        '--formats',
        nargs='+',
        choices=['mermaid', 'plantuml', 'd3', 'flowchart'],
        default=['mermaid', 'd3'],
        help='Diagram formats to generate (default: mermaid d3)'
    )
    
    parser.add_argument(
        '--source-dirs',
        nargs='+',
        help='Specific source directories to analyze (default: auto-detect)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without actually creating files'
    )
    
    return parser.parse_args()

def load_config(config_path: Optional[str], project_root: Path, args) -> DocumentationConfig:
    """Load configuration from file or create from arguments"""
    
    if config_path and Path(config_path).exists():
        logger.info(f"Loading configuration from {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Convert paths to Path objects
            config_data['project_root'] = Path(config_data['project_root'])
            config_data['output_dir'] = Path(config_data['output_dir'])
            
            if 'source_dirs' in config_data:
                config_data['source_dirs'] = [Path(d) for d in config_data['source_dirs']]
            
            return DocumentationConfig(**config_data)
            
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}")
            logger.info("Falling back to default configuration")
    
    # Create configuration from command line arguments
    config = create_default_config(project_root)
    
    # Override with command line arguments
    if args.output:
        config.output_dir = Path(args.output)
    
    if args.source_dirs:
        config.source_dirs = [Path(d) for d in args.source_dirs]
    
    if args.formats:
        config.diagram_formats = args.formats
    
    config.generate_screenshots = args.screenshots
    config.generate_videos = args.videos
    config.integration_mode = args.integration
    
    return config

def validate_project(project_root: Path) -> bool:
    """Validate that the project directory is suitable for documentation"""
    
    if not project_root.exists():
        logger.error(f"Project directory does not exist: {project_root}")
        return False
    
    if not project_root.is_dir():
        logger.error(f"Project path is not a directory: {project_root}")
        return False
    
    # Check for source files
    python_files = list(project_root.rglob("*.py"))
    js_files = list(project_root.rglob("*.js"))
    ts_files = list(project_root.rglob("*.ts"))
    
    if not (python_files or js_files or ts_files):
        logger.warning("No source files found in project directory")
        return False
    
    logger.info(f"Found {len(python_files)} Python files, {len(js_files)} JS files, {len(ts_files)} TS files")
    return True

def check_dependencies() -> Dict[str, bool]:
    """Check for optional dependencies and tools"""
    dependencies = {}
    
    # Check Python packages
    packages = [
        'playwright', 'selenium', 'Pillow', 'matplotlib', 'networkx'
    ]
    
    for package in packages:
        try:
            __import__(package)
            dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    # Check external tools
    tools = ['mmdc', 'plantuml', 'ffmpeg', 'chromium', 'google-chrome']
    
    for tool in tools:
        try:
            import subprocess
            result = subprocess.run([tool, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            dependencies[tool] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            dependencies[tool] = False
    
    return dependencies

def print_dependency_status(dependencies: Dict[str, bool]):
    """Print status of dependencies"""
    logger.info("Dependency Status:")
    
    required = {
        'Core functionality': ['ast', 'pathlib', 'json'],
        'Diagram rendering': ['mmdc', 'plantuml'],
        'Screenshots': ['playwright', 'selenium', 'chromium', 'google-chrome'],
        'Video generation': ['ffmpeg'],
        'Image processing': ['Pillow'],
        'Advanced diagrams': ['matplotlib', 'networkx']
    }
    
    for category, deps in required.items():
        logger.info(f"\n{category}:")
        for dep in deps:
            status = "✓" if dependencies.get(dep, False) else "✗"
            logger.info(f"  {status} {dep}")

def generate_sample_config(project_root: Path) -> Path:
    """Generate a sample configuration file"""
    config = create_default_config(project_root)
    
    config_dict = {
        'project_root': str(config.project_root),
        'output_dir': str(config.output_dir),
        'source_dirs': [str(d) for d in config.source_dirs],
        'include_patterns': config.include_patterns,
        'exclude_patterns': config.exclude_patterns,
        'diagram_formats': config.diagram_formats,
        'generate_screenshots': config.generate_screenshots,
        'generate_videos': config.generate_videos,
        'integration_mode': config.integration_mode
    }
    
    config_file = project_root / "visual_docs_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2)
    
    logger.info(f"Sample configuration saved to: {config_file}")
    return config_file

def print_dry_run_summary(config: DocumentationConfig, analysis: Dict[str, Any]):
    """Print what would be generated in dry run mode"""
    logger.info("\n" + "="*60)
    logger.info("DRY RUN SUMMARY")
    logger.info("="*60)
    
    logger.info(f"Project: {config.project_root}")
    logger.info(f"Output: {config.output_dir}")
    logger.info(f"Integration: {config.integration_mode}")
    logger.info(f"Formats: {', '.join(config.diagram_formats)}")
    
    logger.info(f"\nWould analyze:")
    logger.info(f"  - {len(analysis.get('components', []))} Python components")
    logger.info(f"  - {len(config.source_dirs)} source directories")
    
    logger.info(f"\nWould generate:")
    logger.info(f"  - System architecture diagram")
    logger.info(f"  - {min(len(analysis.get('components', [])), 8)} component diagrams")
    logger.info(f"  - Interactive HTML documentation")
    
    if config.generate_screenshots:
        logger.info(f"  - Screenshots of all pages")
    
    if config.generate_videos:
        logger.info(f"  - Video tutorials and walkthroughs")
    
    logger.info(f"\nOutput structure:")
    structure = [
        "docs/visual/",
        "├── diagrams/",
        "│   ├── mermaid/",
        "│   ├── plantuml/",
        "│   └── d3/",
        "├── interactive/",
        "│   ├── index.html",
        "│   ├── components/",
        "│   └── diagrams/",
    ]
    
    if config.generate_screenshots:
        structure.extend([
            "├── screenshots/",
            "│   └── gallery.html",
        ])
    
    if config.generate_videos:
        structure.extend([
            "└── videos/",
            "    └── index.html",
        ])
    
    for line in structure:
        logger.info(f"  {line}")

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate project directory
    project_root = Path(args.project_root).resolve()
    if not validate_project(project_root):
        sys.exit(1)
    
    logger.info(f"Starting visual documentation pipeline for: {project_root}")
    
    # Check dependencies
    dependencies = check_dependencies()
    print_dependency_status(dependencies)
    
    # Load configuration
    try:
        config = load_config(args.config, project_root, args)
        logger.info(f"Configuration loaded: {config.integration_mode} mode")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Create pipeline
    try:
        pipeline = VisualDocsPipeline(config)
        logger.info("Visual documentation pipeline initialized")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        sys.exit(1)
    
    # Analyze project
    try:
        logger.info("Analyzing project structure...")
        analysis = pipeline.analyze_codebase()
        logger.info(f"Analysis complete: {len(analysis.get('components', []))} components found")
    except Exception as e:
        logger.error(f"Project analysis failed: {e}")
        sys.exit(1)
    
    # Dry run mode
    if args.dry_run:
        print_dry_run_summary(config, analysis)
        
        # Offer to generate sample config
        if not args.config:
            config_file = generate_sample_config(project_root)
            logger.info(f"\nTo run the pipeline, use: python {__file__} {project_root} --config {config_file}")
        
        return
    
    # Run full pipeline
    try:
        logger.info("Running full documentation pipeline...")
        summary = pipeline.run_full_pipeline()
        
        # Print results
        logger.info("\n" + "="*60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
        logger.info(f"Output directory: {config.output_dir}")
        logger.info(f"Diagrams generated: {summary['diagrams_generated']}")
        logger.info(f"Screenshots generated: {summary['screenshots_generated']}")
        logger.info(f"Videos generated: {summary['videos_generated']}")
        logger.info(f"Interactive docs: {summary['interactive_docs']}")
        
        # Show next steps
        logger.info("\nNext steps:")
        logger.info(f"1. Open {config.output_dir / 'interactive' / 'index.html'} in your browser")
        logger.info(f"2. Explore the generated diagrams in {config.output_dir / 'diagrams'}")
        
        if config.generate_screenshots:
            logger.info(f"3. View screenshots at {config.output_dir / 'screenshots' / 'gallery.html'}")
        
        if config.generate_videos:
            logger.info(f"4. Watch videos at {config.output_dir / 'videos' / 'index.html'}")
        
        if config.integration_mode == 'codeboarding':
            onboarding_dir = project_root / "docs" / "onboarding"
            if onboarding_dir.exists():
                logger.info(f"5. Check updated onboarding docs at {onboarding_dir}")
        
        logger.info(f"\nPipeline summary saved to: {config.output_dir / 'pipeline_summary.json'}")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        logger.error("Check the log file for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    main()