#!/usr/bin/env python3
"""
Video Documentation Generator
Creates video tutorials and documentation from templates and scripts
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
import tempfile
import time

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Generator for video documentation and tutorials"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Video configuration
        self.video_formats = ['mp4', 'webm', 'gif']
        self.video_quality = 'high'  # high, medium, low
        self.frame_rate = 30
        self.resolution = (1920, 1080)
        
        # Check available tools
        self.tools_available = self._check_video_tools()
        
        # Video templates
        self.templates = self._load_video_templates()
    
    def _check_video_tools(self) -> Dict[str, bool]:
        """Check availability of video creation tools"""
        tools = {}
        
        # Check FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            tools['ffmpeg'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            tools['ffmpeg'] = False
        
        # Check Playwright for screen recording
        try:
            import playwright
            tools['playwright'] = True
        except ImportError:
            tools['playwright'] = False
        
        # Check OBS Studio (for advanced recording)
        try:
            result = subprocess.run(['obs', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            tools['obs'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            tools['obs'] = False
        
        logger.info(f"Video tools available: {tools}")
        return tools
    
    def _load_video_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load video script templates"""
        return {
            'walkthrough': {
                'name': 'Documentation Walkthrough',
                'duration': 180,  # 3 minutes
                'scenes': [
                    {'type': 'intro', 'duration': 15, 'content': 'Introduction'},
                    {'type': 'overview', 'duration': 45, 'content': 'System overview'},
                    {'type': 'detail', 'duration': 90, 'content': 'Component details'},
                    {'type': 'conclusion', 'duration': 30, 'content': 'Summary and next steps'}
                ]
            },
            'component_demo': {
                'name': 'Component Demonstration',
                'duration': 120,  # 2 minutes
                'scenes': [
                    {'type': 'intro', 'duration': 20, 'content': 'Component introduction'},
                    {'type': 'code_tour', 'duration': 60, 'content': 'Code walkthrough'},
                    {'type': 'usage', 'duration': 40, 'content': 'Usage examples'}
                ]
            },
            'architecture_tour': {
                'name': 'Architecture Tour',
                'duration': 240,  # 4 minutes
                'scenes': [
                    {'type': 'intro', 'duration': 30, 'content': 'Architecture introduction'},
                    {'type': 'diagram_tour', 'duration': 120, 'content': 'Interactive diagram exploration'},
                    {'type': 'integration', 'duration': 60, 'content': 'Integration points'},
                    {'type': 'conclusion', 'duration': 30, 'content': 'Summary'}
                ]
            }
        }
    
    def generate(self, interactive_docs: Path) -> List[Path]:
        """Generate video documentation"""
        try:
            videos = []
            
            if not self.tools_available.get('ffmpeg'):
                logger.warning("FFmpeg not available - video generation limited")
                return self._generate_simple_videos(interactive_docs)
            
            # Generate overview video
            overview_video = self._generate_overview_video(interactive_docs)
            if overview_video:
                videos.append(overview_video)
            
            # Generate component videos
            components_dir = interactive_docs.parent / "components"
            if components_dir.exists():
                component_videos = self._generate_component_videos(components_dir)
                videos.extend(component_videos)
            
            # Generate architecture tour video
            diagrams_dir = interactive_docs.parent / "diagrams"
            if diagrams_dir.exists():
                architecture_video = self._generate_architecture_video(diagrams_dir)
                if architecture_video:
                    videos.append(architecture_video)
            
            # Generate animated GIFs from screenshots
            screenshots_dir = interactive_docs.parent.parent / "screenshots"
            if screenshots_dir.exists():
                gif_videos = self._generate_animated_gifs(screenshots_dir)
                videos.extend(gif_videos)
            
            logger.info(f"Generated {len(videos)} video files")
            return videos
            
        except Exception as e:
            logger.error(f"Failed to generate videos: {e}")
            return []
    
    def _generate_overview_video(self, docs_path: Path) -> Optional[Path]:
        """Generate overview video of the documentation"""
        try:
            video_script = self._create_overview_script(docs_path)
            return self._create_video_from_script(video_script, "overview")
            
        except Exception as e:
            logger.error(f"Failed to generate overview video: {e}")
            return None
    
    def _create_overview_script(self, docs_path: Path) -> Dict[str, Any]:
        """Create script for overview video"""
        template = self.templates['walkthrough']
        
        script = {
            'title': 'Documentation Overview',
            'duration': template['duration'],
            'scenes': []
        }
        
        # Intro scene
        script['scenes'].append({
            'type': 'intro',
            'duration': 15,
            'content': 'Welcome to the interactive documentation',
            'visual': 'main_page',
            'audio': 'Welcome to this comprehensive documentation. Let\'s explore the system architecture and components.',
            'actions': ['navigate_to_main']
        })
        
        # Overview scene
        script['scenes'].append({
            'type': 'overview',
            'duration': 45,
            'content': 'System architecture overview',
            'visual': 'architecture_diagram',
            'audio': 'Here we can see the overall system architecture. The main components work together to provide...',
            'actions': ['show_diagram', 'highlight_components']
        })
        
        # Component details scene
        script['scenes'].append({
            'type': 'detail',
            'duration': 90,
            'content': 'Exploring individual components',
            'visual': 'component_pages',
            'audio': 'Let\'s dive deeper into the individual components. Each component has detailed documentation...',
            'actions': ['navigate_components', 'show_code_examples']
        })
        
        # Conclusion scene
        script['scenes'].append({
            'type': 'conclusion',
            'duration': 30,
            'content': 'Summary and next steps',
            'visual': 'summary_view',
            'audio': 'This concludes our overview. You can explore further by clicking on any component or diagram.',
            'actions': ['show_navigation_options']
        })
        
        return script
    
    def _create_video_from_script(self, script: Dict[str, Any], name: str) -> Optional[Path]:
        """Create video from script definition"""
        if self.tools_available.get('playwright'):
            return self._create_video_with_playwright(script, name)
        else:
            return self._create_video_with_screenshots(script, name)
    
    def _create_video_with_playwright(self, script: Dict[str, Any], name: str) -> Optional[Path]:
        """Create video using Playwright screen recording"""
        try:
            from playwright.sync_api import sync_playwright
            
            output_file = self.output_dir / f"{name}.webm"
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # Need non-headless for recording
                context = browser.new_context(
                    viewport={'width': self.resolution[0], 'height': self.resolution[1]},
                    record_video_dir=str(self.output_dir)
                )
                page = context.new_page()
                
                # Execute script scenes
                for scene in script['scenes']:
                    self._execute_scene_actions(page, scene)
                    
                    # Wait for scene duration
                    page.wait_for_timeout(scene['duration'] * 1000)
                
                context.close()
                browser.close()
                
                # Find the recorded video file
                video_files = list(self.output_dir.glob("*.webm"))
                if video_files:
                    latest_video = max(video_files, key=lambda x: x.stat().st_mtime)
                    final_output = self.output_dir / f"{name}.webm"
                    latest_video.rename(final_output)
                    logger.info(f"Video created with Playwright: {final_output}")
                    return final_output
                
            return None
            
        except Exception as e:
            logger.warning(f"Playwright video creation failed: {e}")
            return None
    
    def _execute_scene_actions(self, page, scene: Dict[str, Any]):
        """Execute actions for a video scene"""
        actions = scene.get('actions', [])
        
        for action in actions:
            try:
                if action == 'navigate_to_main':
                    # Navigate to main documentation page
                    page.goto('file://' + str(self.config.output_dir / "interactive" / "index.html"))
                
                elif action == 'show_diagram':
                    # Scroll to or click on diagram
                    page.evaluate('document.querySelector(".diagram-gallery")?.scrollIntoView()')
                
                elif action == 'highlight_components':
                    # Highlight component sections
                    page.evaluate('''
                        document.querySelectorAll(".component-card").forEach((card, i) => {
                            setTimeout(() => {
                                card.style.border = "3px solid #007bff";
                                setTimeout(() => card.style.border = "", 1000);
                            }, i * 500);
                        });
                    ''')
                
                elif action == 'navigate_components':
                    # Navigate through component pages
                    component_links = page.query_selector_all('.component-link')
                    if component_links:
                        component_links[0].click()
                        page.wait_for_timeout(2000)
                        page.go_back()
                
                elif action == 'show_code_examples':
                    # Scroll to code examples
                    page.evaluate('document.querySelector(".code-examples")?.scrollIntoView()')
                
                elif action == 'show_navigation_options':
                    # Show navigation menu
                    page.evaluate('document.querySelector(".main-navigation")?.scrollIntoView()')
                
                page.wait_for_timeout(500)  # Small delay between actions
                
            except Exception as e:
                logger.warning(f"Action {action} failed: {e}")
    
    def _create_video_with_screenshots(self, script: Dict[str, Any], name: str) -> Optional[Path]:
        """Create video from screenshots using FFmpeg"""
        try:
            # Generate screenshots for each scene
            scene_images = []
            
            for i, scene in enumerate(script['scenes']):
                # Create scene image (placeholder implementation)
                scene_image = self._create_scene_image(scene, f"scene_{i}")
                if scene_image:
                    scene_images.append((scene_image, scene['duration']))
            
            if not scene_images:
                return None
            
            # Create video from images using FFmpeg
            return self._compile_video_from_images(scene_images, name)
            
        except Exception as e:
            logger.error(f"Screenshot-based video creation failed: {e}")
            return None
    
    def _create_scene_image(self, scene: Dict[str, Any], name: str) -> Optional[Path]:
        """Create image for a video scene"""
        # This is a simplified implementation
        # In practice, you'd take actual screenshots or create scene graphics
        
        scene_image = self.output_dir / f"{name}.png"
        
        # Create a simple scene image using PIL if available
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', self.resolution, color='white')
            draw = ImageDraw.Draw(img)
            
            # Add scene content
            title = scene.get('content', 'Scene')
            draw.text((50, 50), title, fill='black')
            
            # Add scene type indicator
            scene_type = scene.get('type', 'scene')
            draw.text((50, 100), f"Type: {scene_type}", fill='gray')
            
            img.save(scene_image)
            return scene_image
            
        except ImportError:
            logger.warning("PIL not available for scene image creation")
            return None
        except Exception as e:
            logger.warning(f"Scene image creation failed: {e}")
            return None
    
    def _compile_video_from_images(self, scene_images: List[Tuple[Path, int]], name: str) -> Optional[Path]:
        """Compile video from scene images using FFmpeg"""
        try:
            output_file = self.output_dir / f"{name}.mp4"
            
            # Create FFmpeg filter for combining images with different durations
            filter_parts = []
            input_files = []
            
            for i, (image_path, duration) in enumerate(scene_images):
                input_files.extend(['-loop', '1', '-t', str(duration), '-i', str(image_path)])
                filter_parts.append(f'[{i}:v]')
            
            if len(filter_parts) > 1:
                filter_complex = ''.join(filter_parts) + f'concat=n={len(scene_images)}:v=1:a=0[outv]'
                cmd = ['ffmpeg'] + input_files + [
                    '-filter_complex', filter_complex,
                    '-map', '[outv]',
                    '-c:v', 'libx264',
                    '-r', str(self.frame_rate),
                    '-pix_fmt', 'yuv420p',
                    str(output_file)
                ]
            else:
                # Single image case
                cmd = ['ffmpeg'] + input_files + [
                    '-c:v', 'libx264',
                    '-r', str(self.frame_rate),
                    '-pix_fmt', 'yuv420p',
                    str(output_file)
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and output_file.exists():
                logger.info(f"Video compiled: {output_file}")
                return output_file
            else:
                logger.warning(f"FFmpeg compilation failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Video compilation failed: {e}")
            return None
    
    def _generate_component_videos(self, components_dir: Path) -> List[Path]:
        """Generate videos for individual components"""
        videos = []
        
        for html_file in list(components_dir.glob("*.html"))[:3]:  # Limit to first 3
            try:
                component_name = html_file.stem
                script = self._create_component_script(html_file, component_name)
                video = self._create_video_from_script(script, f"component_{component_name}")
                if video:
                    videos.append(video)
                    
            except Exception as e:
                logger.warning(f"Failed to create component video for {html_file}: {e}")
        
        return videos
    
    def _create_component_script(self, html_file: Path, component_name: str) -> Dict[str, Any]:
        """Create script for component video"""
        template = self.templates['component_demo']
        
        script = {
            'title': f'{component_name} Component Demo',
            'duration': template['duration'],
            'scenes': [
                {
                    'type': 'intro',
                    'duration': 20,
                    'content': f'Introduction to {component_name}',
                    'visual': html_file,
                    'actions': ['navigate_to_component']
                },
                {
                    'type': 'code_tour',
                    'duration': 60,
                    'content': 'Code structure walkthrough',
                    'visual': html_file,
                    'actions': ['show_classes', 'show_methods']
                },
                {
                    'type': 'usage',
                    'duration': 40,
                    'content': 'Usage examples',
                    'visual': html_file,
                    'actions': ['show_examples']
                }
            ]
        }
        
        return script
    
    def _generate_architecture_video(self, diagrams_dir: Path) -> Optional[Path]:
        """Generate architecture tour video"""
        diagram_files = list(diagrams_dir.glob("*.html"))
        if not diagram_files:
            return None
        
        try:
            script = self._create_architecture_script(diagram_files)
            return self._create_video_from_script(script, "architecture_tour")
            
        except Exception as e:
            logger.error(f"Failed to create architecture video: {e}")
            return None
    
    def _create_architecture_script(self, diagram_files: List[Path]) -> Dict[str, Any]:
        """Create script for architecture tour video"""
        template = self.templates['architecture_tour']
        
        script = {
            'title': 'Architecture Tour',
            'duration': template['duration'],
            'scenes': [
                {
                    'type': 'intro',
                    'duration': 30,
                    'content': 'System architecture introduction',
                    'actions': ['show_main_diagram']
                },
                {
                    'type': 'diagram_tour',
                    'duration': 120,
                    'content': 'Interactive diagram exploration',
                    'actions': ['tour_diagrams']
                },
                {
                    'type': 'integration',
                    'duration': 60,
                    'content': 'Component integration points',
                    'actions': ['highlight_connections']
                },
                {
                    'type': 'conclusion',
                    'duration': 30,
                    'content': 'Architecture summary',
                    'actions': ['show_summary']
                }
            ]
        }
        
        return script
    
    def _generate_animated_gifs(self, screenshots_dir: Path) -> List[Path]:
        """Generate animated GIFs from screenshots"""
        gifs = []
        
        if not self.tools_available.get('ffmpeg'):
            return gifs
        
        try:
            # Group screenshots by type
            screenshot_groups = self._group_screenshots(screenshots_dir)
            
            for group_name, image_files in screenshot_groups.items():
                if len(image_files) > 1:  # Need multiple images for animation
                    gif_path = self._create_animated_gif(image_files, group_name)
                    if gif_path:
                        gifs.append(gif_path)
            
        except Exception as e:
            logger.error(f"Failed to generate animated GIFs: {e}")
        
        return gifs
    
    def _group_screenshots(self, screenshots_dir: Path) -> Dict[str, List[Path]]:
        """Group screenshots by prefix/type"""
        groups = {}
        
        for img_file in screenshots_dir.glob("*.png"):
            # Extract base name (before size suffix)
            base_name = img_file.stem
            
            # Remove size suffixes like _mobile, _tablet
            for suffix in ['_mobile', '_tablet', '_desktop']:
                if base_name.endswith(suffix):
                    base_name = base_name[:-len(suffix)]
                    break
            
            if base_name not in groups:
                groups[base_name] = []
            groups[base_name].append(img_file)
        
        # Sort files in each group
        for group in groups.values():
            group.sort()
        
        return groups
    
    def _create_animated_gif(self, image_files: List[Path], name: str) -> Optional[Path]:
        """Create animated GIF from image files"""
        try:
            output_file = self.output_dir / f"{name}_animated.gif"
            
            # Create FFmpeg command for GIF
            cmd = ['ffmpeg']
            
            # Add input files
            for img_file in image_files:
                cmd.extend(['-i', str(img_file)])
            
            # Add filter for GIF creation
            filter_complex = f'concat=n={len(image_files)}:v=1:a=0,fps=2,palettegen[v1];'
            filter_complex += f'concat=n={len(image_files)}:v=1:a=0,fps=2[v2];[v2][v1]paletteuse'
            
            cmd.extend([
                '-filter_complex', filter_complex,
                '-loop', '0',  # Infinite loop
                str(output_file)
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and output_file.exists():
                logger.info(f"Animated GIF created: {output_file}")
                return output_file
            else:
                logger.warning(f"GIF creation failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Animated GIF creation failed: {e}")
            return None
    
    def _generate_simple_videos(self, interactive_docs: Path) -> List[Path]:
        """Generate simple video documentation when advanced tools aren't available"""
        videos = []
        
        # Create simple video templates
        template_videos = [
            self._create_template_video("overview", "Documentation Overview"),
            self._create_template_video("components", "Component Guide"),
            self._create_template_video("architecture", "Architecture Tour")
        ]
        
        videos.extend([v for v in template_videos if v])
        
        return videos
    
    def _create_template_video(self, name: str, title: str) -> Optional[Path]:
        """Create template video file"""
        try:
            template_content = f'''# {title}

This is a placeholder for the {name} video.

## What this video would cover:
- Interactive documentation walkthrough
- Component exploration
- Code examples and usage
- Architecture overview

## Tools needed for full video generation:
- FFmpeg for video compilation
- Playwright or Selenium for screen recording
- Optional: OBS Studio for advanced recording

Generated by Visual Documentation Pipeline
'''
            
            video_file = self.output_dir / f"{name}_template.md"
            with open(video_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            logger.info(f"Created video template: {video_file}")
            return video_file
            
        except Exception as e:
            logger.error(f"Failed to create video template: {e}")
            return None
    
    def generate_video_index(self, video_files: List[Path]) -> Path:
        """Generate index page for all videos"""
        try:
            index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .video-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .video-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; }
        .video-title { font-weight: bold; margin-bottom: 10px; }
        video { width: 100%; border-radius: 4px; }
        .video-info { margin-top: 10px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Video Documentation</h1>
        <p>Interactive video tutorials and walkthroughs for the documentation.</p>
        
        <div class="video-grid">
'''
            
            for video_file in video_files:
                if video_file.suffix in ['.mp4', '.webm']:
                    video_name = video_file.stem.replace('_', ' ').title()
                    relative_path = video_file.name
                    
                    index_html += f'''
            <div class="video-card">
                <div class="video-title">{video_name}</div>
                <video controls>
                    <source src="{relative_path}" type="video/{video_file.suffix[1:]}">
                    Your browser does not support the video tag.
                </video>
                <div class="video-info">
                    Duration: Auto-generated walkthrough
                </div>
            </div>
'''
                elif video_file.suffix == '.gif':
                    video_name = video_file.stem.replace('_', ' ').title()
                    relative_path = video_file.name
                    
                    index_html += f'''
            <div class="video-card">
                <div class="video-title">{video_name}</div>
                <img src="{relative_path}" alt="{video_name}" style="width: 100%; border-radius: 4px;">
                <div class="video-info">
                    Animated demonstration
                </div>
            </div>
'''
            
            index_html += '''
        </div>
    </div>
</body>
</html>'''
            
            index_file = self.output_dir / "index.html"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_html)
            
            logger.info(f"Generated video index: {index_file}")
            return index_file
            
        except Exception as e:
            logger.error(f"Failed to generate video index: {e}")
            return self.output_dir / "index_error.html"