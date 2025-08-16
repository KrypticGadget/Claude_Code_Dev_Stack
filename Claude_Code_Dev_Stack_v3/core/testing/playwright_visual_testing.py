#!/usr/bin/env python3
"""
Advanced Playwright Visual Testing Framework
Headed browser automation with visual regression testing, screenshot capture, and form automation
"""

import asyncio
import json
import logging
import base64
import hashlib
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import os

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Locator
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytest
from skimage.metrics import structural_similarity as ssim

logger = logging.getLogger(__name__)

@dataclass
class VisualTestResult:
    """Visual test result data structure"""
    test_name: str
    baseline_path: str
    current_path: str
    diff_path: Optional[str]
    similarity_score: float
    threshold: float
    passed: bool
    timestamp: datetime
    browser_info: Dict[str, Any]
    viewport_size: Tuple[int, int]
    pixel_diff_count: int = 0
    total_pixels: int = 0

@dataclass
class BrowserConfig:
    """Browser configuration for headed automation"""
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = False
    viewport: Dict[str, int] = None
    user_agent: str = None
    timezone: str = None
    locale: str = "en-US"
    permissions: List[str] = None
    device_scale_factor: float = 1.0
    record_video: bool = False
    record_har: bool = False
    slow_mo: int = 0  # milliseconds delay between actions

    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}
        if self.permissions is None:
            self.permissions = []

class PlaywrightVisualTestFramework:
    """Advanced Playwright testing framework with visual regression capabilities"""
    
    def __init__(self, config: BrowserConfig = None, output_dir: str = None):
        self.config = config or BrowserConfig()
        self.output_dir = Path(output_dir) if output_dir else Path("test_outputs")
        self.baseline_dir = self.output_dir / "baselines"
        self.current_dir = self.output_dir / "current"
        self.diff_dir = self.output_dir / "diffs"
        self.reports_dir = self.output_dir / "reports"
        
        # Ensure directories exist
        for directory in [self.baseline_dir, self.current_dir, self.diff_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.test_results: List[VisualTestResult] = []
        
        # Visual testing settings
        self.default_threshold = 0.95  # Similarity threshold
        self.pixel_threshold = 0.1  # Pixel difference threshold
        
    async def setup_browser(self, browser_type: str = None) -> Browser:
        """Setup browser instance with configuration"""
        browser_type = browser_type or self.config.browser_type
        
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        browser_launcher = getattr(self.playwright, browser_type)
        
        launch_options = {
            "headless": self.config.headless,
            "slow_mo": self.config.slow_mo,
            "devtools": not self.config.headless,  # Enable devtools in headed mode
        }
        
        # Add video recording if enabled
        if self.config.record_video:
            launch_options["record_video_dir"] = str(self.output_dir / "videos")
        
        self.browser = await browser_launcher.launch(**launch_options)
        logger.info(f"Started {browser_type} browser (headless={self.config.headless})")
        
        return self.browser
    
    async def create_context(self, context_options: Dict[str, Any] = None) -> BrowserContext:
        """Create browser context with configuration"""
        if not self.browser:
            await self.setup_browser()
        
        options = {
            "viewport": self.config.viewport,
            "user_agent": self.config.user_agent,
            "timezone_id": self.config.timezone,
            "locale": self.config.locale,
            "permissions": self.config.permissions,
            "device_scale_factor": self.config.device_scale_factor,
        }
        
        # Add HAR recording if enabled
        if self.config.record_har:
            options["record_har_path"] = str(self.output_dir / "network.har")
        
        # Merge with custom options
        if context_options:
            options.update(context_options)
        
        # Remove None values
        options = {k: v for k, v in options.items() if v is not None}
        
        self.context = await self.browser.new_context(**options)
        
        # Enable request/response logging in headed mode
        if not self.config.headless:
            self.context.on("request", self._log_request)
            self.context.on("response", self._log_response)
        
        return self.context
    
    async def create_page(self) -> Page:
        """Create a new page"""
        if not self.context:
            await self.create_context()
        
        self.page = await self.context.new_page()
        
        # Set up page event handlers
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_page_error)
        
        return self.page
    
    def _log_request(self, request):
        """Log HTTP requests in headed mode"""
        if not self.config.headless:
            logger.debug(f"Request: {request.method} {request.url}")
    
    def _log_response(self, response):
        """Log HTTP responses in headed mode"""
        if not self.config.headless:
            logger.debug(f"Response: {response.status} {response.url}")
    
    def _handle_console(self, msg):
        """Handle browser console messages"""
        logger.info(f"Browser console [{msg.type}]: {msg.text}")
    
    def _handle_page_error(self, error):
        """Handle page errors"""
        logger.error(f"Page error: {error}")
    
    async def navigate_and_wait(self, url: str, wait_for: str = "networkidle") -> None:
        """Navigate to URL and wait for page load"""
        if not self.page:
            await self.create_page()
        
        await self.page.goto(url, wait_until=wait_for)
        logger.info(f"Navigated to: {url}")
    
    async def take_visual_screenshot(self, 
                                   test_name: str, 
                                   selector: str = None,
                                   full_page: bool = True,
                                   mask_selectors: List[str] = None,
                                   threshold: float = None) -> VisualTestResult:
        """Take screenshot and perform visual comparison"""
        threshold = threshold or self.default_threshold
        timestamp = datetime.now()
        
        # Generate screenshot filename
        safe_name = "".join(c for c in test_name if c.isalnum() or c in ('-', '_')).rstrip()
        screenshot_name = f"{safe_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
        
        current_path = self.current_dir / screenshot_name
        baseline_path = self.baseline_dir / f"{safe_name}_baseline.png"
        
        # Screenshot options
        screenshot_options = {
            "path": str(current_path),
            "full_page": full_page,
        }
        
        # Mask dynamic elements if specified
        if mask_selectors:
            await self._mask_elements(mask_selectors)
        
        # Take screenshot
        if selector:
            element = self.page.locator(selector)
            await element.screenshot(**screenshot_options)
        else:
            await self.page.screenshot(**screenshot_options)
        
        logger.info(f"Screenshot captured: {current_path}")
        
        # Perform visual comparison
        similarity_score = 1.0
        diff_path = None
        pixel_diff_count = 0
        total_pixels = 0
        passed = True
        
        if baseline_path.exists():
            similarity_score, diff_path, pixel_diff_count, total_pixels = await self._compare_images(
                baseline_path, current_path, test_name
            )
            passed = similarity_score >= threshold
            
            if not passed:
                logger.warning(f"Visual test failed: {test_name} (similarity: {similarity_score:.3f}, threshold: {threshold})")
            else:
                logger.info(f"Visual test passed: {test_name} (similarity: {similarity_score:.3f})")
        else:
            # First run - create baseline
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.replace(baseline_path)
            logger.info(f"Created baseline image: {baseline_path}")
        
        # Get browser info
        browser_info = {
            "name": self.browser.browser_type.name,
            "version": self.browser.version,
            "user_agent": await self.page.evaluate("navigator.userAgent"),
        }
        
        # Create test result
        result = VisualTestResult(
            test_name=test_name,
            baseline_path=str(baseline_path),
            current_path=str(current_path),
            diff_path=diff_path,
            similarity_score=similarity_score,
            threshold=threshold,
            passed=passed,
            timestamp=timestamp,
            browser_info=browser_info,
            viewport_size=(self.config.viewport["width"], self.config.viewport["height"]),
            pixel_diff_count=pixel_diff_count,
            total_pixels=total_pixels
        )
        
        self.test_results.append(result)
        return result
    
    async def _mask_elements(self, selectors: List[str]):
        """Mask dynamic elements before screenshot"""
        mask_script = """
        (selectors) => {
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    el.style.visibility = 'hidden';
                });
            });
        }
        """
        await self.page.evaluate(mask_script, selectors)
    
    async def _compare_images(self, baseline_path: Path, current_path: Path, test_name: str) -> Tuple[float, Optional[str], int, int]:
        """Compare two images and return similarity score"""
        try:
            # Load images
            baseline_img = cv2.imread(str(baseline_path))
            current_img = cv2.imread(str(current_path))
            
            if baseline_img is None or current_img is None:
                logger.error(f"Failed to load images for comparison: {test_name}")
                return 0.0, None, 0, 0
            
            # Resize images to same dimensions if needed
            if baseline_img.shape != current_img.shape:
                height, width = baseline_img.shape[:2]
                current_img = cv2.resize(current_img, (width, height))
            
            # Convert to grayscale for comparison
            baseline_gray = cv2.cvtColor(baseline_img, cv2.COLOR_BGR2GRAY)
            current_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity
            similarity_score, diff = ssim(baseline_gray, current_gray, full=True)
            
            # Calculate pixel differences
            pixel_diff = np.abs(baseline_gray.astype(float) - current_gray.astype(float))
            pixel_diff_count = np.sum(pixel_diff > self.pixel_threshold * 255)
            total_pixels = baseline_gray.size
            
            # Generate diff image if similarity is below threshold
            diff_path = None
            if similarity_score < self.default_threshold:
                diff_path = await self._generate_diff_image(
                    baseline_img, current_img, diff, test_name
                )
            
            return similarity_score, diff_path, int(pixel_diff_count), int(total_pixels)
            
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            return 0.0, None, 0, 0
    
    async def _generate_diff_image(self, baseline_img, current_img, diff, test_name: str) -> str:
        """Generate visual diff image"""
        try:
            # Normalize diff to 0-255 range
            diff_normalized = (diff * 255).astype(np.uint8)
            
            # Create colored diff image
            diff_colored = cv2.applyColorMap(diff_normalized, cv2.COLORMAP_JET)
            
            # Create side-by-side comparison
            height, width = baseline_img.shape[:2]
            comparison_img = np.zeros((height, width * 3, 3), dtype=np.uint8)
            
            # Baseline on left
            comparison_img[:, :width] = baseline_img
            # Current in middle
            comparison_img[:, width:width*2] = current_img
            # Diff on right
            comparison_img[:, width*2:] = diff_colored
            
            # Add labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(comparison_img, "Baseline", (10, 30), font, 1, (255, 255, 255), 2)
            cv2.putText(comparison_img, "Current", (width + 10, 30), font, 1, (255, 255, 255), 2)
            cv2.putText(comparison_img, "Diff", (width * 2 + 10, 30), font, 1, (255, 255, 255), 2)
            
            # Save diff image
            safe_name = "".join(c for c in test_name if c.isalnum() or c in ('-', '_')).rstrip()
            diff_filename = f"{safe_name}_diff.png"
            diff_path = self.diff_dir / diff_filename
            
            cv2.imwrite(str(diff_path), comparison_img)
            logger.info(f"Generated diff image: {diff_path}")
            
            return str(diff_path)
            
        except Exception as e:
            logger.error(f"Error generating diff image: {e}")
            return None
    
    async def test_form_automation(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced form automation with validation"""
        if not self.page:
            await self.create_page()
        
        results = {
            "filled_fields": {},
            "validation_errors": [],
            "form_submitted": False,
            "success": True
        }
        
        try:
            # Fill form fields
            for field_name, field_config in form_data.items():
                try:
                    selector = field_config.get("selector")
                    value = field_config.get("value")
                    field_type = field_config.get("type", "text")
                    
                    if not selector:
                        continue
                    
                    element = self.page.locator(selector)
                    
                    # Wait for element to be ready
                    await element.wait_for(state="visible")
                    
                    if field_type == "text" or field_type == "email" or field_type == "password":
                        await element.fill(str(value))
                    elif field_type == "select":
                        await element.select_option(str(value))
                    elif field_type == "checkbox":
                        if value:
                            await element.check()
                        else:
                            await element.uncheck()
                    elif field_type == "radio":
                        await element.click()
                    elif field_type == "file":
                        await element.set_input_files(str(value))
                    
                    results["filled_fields"][field_name] = {
                        "selector": selector,
                        "value": value,
                        "type": field_type,
                        "success": True
                    }
                    
                    logger.info(f"Filled field {field_name}: {selector}")
                    
                except Exception as e:
                    error_msg = f"Failed to fill field {field_name}: {e}"
                    logger.error(error_msg)
                    results["validation_errors"].append(error_msg)
                    results["success"] = False
            
            # Submit form if submit selector provided
            submit_selector = form_data.get("submit_selector")
            if submit_selector:
                try:
                    submit_button = self.page.locator(submit_selector)
                    await submit_button.click()
                    
                    # Wait for navigation or response
                    await self.page.wait_for_load_state("networkidle")
                    results["form_submitted"] = True
                    logger.info("Form submitted successfully")
                    
                except Exception as e:
                    error_msg = f"Failed to submit form: {e}"
                    logger.error(error_msg)
                    results["validation_errors"].append(error_msg)
                    results["success"] = False
            
        except Exception as e:
            error_msg = f"Form automation failed: {e}"
            logger.error(error_msg)
            results["validation_errors"].append(error_msg)
            results["success"] = False
        
        return results
    
    async def test_cross_browser_compatibility(self, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test scenarios across multiple browsers"""
        browsers = ["chromium", "firefox", "webkit"]
        results = {}
        
        for browser_name in browsers:
            logger.info(f"Testing with {browser_name}")
            browser_results = []
            
            try:
                # Setup browser
                original_browser_type = self.config.browser_type
                self.config.browser_type = browser_name
                
                await self.cleanup()  # Clean up previous browser
                await self.setup_browser(browser_name)
                await self.create_context()
                await self.create_page()
                
                # Run test scenarios
                for scenario in test_scenarios:
                    scenario_result = await self._run_test_scenario(scenario, browser_name)
                    browser_results.append(scenario_result)
                
                results[browser_name] = {
                    "scenarios": browser_results,
                    "success": all(r["success"] for r in browser_results),
                    "total_scenarios": len(browser_results),
                    "passed_scenarios": sum(1 for r in browser_results if r["success"])
                }
                
                # Restore original browser type
                self.config.browser_type = original_browser_type
                
            except Exception as e:
                logger.error(f"Browser {browser_name} testing failed: {e}")
                results[browser_name] = {
                    "error": str(e),
                    "success": False,
                    "scenarios": []
                }
        
        return results
    
    async def _run_test_scenario(self, scenario: Dict[str, Any], browser_name: str) -> Dict[str, Any]:
        """Run a single test scenario"""
        scenario_name = scenario.get("name", "unnamed_scenario")
        url = scenario.get("url")
        actions = scenario.get("actions", [])
        visual_tests = scenario.get("visual_tests", [])
        
        result = {
            "name": scenario_name,
            "browser": browser_name,
            "success": True,
            "actions_completed": 0,
            "visual_tests_passed": 0,
            "errors": []
        }
        
        try:
            # Navigate to URL
            if url:
                await self.navigate_and_wait(url)
            
            # Execute actions
            for action in actions:
                try:
                    await self._execute_action(action)
                    result["actions_completed"] += 1
                except Exception as e:
                    result["errors"].append(f"Action failed: {e}")
                    result["success"] = False
            
            # Run visual tests
            for visual_test in visual_tests:
                try:
                    test_result = await self.take_visual_screenshot(
                        f"{scenario_name}_{browser_name}_{visual_test.get('name', 'unnamed')}",
                        selector=visual_test.get("selector"),
                        full_page=visual_test.get("full_page", True),
                        threshold=visual_test.get("threshold")
                    )
                    if test_result.passed:
                        result["visual_tests_passed"] += 1
                    else:
                        result["success"] = False
                        result["errors"].append(f"Visual test failed: {test_result.test_name}")
                except Exception as e:
                    result["errors"].append(f"Visual test failed: {e}")
                    result["success"] = False
            
        except Exception as e:
            result["errors"].append(f"Scenario failed: {e}")
            result["success"] = False
        
        return result
    
    async def _execute_action(self, action: Dict[str, Any]):
        """Execute a single action"""
        action_type = action.get("type")
        selector = action.get("selector")
        value = action.get("value")
        
        if action_type == "click":
            await self.page.locator(selector).click()
        elif action_type == "fill":
            await self.page.locator(selector).fill(str(value))
        elif action_type == "select":
            await self.page.locator(selector).select_option(str(value))
        elif action_type == "wait":
            await self.page.wait_for_timeout(int(value))
        elif action_type == "wait_for_selector":
            await self.page.wait_for_selector(selector)
        elif action_type == "scroll":
            await self.page.locator(selector).scroll_into_view_if_needed()
        elif action_type == "hover":
            await self.page.locator(selector).hover()
        elif action_type == "keyboard":
            await self.page.keyboard.press(str(value))
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def generate_test_report(self, output_file: str = None) -> str:
        """Generate comprehensive test report"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_report_{timestamp}.html"
        
        report_path = self.reports_dir / output_file
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        avg_similarity = sum(r.similarity_score for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        # Generate HTML report
        html_content = self._generate_html_report(
            total_tests, passed_tests, failed_tests, avg_similarity
        )
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Test report generated: {report_path}")
        return str(report_path)
    
    def _generate_html_report(self, total_tests: int, passed_tests: int, failed_tests: int, avg_similarity: float) -> str:
        """Generate HTML report content"""
        results_html = ""
        for result in self.test_results:
            status_class = "passed" if result.passed else "failed"
            diff_link = f'<a href="{result.diff_path}" target="_blank">View Diff</a>' if result.diff_path else "N/A"
            
            results_html += f"""
            <tr class="{status_class}">
                <td>{result.test_name}</td>
                <td>{result.similarity_score:.3f}</td>
                <td>{result.threshold:.3f}</td>
                <td>{'PASS' if result.passed else 'FAIL'}</td>
                <td>{result.browser_info['name']}</td>
                <td>{result.viewport_size[0]}x{result.viewport_size[1]}</td>
                <td>{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>
                    <a href="{result.baseline_path}" target="_blank">Baseline</a> | 
                    <a href="{result.current_path}" target="_blank">Current</a> | 
                    {diff_link}
                </td>
            </tr>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Playwright Visual Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Playwright Visual Test Report</h1>
            
            <div class="summary">
                <h2>Test Summary</h2>
                <div class="metric">
                    <strong>Total Tests:</strong> {total_tests}
                </div>
                <div class="metric">
                    <strong>Passed:</strong> {passed_tests}
                </div>
                <div class="metric">
                    <strong>Failed:</strong> {failed_tests}
                </div>
                <div class="metric">
                    <strong>Success Rate:</strong> {(passed_tests/total_tests*100):.1f}% if {total_tests} > 0 else 0
                </div>
                <div class="metric">
                    <strong>Average Similarity:</strong> {avg_similarity:.3f}
                </div>
            </div>
            
            <h2>Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Similarity Score</th>
                        <th>Threshold</th>
                        <th>Status</th>
                        <th>Browser</th>
                        <th>Viewport</th>
                        <th>Timestamp</th>
                        <th>Images</th>
                    </tr>
                </thead>
                <tbody>
                    {results_html}
                </tbody>
            </table>
        </body>
        </html>
        """
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.info("Browser cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Pytest integration
class PlaywrightVisualTestPlugin:
    """Pytest plugin for Playwright visual testing"""
    
    def __init__(self):
        self.framework = None
    
    def pytest_configure(self, config):
        """Configure pytest plugin"""
        # Get configuration from pytest.ini or command line
        browser_config = BrowserConfig(
            browser_type=config.getoption("--browser", "chromium"),
            headless=config.getoption("--headless", False),
        )
        
        output_dir = config.getoption("--output-dir", "test_outputs")
        self.framework = PlaywrightVisualTestFramework(browser_config, output_dir)
    
    def pytest_sessionstart(self, session):
        """Setup browser session"""
        if self.framework:
            asyncio.run(self.framework.setup_browser())
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Cleanup and generate report"""
        if self.framework:
            asyncio.run(self.framework.generate_test_report())
            asyncio.run(self.framework.cleanup())


# Test fixtures
@pytest.fixture
async def visual_test_framework():
    """Pytest fixture for visual testing framework"""
    config = BrowserConfig(headless=False)  # Default to headed mode
    framework = PlaywrightVisualTestFramework(config)
    
    await framework.setup_browser()
    yield framework
    await framework.cleanup()

@pytest.fixture
async def browser_page(visual_test_framework):
    """Pytest fixture for browser page"""
    await visual_test_framework.create_context()
    page = await visual_test_framework.create_page()
    return page


# Example usage and test cases
if __name__ == "__main__":
    async def run_example_tests():
        """Example test suite demonstrating framework capabilities"""
        
        # Setup framework
        config = BrowserConfig(
            browser_type="chromium",
            headless=False,  # Run in headed mode
            viewport={"width": 1920, "height": 1080},
            slow_mo=500  # 500ms delay between actions for demonstration
        )
        
        framework = PlaywrightVisualTestFramework(config, "example_test_outputs")
        
        try:
            await framework.setup_browser()
            await framework.create_context()
            await framework.create_page()
            
            # Test 1: Visual regression on homepage
            await framework.navigate_and_wait("https://example.com")
            await framework.take_visual_screenshot(
                "homepage_full",
                full_page=True,
                threshold=0.95
            )
            
            # Test 2: Form automation
            form_data = {
                "email": {
                    "selector": "#email",
                    "value": "test@example.com",
                    "type": "email"
                },
                "password": {
                    "selector": "#password", 
                    "value": "testpassword",
                    "type": "password"
                },
                "remember": {
                    "selector": "#remember",
                    "value": True,
                    "type": "checkbox"
                },
                "submit_selector": "#submit-btn"
            }
            
            form_result = await framework.test_form_automation(form_data)
            print(f"Form automation result: {form_result}")
            
            # Test 3: Cross-browser compatibility
            test_scenarios = [
                {
                    "name": "basic_navigation",
                    "url": "https://example.com",
                    "actions": [
                        {"type": "wait", "value": 2000},
                        {"type": "scroll", "selector": "body"}
                    ],
                    "visual_tests": [
                        {"name": "after_scroll", "full_page": True}
                    ]
                }
            ]
            
            cross_browser_results = await framework.test_cross_browser_compatibility(test_scenarios)
            print(f"Cross-browser test results: {cross_browser_results}")
            
            # Generate test report
            report_path = await framework.generate_test_report()
            print(f"Test report generated: {report_path}")
            
        finally:
            await framework.cleanup()
    
    # Run example tests
    asyncio.run(run_example_tests())