#!/usr/bin/env python3
"""
Auto Documentation Hook - V3.0+ Documentation Generation
Automatically generates and maintains project documentation
"""

import os
import json
import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

class AutoDocumentationGenerator:
    """Automatically generate project documentation"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        
        # Get documentation settings
        doc_settings = self.settings.get('v3ExtendedFeatures', {}).get('documentation', {})
        self.auto_generate = doc_settings.get('autoGenerate', True)
        self.update_on_save = doc_settings.get('updateOnSave', True)
        self.generate_api_docs = doc_settings.get('generateApiDocs', True)
        self.generate_readme = doc_settings.get('generateReadme', True)
        self.include_examples = doc_settings.get('includeExamples', True)
        
        # Documentation templates
        self.templates = {
            'function': """
### `{name}({params})`

{description}

**Parameters:**
{param_docs}

**Returns:**
{return_info}

{example}
""",
            'class': """
## `{name}`

{description}

{methods}

{example}
""",
            'module': """
# {name}

{description}

## Functions

{functions}

## Classes

{classes}
""",
            'readme': """# {project_name}

{description}

## Installation

```bash
{install_command}
```

## Usage

{usage_examples}

## API Reference

{api_reference}

## Contributing

{contributing_info}

## License

{license_info}
"""
        }
        
        # Language-specific parsers
        self.parsers = {
            '.py': self.parse_python_file,
            '.js': self.parse_javascript_file,
            '.ts': self.parse_typescript_file,
            '.jsx': self.parse_javascript_file,
            '.tsx': self.parse_typescript_file,
            '.go': self.parse_go_file,
            '.rs': self.parse_rust_file,
            '.java': self.parse_java_file,
            '.rb': self.parse_ruby_file,
            '.php': self.parse_php_file
        }
        
        # Project information cache
        self.project_info = {}
    
    def load_settings(self) -> Dict:
        """Load settings from settings.json"""
        settings_path = self.claude_dir / 'settings.json'
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def detect_project_info(self, directory: str = '.') -> Dict:
        """Detect project information from various files"""
        directory = Path(directory)
        info = {
            'name': directory.name,
            'description': '',
            'language': 'unknown',
            'framework': 'none',
            'version': '1.0.0',
            'license': 'MIT',
            'install_command': '',
            'main_files': [],
            'dependencies': []
        }
        
        # Check for package.json (Node.js)
        package_json = directory / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                info.update({
                    'name': data.get('name', info['name']),
                    'description': data.get('description', ''),
                    'language': 'javascript',
                    'version': data.get('version', '1.0.0'),
                    'license': data.get('license', 'MIT'),
                    'install_command': 'npm install',
                    'dependencies': list(data.get('dependencies', {}).keys())
                })
                if 'react' in data.get('dependencies', {}):
                    info['framework'] = 'react'
                elif 'vue' in data.get('dependencies', {}):
                    info['framework'] = 'vue'
                elif 'angular' in data.get('dependencies', {}):
                    info['framework'] = 'angular'
            except:
                pass
        
        # Check for setup.py (Python)
        setup_py = directory / 'setup.py'
        if setup_py.exists():
            info['language'] = 'python'
            info['install_command'] = 'pip install -e .'
            # Try to extract info from setup.py
            try:
                with open(setup_py, 'r') as f:
                    content = f.read()
                name_match = re.search(r"name=['\"]([^'\"]+)['\"]", content)
                if name_match:
                    info['name'] = name_match.group(1)
                desc_match = re.search(r"description=['\"]([^'\"]+)['\"]", content)
                if desc_match:
                    info['description'] = desc_match.group(1)
            except:
                pass
        
        # Check for pyproject.toml (Python)
        pyproject_toml = directory / 'pyproject.toml'
        if pyproject_toml.exists():
            info['language'] = 'python'
            info['install_command'] = 'pip install .'
        
        # Check for requirements.txt (Python)
        requirements_txt = directory / 'requirements.txt'
        if requirements_txt.exists() and info['language'] == 'unknown':
            info['language'] = 'python'
            info['install_command'] = 'pip install -r requirements.txt'
        
        # Check for Cargo.toml (Rust)
        cargo_toml = directory / 'Cargo.toml'
        if cargo_toml.exists():
            info['language'] = 'rust'
            info['install_command'] = 'cargo build'
        
        # Check for go.mod (Go)
        go_mod = directory / 'go.mod'
        if go_mod.exists():
            info['language'] = 'go'
            info['install_command'] = 'go mod download'
        
        # Check for pom.xml (Java/Maven)
        pom_xml = directory / 'pom.xml'
        if pom_xml.exists():
            info['language'] = 'java'
            info['framework'] = 'maven'
            info['install_command'] = 'mvn install'
        
        # Check for build.gradle (Java/Gradle)
        build_gradle = directory / 'build.gradle'
        if build_gradle.exists():
            info['language'] = 'java'
            info['framework'] = 'gradle'
            info['install_command'] = 'gradle build'
        
        # Detect main files
        main_patterns = {
            'python': ['main.py', 'app.py', '__init__.py'],
            'javascript': ['index.js', 'app.js', 'main.js'],
            'typescript': ['index.ts', 'app.ts', 'main.ts'],
            'go': ['main.go'],
            'rust': ['main.rs', 'lib.rs'],
            'java': ['Main.java', 'Application.java']
        }
        
        if info['language'] in main_patterns:
            for pattern in main_patterns[info['language']]:
                main_files = list(directory.rglob(pattern))
                info['main_files'].extend(str(f) for f in main_files[:3])  # Limit to 3
        
        return info
    
    def parse_python_file(self, file_path: Path) -> Dict:
        """Parse Python file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            module_doc = ast.get_docstring(tree) or "No description available."
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "No description available.",
                        'args': [arg.arg for arg in node.args.args],
                        'returns': getattr(node.returns, 'id', 'Any') if node.returns else 'Any'
                    }
                    functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "No description available.",
                        'methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'docstring': ast.get_docstring(item) or "No description available.",
                                'args': [arg.arg for arg in item.args.args]
                            }
                            class_info['methods'].append(method_info)
                    
                    classes.append(class_info)
            
            return {
                'module_doc': module_doc,
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            return {
                'module_doc': f"Error parsing file: {str(e)}",
                'functions': [],
                'classes': []
            }
    
    def parse_javascript_file(self, file_path: Path) -> Dict:
        """Parse JavaScript/TypeScript file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex-based parsing for functions
            functions = []
            classes = []
            
            # Function patterns
            func_patterns = [
                r'function\s+(\w+)\s*\(([^)]*)\)\s*{',
                r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
                r'(\w+):\s*function\s*\(([^)]*)\)',
                r'(\w+)\s*\(([^)]*)\)\s*{'
            ]
            
            for pattern in func_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    name = match.group(1)
                    params = match.group(2) if len(match.groups()) > 1 else ''
                    
                    # Look for JSDoc comment before function
                    start = match.start()
                    before_func = content[:start].strip()
                    jsdoc_match = re.search(r'/\*\*(.*?)\*/', before_func, re.DOTALL)
                    docstring = "No description available."
                    if jsdoc_match:
                        docstring = jsdoc_match.group(1).strip()
                    
                    functions.append({
                        'name': name,
                        'docstring': docstring,
                        'args': [p.strip() for p in params.split(',') if p.strip()],
                        'returns': 'any'
                    })
            
            # Class patterns
            class_matches = re.finditer(r'class\s+(\w+)', content)
            for match in class_matches:
                classes.append({
                    'name': match.group(1),
                    'docstring': "No description available.",
                    'methods': []
                })
            
            return {
                'module_doc': "JavaScript/TypeScript module",
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            return {
                'module_doc': f"Error parsing file: {str(e)}",
                'functions': [],
                'classes': []
            }
    
    def parse_typescript_file(self, file_path: Path) -> Dict:
        """Parse TypeScript file for documentation"""
        return self.parse_javascript_file(file_path)
    
    def parse_go_file(self, file_path: Path) -> Dict:
        """Parse Go file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = []
            
            # Go function pattern
            func_pattern = r'func\s+(\w+)\s*\(([^)]*)\)\s*([^{]*)?{'
            matches = re.finditer(func_pattern, content)
            
            for match in matches:
                name = match.group(1)
                params = match.group(2) if len(match.groups()) > 1 else ''
                returns = match.group(3) if len(match.groups()) > 2 else ''
                
                functions.append({
                    'name': name,
                    'docstring': "No description available.",
                    'args': [p.strip() for p in params.split(',') if p.strip()],
                    'returns': returns.strip() or 'void'
                })
            
            return {
                'module_doc': "Go module",
                'functions': functions,
                'classes': []
            }
            
        except Exception as e:
            return {
                'module_doc': f"Error parsing file: {str(e)}",
                'functions': [],
                'classes': []
            }
    
    def parse_rust_file(self, file_path: Path) -> Dict:
        """Parse Rust file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = []
            
            # Rust function pattern
            func_pattern = r'fn\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^{]+))?'
            matches = re.finditer(func_pattern, content)
            
            for match in matches:
                name = match.group(1)
                params = match.group(2) if len(match.groups()) > 1 else ''
                returns = match.group(3) if len(match.groups()) > 2 and match.group(3) else '()'
                
                functions.append({
                    'name': name,
                    'docstring': "No description available.",
                    'args': [p.strip() for p in params.split(',') if p.strip()],
                    'returns': returns.strip()
                })
            
            return {
                'module_doc': "Rust module",
                'functions': functions,
                'classes': []
            }
            
        except Exception as e:
            return {
                'module_doc': f"Error parsing file: {str(e)}",
                'functions': [],
                'classes': []
            }
    
    def parse_java_file(self, file_path: Path) -> Dict:
        """Parse Java file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = []
            classes = []
            
            # Java method pattern
            method_pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(\w+)\s+(\w+)\s*\(([^)]*)\)'
            matches = re.finditer(method_pattern, content)
            
            for match in matches:
                return_type = match.group(1)
                name = match.group(2)
                params = match.group(3) if len(match.groups()) > 2 else ''
                
                functions.append({
                    'name': name,
                    'docstring': "No description available.",
                    'args': [p.strip() for p in params.split(',') if p.strip()],
                    'returns': return_type
                })
            
            # Java class pattern
            class_pattern = r'class\s+(\w+)'
            class_matches = re.finditer(class_pattern, content)
            for match in class_matches:
                classes.append({
                    'name': match.group(1),
                    'docstring': "No description available.",
                    'methods': []
                })
            
            return {
                'module_doc': "Java class",
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            return {
                'module_doc': f"Error parsing file: {str(e)}",
                'functions': [],
                'classes': []
            }
    
    def parse_ruby_file(self, file_path: Path) -> Dict:
        """Parse Ruby file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = []
            classes = []
            
            # Ruby method pattern
            method_pattern = r'def\s+(\w+)(?:\(([^)]*)\))?'
            matches = re.finditer(method_pattern, content)
            
            for match in matches:
                name = match.group(1)
                params = match.group(2) if len(match.groups()) > 1 and match.group(2) else ''
                
                functions.append({
                    'name': name,
                    'docstring': "No description available.",
                    'args': [p.strip() for p in params.split(',') if p.strip()],
                    'returns': 'Object'
                })
            
            # Ruby class pattern
            class_pattern = r'class\s+(\w+)'
            class_matches = re.finditer(class_pattern, content)
            for match in class_matches:
                classes.append({
                    'name': match.group(1),
                    'docstring': "No description available.",
                    'methods': []
                })
            
            return {
                'module_doc': "Ruby module",
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            return {
                'module_doc': f"Error parsing file: {str(e)}",
                'functions': [],
                'classes': []
            }
    
    def parse_php_file(self, file_path: Path) -> Dict:
        """Parse PHP file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = []
            classes = []
            
            # PHP function pattern
            func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
            matches = re.finditer(func_pattern, content)
            
            for match in matches:
                name = match.group(1)
                params = match.group(2) if len(match.groups()) > 1 else ''
                
                functions.append({
                    'name': name,
                    'docstring': "No description available.",
                    'args': [p.strip() for p in params.split(',') if p.strip()],
                    'returns': 'mixed'
                })
            
            # PHP class pattern
            class_pattern = r'class\s+(\w+)'
            class_matches = re.finditer(class_pattern, content)
            for match in class_matches:
                classes.append({
                    'name': match.group(1),
                    'docstring': "No description available.",
                    'methods': []
                })
            
            return {
                'module_doc': "PHP file",
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            return {
                'module_doc': f"Error parsing file: {str(e)}",
                'functions': [],
                'classes': []
            }
    
    def generate_file_documentation(self, file_path: str) -> str:
        """Generate documentation for a single file"""
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        if ext not in self.parsers:
            return f"# {file_path.name}\n\nNo parser available for {ext} files."
        
        parsed = self.parsers[ext](file_path)
        
        # Generate documentation
        doc_parts = [f"# {file_path.name}", "", parsed['module_doc'], ""]
        
        if parsed['functions']:
            doc_parts.append("## Functions")
            doc_parts.append("")
            for func in parsed['functions']:
                params = ', '.join(func['args'])
                doc_parts.append(f"### `{func['name']}({params})`")
                doc_parts.append("")
                doc_parts.append(func['docstring'])
                doc_parts.append("")
                if func.get('returns'):
                    doc_parts.append(f"**Returns:** `{func['returns']}`")
                    doc_parts.append("")
        
        if parsed['classes']:
            doc_parts.append("## Classes")
            doc_parts.append("")
            for cls in parsed['classes']:
                doc_parts.append(f"### `{cls['name']}`")
                doc_parts.append("")
                doc_parts.append(cls['docstring'])
                doc_parts.append("")
                if cls.get('methods'):
                    doc_parts.append("#### Methods")
                    doc_parts.append("")
                    for method in cls['methods']:
                        method_params = ', '.join(method['args'])
                        doc_parts.append(f"- `{method['name']}({method_params})`")
                    doc_parts.append("")
        
        return '\n'.join(doc_parts)
    
    def generate_api_documentation(self, directory: str = '.') -> str:
        """Generate API documentation for entire project"""
        directory = Path(directory)
        
        # Play audio notification
        self.play_audio('documentation_generating.wav')
        
        # Detect project info
        project_info = self.detect_project_info(directory)
        
        doc_parts = [
            f"# {project_info['name']} API Documentation",
            "",
            project_info['description'] or "No description available.",
            "",
            f"**Language:** {project_info['language']}",
            f"**Version:** {project_info['version']}",
            ""
        ]
        
        # Find all source files
        source_extensions = list(self.parsers.keys())
        all_files = []
        
        for ext in source_extensions:
            all_files.extend(directory.rglob(f"*{ext}"))
        
        # Exclude common directories
        exclude_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build', 'target'}
        source_files = [f for f in all_files 
                       if not any(exc in f.parts for exc in exclude_dirs)]
        
        # Group by directory
        file_groups = {}
        for file_path in source_files:
            rel_path = file_path.relative_to(directory)
            dir_name = str(rel_path.parent) if rel_path.parent != Path('.') else 'root'
            
            if dir_name not in file_groups:
                file_groups[dir_name] = []
            file_groups[dir_name].append(file_path)
        
        # Generate documentation for each group
        for dir_name, files in sorted(file_groups.items()):
            if len(files) == 0:
                continue
            
            doc_parts.append(f"## {dir_name}")
            doc_parts.append("")
            
            for file_path in sorted(files):
                ext = file_path.suffix.lower()
                if ext in self.parsers:
                    parsed = self.parsers[ext](file_path)
                    
                    doc_parts.append(f"### {file_path.name}")
                    doc_parts.append("")
                    doc_parts.append(parsed['module_doc'])
                    doc_parts.append("")
                    
                    # Add functions
                    if parsed['functions']:
                        for func in parsed['functions'][:5]:  # Limit to 5 functions
                            params = ', '.join(func['args'])
                            doc_parts.append(f"- `{func['name']}({params})` - {func['docstring'][:100]}{'...' if len(func['docstring']) > 100 else ''}")
                        doc_parts.append("")
                    
                    # Add classes
                    if parsed['classes']:
                        for cls in parsed['classes'][:3]:  # Limit to 3 classes
                            doc_parts.append(f"- `{cls['name']}` - {cls['docstring'][:100]}{'...' if len(cls['docstring']) > 100 else ''}")
                        doc_parts.append("")
        
        return '\n'.join(doc_parts)
    
    def generate_readme(self, directory: str = '.') -> str:
        """Generate README.md for project"""
        directory = Path(directory)
        project_info = self.detect_project_info(directory)
        
        # Generate usage examples based on language
        usage_examples = self.generate_usage_examples(project_info)
        
        readme_content = self.templates['readme'].format(
            project_name=project_info['name'],
            description=project_info['description'] or "Project description goes here.",
            install_command=project_info['install_command'] or "# Installation instructions",
            usage_examples=usage_examples,
            api_reference="See API documentation for detailed reference.",
            contributing_info="Please read CONTRIBUTING.md for details on our code of conduct.",
            license_info=f"This project is licensed under the {project_info['license']} License."
        )
        
        return readme_content
    
    def generate_usage_examples(self, project_info: Dict) -> str:
        """Generate usage examples based on project language"""
        if project_info['language'] == 'python':
            return f"""```python
import {project_info['name']}

# Basic usage example
result = {project_info['name']}.main()
print(result)
```"""
        elif project_info['language'] == 'javascript':
            return f"""```javascript
const {project_info['name']} = require('{project_info['name']}');

// Basic usage example
const result = {project_info['name']}.main();
console.log(result);
```"""
        elif project_info['language'] == 'go':
            return f"""```go
package main

import "{project_info['name']}"

func main() {{
    result := {project_info['name']}.Main()
    fmt.Println(result)
}}
```"""
        else:
            return "```\n# Usage examples will be added here\n```"
    
    def update_documentation(self, file_path: str) -> bool:
        """Update documentation when a file is saved"""
        if not self.update_on_save:
            return True
        
        file_path = Path(file_path)
        
        # Generate documentation for the file
        doc_content = self.generate_file_documentation(str(file_path))
        
        # Save to docs directory
        docs_dir = file_path.parent / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        doc_file = docs_dir / f"{file_path.stem}_api.md"
        
        try:
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            return True
        except Exception as e:
            print(f"Failed to update documentation: {e}")
            return False
    
    def play_audio(self, filename: str):
        """Play audio notification"""
        try:
            audio_path = self.claude_dir / 'audio' / filename
            if audio_path.exists():
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass

def main():
    """Hook entry point"""
    generator = AutoDocumentationGenerator()
    
    if len(sys.argv) < 2:
        print("Usage: auto_documentation.py <action> [args]")
        print("Actions:")
        print("  file <path>      - Generate docs for single file")
        print("  api [dir]        - Generate API documentation")
        print("  readme [dir]     - Generate README.md")
        print("  update <file>    - Update docs on file save")
        print("  project [dir]    - Generate all project docs")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'file' and len(sys.argv) > 2:
        file_path = sys.argv[2]
        doc = generator.generate_file_documentation(file_path)
        print(doc)
    
    elif action == 'api':
        directory = sys.argv[2] if len(sys.argv) > 2 else '.'
        doc = generator.generate_api_documentation(directory)
        
        # Save to file
        docs_dir = Path(directory) / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        with open(docs_dir / 'API.md', 'w', encoding='utf-8') as f:
            f.write(doc)
        
        print(f"API documentation saved to {docs_dir / 'API.md'}")
    
    elif action == 'readme':
        directory = sys.argv[2] if len(sys.argv) > 2 else '.'
        readme = generator.generate_readme(directory)
        
        readme_path = Path(directory) / 'README.md'
        if not readme_path.exists():  # Don't overwrite existing README
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme)
            print(f"README.md generated at {readme_path}")
        else:
            print("README.md already exists, skipping")
    
    elif action == 'update' and len(sys.argv) > 2:
        file_path = sys.argv[2]
        success = generator.update_documentation(file_path)
        sys.exit(0 if success else 1)
    
    elif action == 'project':
        directory = sys.argv[2] if len(sys.argv) > 2 else '.'
        
        # Generate API docs
        api_doc = generator.generate_api_documentation(directory)
        docs_dir = Path(directory) / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        with open(docs_dir / 'API.md', 'w', encoding='utf-8') as f:
            f.write(api_doc)
        
        # Generate README if it doesn't exist
        readme_path = Path(directory) / 'README.md'
        if not readme_path.exists():
            readme = generator.generate_readme(directory)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme)
        
        print(f"Project documentation generated in {docs_dir}")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()