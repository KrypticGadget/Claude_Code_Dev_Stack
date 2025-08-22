#!/usr/bin/env node

/**
 * Playwright MCP Server
 * Provides browser automation capabilities via Playwright
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { chromium, firefox, webkit } from 'playwright';
import { randomUUID } from 'crypto';

class PlaywrightMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'playwright-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.browsers = new Map();
    this.pages = new Map();
    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'launch_browser',
          description: 'Launch a new browser instance',
          inputSchema: {
            type: 'object',
            properties: {
              browserType: {
                type: 'string',
                description: 'Browser type to launch',
                enum: ['chromium', 'firefox', 'webkit'],
                default: 'chromium',
              },
              headless: {
                type: 'boolean',
                description: 'Run browser in headless mode',
                default: true,
              },
              viewport: {
                type: 'object',
                description: 'Browser viewport settings',
                properties: {
                  width: { type: 'number', default: 1920 },
                  height: { type: 'number', default: 1080 },
                },
              },
            },
          },
        },
        {
          name: 'navigate',
          description: 'Navigate to a URL',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: {
                type: 'string',
                description: 'Page ID (optional, creates new page if not provided)',
              },
              url: {
                type: 'string',
                description: 'URL to navigate to',
              },
              waitUntil: {
                type: 'string',
                description: 'When to consider navigation successful',
                enum: ['load', 'domcontentloaded', 'networkidle'],
                default: 'load',
              },
            },
            required: ['url'],
          },
        },
        {
          name: 'click',
          description: 'Click an element on the page',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: { type: 'string', description: 'Page ID' },
              selector: { type: 'string', description: 'CSS selector for the element' },
              options: {
                type: 'object',
                description: 'Click options',
                properties: {
                  button: { type: 'string', enum: ['left', 'right', 'middle'], default: 'left' },
                  clickCount: { type: 'number', default: 1 },
                  delay: { type: 'number', description: 'Delay in ms between mousedown and mouseup' },
                },
              },
            },
            required: ['pageId', 'selector'],
          },
        },
        {
          name: 'type_text',
          description: 'Type text into an input field',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: { type: 'string', description: 'Page ID' },
              selector: { type: 'string', description: 'CSS selector for the input field' },
              text: { type: 'string', description: 'Text to type' },
              delay: { type: 'number', description: 'Delay between keystrokes in ms', default: 0 },
            },
            required: ['pageId', 'selector', 'text'],
          },
        },
        {
          name: 'screenshot',
          description: 'Take a screenshot of the page',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: { type: 'string', description: 'Page ID' },
              fullPage: { type: 'boolean', description: 'Capture full page', default: false },
              clip: {
                type: 'object',
                description: 'Clip area',
                properties: {
                  x: { type: 'number' },
                  y: { type: 'number' },
                  width: { type: 'number' },
                  height: { type: 'number' },
                },
              },
            },
            required: ['pageId'],
          },
        },
        {
          name: 'get_text',
          description: 'Get text content from an element',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: { type: 'string', description: 'Page ID' },
              selector: { type: 'string', description: 'CSS selector for the element' },
            },
            required: ['pageId', 'selector'],
          },
        },
        {
          name: 'evaluate',
          description: 'Execute JavaScript in the page context',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: { type: 'string', description: 'Page ID' },
              script: { type: 'string', description: 'JavaScript code to execute' },
            },
            required: ['pageId', 'script'],
          },
        },
        {
          name: 'wait_for_selector',
          description: 'Wait for a selector to appear on the page',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: { type: 'string', description: 'Page ID' },
              selector: { type: 'string', description: 'CSS selector to wait for' },
              timeout: { type: 'number', description: 'Timeout in ms', default: 30000 },
              state: {
                type: 'string',
                description: 'State to wait for',
                enum: ['attached', 'detached', 'visible', 'hidden'],
                default: 'visible',
              },
            },
            required: ['pageId', 'selector'],
          },
        },
        {
          name: 'close_page',
          description: 'Close a browser page',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: { type: 'string', description: 'Page ID to close' },
            },
            required: ['pageId'],
          },
        },
        {
          name: 'close_browser',
          description: 'Close a browser instance',
          inputSchema: {
            type: 'object',
            properties: {
              browserId: { type: 'string', description: 'Browser ID to close' },
            },
            required: ['browserId'],
          },
        },
        {
          name: 'list_browsers',
          description: 'List active browser instances',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'list_pages',
          description: 'List active pages',
          inputSchema: {
            type: 'object',
            properties: {
              browserId: {
                type: 'string',
                description: 'Browser ID to list pages for (optional)',
              },
            },
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'launch_browser':
            return await this.launchBrowser(args);
          case 'navigate':
            return await this.navigate(args);
          case 'click':
            return await this.click(args);
          case 'type_text':
            return await this.typeText(args);
          case 'screenshot':
            return await this.screenshot(args);
          case 'get_text':
            return await this.getText(args);
          case 'evaluate':
            return await this.evaluate(args);
          case 'wait_for_selector':
            return await this.waitForSelector(args);
          case 'close_page':
            return await this.closePage(args);
          case 'close_browser':
            return await this.closeBrowser(args);
          case 'list_browsers':
            return await this.listBrowsers();
          case 'list_pages':
            return await this.listPages(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async launchBrowser(args) {
    const { browserType = 'chromium', headless = true, viewport = { width: 1920, height: 1080 } } = args;
    const browserId = randomUUID();

    try {
      let browser;
      switch (browserType) {
        case 'chromium':
          browser = await chromium.launch({ headless });
          break;
        case 'firefox':
          browser = await firefox.launch({ headless });
          break;
        case 'webkit':
          browser = await webkit.launch({ headless });
          break;
        default:
          throw new Error(`Unsupported browser type: ${browserType}`);
      }

      const context = await browser.newContext({ viewport });
      const page = await context.newPage();
      const pageId = randomUUID();

      this.browsers.set(browserId, { browser, context, type: browserType });
      this.pages.set(pageId, { page, browserId });

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              browserId,
              pageId,
              browserType,
              status: 'launched',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to launch browser: ${error.message}`);
    }
  }

  async navigate(args) {
    const { pageId, url, waitUntil = 'load' } = args;
    
    let page;
    if (pageId) {
      const pageInfo = this.pages.get(pageId);
      if (!pageInfo) {
        throw new Error(`Page not found: ${pageId}`);
      }
      page = pageInfo.page;
    } else {
      // Create new page if none specified
      if (this.browsers.size === 0) {
        throw new Error('No browser instances available. Launch a browser first.');
      }
      const browserId = this.browsers.keys().next().value;
      const browserInfo = this.browsers.get(browserId);
      page = await browserInfo.context.newPage();
      const newPageId = randomUUID();
      this.pages.set(newPageId, { page, browserId });
    }

    try {
      await page.goto(url, { waitUntil });
      const title = await page.title();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              url,
              title,
              status: 'navigated',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Navigation failed: ${error.message}`);
    }
  }

  async click(args) {
    const { pageId, selector, options = {} } = args;
    const pageInfo = this.pages.get(pageId);
    
    if (!pageInfo) {
      throw new Error(`Page not found: ${pageId}`);
    }

    try {
      await pageInfo.page.click(selector, options);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              selector,
              action: 'clicked',
              status: 'success',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Click failed: ${error.message}`);
    }
  }

  async typeText(args) {
    const { pageId, selector, text, delay = 0 } = args;
    const pageInfo = this.pages.get(pageId);
    
    if (!pageInfo) {
      throw new Error(`Page not found: ${pageId}`);
    }

    try {
      await pageInfo.page.fill(selector, ''); // Clear existing text
      await pageInfo.page.type(selector, text, { delay });
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              selector,
              text: text.length > 50 ? `${text.substring(0, 50)}...` : text,
              action: 'typed',
              status: 'success',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Type text failed: ${error.message}`);
    }
  }

  async screenshot(args) {
    const { pageId, fullPage = false, clip } = args;
    const pageInfo = this.pages.get(pageId);
    
    if (!pageInfo) {
      throw new Error(`Page not found: ${pageId}`);
    }

    try {
      const screenshot = await pageInfo.page.screenshot({
        fullPage,
        clip,
        type: 'png',
      });
      
      const base64Screenshot = screenshot.toString('base64');
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              action: 'screenshot',
              size: screenshot.length,
              format: 'png',
              fullPage,
              status: 'success',
            }, null, 2),
          },
          {
            type: 'image',
            data: base64Screenshot,
            mimeType: 'image/png',
          },
        ],
      };
    } catch (error) {
      throw new Error(`Screenshot failed: ${error.message}`);
    }
  }

  async getText(args) {
    const { pageId, selector } = args;
    const pageInfo = this.pages.get(pageId);
    
    if (!pageInfo) {
      throw new Error(`Page not found: ${pageId}`);
    }

    try {
      const text = await pageInfo.page.textContent(selector);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              selector,
              text,
              action: 'getText',
              status: 'success',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Get text failed: ${error.message}`);
    }
  }

  async evaluate(args) {
    const { pageId, script } = args;
    const pageInfo = this.pages.get(pageId);
    
    if (!pageInfo) {
      throw new Error(`Page not found: ${pageId}`);
    }

    try {
      const result = await pageInfo.page.evaluate(script);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              script: script.length > 100 ? `${script.substring(0, 100)}...` : script,
              result,
              action: 'evaluate',
              status: 'success',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Script evaluation failed: ${error.message}`);
    }
  }

  async waitForSelector(args) {
    const { pageId, selector, timeout = 30000, state = 'visible' } = args;
    const pageInfo = this.pages.get(pageId);
    
    if (!pageInfo) {
      throw new Error(`Page not found: ${pageId}`);
    }

    try {
      await pageInfo.page.waitForSelector(selector, { timeout, state });
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              selector,
              state,
              action: 'waitForSelector',
              status: 'success',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Wait for selector failed: ${error.message}`);
    }
  }

  async closePage(args) {
    const { pageId } = args;
    const pageInfo = this.pages.get(pageId);
    
    if (!pageInfo) {
      throw new Error(`Page not found: ${pageId}`);
    }

    try {
      await pageInfo.page.close();
      this.pages.delete(pageId);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              pageId,
              action: 'closePage',
              status: 'success',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Close page failed: ${error.message}`);
    }
  }

  async closeBrowser(args) {
    const { browserId } = args;
    const browserInfo = this.browsers.get(browserId);
    
    if (!browserInfo) {
      throw new Error(`Browser not found: ${browserId}`);
    }

    try {
      // Close all pages for this browser
      for (const [pageId, pageInfo] of this.pages) {
        if (pageInfo.browserId === browserId) {
          this.pages.delete(pageId);
        }
      }
      
      await browserInfo.browser.close();
      this.browsers.delete(browserId);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              browserId,
              action: 'closeBrowser',
              status: 'success',
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Close browser failed: ${error.message}`);
    }
  }

  async listBrowsers() {
    const browsers = Array.from(this.browsers.entries()).map(([id, info]) => ({
      browserId: id,
      type: info.type,
      pagesCount: Array.from(this.pages.values()).filter(p => p.browserId === id).length,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(browsers, null, 2),
        },
      ],
    };
  }

  async listPages(args) {
    const { browserId } = args;
    
    let pages = Array.from(this.pages.entries()).map(([id, info]) => ({
      pageId: id,
      browserId: info.browserId,
      url: info.page.url(),
    }));

    if (browserId) {
      pages = pages.filter(p => p.browserId === browserId);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(pages, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Playwright MCP Server running');
  }
}

// Create and start server
const server = new PlaywrightMCPServer();
server.run().catch(console.error);