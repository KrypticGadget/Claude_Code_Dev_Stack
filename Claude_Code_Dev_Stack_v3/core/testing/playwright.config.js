// Playwright Configuration for Headed Browser Testing
// @ts-check
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  // Test directory
  testDir: './tests',
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter to use
  reporter: [
    ['html', { outputFolder: 'test-results/html-report' }],
    ['json', { outputFile: 'test-results/test-results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['line']
  ],
  
  // Shared settings for all the projects below
  use: {
    // Base URL for tests
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Capture screenshot on failure
    screenshot: 'only-on-failure',
    
    // Capture video on failure
    video: 'retain-on-failure',
    
    // Global test timeout
    actionTimeout: 10000,
    
    // Navigation timeout
    navigationTimeout: 30000,
  },

  // Configure projects for major browsers (headed mode by default)
  projects: [
    // Desktop Browsers - Headed Mode
    {
      name: 'chromium-headed',
      use: { 
        ...devices['Desktop Chrome'],
        headless: false,
        viewport: { width: 1920, height: 1080 },
        launchOptions: {
          slowMo: 500, // Slow down actions for visual testing
          devtools: true, // Open devtools
        }
      },
    },
    
    {
      name: 'firefox-headed',
      use: { 
        ...devices['Desktop Firefox'],
        headless: false,
        viewport: { width: 1920, height: 1080 },
        launchOptions: {
          slowMo: 500,
        }
      },
    },
    
    {
      name: 'webkit-headed',
      use: { 
        ...devices['Desktop Safari'],
        headless: false,
        viewport: { width: 1920, height: 1080 },
        launchOptions: {
          slowMo: 500,
        }
      },
    },
    
    // Desktop Browsers - Headless Mode (for CI/CD)
    {
      name: 'chromium-headless',
      use: { 
        ...devices['Desktop Chrome'],
        headless: true,
      },
    },
    
    {
      name: 'firefox-headless',
      use: { 
        ...devices['Desktop Firefox'],
        headless: true,
      },
    },
    
    {
      name: 'webkit-headless',
      use: { 
        ...devices['Desktop Safari'],
        headless: true,
      },
    },

    // Mobile Browsers - Headed Mode
    {
      name: 'mobile-chrome-headed',
      use: { 
        ...devices['Pixel 5'],
        headless: false,
        launchOptions: {
          slowMo: 300,
        }
      },
    },
    
    {
      name: 'mobile-safari-headed',
      use: { 
        ...devices['iPhone 12'],
        headless: false,
        launchOptions: {
          slowMo: 300,
        }
      },
    },

    // Visual Testing Projects
    {
      name: 'visual-chromium',
      use: { 
        ...devices['Desktop Chrome'],
        headless: false,
        viewport: { width: 1920, height: 1080 },
        launchOptions: {
          slowMo: 1000, // Extra slow for visual testing
        }
      },
      testMatch: '**/visual/**/*.spec.js',
    },
    
    {
      name: 'visual-firefox',
      use: { 
        ...devices['Desktop Firefox'],
        headless: false,
        viewport: { width: 1920, height: 1080 },
        launchOptions: {
          slowMo: 1000,
        }
      },
      testMatch: '**/visual/**/*.spec.js',
    },

    // Accessibility Testing
    {
      name: 'accessibility',
      use: { 
        ...devices['Desktop Chrome'],
        headless: false,
        viewport: { width: 1920, height: 1080 },
      },
      testMatch: '**/accessibility/**/*.spec.js',
    },

    // Performance Testing
    {
      name: 'performance',
      use: { 
        ...devices['Desktop Chrome'],
        headless: false,
        viewport: { width: 1920, height: 1080 },
        launchOptions: {
          args: ['--enable-performance-manager-experimental'],
        }
      },
      testMatch: '**/performance/**/*.spec.js',
    },
  ],

  // Global setup and teardown
  globalSetup: './global-setup.js',
  globalTeardown: './global-teardown.js',

  // Configure web server for local development
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },

  // Output directories
  outputDir: 'test-results/artifacts',
  
  // Test timeout
  timeout: 60000,
  
  // Expect timeout
  expect: {
    timeout: 10000,
  },
});