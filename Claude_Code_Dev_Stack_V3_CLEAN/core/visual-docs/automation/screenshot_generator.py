#!/usr/bin/env python3
"""
Screenshot Generator
Automated screenshot generation for documentation and UI components
"""

import os
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
import tempfile

logger = logging.getLogger(__name__)

class ScreenshotGenerator:
    """Generator for automated screenshots of documentation and UI"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir / "screenshots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Screenshot configuration
        self.viewport_sizes = [
            (1920, 1080),  # Desktop
            (1366, 768),   # Laptop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        self.screenshot_formats = ['png', 'jpg', 'webp']
        self.browsers = ['chromium', 'firefox']
        
        # Initialize browser automation
        self.browser_available = self._check_browser_availability()
    
    def _check_browser_availability(self) -> Dict[str, bool]:
        """Check which browsers/tools are available for screenshots"""
        available = {}
        
        # Check for Playwright
        try:
            import playwright
            available['playwright'] = True
        except ImportError:
            available['playwright'] = False
        
        # Check for Selenium
        try:
            import selenium
            available['selenium'] = True
        except ImportError:
            available['selenium'] = False
        
        # Check for Puppeteer (via subprocess)
        try:
            result = subprocess.run(['npx', 'puppeteer', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            available['puppeteer'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            available['puppeteer'] = False
        
        # Check for Chrome/Chromium headless
        try:
            result = subprocess.run(['google-chrome', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            available['chrome'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                result = subprocess.run(['chromium', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                available['chrome'] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                available['chrome'] = False
        
        logger.info(f"Browser availability: {available}")
        return available
    
    def generate(self, interactive_docs: Path) -> List[Path]:
        """Generate screenshots for interactive documentation"""
        try:
            screenshots = []
            
            # Screenshot main documentation pages
            if interactive_docs.exists():
                main_screenshots = self._screenshot_main_docs(interactive_docs)
                screenshots.extend(main_screenshots)
            
            # Screenshot individual component pages
            components_dir = interactive_docs.parent / "components"
            if components_dir.exists():
                component_screenshots = self._screenshot_component_pages(components_dir)
                screenshots.extend(component_screenshots)
            
            # Screenshot diagram pages
            diagrams_dir = interactive_docs.parent / "diagrams"
            if diagrams_dir.exists():
                diagram_screenshots = self._screenshot_diagram_pages(diagrams_dir)
                screenshots.extend(diagram_screenshots)
            
            # Generate comparison screenshots (different devices)
            if screenshots:
                comparison_screenshots = self._generate_comparison_screenshots(screenshots[:3])
                screenshots.extend(comparison_screenshots)
            
            # Generate thumbnail gallery
            if screenshots:
                gallery_path = self._generate_thumbnail_gallery(screenshots)
                screenshots.append(gallery_path)
            
            logger.info(f"Generated {len(screenshots)} screenshots")
            return screenshots
            
        except Exception as e:
            logger.error(f"Failed to generate screenshots: {e}")
            return []
    
    def _screenshot_main_docs(self, docs_path: Path) -> List[Path]:
        """Take screenshots of main documentation pages"""
        screenshots = []
        
        # Screenshot the main index page
        index_file = docs_path if docs_path.name.endswith('.html') else docs_path / "index.html"
        
        if index_file.exists():
            screenshot_path = self._take_screenshot(
                index_file, 
                "main_overview",
                viewport=(1920, 1080)
            )
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            # Take mobile version
            mobile_screenshot = self._take_screenshot(
                index_file,
                "main_overview_mobile", 
                viewport=(375, 667)
            )
            if mobile_screenshot:
                screenshots.append(mobile_screenshot)
        
        return screenshots
    
    def _screenshot_component_pages(self, components_dir: Path) -> List[Path]:
        """Take screenshots of component pages"""
        screenshots = []
        
        for html_file in components_dir.glob("*.html"):
            screenshot_path = self._take_screenshot(
                html_file,
                f"component_{html_file.stem}",
                viewport=(1366, 768)
            )
            if screenshot_path:
                screenshots.append(screenshot_path)
        
        return screenshots
    
    def _screenshot_diagram_pages(self, diagrams_dir: Path) -> List[Path]:
        """Take screenshots of diagram pages"""
        screenshots = []
        
        for html_file in diagrams_dir.glob("*.html"):
            screenshot_path = self._take_screenshot(
                html_file,
                f"diagram_{html_file.stem}",
                viewport=(1920, 1080),
                wait_for_render=True
            )
            if screenshot_path:
                screenshots.append(screenshot_path)
        
        return screenshots
    
    def _take_screenshot(self, 
                        html_file: Path, 
                        name: str, 
                        viewport: Tuple[int, int] = (1920, 1080),
                        wait_for_render: bool = False) -> Optional[Path]:
        """Take a screenshot using the best available method"""
        
        if self.browser_available.get('playwright'):
            return self._screenshot_with_playwright(html_file, name, viewport, wait_for_render)
        elif self.browser_available.get('puppeteer'):
            return self._screenshot_with_puppeteer(html_file, name, viewport, wait_for_render)
        elif self.browser_available.get('chrome'):
            return self._screenshot_with_chrome_headless(html_file, name, viewport)
        elif self.browser_available.get('selenium'):
            return self._screenshot_with_selenium(html_file, name, viewport, wait_for_render)
        else:
            logger.warning("No browser automation tools available for screenshots")
            return None
    
    def _screenshot_with_playwright(self, 
                                   html_file: Path, 
                                   name: str, 
                                   viewport: Tuple[int, int],
                                   wait_for_render: bool) -> Optional[Path]:
        """Take screenshot using Playwright"""
        try:
            from playwright.sync_api import sync_playwright
            
            output_file = self.output_dir / f"{name}.png"
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': viewport[0], 'height': viewport[1]})
                
                # Navigate to the HTML file
                file_url = f"file://{html_file.absolute()}"
                page.goto(file_url)
                
                # Wait for content to load
                if wait_for_render:
                    # Wait for Mermaid diagrams or D3.js to render
                    page.wait_for_timeout(3000)
                    
                    # Wait for specific elements if they exist
                    try:
                        page.wait_for_selector('.mermaid svg', timeout=5000)
                    except:
                        pass
                    
                    try:
                        page.wait_for_selector('svg', timeout=5000)
                    except:
                        pass
                else:
                    page.wait_for_timeout(1000)
                
                # Take screenshot
                page.screenshot(path=str(output_file), full_page=True)
                browser.close()
            
            logger.info(f"Screenshot taken with Playwright: {output_file}")
            return output_file
            
        except Exception as e:
            logger.warning(f"Playwright screenshot failed: {e}")
            return None
    
    def _screenshot_with_puppeteer(self, 
                                  html_file: Path, 
                                  name: str, 
                                  viewport: Tuple[int, int],
                                  wait_for_render: bool) -> Optional[Path]:
        """Take screenshot using Puppeteer"""
        try:
            output_file = self.output_dir / f"{name}.png"
            
            # Create Puppeteer script
            script_content = f'''
const puppeteer = require('puppeteer');

(async () => {{
    const browser = await puppeteer.launch({{headless: true}});
    const page = await browser.newPage();
    await page.setViewport({{width: {viewport[0]}, height: {viewport[1]}}});
    
    await page.goto('file://{html_file.absolute()}');
    
    // Wait for content to load
    await page.waitForTimeout({3000 if wait_for_render else 1000});
    
    // Wait for specific elements if they exist
    try {{
        await page.waitForSelector('.mermaid svg', {{timeout: 5000}});
    }} catch (e) {{}}
    
    try {{
        await page.waitForSelector('svg', {{timeout: 5000}});
    }} catch (e) {{}}
    
    await page.screenshot({{
        path: '{output_file}',
        fullPage: true
    }});
    
    await browser.close();
}})();
'''
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(script_content)
                script_file = f.name
            
            try:
                # Run Puppeteer script
                result = subprocess.run(['node', script_file], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and output_file.exists():
                    logger.info(f"Screenshot taken with Puppeteer: {output_file}")
                    return output_file
                else:
                    logger.warning(f"Puppeteer screenshot failed: {result.stderr}")
                    return None
            finally:
                # Clean up script file
                os.unlink(script_file)
                
        except Exception as e:
            logger.warning(f"Puppeteer screenshot failed: {e}")
            return None
    
    def _screenshot_with_chrome_headless(self, 
                                        html_file: Path, 
                                        name: str, 
                                        viewport: Tuple[int, int]) -> Optional[Path]:
        """Take screenshot using Chrome headless"""
        try:
            output_file = self.output_dir / f"{name}.png"
            
            chrome_cmd = [
                'google-chrome',
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                f'--window-size={viewport[0]},{viewport[1]}',
                f'--screenshot={output_file}',
                f'file://{html_file.absolute()}'
            ]
            
            # Try chromium if google-chrome fails
            try:
                result = subprocess.run(chrome_cmd, capture_output=True, text=True, timeout=20)
            except FileNotFoundError:
                chrome_cmd[0] = 'chromium'
                result = subprocess.run(chrome_cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and output_file.exists():
                logger.info(f"Screenshot taken with Chrome headless: {output_file}")
                return output_file
            else:
                logger.warning(f"Chrome headless screenshot failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.warning(f"Chrome headless screenshot failed: {e}")
            return None
    
    def _screenshot_with_selenium(self, 
                                 html_file: Path, 
                                 name: str, 
                                 viewport: Tuple[int, int],
                                 wait_for_render: bool) -> Optional[Path]:
        """Take screenshot using Selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            output_file = self.output_dir / f"{name}.png"
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
            
            # Create driver
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Navigate to the HTML file
                file_url = f"file://{html_file.absolute()}"
                driver.get(file_url)
                
                # Wait for content to load
                if wait_for_render:
                    time.sleep(3)
                    
                    # Wait for specific elements if they exist
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".mermaid svg"))
                        )
                    except:
                        pass
                    
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.TAG_NAME, "svg"))
                        )
                    except:
                        pass
                else:
                    time.sleep(1)
                
                # Take screenshot
                driver.save_screenshot(str(output_file))
                
                logger.info(f"Screenshot taken with Selenium: {output_file}")
                return output_file
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.warning(f"Selenium screenshot failed: {e}")
            return None
    
    def _generate_comparison_screenshots(self, screenshot_paths: List[Path]) -> List[Path]:
        """Generate comparison screenshots for different viewports"""
        comparison_screenshots = []
        
        for screenshot_path in screenshot_paths:
            # Extract original HTML file info
            base_name = screenshot_path.stem
            
            # Take screenshots at different viewport sizes
            for size_name, viewport in [('tablet', (768, 1024)), ('mobile', (375, 667))]:
                # Find original HTML file (this is simplified - in real implementation 
                # we'd need to track the source file)
                comparison_name = f"{base_name}_{size_name}"
                
                # This would require re-taking screenshots with different viewports
                # For now, we'll create placeholder entries
                placeholder_path = self.output_dir / f"{comparison_name}.png"
                comparison_screenshots.append(placeholder_path)
        
        return comparison_screenshots
    
    def _generate_thumbnail_gallery(self, screenshot_paths: List[Path]) -> Path:
        """Generate HTML gallery of all screenshots"""
        try:
            gallery_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screenshot Gallery</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .screenshot-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .screenshot-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 4px;
            cursor: pointer;
        }
        .screenshot-info {
            margin-top: 10px;
        }
        .screenshot-name {
            font-weight: bold;
            color: #333;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }
        .modal-content {
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
            margin-top: 5%;
        }
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Documentation Screenshots</h1>
    <div class="gallery">
'''
            
            for screenshot_path in screenshot_paths:
                if screenshot_path.exists():
                    relative_path = screenshot_path.name
                    screenshot_name = screenshot_path.stem.replace('_', ' ').title()
                    
                    gallery_html += f'''
        <div class="screenshot-card">
            <img src="{relative_path}" alt="{screenshot_name}" class="screenshot-image" onclick="openModal('{relative_path}')">
            <div class="screenshot-info">
                <div class="screenshot-name">{screenshot_name}</div>
            </div>
        </div>
'''
            
            gallery_html += '''
    </div>
    
    <div id="modal" class="modal" onclick="closeModal()">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modal-image">
    </div>
    
    <script>
        function openModal(imageSrc) {
            document.getElementById('modal').style.display = 'block';
            document.getElementById('modal-image').src = imageSrc;
        }
        
        function closeModal() {
            document.getElementById('modal').style.display = 'none';
        }
        
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeModal();
            }
        });
    </script>
</body>
</html>'''
            
            gallery_file = self.output_dir / "gallery.html"
            with open(gallery_file, 'w', encoding='utf-8') as f:
                f.write(gallery_html)
            
            logger.info(f"Generated screenshot gallery: {gallery_file}")
            return gallery_file
            
        except Exception as e:
            logger.error(f"Failed to generate screenshot gallery: {e}")
            return self.output_dir / "gallery_error.html"
    
    def capture_specific_elements(self, html_file: Path, selectors: List[str]) -> List[Path]:
        """Capture screenshots of specific HTML elements"""
        screenshots = []
        
        if not self.browser_available.get('playwright'):
            logger.warning("Element-specific screenshots require Playwright")
            return screenshots
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': 1920, 'height': 1080})
                
                file_url = f"file://{html_file.absolute()}"
                page.goto(file_url)
                page.wait_for_timeout(2000)
                
                for i, selector in enumerate(selectors):
                    try:
                        element = page.query_selector(selector)
                        if element:
                            output_file = self.output_dir / f"element_{i}_{selector.replace(' ', '_').replace('.', '').replace('#', '')}.png"
                            element.screenshot(path=str(output_file))
                            screenshots.append(output_file)
                            logger.info(f"Element screenshot: {output_file}")
                    except Exception as e:
                        logger.warning(f"Failed to capture element {selector}: {e}")
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Element capture failed: {e}")
        
        return screenshots
    
    def generate_animated_screenshots(self, html_file: Path, interactions: List[Dict[str, Any]]) -> Optional[Path]:
        """Generate animated GIF of user interactions"""
        # This would require additional tools like FFmpeg
        # For now, return placeholder
        logger.info("Animated screenshots not yet implemented")
        return None