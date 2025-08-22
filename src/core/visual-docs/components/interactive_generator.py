#!/usr/bin/env python3
"""
Interactive Documentation Generator
Creates interactive HTML documentation with embedded diagrams and examples
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import base64

logger = logging.getLogger(__name__)

class InteractiveGenerator:
    """Generator for interactive HTML documentation"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir / "interactive"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load templates
        self.templates = self._load_templates()
        
        # Create assets directories
        (self.output_dir / "css").mkdir(exist_ok=True)
        (self.output_dir / "js").mkdir(exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
    
    def _load_templates(self) -> Dict[str, str]:
        """Load HTML templates for interactive documentation"""
        templates_dir = Path(__file__).parent.parent / "templates"
        templates = {}
        
        # Load built-in templates
        templates.update({
            'main': self._get_main_template(),
            'component': self._get_component_template(),
            'diagram_viewer': self._get_diagram_viewer_template(),
            'code_example': self._get_code_example_template(),
            'navigation': self._get_navigation_template()
        })
        
        return templates
    
    def generate(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> Path:
        """Generate complete interactive documentation"""
        try:
            # Generate main documentation page
            main_html = self._generate_main_page(analysis, diagrams)
            
            # Generate component pages
            component_pages = self._generate_component_pages(analysis, diagrams)
            
            # Generate diagram viewer pages
            diagram_pages = self._generate_diagram_pages(diagrams)
            
            # Generate CSS and JavaScript
            self._generate_assets()
            
            # Generate navigation structure
            navigation = self._generate_navigation(analysis, component_pages, diagram_pages)
            
            # Create main index file
            index_file = self._create_index_file(main_html, navigation)
            
            logger.info(f"Generated interactive documentation: {index_file}")
            return index_file
            
        except Exception as e:
            logger.error(f"Failed to generate interactive documentation: {e}")
            return self.output_dir / "error.html"
    
    def _generate_main_page(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> str:
        """Generate main overview page"""
        project_name = analysis.get('project_root', 'Project').split('/')[-1]
        
        # Generate overview content
        overview_content = self._generate_overview_content(analysis)
        
        # Generate diagram gallery
        diagram_gallery = self._generate_diagram_gallery(diagrams)
        
        # Generate component summary
        component_summary = self._generate_component_summary(analysis)
        
        # Generate statistics
        stats = self._generate_project_statistics(analysis, diagrams)
        
        return self.templates['main'].format(
            project_name=project_name,
            overview_content=overview_content,
            diagram_gallery=diagram_gallery,
            component_summary=component_summary,
            project_stats=stats,
            codeboarding_badges=self._get_codeboarding_badges()
        )
    
    def _generate_overview_content(self, analysis: Dict[str, Any]) -> str:
        """Generate project overview content"""
        components_count = len(analysis.get('components', []))
        
        overview_html = f'''
        <div class="overview-section">
            <h2>Project Overview</h2>
            <p>This project contains <strong>{components_count}</strong> components with comprehensive visual documentation.</p>
            
            <div class="quick-stats">
                <div class="stat-item">
                    <span class="stat-number">{components_count}</span>
                    <span class="stat-label">Components</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{sum(len(c.get('classes', [])) for c in analysis.get('components', []))}</span>
                    <span class="stat-label">Classes</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{sum(len(c.get('functions', [])) for c in analysis.get('components', []))}</span>
                    <span class="stat-label">Functions</span>
                </div>
            </div>
        </div>
        '''
        
        return overview_html
    
    def _generate_diagram_gallery(self, diagrams: Dict[str, Path]) -> str:
        """Generate interactive diagram gallery"""
        gallery_html = '''
        <div class="diagram-gallery">
            <h3>Architecture Diagrams</h3>
            <div class="gallery-grid">
        '''
        
        for name, diagram_path in diagrams.items():
            if diagram_path and diagram_path.exists():
                # Create thumbnail and full view
                thumbnail_html = f'''
                <div class="diagram-card" data-diagram="{name}">
                    <div class="diagram-thumbnail">
                        <iframe src="{self._get_relative_path(diagram_path)}" 
                                width="100%" height="200" frameborder="0"></iframe>
                    </div>
                    <div class="diagram-info">
                        <h4>{name.replace('_', ' ').title()}</h4>
                        <p>Interactive diagram</p>
                        <button onclick="openDiagram('{name}')" class="view-btn">View Full</button>
                    </div>
                </div>
                '''
                gallery_html += thumbnail_html
        
        gallery_html += '''
            </div>
        </div>
        '''
        
        return gallery_html
    
    def _generate_component_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate component summary section"""
        components = analysis.get('components', [])
        
        summary_html = '''
        <div class="component-summary">
            <h3>Components</h3>
            <div class="component-grid">
        '''
        
        for component in components[:8]:  # Limit to 8 for display
            file_name = Path(component['file']).stem
            classes_count = len(component.get('classes', []))
            functions_count = len(component.get('functions', []))
            
            component_html = f'''
            <div class="component-card">
                <h4>{file_name}</h4>
                <div class="component-stats">
                    <span>{classes_count} classes</span>
                    <span>{functions_count} functions</span>
                </div>
                <p>{component.get('docstring', 'No description available')[:100]}...</p>
                <a href="components/{file_name}.html" class="component-link">View Details</a>
            </div>
            '''
            summary_html += component_html
        
        summary_html += '''
            </div>
        </div>
        '''
        
        return summary_html
    
    def _generate_project_statistics(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> str:
        """Generate project statistics section"""
        stats = {
            'total_files': len(analysis.get('components', [])),
            'total_classes': sum(len(c.get('classes', [])) for c in analysis.get('components', [])),
            'total_functions': sum(len(c.get('functions', [])) for c in analysis.get('components', [])),
            'diagrams_generated': len(diagrams),
            'documentation_coverage': min(100, (len(diagrams) / max(1, len(analysis.get('components', [])))) * 100)
        }
        
        stats_html = f'''
        <div class="project-statistics">
            <h3>Project Statistics</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{stats['total_files']}</div>
                    <div class="stat-name">Python Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['total_classes']}</div>
                    <div class="stat-name">Classes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['total_functions']}</div>
                    <div class="stat-name">Functions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['diagrams_generated']}</div>
                    <div class="stat-name">Diagrams</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['documentation_coverage']:.0f}%</div>
                    <div class="stat-name">Coverage</div>
                </div>
            </div>
        </div>
        '''
        
        return stats_html
    
    def _generate_component_pages(self, analysis: Dict[str, Any], diagrams: Dict[str, Path]) -> List[Path]:
        """Generate individual component detail pages"""
        component_pages = []
        components_dir = self.output_dir / "components"
        components_dir.mkdir(exist_ok=True)
        
        for component in analysis.get('components', []):
            try:
                file_name = Path(component['file']).stem
                component_html = self._generate_component_page_content(component, diagrams)
                
                page_file = components_dir / f"{file_name}.html"
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(component_html)
                
                component_pages.append(page_file)
                
            except Exception as e:
                logger.warning(f"Failed to generate component page for {component.get('file', 'unknown')}: {e}")
        
        return component_pages
    
    def _generate_component_page_content(self, component: Dict[str, Any], diagrams: Dict[str, Path]) -> str:
        """Generate content for individual component page"""
        file_name = Path(component['file']).stem
        
        # Find related diagram
        related_diagram = None
        for name, path in diagrams.items():
            if file_name in name:
                related_diagram = path
                break
        
        # Generate class documentation
        classes_html = self._generate_classes_documentation(component.get('classes', []))
        
        # Generate functions documentation
        functions_html = self._generate_functions_documentation(component.get('functions', []))
        
        # Generate code examples
        examples_html = self._generate_code_examples(component)
        
        # Generate imports and dependencies
        imports_html = self._generate_imports_section(component.get('imports', []))
        
        component_content = self.templates['component'].format(
            component_name=file_name,
            component_description=component.get('docstring', 'No description available'),
            component_diagram=self._embed_diagram(related_diagram) if related_diagram else '',
            classes_documentation=classes_html,
            functions_documentation=functions_html,
            code_examples=examples_html,
            imports_section=imports_html,
            file_path=component['file']
        )
        
        # Wrap in full HTML page
        return self._wrap_in_page_template(component_content, f"{file_name} Component")
    
    def _generate_classes_documentation(self, classes: List[Dict[str, Any]]) -> str:
        """Generate documentation for classes"""
        if not classes:
            return '<p>No classes found in this component.</p>'
        
        classes_html = '<div class="classes-section">'
        
        for cls in classes:
            class_html = f'''
            <div class="class-documentation">
                <h4 class="class-name">{cls['name']}</h4>
                <p class="class-description">{cls.get('docstring', 'No description available')}</p>
                
                <div class="class-details">
                    <div class="inheritance">
                        <strong>Inherits from:</strong> {', '.join(cls.get('bases', [])) or 'object'}
                    </div>
                    
                    <div class="methods">
                        <strong>Methods:</strong>
                        <ul>
                            {self._generate_methods_list(cls.get('methods', []))}
                        </ul>
                    </div>
                </div>
            </div>
            '''
            classes_html += class_html
        
        classes_html += '</div>'
        return classes_html
    
    def _generate_methods_list(self, methods: List[str]) -> str:
        """Generate HTML list of methods"""
        if not methods:
            return '<li>No methods found</li>'
        
        return '\n'.join(f'<li><code>{method}()</code></li>' for method in methods)
    
    def _generate_functions_documentation(self, functions: List[Dict[str, Any]]) -> str:
        """Generate documentation for functions"""
        if not functions:
            return '<p>No top-level functions found in this component.</p>'
        
        functions_html = '<div class="functions-section">'
        
        for func in functions:
            func_html = f'''
            <div class="function-documentation">
                <h4 class="function-name">{func['name']}()</h4>
                <p class="function-description">{func.get('docstring', 'No description available')}</p>
                
                <div class="function-details">
                    <div class="parameters">
                        <strong>Parameters:</strong> {', '.join(func.get('args', [])) or 'None'}
                    </div>
                </div>
            </div>
            '''
            functions_html += func_html
        
        functions_html += '</div>'
        return functions_html
    
    def _generate_code_examples(self, component: Dict[str, Any]) -> str:
        """Generate code usage examples"""
        file_name = Path(component['file']).stem
        
        examples_html = f'''
        <div class="code-examples">
            <h4>Usage Example</h4>
            <div class="code-block">
                <pre><code class="language-python">
# Import the component
from {file_name} import *

# Example usage would go here
# This is a placeholder for actual usage examples
</code></pre>
            </div>
        </div>
        '''
        
        return examples_html
    
    def _generate_imports_section(self, imports: List[str]) -> str:
        """Generate imports and dependencies section"""
        if not imports:
            return '<p>No external dependencies found.</p>'
        
        imports_html = f'''
        <div class="imports-section">
            <h4>Dependencies</h4>
            <ul class="imports-list">
                {'\n'.join(f'<li><code>{imp}</code></li>' for imp in imports[:10])}
            </ul>
        </div>
        '''
        
        return imports_html
    
    def _generate_diagram_pages(self, diagrams: Dict[str, Path]) -> List[Path]:
        """Generate dedicated pages for each diagram"""
        diagram_pages = []
        diagrams_dir = self.output_dir / "diagrams"
        diagrams_dir.mkdir(exist_ok=True)
        
        for name, diagram_path in diagrams.items():
            if diagram_path and diagram_path.exists():
                try:
                    diagram_html = self._generate_diagram_page_content(name, diagram_path)
                    
                    page_file = diagrams_dir / f"{name}.html"
                    with open(page_file, 'w', encoding='utf-8') as f:
                        f.write(diagram_html)
                    
                    diagram_pages.append(page_file)
                    
                except Exception as e:
                    logger.warning(f"Failed to generate diagram page for {name}: {e}")
        
        return diagram_pages
    
    def _generate_diagram_page_content(self, name: str, diagram_path: Path) -> str:
        """Generate content for diagram detail page"""
        diagram_content = f'''
        <div class="diagram-detail">
            <h2>{name.replace('_', ' ').title()}</h2>
            
            <div class="diagram-viewer">
                {self._embed_diagram(diagram_path)}
            </div>
            
            <div class="diagram-info">
                <h3>Diagram Information</h3>
                <ul>
                    <li><strong>Type:</strong> {diagram_path.suffix.upper()}</li>
                    <li><strong>Generated:</strong> Automatically from code analysis</li>
                    <li><strong>Interactive:</strong> Yes</li>
                </ul>
            </div>
            
            <div class="diagram-actions">
                <button onclick="downloadDiagram('{name}')" class="download-btn">Download</button>
                <button onclick="printDiagram()" class="print-btn">Print</button>
                <button onclick="shareDiagram('{name}')" class="share-btn">Share</button>
            </div>
        </div>
        '''
        
        return self._wrap_in_page_template(diagram_content, f"{name} Diagram")
    
    def _embed_diagram(self, diagram_path: Path) -> str:
        """Embed diagram in HTML"""
        if not diagram_path or not diagram_path.exists():
            return '<p>Diagram not available</p>'
        
        if diagram_path.suffix.lower() == '.html':
            # Embed HTML diagram (like D3.js)
            return f'<iframe src="{self._get_relative_path(diagram_path)}" width="100%" height="600" frameborder="0"></iframe>'
        elif diagram_path.suffix.lower() in ['.svg', '.png']:
            # Embed image
            return f'<img src="{self._get_relative_path(diagram_path)}" alt="Diagram" class="diagram-image">'
        elif diagram_path.suffix.lower() == '.mmd':
            # Embed Mermaid diagram
            try:
                with open(diagram_path, 'r', encoding='utf-8') as f:
                    mermaid_content = f.read()
                
                return f'''
                <div class="mermaid">
                    {mermaid_content}
                </div>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                <script>mermaid.initialize({{startOnLoad: true}});</script>
                '''
            except Exception as e:
                logger.warning(f"Failed to embed Mermaid diagram: {e}")
                return f'<p>Failed to load diagram: {e}</p>'
        else:
            return f'<p>Unsupported diagram format: {diagram_path.suffix}</p>'
    
    def _get_relative_path(self, file_path: Path) -> str:
        """Get relative path for HTML embedding"""
        try:
            return str(file_path.relative_to(self.output_dir))
        except ValueError:
            # If not relative to output_dir, copy file and return relative path
            import shutil
            dest_path = self.output_dir / "images" / file_path.name
            shutil.copy2(file_path, dest_path)
            return f"images/{file_path.name}"
    
    def _generate_assets(self):
        """Generate CSS and JavaScript files"""
        # Generate CSS
        css_content = self._get_css_styles()
        with open(self.output_dir / "css" / "styles.css", 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # Generate JavaScript
        js_content = self._get_javascript()
        with open(self.output_dir / "js" / "script.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _generate_navigation(self, analysis: Dict[str, Any], component_pages: List[Path], diagram_pages: List[Path]) -> str:
        """Generate navigation menu"""
        nav_html = '''
        <nav class="main-navigation">
            <ul>
                <li><a href="index.html">Overview</a></li>
                <li class="nav-section">
                    <span>Components</span>
                    <ul class="nav-subsection">
        '''
        
        for page in component_pages:
            page_name = page.stem.replace('_', ' ').title()
            nav_html += f'<li><a href="components/{page.name}">{page_name}</a></li>\n'
        
        nav_html += '''
                    </ul>
                </li>
                <li class="nav-section">
                    <span>Diagrams</span>
                    <ul class="nav-subsection">
        '''
        
        for page in diagram_pages:
            page_name = page.stem.replace('_', ' ').title()
            nav_html += f'<li><a href="diagrams/{page.name}">{page_name}</a></li>\n'
        
        nav_html += '''
                    </ul>
                </li>
            </ul>
        </nav>
        '''
        
        return nav_html
    
    def _create_index_file(self, main_content: str, navigation: str) -> Path:
        """Create main index.html file"""
        index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Documentation</title>
    <link rel="stylesheet" href="css/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            {navigation}
        </header>
        
        <main>
            {main_content}
        </main>
        
        <footer>
            {self._get_codeboarding_badges()}
        </footer>
    </div>
    
    <script src="js/script.js"></script>
    <script>
        mermaid.initialize({{startOnLoad: true}});
    </script>
</body>
</html>'''
        
        index_file = self.output_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        return index_file
    
    def _wrap_in_page_template(self, content: str, title: str) -> str:
        """Wrap content in full page template"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="../css/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <nav class="breadcrumb">
                <a href="../index.html">Home</a> > {title}
            </nav>
        </header>
        
        <main>
            {content}
        </main>
        
        <footer>
            {self._get_codeboarding_badges()}
        </footer>
    </div>
    
    <script src="../js/script.js"></script>
    <script>
        mermaid.initialize({{startOnLoad: true}});
    </script>
</body>
</html>'''
    
    def _get_codeboarding_badges(self) -> str:
        """Get CodeBoarding badges HTML"""
        return '''
        <div class="codeboarding-badges">
            <a href="https://github.com/CodeBoarding/CodeBoarding">
                <img src="https://img.shields.io/badge/Generated%20by-CodeBoarding-9cf?style=flat-square" alt="CodeBoarding">
            </a>
            <a href="https://www.codeboarding.org/demo">
                <img src="https://img.shields.io/badge/Try%20our-Demo-blue?style=flat-square" alt="Demo">
            </a>
            <a href="mailto:contact@codeboarding.org">
                <img src="https://img.shields.io/badge/Contact%20us%20-%20contact@codeboarding.org-lightgrey?style=flat-square" alt="Contact">
            </a>
        </div>
        '''
    
    def _get_main_template(self) -> str:
        """Main page template"""
        return '''
        <div class="main-content">
            <h1>{project_name}</h1>
            
            {overview_content}
            
            {diagram_gallery}
            
            {component_summary}
            
            {project_stats}
        </div>
        '''
    
    def _get_component_template(self) -> str:
        """Component page template"""
        return '''
        <div class="component-content">
            <h1>{component_name}</h1>
            <p class="component-description">{component_description}</p>
            
            <div class="component-diagram">
                {component_diagram}
            </div>
            
            <section class="classes">
                <h2>Classes</h2>
                {classes_documentation}
            </section>
            
            <section class="functions">
                <h2>Functions</h2>
                {functions_documentation}
            </section>
            
            <section class="examples">
                <h2>Examples</h2>
                {code_examples}
            </section>
            
            <section class="imports">
                <h2>Dependencies</h2>
                {imports_section}
            </section>
        </div>
        '''
    
    def _get_diagram_viewer_template(self) -> str:
        """Diagram viewer template"""
        return '''
        <div class="diagram-viewer">
            {diagram_content}
        </div>
        '''
    
    def _get_code_example_template(self) -> str:
        """Code example template"""
        return '''
        <div class="code-example">
            <pre><code>{code_content}</code></pre>
        </div>
        '''
    
    def _get_navigation_template(self) -> str:
        """Navigation template"""
        return '''
        <nav class="navigation">
            {nav_items}
        </nav>
        '''
    
    def _get_css_styles(self) -> str:
        """Generate CSS styles for interactive documentation"""
        return '''
/* Interactive Documentation Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

main {
    background: white;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Navigation */
.main-navigation ul {
    list-style: none;
    display: flex;
    gap: 20px;
}

.main-navigation a {
    text-decoration: none;
    color: #007bff;
    font-weight: 500;
}

.main-navigation a:hover {
    color: #0056b3;
}

.nav-section > span {
    font-weight: bold;
    color: #333;
}

.nav-subsection {
    margin-left: 20px;
    margin-top: 10px;
}

/* Overview Section */
.overview-section {
    margin-bottom: 40px;
}

.quick-stats {
    display: flex;
    gap: 30px;
    margin-top: 20px;
}

.stat-item {
    text-align: center;
}

.stat-number {
    display: block;
    font-size: 2em;
    font-weight: bold;
    color: #007bff;
}

.stat-label {
    color: #666;
    font-size: 0.9em;
}

/* Diagram Gallery */
.diagram-gallery {
    margin-bottom: 40px;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.diagram-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    background: white;
    transition: box-shadow 0.3s ease;
}

.diagram-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.diagram-thumbnail {
    border: 1px solid #eee;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 10px;
}

.diagram-info h4 {
    margin-bottom: 5px;
    color: #333;
}

.view-btn {
    background: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
}

.view-btn:hover {
    background: #0056b3;
}

/* Component Grid */
.component-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.component-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    background: white;
}

.component-card h4 {
    margin-bottom: 10px;
    color: #333;
}

.component-stats {
    color: #666;
    font-size: 0.9em;
    margin-bottom: 10px;
}

.component-stats span {
    margin-right: 15px;
}

.component-link {
    color: #007bff;
    text-decoration: none;
    font-weight: 500;
}

/* Statistics */
.project-statistics {
    margin-top: 40px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.stat-card {
    text-align: center;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
}

.stat-value {
    font-size: 2em;
    font-weight: bold;
    color: #007bff;
}

.stat-name {
    color: #666;
    font-size: 0.9em;
    margin-top: 5px;
}

/* Component Documentation */
.class-documentation,
.function-documentation {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    background: #fafafa;
}

.class-name,
.function-name {
    color: #007bff;
    margin-bottom: 10px;
}

.class-details,
.function-details {
    margin-top: 15px;
}

.methods ul {
    margin-left: 20px;
}

.methods li {
    margin-bottom: 5px;
}

/* Code Examples */
.code-block {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 15px;
    margin: 15px 0;
}

.code-block pre {
    margin: 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9em;
    line-height: 1.4;
}

/* Diagram Viewer */
.diagram-viewer {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    background: white;
}

.diagram-image {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
}

.diagram-actions {
    margin-top: 20px;
    text-align: center;
}

.diagram-actions button {
    margin: 0 10px;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
}

.download-btn {
    background: #28a745;
    color: white;
}

.print-btn {
    background: #6c757d;
    color: white;
}

.share-btn {
    background: #17a2b8;
    color: white;
}

/* CodeBoarding Badges */
.codeboarding-badges {
    text-align: center;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.codeboarding-badges img {
    margin: 0 5px;
}

/* Breadcrumb */
.breadcrumb {
    margin-bottom: 20px;
}

.breadcrumb a {
    color: #007bff;
    text-decoration: none;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .quick-stats {
        flex-direction: column;
        gap: 15px;
    }
    
    .gallery-grid,
    .component-grid,
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .main-navigation ul {
        flex-direction: column;
        gap: 10px;
    }
}

/* Mermaid Diagrams */
.mermaid {
    text-align: center;
    margin: 20px 0;
}

/* Print Styles */
@media print {
    .main-navigation,
    .diagram-actions,
    .codeboarding-badges {
        display: none;
    }
    
    .container {
        max-width: none;
        padding: 0;
    }
    
    .diagram-card,
    .component-card,
    .stat-card {
        page-break-inside: avoid;
    }
}
'''
    
    def _get_javascript(self) -> str:
        """Generate JavaScript for interactive functionality"""
        return '''
// Interactive Documentation JavaScript

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeInteractivity();
});

function initializeInteractivity() {
    // Initialize diagram interactions
    setupDiagramInteractions();
    
    // Initialize navigation
    setupNavigation();
    
    // Initialize search functionality
    setupSearch();
    
    // Initialize responsive features
    setupResponsive();
}

function setupDiagramInteractions() {
    // Handle diagram card clicks
    const diagramCards = document.querySelectorAll('.diagram-card');
    diagramCards.forEach(card => {
        card.addEventListener('click', function() {
            const diagramName = this.getAttribute('data-diagram');
            if (diagramName) {
                openDiagram(diagramName);
            }
        });
    });
    
    // Handle diagram zoom
    const diagramImages = document.querySelectorAll('.diagram-image');
    diagramImages.forEach(img => {
        img.addEventListener('click', function() {
            toggleImageZoom(this);
        });
    });
}

function setupNavigation() {
    // Handle navigation section toggles
    const navSections = document.querySelectorAll('.nav-section');
    navSections.forEach(section => {
        const span = section.querySelector('span');
        if (span) {
            span.addEventListener('click', function() {
                const subsection = section.querySelector('.nav-subsection');
                if (subsection) {
                    subsection.style.display = 
                        subsection.style.display === 'none' ? 'block' : 'none';
                }
            });
        }
    });
    
    // Highlight current page in navigation
    highlightCurrentNavItem();
}

function setupSearch() {
    // Add search functionality if search box exists
    const searchBox = document.getElementById('search');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            filterContent(this.value);
        });
    }
}

function setupResponsive() {
    // Handle mobile menu toggle
    const menuToggle = document.getElementById('menu-toggle');
    const navigation = document.querySelector('.main-navigation');
    
    if (menuToggle && navigation) {
        menuToggle.addEventListener('click', function() {
            navigation.classList.toggle('mobile-open');
        });
    }
}

function openDiagram(diagramName) {
    // Open diagram in new window or modal
    const diagramUrl = `diagrams/${diagramName}.html`;
    
    // Try to open in modal first, fallback to new window
    if (typeof openModal === 'function') {
        openModal(diagramUrl);
    } else {
        window.open(diagramUrl, '_blank', 'width=800,height=600,scrollbars=yes');
    }
}

function toggleImageZoom(img) {
    // Toggle zoom state
    if (img.classList.contains('zoomed')) {
        img.classList.remove('zoomed');
        img.style.transform = 'scale(1)';
        img.style.cursor = 'zoom-in';
    } else {
        img.classList.add('zoomed');
        img.style.transform = 'scale(1.5)';
        img.style.cursor = 'zoom-out';
        img.style.transition = 'transform 0.3s ease';
    }
}

function highlightCurrentNavItem() {
    // Highlight current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.main-navigation a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath.split('/').pop()) {
            link.classList.add('current');
        }
    });
}

function filterContent(searchTerm) {
    // Filter content based on search term
    const cards = document.querySelectorAll('.component-card, .diagram-card');
    const term = searchTerm.toLowerCase();
    
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        if (text.includes(term) || term === '') {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Diagram-specific functions
function downloadDiagram(diagramName) {
    // Download diagram file
    const link = document.createElement('a');
    link.href = `diagrams/${diagramName}.svg`;
    link.download = `${diagramName}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function printDiagram() {
    // Print current diagram
    window.print();
}

function shareDiagram(diagramName) {
    // Share diagram (copy URL to clipboard)
    const url = `${window.location.origin}${window.location.pathname}`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function() {
            showNotification('Diagram URL copied to clipboard!');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Diagram URL copied to clipboard!');
    }
}

function showNotification(message) {
    // Show temporary notification
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 10px 20px;
        border-radius: 4px;
        z-index: 1000;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Performance optimization
const debouncedFilterContent = debounce(filterContent, 300);

// Export functions for global access
window.openDiagram = openDiagram;
window.downloadDiagram = downloadDiagram;
window.printDiagram = printDiagram;
window.shareDiagram = shareDiagram;
'''