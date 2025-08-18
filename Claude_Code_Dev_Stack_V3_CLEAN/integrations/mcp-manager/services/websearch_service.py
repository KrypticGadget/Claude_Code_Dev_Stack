#!/usr/bin/env python3
"""
WebSearch MCP Service Implementation
Web search and scraping service integration

Original concept by @qdhenry (MIT License)
Enhanced for Claude Code Dev Stack by DevOps Agent
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
import requests

from ..core.manager import ServiceInstance, ServiceType, ServiceStatus, ServiceMetrics

logger = logging.getLogger(__name__)


class WebSearchMCPService:
    """WebSearch MCP service implementation with search and scraping capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.service_instance: Optional[ServiceInstance] = None
        self.server_process: Optional[subprocess.Popen] = None
        self.running = False
        
        # Configuration
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 8082)
        self.search_engines = self.config.get('search_engines', ['duckduckgo', 'bing'])
        self.api_keys = self.config.get('api_keys', {})
        self.server_script = self.config.get('server_script', self._get_default_server_script())
        
        # Initialize service instance
        self._init_service_instance()
    
    def _init_service_instance(self):
        """Initialize the service instance metadata"""
        self.service_instance = ServiceInstance(
            id=f"websearch-mcp-{self.port}",
            name="WebSearch MCP Service",
            service_type=ServiceType.WEBSEARCH,
            host=self.host,
            port=self.port,
            path="/",
            protocol="http",
            description="Web search and scraping service with multiple search engines",
            version="1.0.0",
            tags={"search", "web", "scraping", "data", "extraction"},
            metadata={
                "search_engines": self.search_engines,
                "api_keys_configured": list(self.api_keys.keys()),
                "supported_operations": [
                    "web_search",
                    "page_scraping", 
                    "content_extraction",
                    "link_analysis",
                    "metadata_extraction"
                ]
            },
            health_check_url=f"http://{self.host}:{self.port}/health"
        )
    
    def _get_default_server_script(self) -> str:
        """Get the default WebSearch MCP server script"""
        return '''
#!/usr/bin/env python3
"""
WebSearch MCP Server
Provides web search and scraping capabilities via MCP protocol
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse, quote

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebSearch MCP Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
service_metrics = {
    "requests_total": 0,
    "error_count": 0,
    "searches_performed": 0,
    "pages_scraped": 0,
    "start_time": datetime.now()
}

# User agent for requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - service_metrics["start_time"]).total_seconds()
    return {
        "status": "healthy",
        "service": "websearch-mcp",
        "version": "1.0.0",
        "uptime": uptime,
        "metrics": service_metrics
    }

@app.get("/mcp/info")
async def mcp_info():
    """MCP service information"""
    return {
        "id": "websearch-mcp",
        "name": "WebSearch MCP Service",
        "type": "websearch",
        "version": "1.0.0",
        "description": "Web search and scraping service",
        "capabilities": [
            "web_search",
            "page_scraping",
            "content_extraction",
            "link_analysis",
            "metadata_extraction",
            "multi_engine_search"
        ]
    }

# DuckDuckGo Search Implementation
async def duckduckgo_search(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """Search using DuckDuckGo"""
    try:
        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=30.0
        ) as client:
            # DuckDuckGo instant answer API
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = await client.get("https://api.duckduckgo.com/", params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Add instant answer if available
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", ""),
                    "source": "duckduckgo_instant"
                })
            
            # Add related topics
            for topic in data.get("RelatedTopics", [])[:num_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "source": "duckduckgo_related"
                    })
            
            # If we don't have enough results, try HTML scraping (simplified)
            if len(results) < 3:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                html_response = await client.get(search_url)
                soup = BeautifulSoup(html_response.text, 'html.parser')
                
                for result in soup.find_all('div', class_='result')[:num_results]:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "url": title_elem.get('href', ''),
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                            "source": "duckduckgo_html"
                        })
            
            return results[:num_results]
            
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return []

# Bing Search Implementation (simplified, no API key required)
async def bing_search(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """Search using Bing (HTML scraping)"""
    try:
        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=30.0
        ) as client:
            search_url = f"https://www.bing.com/search?q={quote(query)}"
            response = await client.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Find search results
            for result in soup.find_all('li', class_='b_algo')[:num_results]:
                title_elem = result.find('h2')
                link_elem = title_elem.find('a') if title_elem else None
                snippet_elem = result.find('p') or result.find('div', class_='b_caption')
                
                if link_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "url": link_elem.get('href', ''),
                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                        "source": "bing"
                    })
            
            return results
            
    except Exception as e:
        logger.error(f"Bing search error: {e}")
        return []

@app.get("/search")
async def web_search(
    q: str = Query(..., description="Search query"),
    engine: str = Query("auto", description="Search engine (duckduckgo, bing, auto)"),
    num_results: int = Query(10, description="Number of results"),
    safe: bool = Query(True, description="Safe search")
):
    """Perform web search"""
    service_metrics["requests_total"] += 1
    service_metrics["searches_performed"] += 1
    
    try:
        results = []
        
        if engine == "auto" or engine == "duckduckgo":
            ddg_results = await duckduckgo_search(q, num_results)
            results.extend(ddg_results)
        
        if engine == "auto" or engine == "bing":
            bing_results = await bing_search(q, num_results)
            results.extend(bing_results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in results:
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
        
        # Limit to requested number of results
        unique_results = unique_results[:num_results]
        
        return {
            "query": q,
            "engine": engine,
            "total_results": len(unique_results),
            "results": unique_results,
            "search_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape")
async def scrape_page(request_data: Dict[str, Any]):
    """Scrape a web page"""
    service_metrics["requests_total"] += 1
    service_metrics["pages_scraped"] += 1
    
    try:
        url = request_data["url"]
        include_links = request_data.get("include_links", False)
        include_images = request_data.get("include_images", False)
        selectors = request_data.get("selectors", {})
        
        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=30.0,
            follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Basic page information
            result = {
                "url": str(response.url),
                "status_code": response.status_code,
                "title": soup.title.string.strip() if soup.title else "",
                "content": soup.get_text(strip=True),
                "meta": {}
            }
            
            # Extract meta information
            for meta in soup.find_all('meta'):
                if meta.get('name'):
                    result["meta"][meta.get('name')] = meta.get('content', '')
                elif meta.get('property'):
                    result["meta"][meta.get('property')] = meta.get('content', '')
            
            # Extract links if requested
            if include_links:
                links = []
                for link in soup.find_all('a', href=True):
                    href = urljoin(url, link['href'])
                    links.append({
                        "text": link.get_text(strip=True),
                        "url": href,
                        "title": link.get('title', '')
                    })
                result["links"] = links
            
            # Extract images if requested
            if include_images:
                images = []
                for img in soup.find_all('img', src=True):
                    src = urljoin(url, img['src'])
                    images.append({
                        "src": src,
                        "alt": img.get('alt', ''),
                        "title": img.get('title', '')
                    })
                result["images"] = images
            
            # Extract custom selectors
            if selectors:
                extracted = {}
                for name, selector in selectors.items():
                    try:
                        elements = soup.select(selector)
                        if len(elements) == 1:
                            extracted[name] = elements[0].get_text(strip=True)
                        elif len(elements) > 1:
                            extracted[name] = [elem.get_text(strip=True) for elem in elements]
                        else:
                            extracted[name] = None
                    except Exception as e:
                        logger.warning(f"Selector '{selector}' failed: {e}")
                        extracted[name] = None
                
                result["extracted"] = extracted
            
            return result
            
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Scraping error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-content")
async def extract_content(request_data: Dict[str, Any]):
    """Extract specific content from a webpage"""
    service_metrics["requests_total"] += 1
    
    try:
        url = request_data["url"]
        content_type = request_data.get("content_type", "text")  # text, article, links, images
        
        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=30.0,
            follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = {
                "url": str(response.url),
                "content_type": content_type,
                "extracted_at": datetime.now().isoformat()
            }
            
            if content_type == "text":
                # Extract main text content
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                result["content"] = soup.get_text(strip=True)
                result["word_count"] = len(result["content"].split())
            
            elif content_type == "article":
                # Try to extract main article content
                article_selectors = [
                    'article',
                    '[role="main"]',
                    '.article-content',
                    '.post-content',
                    '.content',
                    'main'
                ]
                
                content = ""
                for selector in article_selectors:
                    article = soup.select_one(selector)
                    if article:
                        content = article.get_text(strip=True)
                        break
                
                if not content:
                    # Fallback to all text
                    content = soup.get_text(strip=True)
                
                result["content"] = content
                result["word_count"] = len(content.split())
            
            elif content_type == "links":
                # Extract all links
                links = []
                for link in soup.find_all('a', href=True):
                    href = urljoin(url, link['href'])
                    links.append({
                        "text": link.get_text(strip=True),
                        "url": href,
                        "domain": urlparse(href).netloc
                    })
                
                result["links"] = links
                result["link_count"] = len(links)
            
            elif content_type == "images":
                # Extract all images
                images = []
                for img in soup.find_all('img', src=True):
                    src = urljoin(url, img['src'])
                    images.append({
                        "src": src,
                        "alt": img.get('alt', ''),
                        "width": img.get('width'),
                        "height": img.get('height')
                    })
                
                result["images"] = images
                result["image_count"] = len(images)
            
            return result
            
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Content extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-search")
async def batch_search(request_data: Dict[str, Any]):
    """Perform batch search with multiple queries"""
    service_metrics["requests_total"] += 1
    
    try:
        queries = request_data["queries"]
        engine = request_data.get("engine", "auto")
        num_results = request_data.get("num_results", 5)
        
        results = {}
        
        for query in queries:
            search_results = []
            
            if engine == "auto" or engine == "duckduckgo":
                ddg_results = await duckduckgo_search(query, num_results)
                search_results.extend(ddg_results)
            
            if engine == "auto" or engine == "bing":
                bing_results = await bing_search(query, num_results)
                search_results.extend(bing_results)
            
            # Remove duplicates
            seen_urls = set()
            unique_results = []
            for result in search_results:
                if result["url"] not in seen_urls:
                    seen_urls.add(result["url"])
                    unique_results.append(result)
            
            results[query] = unique_results[:num_results]
            service_metrics["searches_performed"] += 1
        
        return {
            "queries": queries,
            "engine": engine,
            "results": results,
            "search_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Batch search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze-domain/{domain}")
async def analyze_domain(domain: str):
    """Analyze a domain for basic information"""
    service_metrics["requests_total"] += 1
    
    try:
        if not domain.startswith(('http://', 'https://')):
            url = f"https://{domain}"
        else:
            url = domain
            domain = urlparse(url).netloc
        
        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=30.0,
            follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Basic analysis
            result = {
                "domain": domain,
                "url": str(response.url),
                "status_code": response.status_code,
                "title": soup.title.string.strip() if soup.title else "",
                "description": "",
                "keywords": "",
                "language": soup.get('lang', ''),
                "links_count": len(soup.find_all('a', href=True)),
                "images_count": len(soup.find_all('img', src=True)),
                "scripts_count": len(soup.find_all('script')),
                "stylesheets_count": len(soup.find_all('link', rel='stylesheet')),
                "meta_tags": {}
            }
            
            # Extract meta information
            for meta in soup.find_all('meta'):
                if meta.get('name') == 'description':
                    result["description"] = meta.get('content', '')
                elif meta.get('name') == 'keywords':
                    result["keywords"] = meta.get('content', '')
                elif meta.get('name'):
                    result["meta_tags"][meta.get('name')] = meta.get('content', '')
                elif meta.get('property'):
                    result["meta_tags"][meta.get('property')] = meta.get('content', '')
            
            # Check for common technologies
            technologies = []
            if soup.find('script', src=re.compile(r'jquery', re.I)):
                technologies.append('jQuery')
            if soup.find('script', src=re.compile(r'react', re.I)):
                technologies.append('React')
            if soup.find('script', src=re.compile(r'angular', re.I)):
                technologies.append('Angular')
            if soup.find('script', src=re.compile(r'vue', re.I)):
                technologies.append('Vue.js')
            
            result["technologies"] = technologies
            
            return result
            
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Domain analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8082
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
'''
    
    async def start(self) -> bool:
        """Start the WebSearch MCP service"""
        if self.running:
            logger.warning("WebSearch MCP service is already running")
            return True
        
        try:
            logger.info(f"Starting WebSearch MCP service on {self.host}:{self.port}")
            
            # Create server script if it doesn't exist
            server_script_path = Path("websearch_mcp_server.py")
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
                logger.info("WebSearch MCP service started successfully")
                return True
            else:
                logger.error("WebSearch MCP service failed to start properly")
                await self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start WebSearch MCP service: {e}")
            self.service_instance.status = ServiceStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """Stop the WebSearch MCP service"""
        if not self.running:
            logger.warning("WebSearch MCP service is not running")
            return True
        
        try:
            logger.info("Stopping WebSearch MCP service")
            
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
            logger.info("WebSearch MCP service stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop WebSearch MCP service: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart the WebSearch MCP service"""
        logger.info("Restarting WebSearch MCP service")
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
    
    # High-level search and scraping operations
    
    async def search(self, query: str, engine: str = "auto", num_results: int = 10) -> Dict[str, Any]:
        """Perform web search"""
        try:
            params = {
                "q": query,
                "engine": engine,
                "num_results": num_results
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{self.host}:{self.port}/search",
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to perform search: {e}")
            raise
    
    async def scrape_page(self, url: str, include_links: bool = False, include_images: bool = False, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """Scrape a web page"""
        try:
            data = {
                "url": url,
                "include_links": include_links,
                "include_images": include_images,
                "selectors": selectors or {}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{self.host}:{self.port}/scrape",
                    json=data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to scrape page: {e}")
            raise
    
    async def extract_content(self, url: str, content_type: str = "text") -> Dict[str, Any]:
        """Extract specific content from a webpage"""
        try:
            data = {
                "url": url,
                "content_type": content_type
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{self.host}:{self.port}/extract-content",
                    json=data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to extract content: {e}")
            raise
    
    async def batch_search(self, queries: List[str], engine: str = "auto", num_results: int = 5) -> Dict[str, Any]:
        """Perform batch search with multiple queries"""
        try:
            data = {
                "queries": queries,
                "engine": engine,
                "num_results": num_results
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{self.host}:{self.port}/batch-search",
                    json=data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to perform batch search: {e}")
            raise
    
    async def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze a domain for basic information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{self.host}:{self.port}/analyze-domain/{domain}"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to analyze domain: {e}")
            raise


# Factory function for creating WebSearch service instances
def create_websearch_service(config: Dict[str, Any] = None) -> WebSearchMCPService:
    """Create a new WebSearch MCP service instance"""
    return WebSearchMCPService(config)


# Example usage and testing
if __name__ == "__main__":
    async def test_websearch_service():
        """Test the WebSearch MCP service"""
        service = create_websearch_service({
            "host": "localhost",
            "port": 8082,
            "search_engines": ["duckduckgo", "bing"]
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
            
            # Test search
            search_results = await service.search("python programming", num_results=5)
            print(f"Search found {search_results['total_results']} results")
            
            # Test page scraping
            if search_results['results']:
                first_url = search_results['results'][0]['url']
                scrape_result = await service.scrape_page(first_url)
                print(f"Scraped page: {scrape_result['title']} ({len(scrape_result['content'])} chars)")
            
            # Test batch search
            batch_results = await service.batch_search(["python", "javascript", "rust"])
            print(f"Batch search completed for {len(batch_results['queries'])} queries")
            
        except Exception as e:
            print(f"Test error: {e}")
        finally:
            # Stop service
            await service.stop()
            print("Service stopped")
    
    # Run the test
    asyncio.run(test_websearch_service())