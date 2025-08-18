#!/usr/bin/env python3
"""
Playwright MCP Service Implementation
Browser automation and testing service integration

Original concept by @qdhenry (MIT License)
Enhanced for Claude Code Dev Stack by DevOps Agent
"""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
import psutil
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from ..core.manager import ServiceInstance, ServiceType, ServiceStatus, ServiceMetrics

logger = logging.getLogger(__name__)


class PlaywrightMCPService:
    """Playwright MCP service implementation with browser automation capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.service_instance: Optional[ServiceInstance] = None
        self.browser: Optional[Browser] = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.playwright_process: Optional[subprocess.Popen] = None
        self.server_process: Optional[subprocess.Popen] = None
        self.running = False
        
        # Configuration
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 8080)
        self.browser_type = self.config.get('browser_type', 'chromium')
        self.headless = self.config.get('headless', True)
        self.server_script = self.config.get('server_script', self._get_default_server_script())
        
        # Initialize service instance
        self._init_service_instance()
    
    def _init_service_instance(self):
        """Initialize the service instance metadata"""
        self.service_instance = ServiceInstance(
            id=f"playwright-mcp-{self.port}",
            name="Playwright MCP Service",
            service_type=ServiceType.PLAYWRIGHT,
            host=self.host,
            port=self.port,
            path="/",
            protocol="http",
            description="Browser automation and testing service using Playwright",
            version="1.0.0",
            tags={"automation", "testing", "browser", "playwright"},
            metadata={
                "browser_type": self.browser_type,
                "headless": self.headless,
                "supported_browsers": ["chromium", "firefox", "webkit"]
            },
            health_check_url=f"http://{self.host}:{self.port}/health"
        )
    
    def _get_default_server_script(self) -> str:
        """Get the default Playwright MCP server script"""
        return '''
#!/usr/bin/env python3
"""
Playwright MCP Server
Provides browser automation capabilities via MCP protocol
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Playwright MCP Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
playwright_instance = None
browser = None
contexts = {}
pages = {}
service_metrics = {
    "requests_total": 0,
    "error_count": 0,
    "browser_sessions": 0,
    "pages_created": 0,
    "start_time": datetime.now()
}

async def startup():
    """Initialize Playwright"""
    global playwright_instance, browser
    try:
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.chromium.launch(headless=True)
        logger.info("Playwright browser started successfully")
    except Exception as e:
        logger.error(f"Failed to start Playwright: {e}")
        raise

async def shutdown():
    """Cleanup Playwright resources"""
    global playwright_instance, browser, contexts, pages
    try:
        # Close all pages
        for page in pages.values():
            await page.close()
        pages.clear()
        
        # Close all contexts
        for context in contexts.values():
            await context.close()
        contexts.clear()
        
        # Close browser
        if browser:
            await browser.close()
        
        # Stop playwright
        if playwright_instance:
            await playwright_instance.stop()
        
        logger.info("Playwright cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

@app.on_event("startup")
async def on_startup():
    await startup()

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - service_metrics["start_time"]).total_seconds()
    return {
        "status": "healthy",
        "service": "playwright-mcp",
        "version": "1.0.0",
        "uptime": uptime,
        "metrics": service_metrics,
        "browser_running": browser is not None
    }

@app.get("/mcp/info")
async def mcp_info():
    """MCP service information"""
    return {
        "id": "playwright-mcp",
        "name": "Playwright MCP Service",
        "type": "playwright",
        "version": "1.0.0",
        "description": "Browser automation and testing service",
        "capabilities": [
            "browser_automation",
            "web_scraping",
            "screenshot_capture",
            "pdf_generation",
            "form_interaction",
            "navigation"
        ]
    }

@app.post("/browser/new-context")
async def create_browser_context(config: Dict[str, Any] = None):
    """Create a new browser context"""
    global browser, contexts
    service_metrics["requests_total"] += 1
    
    try:
        if not browser:
            raise HTTPException(status_code=500, detail="Browser not available")
        
        context_config = config or {}
        context = await browser.new_context(**context_config)
        context_id = f"context_{len(contexts)}"
        contexts[context_id] = context
        
        service_metrics["browser_sessions"] += 1
        
        return {
            "context_id": context_id,
            "status": "created"
        }
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to create browser context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/new-page")
async def create_page(context_id: str = None):
    """Create a new page in a browser context"""
    global browser, contexts, pages
    service_metrics["requests_total"] += 1
    
    try:
        if context_id and context_id in contexts:
            context = contexts[context_id]
        else:
            # Create default context if none specified
            context = await browser.new_context()
            context_id = f"context_{len(contexts)}"
            contexts[context_id] = context
        
        page = await context.new_page()
        page_id = f"page_{len(pages)}"
        pages[page_id] = page
        
        service_metrics["pages_created"] += 1
        
        return {
            "page_id": page_id,
            "context_id": context_id,
            "status": "created"
        }
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to create page: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/page/{page_id}/navigate")
async def navigate_page(page_id: str, url: str, wait_until: str = "load"):
    """Navigate page to URL"""
    service_metrics["requests_total"] += 1
    
    try:
        if page_id not in pages:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page = pages[page_id]
        response = await page.goto(url, wait_until=wait_until)
        
        return {
            "url": page.url,
            "title": await page.title(),
            "status": response.status if response else None
        }
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to navigate page: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/page/{page_id}/screenshot")
async def take_screenshot(page_id: str, options: Dict[str, Any] = None):
    """Take a screenshot of the page"""
    service_metrics["requests_total"] += 1
    
    try:
        if page_id not in pages:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page = pages[page_id]
        screenshot_options = options or {}
        
        screenshot = await page.screenshot(**screenshot_options)
        
        # Convert to base64 for JSON response
        import base64
        screenshot_b64 = base64.b64encode(screenshot).decode()
        
        return {
            "screenshot": screenshot_b64,
            "format": screenshot_options.get("type", "png")
        }
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to take screenshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/page/{page_id}/content")
async def get_page_content(page_id: str):
    """Get page content"""
    service_metrics["requests_total"] += 1
    
    try:
        if page_id not in pages:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page = pages[page_id]
        content = await page.content()
        
        return {
            "content": content,
            "url": page.url,
            "title": await page.title()
        }
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to get page content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/page/{page_id}/evaluate")
async def evaluate_javascript(page_id: str, script: str):
    """Evaluate JavaScript on the page"""
    service_metrics["requests_total"] += 1
    
    try:
        if page_id not in pages:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page = pages[page_id]
        result = await page.evaluate(script)
        
        return {
            "result": result,
            "script": script
        }
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to evaluate JavaScript: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/page/{page_id}/fill")
async def fill_input(page_id: str, selector: str, value: str):
    """Fill an input field"""
    service_metrics["requests_total"] += 1
    
    try:
        if page_id not in pages:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page = pages[page_id]
        await page.fill(selector, value)
        
        return {
            "status": "filled",
            "selector": selector,
            "value": value
        }
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to fill input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/page/{page_id}/click")
async def click_element(page_id: str, selector: str):
    """Click an element"""
    service_metrics["requests_total"] += 1
    
    try:
        if page_id not in pages:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page = pages[page_id]
        await page.click(selector)
        
        return {
            "status": "clicked",
            "selector": selector
        }
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to click element: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/page/{page_id}")
async def close_page(page_id: str):
    """Close a page"""
    service_metrics["requests_total"] += 1
    
    try:
        if page_id not in pages:
            raise HTTPException(status_code=404, detail="Page not found")
        
        page = pages[page_id]
        await page.close()
        del pages[page_id]
        
        return {"status": "closed", "page_id": page_id}
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to close page: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/context/{context_id}")
async def close_context(context_id: str):
    """Close a browser context"""
    service_metrics["requests_total"] += 1
    
    try:
        if context_id not in contexts:
            raise HTTPException(status_code=404, detail="Context not found")
        
        context = contexts[context_id]
        
        # Close all pages in this context
        context_pages = [pid for pid, page in pages.items() if page.context == context]
        for pid in context_pages:
            await pages[pid].close()
            del pages[pid]
        
        await context.close()
        del contexts[context_id]
        
        return {"status": "closed", "context_id": context_id}
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Failed to close context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
'''
    
    async def start(self) -> bool:
        """Start the Playwright MCP service"""
        if self.running:
            logger.warning("Playwright MCP service is already running")
            return True
        
        try:
            logger.info(f"Starting Playwright MCP service on {self.host}:{self.port}")
            
            # Create server script if it doesn't exist
            server_script_path = Path("playwright_mcp_server.py")
            if not server_script_path.exists():
                with open(server_script_path, 'w') as f:
                    f.write(self.server_script)
            
            # Start the server process
            self.server_process = subprocess.Popen([
                "python", str(server_script_path), str(self.port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Check if server is running
            if await self._check_server_health():
                self.running = True
                self.service_instance.status = ServiceStatus.RUNNING
                logger.info("Playwright MCP service started successfully")
                return True
            else:
                logger.error("Playwright MCP service failed to start properly")
                await self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Playwright MCP service: {e}")
            self.service_instance.status = ServiceStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """Stop the Playwright MCP service"""
        if not self.running:
            logger.warning("Playwright MCP service is not running")
            return True
        
        try:
            logger.info("Stopping Playwright MCP service")
            
            # Terminate server process
            if self.server_process:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()
                self.server_process = None
            
            self.running = False
            self.service_instance.status = ServiceStatus.STOPPED
            logger.info("Playwright MCP service stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop Playwright MCP service: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart the Playwright MCP service"""
        logger.info("Restarting Playwright MCP service")
        await self.stop()
        await asyncio.sleep(2)
        return await self.start()
    
    async def _check_server_health(self) -> bool:
        """Check if the server is healthy"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://{self.host}:{self.port}/health")
                return response.status_code == 200
        except:
            return False
    
    async def get_metrics(self) -> ServiceMetrics:
        """Get service metrics"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://{self.host}:{self.port}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    metrics_data = health_data.get("metrics", {})
                    
                    # Update service metrics
                    self.service_instance.metrics.requests_total = metrics_data.get("requests_total", 0)
                    self.service_instance.metrics.error_count = metrics_data.get("error_count", 0)
                    self.service_instance.metrics.uptime = health_data.get("uptime", 0)
                    
                    return self.service_instance.metrics
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
        
        return self.service_instance.metrics
    
    def get_service_instance(self) -> ServiceInstance:
        """Get the service instance"""
        return self.service_instance
    
    # High-level automation methods
    
    async def create_browser_session(self, config: Dict[str, Any] = None) -> str:
        """Create a new browser session (context + page)"""
        try:
            async with httpx.AsyncClient() as client:
                # Create context
                context_response = await client.post(
                    f"http://{self.host}:{self.port}/browser/new-context",
                    json=config or {}
                )
                context_data = context_response.json()
                context_id = context_data["context_id"]
                
                # Create page
                page_response = await client.post(
                    f"http://{self.host}:{self.port}/browser/new-page",
                    json={"context_id": context_id}
                )
                page_data = page_response.json()
                
                return page_data["page_id"]
        except Exception as e:
            logger.error(f"Failed to create browser session: {e}")
            raise
    
    async def navigate_and_screenshot(self, url: str, screenshot_options: Dict[str, Any] = None) -> str:
        """Navigate to URL and take screenshot"""
        try:
            # Create session
            page_id = await self.create_browser_session()
            
            async with httpx.AsyncClient() as client:
                # Navigate
                await client.post(
                    f"http://{self.host}:{self.port}/page/{page_id}/navigate",
                    json={"url": url}
                )
                
                # Take screenshot
                screenshot_response = await client.post(
                    f"http://{self.host}:{self.port}/page/{page_id}/screenshot",
                    json=screenshot_options or {}
                )
                screenshot_data = screenshot_response.json()
                
                # Close page
                await client.delete(f"http://{self.host}:{self.port}/page/{page_id}")
                
                return screenshot_data["screenshot"]
        except Exception as e:
            logger.error(f"Failed to navigate and screenshot: {e}")
            raise
    
    async def extract_page_data(self, url: str, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """Navigate to URL and extract data using selectors"""
        try:
            # Create session
            page_id = await self.create_browser_session()
            
            async with httpx.AsyncClient() as client:
                # Navigate
                nav_response = await client.post(
                    f"http://{self.host}:{self.port}/page/{page_id}/navigate",
                    json={"url": url}
                )
                nav_data = nav_response.json()
                
                # Get page content
                content_response = await client.post(
                    f"http://{self.host}:{self.port}/page/{page_id}/content"
                )
                content_data = content_response.json()
                
                result = {
                    "url": nav_data["url"],
                    "title": nav_data["title"],
                    "content": content_data["content"]
                }
                
                # Extract data using selectors if provided
                if selectors:
                    extracted_data = {}
                    for name, selector in selectors.items():
                        try:
                            eval_response = await client.post(
                                f"http://{self.host}:{self.port}/page/{page_id}/evaluate",
                                json={"script": f"document.querySelector('{selector}')?.textContent || null"}
                            )
                            eval_data = eval_response.json()
                            extracted_data[name] = eval_data["result"]
                        except:
                            extracted_data[name] = None
                    
                    result["extracted_data"] = extracted_data
                
                # Close page
                await client.delete(f"http://{self.host}:{self.port}/page/{page_id}")
                
                return result
        except Exception as e:
            logger.error(f"Failed to extract page data: {e}")
            raise


# Factory function for creating Playwright service instances
def create_playwright_service(config: Dict[str, Any] = None) -> PlaywrightMCPService:
    """Create a new Playwright MCP service instance"""
    return PlaywrightMCPService(config)


# Example usage and testing
if __name__ == "__main__":
    async def test_playwright_service():
        """Test the Playwright MCP service"""
        service = create_playwright_service({
            "host": "localhost",
            "port": 8080,
            "browser_type": "chromium",
            "headless": True
        })
        
        # Start service
        started = await service.start()
        if not started:
            print("Failed to start service")
            return
        
        print("Service started successfully")
        
        try:
            # Wait a bit for service to be ready
            await asyncio.sleep(2)
            
            # Test navigation and screenshot
            screenshot = await service.navigate_and_screenshot("https://example.com")
            print(f"Screenshot captured: {len(screenshot)} bytes")
            
            # Test data extraction
            data = await service.extract_page_data(
                "https://example.com",
                {"title": "h1", "description": "p"}
            )
            print(f"Extracted data: {data}")
            
        finally:
            # Stop service
            await service.stop()
            print("Service stopped")
    
    # Run the test
    asyncio.run(test_playwright_service())