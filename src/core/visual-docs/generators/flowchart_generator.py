#!/usr/bin/env python3
"""
Flowchart Generator
Generates flowcharts from code workflows and processes
"""

import os
import json
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class FlowchartGenerator:
    """Generator for workflow and process flowcharts"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir / "diagrams" / "flowcharts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Flowchart templates
        self.templates = {
            'process': self._get_process_template(),
            'decision': self._get_decision_template(),
            'data_flow': self._get_data_flow_template(),
            'workflow': self._get_workflow_template()
        }
    
    def generate(self, diagram_spec) -> Optional[Path]:
        """Generate flowchart from specification"""
        try:
            # Analyze source files for workflows
            workflow_data = self._analyze_workflows(diagram_spec.source_files)
            
            # Generate flowchart content
            flowchart_content = self._generate_flowchart_content(diagram_spec, workflow_data)
            
            # Save as Mermaid flowchart
            output_file = self.output_dir / f"{diagram_spec.name}_flowchart.mmd"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(flowchart_content)
            
            # Render to SVG if possible
            svg_file = self._render_to_svg(output_file)
            
            logger.info(f"Generated flowchart: {output_file}")
            return svg_file or output_file
            
        except Exception as e:
            logger.error(f"Failed to generate flowchart: {e}")
            return None
    
    def _analyze_workflows(self, source_files: List[Path]) -> Dict[str, Any]:
        """Analyze source files to extract workflow patterns"""
        workflows = {
            'functions': [],
            'classes': [],
            'decision_points': [],
            'loops': [],
            'try_catch': [],
            'imports': [],
            'main_flow': []
        }
        
        for file_path in source_files:
            if file_path.suffix == '.py' and file_path.exists():
                workflows.update(self._analyze_python_file(file_path))
        
        return workflows
    
    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file for workflow patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            return self._extract_workflow_from_ast(tree, file_path)
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
            return {}
    
    def _extract_workflow_from_ast(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
        """Extract workflow patterns from AST"""
        workflow = {
            'file': str(file_path),
            'functions': [],
            'classes': [],
            'decision_points': [],
            'loops': [],
            'try_catch': [],
            'imports': [],
            'main_flow': []
        }
        
        # Walk through AST nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                workflow['functions'].append(self._analyze_function(node))
            elif isinstance(node, ast.ClassDef):
                workflow['classes'].append(self._analyze_class(node))
            elif isinstance(node, ast.If):
                workflow['decision_points'].append(self._analyze_if_statement(node))
            elif isinstance(node, (ast.For, ast.While)):
                workflow['loops'].append(self._analyze_loop(node))
            elif isinstance(node, ast.Try):
                workflow['try_catch'].append(self._analyze_try_catch(node))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                workflow['imports'].append(self._analyze_import(node))
        
        # Extract main execution flow
        workflow['main_flow'] = self._extract_main_flow(tree)
        
        return workflow
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze function for workflow patterns"""
        return {
            'name': node.name,
            'args': [arg.arg for arg in node.args.args],
            'returns': self._has_return_statement(node),
            'calls': self._extract_function_calls(node),
            'complexity': self._calculate_complexity(node),
            'docstring': ast.get_docstring(node)
        }
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze class for workflow patterns"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        return {
            'name': node.name,
            'methods': methods,
            'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
            'docstring': ast.get_docstring(node)
        }
    
    def _analyze_if_statement(self, node: ast.If) -> Dict[str, Any]:
        """Analyze if statement for decision flow"""
        return {
            'type': 'if',
            'has_else': node.orelse is not None and len(node.orelse) > 0,
            'has_elif': any(isinstance(stmt, ast.If) for stmt in node.orelse),
            'condition_complexity': self._get_condition_complexity(node.test)
        }
    
    def _analyze_loop(self, node) -> Dict[str, Any]:
        """Analyze loop for iteration flow"""
        loop_type = 'for' if isinstance(node, ast.For) else 'while'
        return {
            'type': loop_type,
            'has_break': self._has_break_statement(node),
            'has_continue': self._has_continue_statement(node),
            'nested': self._has_nested_loops(node)
        }
    
    def _analyze_try_catch(self, node: ast.Try) -> Dict[str, Any]:
        """Analyze try-catch for error handling flow"""
        return {
            'type': 'try_catch',
            'handlers': len(node.handlers),
            'has_finally': node.finalbody is not None and len(node.finalbody) > 0,
            'has_else': node.orelse is not None and len(node.orelse) > 0
        }
    
    def _analyze_import(self, node) -> Dict[str, Any]:
        """Analyze import statements"""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'modules': [alias.name for alias in node.names]
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'from_import',
                'module': node.module,
                'names': [alias.name for alias in node.names]
            }
    
    def _extract_main_flow(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract main execution flow"""
        main_statements = []
        
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                if node.name == 'main':
                    main_statements.append({'type': 'main_function', 'name': 'main'})
            elif isinstance(node, ast.If) and self._is_main_guard(node):
                main_statements.append({'type': 'main_guard', 'content': '__main__'})
            elif isinstance(node, ast.Expr):
                main_statements.append({'type': 'expression', 'content': 'expression'})
        
        return main_statements
    
    def _is_main_guard(self, node: ast.If) -> bool:
        """Check if this is a __name__ == '__main__' guard"""
        if isinstance(node.test, ast.Compare):
            if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                return True
        return False
    
    def _has_return_statement(self, node: ast.FunctionDef) -> bool:
        """Check if function has return statements"""
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                return True
        return False
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls within a function"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls[:5]  # Limit for readability
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate basic cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def _get_condition_complexity(self, node: ast.AST) -> int:
        """Get complexity of condition (number of boolean operators)"""
        complexity = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        return complexity
    
    def _has_break_statement(self, node) -> bool:
        """Check if loop has break statements"""
        for child in ast.walk(node):
            if isinstance(child, ast.Break):
                return True
        return False
    
    def _has_continue_statement(self, node) -> bool:
        """Check if loop has continue statements"""
        for child in ast.walk(node):
            if isinstance(child, ast.Continue):
                return True
        return False
    
    def _has_nested_loops(self, node) -> bool:
        """Check if loop has nested loops"""
        for child in node.body:
            for grandchild in ast.walk(child):
                if isinstance(grandchild, (ast.For, ast.While)) and grandchild != node:
                    return True
        return False
    
    def _generate_flowchart_content(self, diagram_spec, workflow_data: Dict[str, Any]) -> str:
        """Generate Mermaid flowchart content"""
        title = diagram_spec.metadata.get('title', 'Workflow')
        
        # Determine flowchart type based on workflow complexity
        if workflow_data.get('decision_points') or workflow_data.get('loops'):
            return self._generate_complex_flowchart(title, workflow_data)
        elif workflow_data.get('functions'):
            return self._generate_function_flowchart(title, workflow_data)
        else:
            return self._generate_simple_flowchart(title, workflow_data)
    
    def _generate_complex_flowchart(self, title: str, workflow_data: Dict[str, Any]) -> str:
        """Generate complex flowchart with decisions and loops"""
        lines = [
            'flowchart TD',
            f'    %% {title}',
            '',
            '    Start([Start]) --> Input[Input Data]'
        ]
        
        node_count = 1
        current_node = 'Input'
        
        # Add decision points
        for decision in workflow_data.get('decision_points', [])[:3]:
            decision_node = f'Decision{node_count}'
            true_node = f'Process{node_count}A'
            false_node = f'Process{node_count}B'
            
            lines.extend([
                f'    {current_node} --> {decision_node}{{Decision Point}}',
                f'    {decision_node} -->|Yes| {true_node}[Process A]',
                f'    {decision_node} -->|No| {false_node}[Process B]'
            ])
            
            if decision['has_else']:
                lines.append(f'    {false_node} --> Merge{node_count}[Merge]')
                lines.append(f'    {true_node} --> Merge{node_count}')
                current_node = f'Merge{node_count}'
            else:
                current_node = true_node
            
            node_count += 1
        
        # Add loops
        for loop in workflow_data.get('loops', [])[:2]:
            loop_node = f'Loop{node_count}'
            loop_condition = f'LoopCondition{node_count}'
            
            lines.extend([
                f'    {current_node} --> {loop_condition}{{Continue Loop?}}',
                f'    {loop_condition} -->|Yes| {loop_node}[Loop Body]',
                f'    {loop_node} --> {loop_condition}',
                f'    {loop_condition} -->|No| After{loop_node}[Continue]'
            ])
            
            current_node = f'After{loop_node}'
            node_count += 1
        
        # Add try-catch
        for try_catch in workflow_data.get('try_catch', [])[:1]:
            try_node = f'TryBlock{node_count}'
            catch_node = f'CatchBlock{node_count}'
            
            lines.extend([
                f'    {current_node} --> {try_node}[Try Block]',
                f'    {try_node} --> {catch_node}[Error Handler]',
                f'    {try_node} --> Success{node_count}[Success]',
                f'    {catch_node} --> Success{node_count}'
            ])
            
            current_node = f'Success{node_count}'
            node_count += 1
        
        lines.extend([
            f'    {current_node} --> End([End])',
            '',
            '    %% Styling',
            '    classDef startEnd fill:#e1f5fe',
            '    classDef process fill:#f3e5f5',
            '    classDef decision fill:#fff3e0',
            '    class Start,End startEnd',
            '    class Input,Process1A,Process1B process'
        ])
        
        return '\n'.join(lines)
    
    def _generate_function_flowchart(self, title: str, workflow_data: Dict[str, Any]) -> str:
        """Generate flowchart based on function calls"""
        lines = [
            'flowchart LR',
            f'    %% {title}',
            ''
        ]
        
        functions = workflow_data.get('functions', [])[:6]  # Limit functions
        
        if not functions:
            return self._generate_simple_flowchart(title, workflow_data)
        
        # Start with main or first function
        main_func = next((f for f in functions if f['name'] == 'main'), functions[0])
        
        lines.append(f'    Start([Start]) --> {main_func["name"]}[{main_func["name"]}()]')
        current_node = main_func['name']
        
        # Add function call chain
        for func in functions[1:4]:  # Limit chain length
            func_node = func['name']
            lines.append(f'    {current_node} --> {func_node}[{func_node}()]')
            
            # Add complexity indicator
            if func['complexity'] > 3:
                lines.append(f'    {func_node} -.-> Complex{func_node}[Complex Logic]')
            
            current_node = func_node
        
        lines.append(f'    {current_node} --> End([End])')
        
        return '\n'.join(lines)
    
    def _generate_simple_flowchart(self, title: str, workflow_data: Dict[str, Any]) -> str:
        """Generate simple linear flowchart"""
        lines = [
            'flowchart TD',
            f'    %% {title}',
            '',
            '    Start([Start]) --> Process1[Initialize]',
            '    Process1 --> Process2[Process Data]',
            '    Process2 --> Process3[Generate Output]',
            '    Process3 --> End([End])'
        ]
        
        return '\n'.join(lines)
    
    def _render_to_svg(self, flowchart_file: Path) -> Optional[Path]:
        """Render flowchart to SVG using mermaid-cli"""
        try:
            svg_file = flowchart_file.with_suffix('.svg')
            
            result = subprocess.run([
                'mmdc', '-i', str(flowchart_file), '-o', str(svg_file),
                '--theme', 'default', '--backgroundColor', 'white'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and svg_file.exists():
                logger.info(f"Rendered flowchart SVG: {svg_file}")
                return svg_file
            else:
                logger.warning(f"Flowchart rendering failed: {result.stderr}")
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"mermaid-cli not available for flowchart: {e}")
            return None
    
    def generate_workflow_from_main(self, main_file: Path) -> Optional[Path]:
        """Generate workflow flowchart specifically from main execution file"""
        try:
            # Create a diagram spec for the main file
            diagram_spec = type('DiagramSpec', (), {
                'name': f'workflow_{main_file.stem}',
                'type': 'flowchart',
                'source_files': [main_file],
                'metadata': {
                    'title': f'{main_file.stem} Workflow',
                    'description': f'Execution flow of {main_file.name}'
                }
            })()
            
            return self.generate(diagram_spec)
            
        except Exception as e:
            logger.error(f"Failed to generate workflow from main file: {e}")
            return None
    
    def _get_process_template(self) -> str:
        """Template for process flowchart"""
        return '''flowchart TD
    %% {title}
    Start([Start]) --> Process[Process]
    Process --> End([End])'''
    
    def _get_decision_template(self) -> str:
        """Template for decision flowchart"""
        return '''flowchart TD
    %% {title}
    Start([Start]) --> Decision{{Decision?}}
    Decision -->|Yes| ProcessA[Process A]
    Decision -->|No| ProcessB[Process B]
    ProcessA --> End([End])
    ProcessB --> End'''
    
    def _get_data_flow_template(self) -> str:
        """Template for data flow flowchart"""
        return '''flowchart LR
    %% {title}
    Input[Input] --> Transform[Transform]
    Transform --> Output[Output]'''
    
    def _get_workflow_template(self) -> str:
        """Template for workflow flowchart"""
        return '''flowchart TD
    %% {title}
    Start([Start]) --> Initialize[Initialize]
    Initialize --> Process[Process]
    Process --> Validate{{Valid?}}
    Validate -->|Yes| Output[Generate Output]
    Validate -->|No| Error[Handle Error]
    Output --> End([End])
    Error --> End'''