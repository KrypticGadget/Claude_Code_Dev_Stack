#!/usr/bin/env python3
"""
D3.js Interactive Diagram Generator
Generates interactive D3.js visualizations for complex data relationships
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class D3Generator:
    """Generator for interactive D3.js visualizations"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir / "diagrams" / "d3"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # D3.js templates for different visualization types
        self.templates = {
            'force_graph': self._get_force_graph_template(),
            'tree': self._get_tree_template(),
            'network': self._get_network_template(),
            'hierarchy': self._get_hierarchy_template(),
            'dependency': self._get_dependency_template()
        }
    
    def generate(self, diagram_spec) -> Optional[Path]:
        """Generate D3.js visualization from specification"""
        try:
            # Determine visualization type
            viz_type = self._determine_viz_type(diagram_spec)
            
            # Generate data and HTML
            data = self._generate_data(diagram_spec, viz_type)
            html_content = self._generate_html(diagram_spec, viz_type, data)
            
            # Save HTML file
            output_file = self.output_dir / f"{diagram_spec.name}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Save data file
            data_file = self.output_dir / f"{diagram_spec.name}_data.json"
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Generated D3.js visualization: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate D3.js visualization: {e}")
            return None
    
    def _determine_viz_type(self, diagram_spec) -> str:
        """Determine the appropriate D3.js visualization type"""
        metadata = diagram_spec.metadata
        
        # Check for network/dependency relationships
        if 'modules' in metadata and len(metadata['modules']) > 1:
            return 'network'
        
        # Check for hierarchical structure
        if 'component' in metadata:
            component = metadata['component']
            if component.get('classes') and len(component['classes']) > 1:
                return 'hierarchy'
        
        # Check for dependency mapping
        if 'dependencies' in diagram_spec.name or 'import' in diagram_spec.name:
            return 'dependency'
        
        # Default to force graph
        return 'force_graph'
    
    def _generate_data(self, diagram_spec, viz_type: str) -> Dict[str, Any]:
        """Generate data structure for D3.js visualization"""
        metadata = diagram_spec.metadata
        
        if viz_type == 'network':
            return self._generate_network_data(metadata)
        elif viz_type == 'hierarchy':
            return self._generate_hierarchy_data(metadata)
        elif viz_type == 'dependency':
            return self._generate_dependency_data(metadata)
        elif viz_type == 'tree':
            return self._generate_tree_data(metadata)
        else:
            return self._generate_force_graph_data(metadata)
    
    def _generate_network_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate network graph data for module relationships"""
        modules = metadata.get('modules', {})
        
        nodes = []
        links = []
        
        # Create nodes for each module
        for i, (module_name, components) in enumerate(modules.items()):
            display_name = module_name.replace('.', ' ').title() or 'Core'
            
            nodes.append({
                'id': module_name or 'core',
                'name': display_name,
                'group': i + 1,
                'size': len(components),
                'type': 'module',
                'components': len(components)
            })
            
            # Create nodes for significant components
            for comp in components[:3]:  # Limit for readability
                comp_name = Path(comp['file']).stem
                nodes.append({
                    'id': f"{module_name}.{comp_name}",
                    'name': comp_name,
                    'group': i + 1,
                    'size': len(comp.get('classes', [])) + len(comp.get('functions', [])),
                    'type': 'component',
                    'parent': module_name or 'core'
                })
                
                # Link component to module
                links.append({
                    'source': module_name or 'core',
                    'target': f"{module_name}.{comp_name}",
                    'value': 1,
                    'type': 'contains'
                })
        
        # Create links between modules based on potential dependencies
        module_names = list(modules.keys())
        for i, module in enumerate(module_names):
            for other_module in module_names[i+1:]:
                # Simple heuristic: modules with similar names might be related
                if module and other_module and len(set(module.split('.')) & set(other_module.split('.'))) > 0:
                    links.append({
                        'source': module,
                        'target': other_module,
                        'value': 2,
                        'type': 'depends'
                    })
        
        return {
            'nodes': nodes,
            'links': links,
            'title': metadata.get('title', 'Module Network'),
            'description': metadata.get('description', 'Interactive network of modules and components')
        }
    
    def _generate_hierarchy_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hierarchical tree data"""
        component = metadata.get('component', {})
        
        # Build hierarchy from component structure
        hierarchy = {
            'name': Path(component.get('file', 'Component')).stem,
            'children': []
        }
        
        # Add classes as children
        for cls in component.get('classes', []):
            class_node = {
                'name': cls['name'],
                'type': 'class',
                'children': []
            }
            
            # Add methods as children
            for method in cls.get('methods', [])[:5]:  # Limit methods
                class_node['children'].append({
                    'name': method,
                    'type': 'method',
                    'size': 1
                })
            
            hierarchy['children'].append(class_node)
        
        # Add functions as children
        for func in component.get('functions', []):
            hierarchy['children'].append({
                'name': func['name'],
                'type': 'function',
                'size': 2
            })
        
        return {
            'hierarchy': hierarchy,
            'title': metadata.get('title', 'Component Hierarchy'),
            'description': metadata.get('description', 'Hierarchical view of component structure')
        }
    
    def _generate_dependency_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dependency graph data"""
        # This would analyze actual import dependencies
        # For now, create a sample structure
        
        return {
            'nodes': [
                {'id': 'core', 'name': 'Core', 'level': 0},
                {'id': 'utils', 'name': 'Utils', 'level': 1},
                {'id': 'models', 'name': 'Models', 'level': 1},
                {'id': 'api', 'name': 'API', 'level': 2}
            ],
            'links': [
                {'source': 'core', 'target': 'utils', 'type': 'imports'},
                {'source': 'core', 'target': 'models', 'type': 'imports'},
                {'source': 'api', 'target': 'models', 'type': 'imports'},
                {'source': 'api', 'target': 'utils', 'type': 'imports'}
            ],
            'title': metadata.get('title', 'Dependency Graph'),
            'description': metadata.get('description', 'Module dependency relationships')
        }
    
    def _generate_tree_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tree data for hierarchical layouts"""
        return self._generate_hierarchy_data(metadata)
    
    def _generate_force_graph_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate force-directed graph data"""
        return self._generate_network_data(metadata)
    
    def _generate_html(self, diagram_spec, viz_type: str, data: Dict[str, Any]) -> str:
        """Generate complete HTML file with D3.js visualization"""
        title = data.get('title', diagram_spec.name)
        description = data.get('description', '')
        
        if viz_type == 'network' or viz_type == 'force_graph':
            return self._generate_network_html(title, description, data)
        elif viz_type == 'hierarchy' or viz_type == 'tree':
            return self._generate_tree_html(title, description, data)
        elif viz_type == 'dependency':
            return self._generate_dependency_html(title, description, data)
        else:
            return self._generate_generic_html(title, description, data)
    
    def _generate_network_html(self, title: str, description: str, data: Dict[str, Any]) -> str:
        """Generate HTML for network/force graph visualization"""
        nodes_json = json.dumps(data.get('nodes', []))
        links_json = json.dumps(data.get('links', []))
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .description {{
            color: #666;
            margin-bottom: 20px;
        }}
        .network-container {{
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .node {{
            cursor: pointer;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        .tooltip {{
            position: absolute;
            padding: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
        }}
        .legend {{
            margin-top: 20px;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="description">{description}</div>
        <div class="network-container">
            <svg id="network" width="100%" height="600"></svg>
        </div>
        <div class="legend">
            <strong>Legend:</strong>
            <span style="color: #1f77b4;">● Modules</span>
            <span style="color: #ff7f0e;">● Components</span>
            <span style="color: #2ca02c;">— Contains</span>
            <span style="color: #d62728;">— Depends</span>
        </div>
    </div>

    <div class="tooltip" style="display: none;"></div>

    <script>
        const nodes = {nodes_json};
        const links = {links_json};
        
        const width = 1160;
        const height = 600;
        
        const svg = d3.select("#network")
            .attr("width", width)
            .attr("height", height);
        
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", d => Math.sqrt(d.value))
            .attr("stroke", d => d.type === "contains" ? "#2ca02c" : "#d62728");
        
        const node = svg.append("g")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => Math.max(5, Math.sqrt(d.size) * 3))
            .attr("fill", d => d.type === "module" ? "#1f77b4" : "#ff7f0e")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        const label = svg.append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .text(d => d.name)
            .attr("font-size", 12)
            .attr("dx", 15)
            .attr("dy", 4);
        
        const tooltip = d3.select(".tooltip");
        
        node.on("mouseover", function(event, d) {{
            tooltip.style("display", "block")
                .html(`<strong>${{d.name}}</strong><br/>Type: ${{d.type}}<br/>Size: ${{d.size}}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }})
        .on("mouseout", function() {{
            tooltip.style("display", "none");
        }});
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>'''
    
    def _generate_tree_html(self, title: str, description: str, data: Dict[str, Any]) -> str:
        """Generate HTML for tree/hierarchy visualization"""
        hierarchy_json = json.dumps(data.get('hierarchy', {}))
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .description {{
            color: #666;
            margin-bottom: 20px;
        }}
        .tree-container {{
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow: auto;
        }}
        .node circle {{
            fill: #999;
            stroke: steelblue;
            stroke-width: 1.5px;
        }}
        .node text {{
            font: 12px sans-serif;
        }}
        .link {{
            fill: none;
            stroke: #ccc;
            stroke-width: 1.5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="description">{description}</div>
        <div class="tree-container">
            <svg id="tree" width="100%" height="600"></svg>
        </div>
    </div>

    <script>
        const data = {hierarchy_json};
        
        const width = 1160;
        const height = 600;
        
        const svg = d3.select("#tree")
            .attr("width", width)
            .attr("height", height);
        
        const g = svg.append("g")
            .attr("transform", "translate(40,40)");
        
        const tree = d3.tree()
            .size([height - 80, width - 160]);
        
        const root = d3.hierarchy(data);
        tree(root);
        
        const link = g.selectAll(".link")
            .data(root.descendants().slice(1))
            .enter().append("path")
            .attr("class", "link")
            .attr("d", d => {{
                return "M" + d.y + "," + d.x
                    + "C" + (d.y + d.parent.y) / 2 + "," + d.x
                    + " " + (d.y + d.parent.y) / 2 + "," + d.parent.x
                    + " " + d.parent.y + "," + d.parent.x;
            }});
        
        const node = g.selectAll(".node")
            .data(root.descendants())
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", d => "translate(" + d.y + "," + d.x + ")");
        
        node.append("circle")
            .attr("r", 4.5)
            .style("fill", d => d.data.type === "class" ? "#ff7f0e" : 
                                 d.data.type === "method" ? "#2ca02c" : "#1f77b4");
        
        node.append("text")
            .attr("dy", 3)
            .attr("x", d => d.children ? -8 : 8)
            .style("text-anchor", d => d.children ? "end" : "start")
            .text(d => d.data.name);
    </script>
</body>
</html>'''
    
    def _generate_dependency_html(self, title: str, description: str, data: Dict[str, Any]) -> str:
        """Generate HTML for dependency graph visualization"""
        return self._generate_network_html(title, description, data)
    
    def _generate_generic_html(self, title: str, description: str, data: Dict[str, Any]) -> str:
        """Generate generic HTML visualization"""
        return self._generate_network_html(title, description, data)
    
    def _get_force_graph_template(self) -> str:
        """Template for force-directed graph"""
        return "force_graph_template"
    
    def _get_tree_template(self) -> str:
        """Template for tree visualization"""
        return "tree_template"
    
    def _get_network_template(self) -> str:
        """Template for network visualization"""
        return "network_template"
    
    def _get_hierarchy_template(self) -> str:
        """Template for hierarchy visualization"""
        return "hierarchy_template"
    
    def _get_dependency_template(self) -> str:
        """Template for dependency graph"""
        return "dependency_template"