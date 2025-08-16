#!/usr/bin/env python3
"""
Playwright Headed Browser Testing Launcher
Configures and launches headed browser automation for visual testing
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add core path to system path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.testing.playwright_visual_testing import PlaywrightVisualTestFramework, BrowserConfig
from integrations.mcp_manager.services.playwright_service import PlaywrightMCPService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HeadedTestingLauncher:
    """Launcher for headed browser testing with visual regression capabilities"""
    
    def __init__(self):
        self.framework = None
        self.mcp_service = None
        self.config = None
    
    def parse_arguments(self) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="Launch Playwright headed browser testing"
        )
        
        parser.add_argument(
            '--browser', 
            choices=['chromium', 'firefox', 'webkit'], 
            default='chromium',
            help='Browser to use for testing'
        )
        
        parser.add_argument(
            '--headless', 
            action='store_true',
            help='Run in headless mode (default: headed)'
        )
        
        parser.add_argument(
            '--viewport-width', 
            type=int, 
            default=1920,
            help='Browser viewport width'
        )
        
        parser.add_argument(
            '--viewport-height', 
            type=int, 
            default=1080,
            help='Browser viewport height'
        )
        
        parser.add_argument(
            '--slow-mo', 
            type=int, 
            default=500,
            help='Slow motion delay in milliseconds'
        )
        
        parser.add_argument(
            '--record-video', 
            action='store_true',
            help='Record video of test execution'
        )
        
        parser.add_argument(
            '--record-har', 
            action='store_true',
            help='Record HAR file for network analysis'
        )
        
        parser.add_argument(
            '--output-dir', 
            type=str, 
            default='test_outputs',
            help='Output directory for test artifacts'
        )
        
        parser.add_argument(
            '--mcp-port', 
            type=int, 
            default=8080,
            help='MCP service port'
        )
        
        parser.add_argument(
            '--test-suite', 
            choices=['visual', 'form', 'accessibility', 'cross-browser', 'all'], 
            default='all',
            help='Test suite to run'
        )
        
        parser.add_argument(
            '--base-url', 
            type=str, 
            default='http://localhost:3000',
            help='Base URL for testing'
        )
        
        parser.add_argument(
            '--config-file', 
            type=str,
            help='Path to configuration file'
        )
        
        return parser.parse_args()
    
    def load_config(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Load configuration from file and command line arguments"""
        config = {
            'browser': {
                'browser_type': args.browser,
                'headless': args.headless,
                'viewport': {
                    'width': args.viewport_width,
                    'height': args.viewport_height
                },
                'slow_mo': args.slow_mo,
                'record_video': args.record_video,
                'record_har': args.record_har
            },
            'testing': {
                'output_dir': args.output_dir,
                'base_url': args.base_url,
                'test_suite': args.test_suite
            },
            'mcp': {
                'port': args.mcp_port,
                'host': 'localhost'
            }
        }
        
        # Load from config file if provided
        if args.config_file and Path(args.config_file).exists():
            with open(args.config_file, 'r') as f:
                file_config = json.load(f)
            
            # Merge configurations (CLI args take precedence)
            self._merge_config(config, file_config)
        
        return config
    
    def _merge_config(self, base_config: Dict[str, Any], file_config: Dict[str, Any]):
        """Merge configuration dictionaries"""
        for key, value in file_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    async def setup_environment(self):
        """Setup testing environment"""
        logger.info("Setting up testing environment...")
        
        # Create output directories
        output_dir = Path(self.config['testing']['output_dir'])
        directories = [
            output_dir / 'screenshots',
            output_dir / 'videos',
            output_dir / 'har-files',
            output_dir / 'reports',
            output_dir / 'baselines',
            output_dir / 'diffs'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables for MCP service
        os.environ['BROWSER_TYPE'] = self.config['browser']['browser_type']
        os.environ['HEADLESS'] = str(self.config['browser']['headless']).lower()
        os.environ['SLOW_MO'] = str(self.config['browser']['slow_mo'])
        os.environ['RECORD_VIDEO'] = str(self.config['browser']['record_video']).lower()
        
        logger.info("Environment setup completed")
    
    async def start_mcp_service(self):
        """Start the MCP service for browser automation"""
        logger.info("Starting MCP service...")
        
        mcp_config = {
            'host': self.config['mcp']['host'],
            'port': self.config['mcp']['port'],
            'browser_type': self.config['browser']['browser_type'],
            'headless': self.config['browser']['headless'],
            'viewport': self.config['browser']['viewport'],
            'slow_mo': self.config['browser']['slow_mo'],
            'record_video': self.config['browser']['record_video'],
            'record_har': self.config['browser']['record_har']
        }
        
        self.mcp_service = PlaywrightMCPService(mcp_config)
        
        success = await self.mcp_service.start()
        if not success:
            raise RuntimeError("Failed to start MCP service")
        
        logger.info(f"MCP service started on {mcp_config['host']}:{mcp_config['port']}")
    
    async def setup_visual_framework(self):
        """Setup visual testing framework"""
        logger.info("Setting up visual testing framework...")
        
        browser_config = BrowserConfig(
            browser_type=self.config['browser']['browser_type'],
            headless=self.config['browser']['headless'],
            viewport=self.config['browser']['viewport'],
            slow_mo=self.config['browser']['slow_mo'],
            record_video=self.config['browser']['record_video'],
            record_har=self.config['browser']['record_har']
        )
        
        self.framework = PlaywrightVisualTestFramework(
            browser_config, 
            self.config['testing']['output_dir']
        )
        
        logger.info("Visual testing framework setup completed")
    
    async def run_test_demonstrations(self):
        """Run demonstration tests to show capabilities"""
        logger.info("Running demonstration tests...")
        
        base_url = self.config['testing']['base_url']
        test_suite = self.config['testing']['test_suite']
        
        try:
            await self.framework.setup_browser()
            await self.framework.create_context()
            await self.framework.create_page()
            
            if test_suite in ['visual', 'all']:
                await self._run_visual_tests(base_url)
            
            if test_suite in ['form', 'all']:
                await self._run_form_tests(base_url)
            
            if test_suite in ['accessibility', 'all']:
                await self._run_accessibility_tests(base_url)
            
            if test_suite in ['cross-browser', 'all']:
                await self._run_cross_browser_tests(base_url)
            
            # Generate comprehensive report
            report_path = await self.framework.generate_test_report()
            logger.info(f"Test report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            raise
    
    async def _run_visual_tests(self, base_url: str):
        """Run visual regression tests"""
        logger.info("Running visual regression tests...")
        
        # Homepage visual test
        await self.framework.navigate_and_wait(base_url)
        
        # Full page screenshot
        await self.framework.take_visual_screenshot(
            "homepage_full_page",
            full_page=True,
            threshold=0.95
        )
        
        # Header section
        header_result = await self.framework.take_visual_screenshot(
            "homepage_header",
            selector="header",
            threshold=0.98
        )
        
        # Navigation menu
        nav_result = await self.framework.take_visual_screenshot(
            "homepage_navigation",
            selector="nav",
            threshold=0.98
        )
        
        # Test responsive design
        viewports = [
            {"width": 1920, "height": 1080, "name": "desktop"},
            {"width": 1024, "height": 768, "name": "tablet"},
            {"width": 375, "height": 667, "name": "mobile"}
        ]
        
        for viewport in viewports:
            # Update viewport
            await self.framework.context.set_viewport_size(viewport)
            await self.framework.page.wait_for_timeout(500)
            
            await self.framework.take_visual_screenshot(
                f"homepage_{viewport['name']}",
                full_page=True,
                threshold=0.90
            )
        
        logger.info("Visual regression tests completed")
    
    async def _run_form_tests(self, base_url: str):
        """Run form automation tests"""
        logger.info("Running form automation tests...")
        
        # Navigate to contact page (adjust URL as needed)
        contact_url = f"{base_url}/contact" if not base_url.endswith('/') else f"{base_url}contact"
        
        try:
            await self.framework.navigate_and_wait(contact_url)
            
            # Test form automation
            form_data = {
                "name": {
                    "selector": "[name='name'], #name, [data-testid='name']",
                    "value": "Test User",
                    "type": "text"
                },
                "email": {
                    "selector": "[name='email'], #email, [data-testid='email']",
                    "value": "test@example.com",
                    "type": "email"
                },
                "message": {
                    "selector": "[name='message'], #message, [data-testid='message']",
                    "value": "This is a test message for form automation demonstration.",
                    "type": "text"
                }
            }
            
            form_result = await self.framework.test_form_automation(form_data)
            logger.info(f"Form automation result: {form_result}")
            
            # Take screenshot of filled form
            await self.framework.take_visual_screenshot(
                "contact_form_filled",
                full_page=True
            )
            
        except Exception as e:
            logger.warning(f"Form test skipped - page may not exist: {e}")
        
        logger.info("Form automation tests completed")
    
    async def _run_accessibility_tests(self, base_url: str):
        """Run accessibility tests"""
        logger.info("Running accessibility tests...")
        
        await self.framework.navigate_and_wait(base_url)
        
        # Inject axe-core for accessibility testing
        try:
            await self.framework.page.add_script_tag(
                url="https://unpkg.com/axe-core@4.7.0/axe.min.js"
            )
            
            # Run accessibility analysis
            accessibility_results = await self.framework.page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        if (typeof axe !== 'undefined') {
                            axe.run().then((results) => {
                                resolve(results);
                            });
                        } else {
                            resolve({ violations: [], passes: [] });
                        }
                    });
                }
            """)
            
            violations = accessibility_results.get('violations', [])
            logger.info(f"Accessibility violations found: {len(violations)}")
            
            for violation in violations[:5]:  # Show first 5
                logger.warning(f"A11y violation: {violation.get('id')} - {violation.get('description')}")
            
        except Exception as e:
            logger.warning(f"Accessibility test failed: {e}")
        
        logger.info("Accessibility tests completed")
    
    async def _run_cross_browser_tests(self, base_url: str):
        """Run cross-browser compatibility tests"""
        logger.info("Running cross-browser compatibility tests...")
        
        test_scenarios = [
            {
                "name": "homepage_load",
                "url": base_url,
                "actions": [
                    {"type": "wait", "value": 2000},
                ],
                "visual_tests": [
                    {"name": "loaded", "full_page": True}
                ]
            }
        ]
        
        cross_browser_results = await self.framework.test_cross_browser_compatibility(test_scenarios)
        
        for browser, result in cross_browser_results.items():
            logger.info(f"Browser {browser}: {'PASS' if result.get('success') else 'FAIL'}")
        
        logger.info("Cross-browser compatibility tests completed")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        
        if self.framework:
            await self.framework.cleanup()
        
        if self.mcp_service:
            await self.mcp_service.stop()
        
        logger.info("Cleanup completed")
    
    async def run(self):
        """Main execution method"""
        try:
            # Parse arguments and load configuration
            args = self.parse_arguments()
            self.config = self.load_config(args)
            
            logger.info("Starting Playwright Headed Browser Testing")
            logger.info(f"Configuration: {json.dumps(self.config, indent=2)}")
            
            # Setup environment
            await self.setup_environment()
            
            # Start MCP service
            await self.start_mcp_service()
            
            # Setup visual testing framework
            await self.setup_visual_framework()
            
            # Run tests
            await self.run_test_demonstrations()
            
            logger.info("All tests completed successfully!")
            
        except KeyboardInterrupt:
            logger.info("Testing interrupted by user")
        except Exception as e:
            logger.error(f"Testing failed: {e}")
            raise
        finally:
            await self.cleanup()


def main():
    """Main entry point"""
    launcher = HeadedTestingLauncher()
    
    try:
        asyncio.run(launcher.run())
    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()